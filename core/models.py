"""Database models for the «ألف دينار» initiative site.

All public-facing content (cases, the monthly cycle dashboard, statistics and
FAQ) is editable from the Django admin, and the two public forms (contact +
subscription) are stored here for staff to review.
"""
from django.db import models

# Monthly contribution per subscriber, in Iraqi dinars. Used to derive the
# fund totals shown on the homepage dashboard from the subscriber count.
CONTRIBUTION_DINARS = 1000


class Tag(models.Model):
    """A small coloured label shown on a case card (e.g. «عاجل»، «علاج»)."""

    DEFAULT = 'default'
    GOLD = 'gold'
    URGENT = 'urgent'
    DONE = 'done'
    VARIANT_CHOICES = [
        (DEFAULT, 'أخضر (افتراضي)'),
        (GOLD, 'ذهبي'),
        (URGENT, 'عاجل (أحمر)'),
        (DONE, 'مكتملة'),
    ]

    name = models.CharField('الاسم', max_length=60, unique=True)
    variant = models.CharField('النمط', max_length=10, choices=VARIANT_CHOICES, default=DEFAULT)

    class Meta:
        verbose_name = 'وسم'
        verbose_name_plural = 'الوسوم'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def css_class(self):
        return {
            self.DEFAULT: 'tag',
            self.GOLD: 'tag tag--gold',
            self.URGENT: 'tag tag--urgent',
            self.DONE: 'tag tag--done',
        }[self.variant]


class Case(models.Model):
    """A beneficiary case displayed on the homepage and the cases page."""

    ACTIVE = 'active'
    DONE = 'done'
    STATUS_CHOICES = [
        (ACTIVE, 'قيد الدعم'),
        (DONE, 'مكتملة'),
    ]

    title = models.CharField('العنوان', max_length=160)
    location = models.CharField('الموقع', max_length=120, blank=True)
    description = models.TextField('الوصف', blank=True)
    image = models.ImageField('الصورة', upload_to='cases/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, verbose_name='الوسوم', blank=True, related_name='cases')

    collected_amount = models.BigIntegerField('المبلغ المجموع (دينار)', default=0,help_text='أدخل المبلغ بالدينار كاملاً، مثال: ٣٢٠٠٠٠٠ (٣٫٢ مليون). يُعرض تلقائياً بالملايين.')
    target_amount = models.BigIntegerField('المبلغ المستهدف (دينار)', default=0,help_text='أدخل المبلغ بالدينار كاملاً، مثال: ٥٠٠٠٠٠٠ (٥ مليون).')

    status = models.CharField('الحالة', max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    is_urgent = models.BooleanField('عاجلة', default=False)
    show_on_home = models.BooleanField('إظهار في الصفحة الرئيسية', default=False)

    order = models.PositiveIntegerField('الترتيب', default=0)
    created_at = models.DateTimeField('تاريخ الإضافة', auto_now_add=True)

    class Meta:
        verbose_name = 'حالة'
        verbose_name_plural = 'الحالات'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_done(self):
        return self.status == self.DONE

    @property
    def percent(self):
        if not self.target_amount:
            return 0
        return min(100, round(self.collected_amount / self.target_amount * 100))

    @property
    def data_cat(self):
        """Space-separated categories consumed by the client-side filter."""
        cats = []
        if self.is_urgent:
            cats.append('urgent')
        cats.append(self.status)
        return ' '.join(cats)

    def _millions(self, value):
        m = value / 1_000_000
        return ('%g' % round(m, 1)).replace('.', '٫')

    @property
    def collected_millions(self):
        return self._millions(self.collected_amount)

    @property
    def target_millions(self):
        return self._millions(self.target_amount)


class Cycle(models.Model):
    """A monthly fundraising cycle. The one flagged «current» drives the
    live dashboard on the homepage."""

    month_label = models.CharField('عنوان الدورة', max_length=60, help_text='مثال: حزيران ٢٠٢٦')
    target_subscribers = models.PositiveIntegerField('عدد المشتركين المستهدف', default=0)
    current_subscribers = models.PositiveIntegerField('عدد المشتركين الحالي', default=0)
    amount_collected = models.BigIntegerField(
        'المبلغ المجموع فعلياً (دينار)', default=0,
        help_text='المبلغ الحقيقي المجموع هذه الدورة بالدينار — يُعرض في الصفحة الرئيسية. مثال: ٧٥٠٠٠٠')
    active_cases = models.PositiveIntegerField('عدد الحالات قيد الدعم', default=0)
    is_current = models.BooleanField('الدورة الحالية', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'دورة'
        verbose_name_plural = 'الدورات'
        ordering = ['-created_at']

    def __str__(self):
        return self.month_label

    @property
    def percent(self):
        if not self.target_subscribers:
            return 0
        return min(100, round(self.current_subscribers / self.target_subscribers * 100))

    @property
    def remaining(self):
        return max(0, self.target_subscribers - self.current_subscribers)

    @property
    def collected_fmt(self):
        """The actual amount raised this cycle, formatted with its unit.

        Western digits are kept here and converted to Arabic-Indic by the
        ``|ar`` template filter (which leaves the Arabic unit word intact).
        e.g. 750000 -> "750 ألف" , 8400000 -> "8.4 مليون".
        """
        v = self.amount_collected
        if v >= 1_000_000:
            return ('%g' % round(v / 1_000_000, 1)) + ' مليون'
        if v >= 1000:
            return '%d ألف' % (v // 1000)
        return str(v)

    @property
    def target_total(self):
        """Illustrative minimum monthly fund (target subscribers × 1000)."""
        return self.target_subscribers * CONTRIBUTION_DINARS

    @property
    def ring_offset(self):
        """stroke-dashoffset for the SVG progress ring (dasharray = 402)."""
        return round(402 * (1 - self.percent / 100))


class Statistic(models.Model):
    """A free-form headline number shown in the hero chips, the stat band or
    the transparency band. The value is stored as text so staff can type it in
    Arabic numerals exactly as it should appear."""

    HERO = 'hero'
    BAND = 'band'
    TRANSPARENCY = 'transparency'
    GROUP_CHOICES = [
        (HERO, 'شريط البطل (الرئيسية)'),
        (BAND, 'شريط الإحصاءات (الرئيسية)'),
        (TRANSPARENCY, 'شريط الشفافية (عن المبادرة)'),
    ]

    group = models.CharField('المجموعة', max_length=15, choices=GROUP_CHOICES)
    value = models.CharField('القيمة', max_length=40, help_text='مثال: ٨٫٤ مليون أو ١٠٠٪')
    label = models.CharField('الوصف', max_length=120)
    order = models.PositiveIntegerField('الترتيب', default=0)

    class Meta:
        verbose_name = 'إحصائية'
        verbose_name_plural = 'الإحصاءات'
        ordering = ['group', 'order']

    def __str__(self):
        return f'{self.value} — {self.label}'


class FAQ(models.Model):
    """A question/answer pair shown on the «كيف تعمل» page."""

    question = models.CharField('السؤال', max_length=255)
    answer = models.TextField('الجواب')
    is_open = models.BooleanField('مفتوح افتراضياً', default=False)
    order = models.PositiveIntegerField('الترتيب', default=0)

    class Meta:
        verbose_name = 'سؤال شائع'
        verbose_name_plural = 'الأسئلة الشائعة'
        ordering = ['order']

    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    """A message submitted through the contact form."""

    SUBJECT_CHOICES = [
        ('استفسار عن الاشتراك', 'استفسار عن الاشتراك'),
        ('ترشيح حالة للدعم', 'ترشيح حالة للدعم'),
        ('اقتراح أو ملاحظة', 'اقتراح أو ملاحظة'),
        ('تطوّع / شراكة', 'تطوّع / شراكة'),
        ('أخرى', 'أخرى'),
    ]

    name = models.CharField('الاسم', max_length=120)
    phone = models.CharField('رقم الهاتف', max_length=30, blank=True)
    email = models.EmailField('البريد الإلكتروني', blank=True)
    subject = models.CharField('الموضوع', max_length=40, choices=SUBJECT_CHOICES)
    message = models.TextField('الرسالة')
    is_read = models.BooleanField('تمت المعالجة', default=False)
    created_at = models.DateTimeField('تاريخ الإرسال', auto_now_add=True)

    class Meta:
        verbose_name = 'رسالة تواصل'
        verbose_name_plural = 'رسائل التواصل'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.subject}'


class SubscriptionRequest(models.Model):
    """A subscription request submitted through the «اشترك الآن» form.

    Open to everyone (not only officers). The phone number is preferably a
    WhatsApp number, used to send the optional monthly reminder via OTPIQ.
    """

    AMOUNT_CHOICES = [
        ('١٬٠٠٠ دينار (الحد الأدنى)', '١٬٠٠٠ دينار (الحد الأدنى)'),
        ('٢٬٠٠٠ دينار', '٢٬٠٠٠ دينار'),
        ('٥٬٠٠٠ دينار', '٥٬٠٠٠ دينار'),
        ('١٠٬٠٠٠ دينار', '١٠٬٠٠٠ دينار'),
        ('مبلغ آخر', 'مبلغ آخر'),
    ]

    NEW = 'new'
    CONTACTED = 'contacted'
    DONE = 'done'
    STATUS_CHOICES = [
        (NEW, 'جديد'),
        (CONTACTED, 'تم التواصل'),
        (DONE, 'مكتمل'),
    ]

    full_name = models.CharField('الاسم الكامل', max_length=160)
    phone = models.CharField('رقم الهاتف (واتساب)', max_length=30,
                             help_text='يُفضّل أن يكون مرتبطاً بواتساب لاستلام التذكير الشهري.')
    monthly_amount = models.CharField('المساهمة الشهرية', max_length=40, choices=AMOUNT_CHOICES,
                                      default='١٬٠٠٠ دينار (الحد الأدنى)')
    consent = models.BooleanField('الموافقة', default=False)
    whatsapp_opt_in = models.BooleanField('استلام تذكير واتساب الشهري', default=True)
    is_active = models.BooleanField('مشترك فعّال', default=True,
                                    help_text='ألغِ التفعيل لإيقاف التذكيرات عن هذا الشخص.')
    last_reminder_at = models.DateTimeField('آخر تذكير', null=True, blank=True)
    status = models.CharField('الحالة', max_length=12, choices=STATUS_CHOICES, default=NEW)
    created_at = models.DateTimeField('تاريخ الطلب', auto_now_add=True)

    class Meta:
        verbose_name = 'طلب اشتراك'
        verbose_name_plural = 'طلبات الاشتراك'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


class PaymentInfo(models.Model):
    """Wallet / transfer details shown on the subscribe section (admin-managed).

    The most recently updated active record is displayed, so staff can update
    the SuperKey wallet number any time without code changes.
    """

    provider = models.CharField('مزوّد المحفظة', max_length=80, default='سوبر كي العراق')
    wallet_number = models.CharField('رقم المحفظة', max_length=60,
                                     help_text='الرقم الذي يحوّل إليه المتبرّع عبر تطبيق سوبر كي.')
    holder_name = models.CharField('اسم صاحب المحفظة', max_length=120, blank=True)
    fallback_phone = models.CharField('رقم الهاتف البديل للتحويل', max_length=30, blank=True,
                                      help_text='في حال تعذّر التحويل لرقم المحفظة، يمكن التحويل عبر هذا الرقم.')
    qr_image = models.ImageField('صورة QR للتحويل', upload_to='payment/', blank=True, null=True,
                                 help_text='صورة رمز الاستجابة السريعة (QR) للتحويل — اختيارية.')
    note = models.CharField('ملاحظة', max_length=200, blank=True,
                            help_text='تظهر أسفل رقم المحفظة، مثل: يُرجى إرسال الاسم بعد التحويل.')
    is_active = models.BooleanField('مفعّل', default=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)

    class Meta:
        verbose_name = 'معلومات التحويل'
        verbose_name_plural = 'معلومات التحويل'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.provider} — {self.wallet_number}'


class Visit(models.Model):
    """A field visit to a martyr's / wounded soldier's family."""

    title = models.CharField('العنوان', max_length=160)
    location = models.CharField('الموقع', max_length=120, blank=True)
    visit_date = models.DateField('تاريخ الزيارة', null=True, blank=True)
    summary = models.CharField('مقتطف', max_length=240, blank=True,
                               help_text='سطر مختصر يظهر في البطاقة والصفحة الرئيسية.')
    description = models.TextField('التفاصيل', blank=True)
    image = models.ImageField('الصورة', upload_to='visits/', blank=True, null=True)
    show_on_home = models.BooleanField('إظهار في الصفحة الرئيسية', default=False)
    order = models.PositiveIntegerField('الترتيب', default=0)
    created_at = models.DateTimeField('تاريخ الإضافة', auto_now_add=True)

    class Meta:
        verbose_name = 'زيارة ميدانية'
        verbose_name_plural = 'الزيارات الميدانية'
        ordering = ['order', '-visit_date', '-created_at']

    def __str__(self):
        return self.title

    @property
    def date_fmt(self):
        return self.visit_date.strftime('%Y-%m-%d') if self.visit_date else ''
