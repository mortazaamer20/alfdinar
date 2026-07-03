"""Send the optional monthly WhatsApp donation reminder via OTPIQ.

Schedule this once a month (e.g. a PythonAnywhere scheduled task):

    python manage.py send_monthly_reminders

It messages every active subscriber who opted in, with a polite, thankful
note and the current SuperKey wallet number. Use --dry-run to preview without
sending, and --once-per-month to skip people already reminded this month.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import PaymentInfo, SubscriptionRequest
from core.services import otpiq


def build_message(name, payment):
    """A warm, thankful Arabic reminder. Donation is explicitly optional."""
    lines = [
        f'السلام عليكم {name} 🌿',
        'تحية من «مبادرة لن ننسى أبطالنا» برعاية تجمع ضباط الحشد الشعبي.',
        'نشكر لك دعمك المتواصل لعوائلنا المتعففة وعوائل الشهداء والجرحى.',
        'حلّت دورة هذا الشهر، والمساهمة اختيارية تماماً — ألف دينار فأكثر، وكلٌّ حسب استطاعته.',
    ]
    if payment and payment.wallet_number:
        lines.append(f'للتحويل عبر {payment.provider}: {payment.wallet_number}')
    lines.append('شكراً لكرمكم، وجزاكم الله خيراً 🤍')
    return '\n'.join(lines)


class Command(BaseCommand):
    help = 'إرسال تذكير التبرّع الشهري عبر واتساب (OTPIQ).'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='اعرض الرسائل دون إرسالها فعلياً.')
        parser.add_argument('--once-per-month', action='store_true',
                            help='تجاوز من تم تذكيره خلال آخر ٢٥ يوماً.')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        payment = PaymentInfo.objects.filter(is_active=True).order_by('-updated_at').first()

        recipients = SubscriptionRequest.objects.filter(is_active=True, whatsapp_opt_in=True)
        if options['once_per_month']:
            cutoff = now - timezone.timedelta(days=25)
            recipients = recipients.filter(
                models_q_recent(cutoff)
            )

        sent = failed = 0
        for sub in recipients:
            message = build_message(sub.full_name, payment)
            if dry_run:
                self.stdout.write(f'[dry-run] → {sub.phone}\n{message}\n{"-"*40}')
                sent += 1
                continue
            ok, info = otpiq.send_message(sub.phone, message)
            if ok:
                sub.last_reminder_at = now
                sub.save(update_fields=['last_reminder_at'])
                sent += 1
            else:
                failed += 1
                self.stderr.write(f'فشل الإرسال إلى {sub.phone}: {info}')

        verb = 'سيتم إرسالها' if dry_run else 'أُرسلت'
        self.stdout.write(self.style.SUCCESS(
            f'{verb}: {sent} رسالة' + (f' · فشل: {failed}' if failed else '')))


def models_q_recent(cutoff):
    """Subscribers never reminded, or last reminded before the cutoff."""
    from django.db.models import Q
    return Q(last_reminder_at__isnull=True) | Q(last_reminder_at__lt=cutoff)
