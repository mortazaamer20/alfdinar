# مبادرة ألف دينار — Backend (Django)

Server-rendered Django backend for the **«مبادرة ألف دينار»** initiative
website. All public content (cases, the live monthly-cycle dashboard,
statistics and FAQ) is managed from the Django admin, and the public
**contact** and **subscription** forms are stored in the database for staff
to review.

## Stack

- Python 3.12+ (developed on 3.13)
- Django 6.0
- SQLite (default)
- Pillow (case photo uploads)

## Project layout

```
config/                 Django project (settings, urls, wsgi/asgi)
core/                   Main app
├── models.py           Tag, Case, Cycle, Statistic, FAQ,
│                       ContactMessage, SubscriptionRequest
├── forms.py            Public contact + subscription forms
├── views.py            Home, About, How, Cases, Contact
├── admin.py            Arabic admin for every model
├── templatetags/
│   └── ar_extras.py    `|ar` filter → Arabic-Indic numerals
├── management/commands/
│   └── seed_demo.py    Loads the site's default content
├── templates/core/     base.html + one template per page
└── static/core/        styles.css, app.js, logo, per-page CSS
```

## Getting started

```bash
# 1. Create a virtualenv (Python 3.12+) and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Apply migrations
python manage.py migrate

# 3. Load the default content (cases, cycle, stats, FAQ)
python manage.py seed_demo

# 4. Create an admin account
python manage.py createsuperuser

# 5. Run
python manage.py runserver
```

Then open:

- Site: <http://127.0.0.1:8000/>
- Admin: <http://127.0.0.1:8000/admin/>

## Pages → URLs

| Page            | URL          | View                |
|-----------------|--------------|---------------------|
| الرئيسية        | `/`          | `core.views.home`   |
| عن المبادرة     | `/about/`    | `core.views.about`  |
| كيف تعمل        | `/how/`      | `core.views.how`    |
| الحالات         | `/cases/`    | `core.views.cases`  |
| تواصل معنا      | `/contact/`  | `core.views.contact`|

## Managing content

Everything shown on the site is editable in the admin:

- **الحالات (Cases):** title, location, photo, tags, collected/target amounts
  (in dinars), status (قيد الدعم / مكتملة), `عاجلة` flag, and
  `إظهار في الصفحة الرئيسية` to feature it on the homepage.
- **الدورات (Cycles):** the one flagged `الدورة الحالية` drives the live
  homepage dashboard (progress ring, subscriber counts, fund total).
- **الإحصاءات (Statistics):** the hero chips, the homepage stat band, and the
  transparency band on the About page.
- **الأسئلة الشائعة (FAQ):** questions/answers on the «كيف تعمل» page.
- **رسائل التواصل / طلبات الاشتراك:** submissions from the two public forms.

> Amounts are stored in Iraqi dinars and displayed in millions/thousands.
> Numbers are rendered as Arabic-Indic numerals via the `|ar` template filter.

## Notes

- `seed_demo` is idempotent — it resets the content models (but never the
  submitted forms) and reloads the defaults.
- For production: set `DEBUG = False`, configure `ALLOWED_HOSTS`, move
  `SECRET_KEY` to an environment variable, and run `collectstatic`.

## تذكير واتساب الشهري (OTPIQ)

المبادرة مفتوحة للجميع، والمساهمة اختيارية (ألف دينار فأكثر). يمكن إرسال
تذكير شهري لطيف للمساهمين عبر واتساب باستخدام خدمة OTPIQ.

**الإعداد:** عيّن متغيّر البيئة على الخادم (مثل PythonAnywhere) — لا تضعه في الكود:

```bash
export OTPIQ_API_KEY="ضع_المفتاح_هنا"
# اختياري: export OTPIQ_PROVIDER="whatsapp"   # whatsapp | sms | auto
```

**الإرسال يدوياً / مجدولاً:**

```bash
python manage.py send_monthly_reminders            # إرسال فعلي
python manage.py send_monthly_reminders --dry-run  # معاينة دون إرسال
python manage.py send_monthly_reminders --once-per-month  # تخطّي من ذُكّر مؤخراً
```

جدوِل الأمر مرّة شهرياً عبر **Scheduled Tasks** في PythonAnywhere.
الرسالة لبقة وتتضمّن رقم محفظة سوبر كي تلقائياً.

> إن غيّرت OTPIQ أسماء الحقول، فالتعديل في مكان واحد:
> `core/services/otpiq.py` (الدالة `_build_payload`). راجع <https://docs.otpiq.com>.

## محتوى يُدار من لوحة التحكم (إضافات)

- **معلومات التحويل (سوبر كي):** رقم المحفظة واسم صاحبها وملاحظة — يظهر في صفحة
  المساهمة مع زرّ نسخ. حدّث الرقم من القائمة «معلومات التحويل».
- **الزيارات الميدانية:** زيارات عوائل الشهداء والجرحى (عنوان، موقع، تاريخ،
  مقتطف، تفاصيل، صورة)، مع خيار الإظهار في الصفحة الرئيسية. تظهر في صفحة
  «الزيارات الميدانية».
- **الدورة:** أضف «المبلغ المجموع فعلياً» ليُعرض المبلغ الحقيقي في الرئيسية
  بدل افتراض ألف دينار لكل مشترك.
