import re

from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Post


@admin.register(Post)
class PostAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'slug', 'category', 'published']
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image', 'twitter_card', 'canonical_url', 'noindex', 'nofollow')

    # Seul 'content' est affiché avec |safe : seul lui a CKEditor.
    # Le reste (excerpt...) s'affiche en brut : textarea simple.
    rich_text_fields = {'content'}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        base = re.sub(r'_(fr|en|ar)$', '', db_field.name)
        if base in self.rich_text_fields:
            kwargs['widget'] = CKEditorWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)
