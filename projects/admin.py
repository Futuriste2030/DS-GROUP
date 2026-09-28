from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from .models import Project, ProjectPoint, ProjectStep


class ProjectPointInline(TranslationTabularInline):
    model = ProjectPoint
    extra = 1


class ProjectStepInline(TranslationTabularInline):
    model = ProjectStep
    extra = 1


@admin.register(Project)
class ProjectAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'slug', 'category', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order']
    inlines = [ProjectPointInline, ProjectStepInline]
    exclude = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image', 'twitter_card', 'canonical_url', 'noindex', 'nofollow')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
