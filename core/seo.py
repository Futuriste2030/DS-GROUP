"""SEO helper — même logique que DIGI-AGENCY (adapté BS GROUP)."""


def absolute_url(request, path):
    if not path:
        return ''
    if path.startswith(('http://', 'https://')):
        return path
    if not path.startswith('/'):
        path = '/' + path
    return f'{request.scheme}://{request.get_host()}{path}'


def seo_for(request, obj=None, *, title=None, description=None, image=None):
    data = {}
    og_title = og_description = None
    if obj is not None:
        if title is None:
            title = obj.get_meta_title()
        og_title = obj.get_og_title()
        if description is None:
            description = obj.get_meta_description()
        og_description = obj.get_og_description()
        image = image or obj.get_og_image()
        if getattr(obj, 'canonical_url', ''):
            data['canonical_url'] = obj.canonical_url
        robots = 'noindex' if getattr(obj, 'noindex', False) else 'index'
        robots += ', nofollow' if getattr(obj, 'nofollow', False) else ', follow'
        data['page_robots'] = robots
        data['page_twitter_card'] = getattr(obj, 'twitter_card', '') or 'summary_large_image'
    if title:
        data['page_og_title'] = title
    if og_title and og_title != title:
        data['page_og_title'] = og_title
    if description:
        data['page_meta_description'] = description
    if og_description and og_description != description:
        data['page_og_description'] = og_description
    elif description:
        data['page_og_description'] = description
    if image:
        data['page_og_image'] = absolute_url(request, image)
    return data
