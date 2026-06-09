"""Populate the database with the initiative's default content.

This mirrors the original static HTML so a fresh install renders identically.
It is idempotent: it clears the content models (not the submitted forms) and
recreates them on each run.

    python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Case, Cycle, FAQ, Statistic, Tag

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
            active_cases=9,
            is_current=True,
        )

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
             'تُشرف رابطة ضباط الحشد الشعبي ولجنة مالية مستقلة على إدارة الصندوق، '
             'وتضمن وصول الدعم دون أي اقتطاعات إدارية.', False, 3),
            ('كيف تُختار الحالات المستفيدة؟',
             'تُدرس كل حالة وفق معايير واضحة للاستحقاق والإلحاح، وتُعطى الأولوية للعوائل '
             'المتعففة وعوائل الشهداء والحالات الطارئة.', False, 4),
            ('هل المبادرة مقتصرة على الضباط فقط؟',
             'تنطلق المبادرة من ضباط الحشد الشعبي كنواة أساسية، مع إمكانية توسّعها مستقبلاً '
             'لتشمل داعمين آخرين.', False, 5),
        ]
        for question, answer, is_open, order in faqs:
            FAQ.objects.create(question=question, answer=answer, is_open=is_open, order=order)

        self.stdout.write(self.style.SUCCESS('تم تعبئة البيانات الافتراضية بنجاح.'))
