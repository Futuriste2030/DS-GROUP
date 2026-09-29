from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from .models import SiteSettings, FAQ, Partner, SiteStat, SkillBar, ProcessStep, Feature, TimelineEvent, LegalPage, LegalArticle, CookieConsent, CookieConsentLog


@admin.register(FAQ)
class FAQAdmin(TabbedTranslationAdmin):
    list_display = ['question', 'order']
    list_editable = ['order']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


@admin.register(Partner)
class PartnerAdmin(TabbedTranslationAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']


@admin.register(SiteSettings)
class SiteSettingsAdmin(TabbedTranslationAdmin):
    fieldsets = (
        ('Company', {'fields': ('company_name', 'company_short_name', 'site_url', 'logo', 'footer_description')}),
        ('SEO', {'fields': ('meta_description', 'meta_keywords', 'meta_author')}),
        ('Contact', {'fields': ('phone', 'email', 'careers_email', 'address', 'map_query', 'opening_hours_weekdays', 'opening_hours_weekend', 'latitude', 'longitude')}),
        ('Legal', {'classes': ('collapse',), 'fields': ('nif', 'rccm', 'director_name', 'hosting_provider', 'hosting_address', 'hosting_city_country')}),
        ('Social', {'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url', 'pinterest_url')}),
        ('About', {'fields': ('about_title', 'about_description', 'about_description_2', 'about_section_title', 'about_section_subtitle', 'about_image_1', 'about_image_2', 'vision_title', 'vision_description', 'mission_title', 'mission_description', 'process_title', 'process_description', 'why_subtitle', 'why_title', 'why_image_1', 'why_image_2')}),
        ('Vidéo du site', {'description': 'Liens + covers des vidéos (hero, showcase About, section Why, modales). Vide = vidéo et image de démo.', 'fields': ('about_video_url', 'about_video_cover')}),
        ('Hero', {'fields': ('hero_badge', 'hero_title', 'hero_description', 'hero_image_1', 'hero_image_2', 'hero_image_3', 'hero_video_url', 'hero_video_cover')}),
        ('Sections', {'fields': ('services_section_title', 'contact_image', 'coming_soon_enabled', 'launch_date')}),
    )
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteStat)
class SiteStatAdmin(TabbedTranslationAdmin):
    list_display = ['value', 'suffix', 'label', 'order']
    list_editable = ['order']


@admin.register(SkillBar)
class SkillBarAdmin(TabbedTranslationAdmin):
    list_display = ['label', 'percentage', 'order']
    list_editable = ['order', 'percentage']


@admin.register(ProcessStep)
class ProcessStepAdmin(TabbedTranslationAdmin):
    list_display = ['number', 'title', 'order']
    list_editable = ['order']


@admin.register(Feature)
class FeatureAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']


@admin.register(TimelineEvent)
class TimelineEventAdmin(TabbedTranslationAdmin):
    list_display = ['year', 'title', 'order']
    list_editable = ['order']


class LegalArticleInline(TranslationTabularInline):
    model = LegalArticle
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


@admin.register(LegalPage)
class LegalPageAdmin(TabbedTranslationAdmin):
    list_display = ['get_page_type_display', 'title', 'version_number']
    inlines = [LegalArticleInline]
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ['short_id', 'statistics', 'marketing', 'policy_version', 'updated_at']
    list_filter = ['statistics', 'marketing', 'policy_version']
    readonly_fields = ['consent_id', 'session_key', 'ip_hash', 'user_agent', 'created_at', 'updated_at']
    search_fields = ['consent_id', 'session_key']

    def short_id(self, obj):
        return str(obj.consent_id)[:8]
    short_id.short_description = 'Consent ID'


class CookieConsentLogInline(admin.TabularInline):
    model = CookieConsentLog
    extra = 0
    readonly_fields = ['action', 'statistics', 'marketing', 'policy_version', 'created_at']
    can_delete = False
    fields = ['action', 'statistics', 'marketing', 'policy_version', 'created_at']


# Attach history inline to consent admin
CookieConsentAdmin.inlines = [CookieConsentLogInline]


@admin.register(CookieConsentLog)
class CookieConsentLogAdmin(admin.ModelAdmin):
    list_display = ['consent', 'action', 'statistics', 'marketing', 'policy_version', 'created_at']
    list_filter = ['action', 'statistics', 'marketing']
    readonly_fields = ['consent', 'action', 'statistics', 'marketing', 'policy_version', 'ip_hash', 'user_agent', 'created_at']
    search_fields = ['consent__consent_id']
