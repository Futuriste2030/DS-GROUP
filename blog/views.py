"""Vues blog BS GROUP — même logique que DIGI (filtre, recherche, pagination)."""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from core.seo import seo_for
from .models import Post


def blogs(request):
    posts = Post.objects.all()
    category = request.GET.get('category', '').strip()
    if category:
        posts = posts.filter(category=category)
    query = request.GET.get('q', '').strip()
    if query:
        posts = posts.filter(title__icontains=query)
    paginator = Paginator(posts, 6)
    posts_page = paginator.get_page(request.GET.get('page', 1))
    all_tags = set()
    for p in Post.objects.all():
        all_tags.update(p.tags_list())
    categories = Post.objects.values_list('category', flat=True).distinct().order_by('category')
    return render(request, 'blog/blogs.html', {
        **seo_for(request, title=_('News & Blogs')),
        'posts': posts_page,
        'all_tags': sorted(all_tags),
        'categories': categories,
        'recent_posts': Post.objects.all()[:3],
        'active_category': category,
    })


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    related = Post.objects.exclude(pk=post.pk)[:3]
    all_tags = set()
    for p in Post.objects.all():
        all_tags.update(p.tags_list())
    categories = Post.objects.values_list('category', flat=True).distinct().order_by('category')
    return render(request, 'blog/blog-detail.html', {
        **seo_for(request, obj=post),
        'post': post,
        'related_posts': related,
        'all_tags': sorted(all_tags),
        'categories': categories,
        'recent_posts': Post.objects.all()[:3],
    })
