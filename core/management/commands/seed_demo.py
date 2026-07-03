"""Populate the database with the initiative's default content.

This mirrors the original static HTML so a fresh install renders identically.
It is idempotent: it clears the content models (not the submitted forms) and
recreates them on each run.

    python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.db import transaction

import datetime

from core.models import Case, Cycle, FAQ, PaymentInfo, Statistic, Tag, Visit

M = 1_000_000  # one million dinars


class Command(BaseCommand):
    help = 'Seed the database with the default «ألف دينار» content.'

    @transaction.atomic
    def handle(self, *args, **options):
        # Reset content models (leave ContactMessage / SubscriptionRequest alone).
        Case.objects.all().delete()
        Tag.objects.all().delete()
        Cycle.objects.all().delete()
        Statistic.objects.all().delete()
        FAQ.objects.all().delete()
        Visit.objects.all().delete()
        PaymentInfo.objects.all().delete()

        # --- Tags ---------------------------------------------------------
        tag_specs = {
            'عاجل': Tag.URGENT,
            'مكتملة': Tag.DONE,
            'شهري': Tag.GOLD,
            'علاج': Tag.DEFAULT,
            'سلال غذائية': Tag.DEFAULT,
            'ترميم': Tag.DEFAULT,
            'إيواء': Tag.DEFAULT,
            'أدوية': Tag.DEFAULT,
            'تعليم': Tag.DEFAULT,
            'كسوة': Tag.DEFAULT,
        }
        tags = {name: Tag.objects.create(name=name, variant=variant)
                for name, variant in tag_specs.items()}

        # --- Cases --------------------------------------------------------
        cases = [
            dict(title='تغطية عملية جراحية لطفل', location='بغداد — الكرخ',
                 description='طفلٌ بحاجة لعملية جراحية عاجلة تعجز عائلته عن تغطية تكاليفها.',
                 collected_amount=int(3.2 * M), target_amount=5 * M,
                 status=Case.ACTIVE, is_urgent=True, show_on_home=True, order=1,
                 tags=['عاجل', 'علاج']),
            dict(title='سلال غذائية لـ٢٠ عائلة', location='ديالى — بعقوبة',
                 description='توزيع سلال غذائية شهرية على عشرين عائلة متعففة ضمن الدورة الحالية.',
                 collected_amount=int(4.4 * M), target_amount=5 * M,
                 status=Case.ACTIVE, is_urgent=False, show_on_home=True, order=2,
                 tags=['شهري', 'سلال غذائية']),
            dict(title='ترميم منزل عائلة شهيد', location='صلاح الدين — تكريت',
                 description='إعادة تأهيل منزلٍ آيلٍ للسقوط تسكنه عائلة أحد الشهداء.',
                 collected_amount=int(2.1 * M), target_amount=5 * M,
                 status=Case.ACTIVE, is_urgent=False, show_on_home=True, order=3,
                 tags=['ترميم', 'إيواء']),
            dict(title='أدوية مزمنة لمسنّة', location='النجف',
                 description='توفير أدوية شهرية لمريضةٍ مسنّة تعيش بمفردها دون معيل.',
                 collected_amount=int(1.1 * M), target_amount=int(1.5 * M),
                 status=Case.ACTIVE, is_urgent=True, show_on_home=False, order=4,
                 tags=['عاجل', 'أدوية']),
            dict(title='مستلزمات مدرسية لـ٤٠ طالباً', location='بابل — الحلة',
                 description='تم تجهيز أربعين طالباً من عوائل متعففة بالحقائب والقرطاسية.',
                 collected_amount=3 * M, target_amount=3 * M,
                 status=Case.DONE, is_urgent=False, show_on_home=False, order=5,
                 tags=['مكتملة', 'تعليم']),
            dict(title='كسوة الشتاء لعوائل الشهداء', location='الأنبار — الرمادي',
                 description='تم توزيع كسوة شتوية على خمس عشرة عائلة من عوائل الشهداء.',
                 collected_amount=4 * M, target_amount=4 * M,
                 status=Case.DONE, is_urgent=False, show_on_home=False, order=6,
                 tags=['مكتملة', 'كسوة']),
        ]
        for spec in cases:
            tag_names = spec.pop('tags')
            case = Case.objects.create(**spec)
            case.tags.set([tags[name] for name in tag_names])

        # --- Current cycle ------------------------------------------------
        Cycle.objects.create(
            month_label='حزيران ٢٠٢٦',
            target_subscribers=746,
            current_subscribers=581,
            amount_collected=1_240_000,  # actual dinars raised this cycle
            active_cases=9,
            is_current=True,
        )

        # --- Payment / wallet info (replace with the real number in admin) -
        PaymentInfo.objects.create(
            provider='سوبر كي العراق',
            wallet_number='8916737730',
            holder_name='مبادرة لن ننسى أبطالنا',
            fallback_phone='07736835130',
            note='يُرجى إرسال اسمك بعد التحويل عبر نموذج التواصل ليُسجّل ضمن الدورة.',
            is_active=True,
        )

        # --- Field visits -------------------------------------------------
        visits = [
            dict(title='زيارة عائلة الشهيد أبو حيدر', location='بغداد — الكرّادة',
                 visit_date=datetime.date(2026, 6, 5), show_on_home=True, order=1,
                 summary='وقفنا إلى جانب العائلة بسلّةٍ غذائية ودعمٍ نقدي، واطمأننا على أبنائها.',
                 description='زار وفد التجمع منزل عائلة الشهيد، وقدّم الدعم المادي والمعنوي، '
                             'واستمع إلى احتياجاتها لإدراجها ضمن خطة الدعم القادمة.'),
            dict(title='زيارة جريحٍ من أبطال الحشد', location='النجف الأشرف',
                 visit_date=datetime.date(2026, 5, 22), show_on_home=True, order=2,
                 summary='زيارة تفقّدية لأحد الجرحى وتقديم مساعدة لعلاجه ومتابعة حالته.',
                 description='اطمأن الوفد على صحة الجريح، وقدّم مساهمةً لتغطية جزءٍ من تكاليف '
                             'العلاج والأدوية، مع متابعةٍ دورية لحالته.'),
            dict(title='زيارة عائلة شهيدٍ في بعقوبة', location='ديالى — بعقوبة',
                 visit_date=datetime.date(2026, 5, 9), show_on_home=True, order=3,
                 summary='تسليم سلال غذائية ومستلزمات للعائلة قبيل بداية الدورة.',
                 description='ضمن جولات التجمع الميدانية، سُلّمت العائلة سلالاً غذائية '
                             'ومستلزمات أساسية، مع كلمة وفاءٍ لتضحيات الشهيد.'),
        ]
        for spec in visits:
            Visit.objects.create(**spec)

        # --- Statistics ---------------------------------------------------
        stats = [
            (Statistic.HERO, '١٠٠٪', 'شفافية مالية', 1),
            (Statistic.HERO, '١٤', 'دورة منذ الانطلاق', 2),
            (Statistic.BAND, '٨٫٤ مليون', 'دينار وُزّعت منذ الانطلاق', 1),
            (Statistic.BAND, '١٣٢', 'عائلة استفادت من الدعم', 2),
            (Statistic.BAND, '١٤', 'دورة شهرية مكتملة', 3),
            (Statistic.BAND, '١٠٠٪', 'من التبرعات تصل للمستحقين', 4),
            (Statistic.TRANSPARENCY, '١٠٠٪', 'من المساهمات تصل للمستحقين', 1),
            (Statistic.TRANSPARENCY, '٠', 'اقتطاعات إدارية', 2),
            (Statistic.TRANSPARENCY, '١٤', 'كشف حساب منشور', 3),
        ]
        for group, value, label, order in stats:
            Statistic.objects.create(group=group, value=value, label=label, order=order)

        # --- FAQ ----------------------------------------------------------
        faqs = [
            ('كيف أتأكد من وصول مساهمتي لمستحقيها؟',
             'تُنشر بنهاية كل دورة كشوف حساب تفصيلية توضّح إجمالي المساهمات وأوجه الصرف '
             'والجهات المستفيدة، مع توثيق بالصور والتقارير.', True, 1),
            ('هل يمكنني تعديل قيمة مساهمتي أو إيقافها؟',
             'نعم، الاشتراك مرن تماماً ويمكنك تعديل المبلغ أو إيقاف المساهمة في أي وقت دون أي التزامات.',
             False, 2),
            ('من يُشرف على إدارة الأموال؟',
             'يُشرف تجمع ضباط الحشد الشعبي ولجنة مالية مستقلة على إدارة الصندوق، '
             'ويضمن وصول الدعم دون أي اقتطاعات إدارية.', False, 3),
            ('كيف تُختار الحالات المستفيدة؟',
             'تُدرس كل حالة وفق معايير واضحة للاستحقاق والإلحاح، وتُعطى الأولوية للعوائل '
             'المتعففة وعوائل الشهداء والحالات الطارئة.', False, 4),
            ('هل المبادرة مقتصرة على الضباط فقط؟',
             'لا، المبادرة مفتوحة للجميع. انطلقت برعاية تجمع ضباط الحشد الشعبي، '
             'لكنّ باب المساهمة متاحٌ لكل من يرغب بفعل الخير.', False, 5),
            ('كم مقدار المساهمة؟ وهل هي إلزامية؟',
             'المساهمة اختيارية تماماً، وحدّها الأدنى ألف دينار شهرياً، ويمكنك التبرّع بأكثر '
             'حسب استطاعتك. تُحوّل المبالغ عبر محفظة سوبر كي العراق المعروضة في صفحة المساهمة.', False, 6),
            ('كيف يصلني التذكير الشهري؟',
             'إن اخترت ذلك عند التسجيل، تصلك رسالة واتساب لطيفة شهرياً للتذكير بالمساهمة — '
             'ويمكنك إيقافها في أي وقت دون أي التزام.', False, 7),
        ]
        for question, answer, is_open, order in faqs:
            FAQ.objects.create(question=question, answer=answer, is_open=is_open, order=order)

        self.stdout.write(self.style.SUCCESS('تم تعبئة البيانات الافتراضية بنجاح.'))
