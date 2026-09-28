from modeltranslation.translator import register, TranslationOptions
from .models import Post


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'category', 'author_name', 'author_bio', 'excerpt', 'content', 'reading_time', 'tags', 'meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description')
