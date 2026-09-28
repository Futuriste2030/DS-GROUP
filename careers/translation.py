from modeltranslation.translator import register, TranslationOptions
from .models import CareerPage, Perk, JobOpening


@register(CareerPage)
class CareerPageTranslationOptions(TranslationOptions):
    fields = ('hero_title', 'hero_subtitle', 'openings_title', 'openings_subtitle')


@register(Perk)
class PerkTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(JobOpening)
class JobOpeningTranslationOptions(TranslationOptions):
    fields = ('title', 'department', 'location', 'experience', 'salary', 'deadline', 'description', 'responsibilities', 'requirements', 'nice_to_have', 'meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description')
