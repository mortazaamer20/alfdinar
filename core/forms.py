"""Public forms: contact message + subscription request.

Widget ids/placeholders mirror the original static markup so the existing CSS
and ``<label for=...>`` associations keep working unchanged.
"""
from django import forms

from .models import ContactMessage, SubscriptionRequest


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'id': 'cn', 'placeholder': 'اسمك الكامل'}),
            'phone': forms.TextInput(attrs={'id': 'cp', 'type': 'tel', 'placeholder': '07XX XXX XXXX'}),
            'email': forms.EmailInput(attrs={'id': 'ce', 'placeholder': 'name@example.com'}),
            'subject': forms.Select(attrs={'id': 'ct'}),
            'message': forms.Textarea(attrs={'id': 'cm', 'placeholder': 'اكتب رسالتك هنا…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].choices = [('', 'اختر الموضوع…')] + list(ContactMessage.SUBJECT_CHOICES)
        # Phone/email are optional on the public form.
        self.fields['phone'].required = False
        self.fields['email'].required = False


class SubscriptionForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        error_messages={'required': 'يجب الموافقة على الالتزام بالمساهمة وسياسة الشفافية.'},
    )

    class Meta:
        model = SubscriptionRequest
        fields = ['full_name', 'rank', 'unit', 'phone', 'monthly_amount', 'consent']
        widgets = {
            'full_name': forms.TextInput(attrs={'id': 'n', 'placeholder': 'الاسم الثلاثي'}),
            'rank': forms.TextInput(attrs={'id': 'r', 'placeholder': 'مثال: نقيب'}),
            'unit': forms.TextInput(attrs={'id': 'u', 'placeholder': 'اسم الوحدة'}),
            'phone': forms.TextInput(attrs={'id': 'p', 'type': 'tel', 'placeholder': '07XX XXX XXXX'}),
            'monthly_amount': forms.Select(attrs={'id': 'a'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rank'].required = False
        self.fields['unit'].required = False
