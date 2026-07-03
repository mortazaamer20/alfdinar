"""Server-rendered views for the «ألف دينار» site."""
from django.shortcuts import get_object_or_404, render

from .forms import ContactForm, SubscriptionForm
from .models import Case, Cycle, FAQ, PaymentInfo, Statistic, Visit


def _payment_info():
    return PaymentInfo.objects.filter(is_active=True).order_by('-updated_at').first()


def _current_cycle():
    return Cycle.objects.filter(is_current=True).first() or Cycle.objects.first()


def home(request):
    context = {
        'active_page': 'index',
        'cycle': _current_cycle(),
        'home_cases': Case.objects.prefetch_related('tags').filter(show_on_home=True)[:3],
        'home_visits': Visit.objects.filter(show_on_home=True)[:3],
        'hero_stats': Statistic.objects.filter(group=Statistic.HERO),
        'band_stats': Statistic.objects.filter(group=Statistic.BAND),
    }
    return render(request, 'core/index.html', context)


def about(request):
    context = {
        'active_page': 'about',
        'transparency_stats': Statistic.objects.filter(group=Statistic.TRANSPARENCY),
    }
    return render(request, 'core/about.html', context)


def how(request):
    subscribed = False
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            subscribed = True
            form = SubscriptionForm()
    else:
        form = SubscriptionForm()

    context = {
        'active_page': 'how',
        'cycle': _current_cycle(),
        'faqs': FAQ.objects.all(),
        'form': form,
        'subscribed': subscribed,
        'payment': _payment_info(),
    }
    return render(request, 'core/how.html', context)


def visits(request):
    context = {
        'active_page': 'visits',
        'visits': Visit.objects.all(),
    }
    return render(request, 'core/visits.html', context)


def visit_detail(request, pk):
    visit = get_object_or_404(Visit.objects.prefetch_related('gallery_images'), pk=pk)
    context = {
        'active_page': 'visits',
        'visit': visit,
    }
    return render(request, 'core/visit_detail.html', context)


def cases(request):
    context = {
        'active_page': 'cases',
        'cases': Case.objects.prefetch_related('tags').all(),
    }
    return render(request, 'core/cases.html', context)


def case_detail(request, pk):
    case = get_object_or_404(
        Case.objects.prefetch_related('tags', 'gallery_images'), pk=pk)
    context = {
        'active_page': 'cases',
        'case': case,
    }
    return render(request, 'core/case_detail.html', context)


def contact(request):
    sent = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            sent = True
            form = ContactForm()
    else:
        form = ContactForm()

    context = {
        'active_page': 'contact',
        'form': form,
        'sent': sent,
    }
    return render(request, 'core/contact.html', context)
