from modeltranslation.translator import register, TranslationOptions
from .models import SiteSettings, FAQ, Partner, SiteStat, SkillBar, ProcessStep, Feature, TimelineEvent, LegalPage, LegalArticle


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ('company_name', 'footer_description', 'address', 'opening_hours_weekdays', 'opening_hours_weekend', 'director_name', 'hosting_provider', 'hosting_address', 'hosting_city_country', 'company_short_name', 'about_title', 'about_description', 'about_description_2', 'about_section_title', 'about_section_subtitle', 'vision_title', 'vision_description', 'mission_title', 'mission_description', 'process_title', 'process_description', 'why_subtitle', 'why_title', 'hero_badge', 'hero_title', 'hero_description', 'services_section_title', 'meta_description', 'meta_keywords', 'meta_author')


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')


@register(Partner)
class PartnerTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(SiteStat)
class SiteStatTranslationOptions(TranslationOptions):
    fields = ('label',)


@register(SkillBar)
class SkillBarTranslationOptions(TranslationOptions):
    fields = ('label',)


@register(ProcessStep)
class ProcessStepTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(Feature)
class FeatureTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(TimelineEvent)
class TimelineEventTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(LegalPage)
class LegalPageTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'description', 'intro')


@register(LegalArticle)
class LegalArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
