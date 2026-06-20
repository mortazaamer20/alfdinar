from django.contrib import admin

from .models import (
    Case,
    ContactMessage,
    Cycle,
    FAQ,
    PaymentInfo,
    Statistic,
    SubscriptionRequest,
    Tag,
    Visit,
)

admin.site.site_header = 'إدارة مبادرة ألف دينار'
admin.site.site_title = 'مبادرة ألف دينار'
admin.site.index_title = 'لوحة التحكم'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'variant')
    list_filter = ('variant',)
    search_fields = ('name',)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'status', 'is_urgent', 'percent',
                    'show_on_home', 'order')
    list_filter = ('status', 'is_urgent', 'show_on_home', 'tags')
    list_editable = ('order', 'show_on_home')
    search_fields = ('title', 'location', 'description')
    filter_horizontal = ('tags',)

    @admin.display(description='نسبة الإنجاز')
    def percent(self, obj):
        return f'{obj.percent}٪'


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('month_label', 'current_subscribers', 'target_subscribers',
                    'amount_collected', 'percent', 'active_cases', 'is_current')
    list_editable = ('is_current',)

    @admin.display(description='نسبة الإنجاز')
    def percent(self, obj):
        return f'{obj.percent}٪'


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('value', 'label', 'group', 'order')
    list_filter = ('group',)
    list_editable = ('order',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_open', 'order')
    list_editable = ('is_open', 'order')
    search_fields = ('question', 'answer')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'phone', 'email', 'is_read', 'created_at')
    list_filter = ('is_read', 'subject', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('name', 'phone', 'email', 'message')
    readonly_fields = ('created_at',)


@admin.register(SubscriptionRequest)
class SubscriptionRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'monthly_amount', 'whatsapp_opt_in',
                    'is_active', 'status', 'last_reminder_at', 'created_at')
    list_filter = ('status', 'is_active', 'whatsapp_opt_in', 'monthly_amount', 'created_at')
    list_editable = ('is_active', 'status')
    search_fields = ('full_name', 'phone')
    readonly_fields = ('created_at', 'last_reminder_at')


@admin.register(PaymentInfo)
class PaymentInfoAdmin(admin.ModelAdmin):
    list_display = ('provider', 'wallet_number', 'holder_name', 'is_active', 'updated_at')
    list_editable = ('is_active',)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'visit_date', 'show_on_home', 'order')
    list_filter = ('show_on_home', 'visit_date')
    list_editable = ('show_on_home', 'order')
    search_fields = ('title', 'location', 'summary', 'description')
