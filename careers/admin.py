from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from modeltranslation.admin import TabbedTranslationAdmin
from .models import CareerPage, Perk, HiringStep, JobOpening, Application


@admin.register(CareerPage)
class CareerPageAdmin(TabbedTranslationAdmin):
    def has_add_permission(self, request):
        return not CareerPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Perk)
class PerkAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


@admin.register(HiringStep)
class HiringStepAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']


@admin.register(JobOpening)
class JobOpeningAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'job_type', 'is_active', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'order']
    exclude = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image', 'twitter_card', 'canonical_url', 'noindex', 'nofollow')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['reference', 'full_name', 'job', 'created_at']
    readonly_fields = ['reference', 'created_at']
