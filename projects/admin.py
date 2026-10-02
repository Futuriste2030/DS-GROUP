import re

from django.contrib import admin
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

    # Champs affichés avec |safe : CKEditor. Le reste (excerpt, intro...) : brut.
    rich_text_fields = {'description', 'challenge', 'solution', 'scope_description', 'result'}

    def formfield_for_dbfield(self, db_field, **kwargs):
        base = re.sub(r'_(fr|en|ar)$', '', db_field.name)
        if base in self.rich_text_fields:
            kwargs['widget'] = CKEditorWidget
        return super().formfield_for_dbfield(db_field, **kwargs)
