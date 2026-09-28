from modeltranslation.translator import register, TranslationOptions
from .models import Service, ServiceFeature, ServiceBenefit, ServiceStep


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'category', 'timeline', 'team_size', 'warranty', 'intro', 'approach_title', 'approach', 'includes_title', 'includes_description', 'benefits_title', 'benefits_description', 'process_title', 'process_description', 'image_1_alt', 'image_2_alt', 'video_cover_alt', 'meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description')


@register(ServiceFeature)
class ServiceFeatureTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(ServiceBenefit)
class ServiceBenefitTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(ServiceStep)
class ServiceStepTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
