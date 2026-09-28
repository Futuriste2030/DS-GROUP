from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Post


@admin.register(Post)
class PostAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'slug', 'category', 'published']
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image', 'twitter_card', 'canonical_url', 'noindex', 'nofollow')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
