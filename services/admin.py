from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from .models import Service, ServiceFeature, ServiceBenefit, ServiceStep


class ServiceFeatureInline(TranslationTabularInline):
    model = ServiceFeature
    extra = 1


class ServiceBenefitInline(TranslationTabularInline):
    model = ServiceBenefit
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


class ServiceStepInline(TranslationTabularInline):
    model = ServiceStep
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


@admin.register(Service)
class ServiceAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'slug', 'category', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order']
    inlines = [ServiceFeatureInline, ServiceBenefitInline, ServiceStepInline]
    exclude = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image', 'twitter_card', 'canonical_url', 'noindex', 'nofollow')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
