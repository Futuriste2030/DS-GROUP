from django.contrib import admin
from .models import ContactMessage, QuoteRequest, NewsletterSubscriber, NotifySubscriber


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['reference', 'name', 'email', 'service', 'created_at']
    readonly_fields = ['reference', 'created_at']


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['reference', 'name', 'email', 'subject', 'created_at']
    readonly_fields = ['reference', 'created_at']


@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at']


@admin.register(NotifySubscriber)
class NotifyAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at']
