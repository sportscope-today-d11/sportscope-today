from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.templatetags.static import static
from urllib.parse import urlparse

from .models import News
from .forms import NewsForm

def is_admin(user):
    return user.is_staff

# ------------------------------
# NEWS VIEWS
# ------------------------------

def news_list(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    news_qs = News.objects.all().order_by('-publish_time')

    if q:
        news_qs = news_qs.filter(
            Q(title__icontains=q) | Q(content__icontains=q) | Q(source__icontains=q)
        )
    if category:
        news_qs = news_qs.filter(category=category)

    paginator = Paginator(news_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/news_list.html', {
        'all_news': page_obj,
        'q': q,
        'category': category,
    })


def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'news/news_detail.html', {'news': news})


@login_required
@user_passes_test(is_admin)
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save()
            # Response AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': news.id,
                    'title': news.title,
                    'thumbnail': news.thumbnail_url,
                })
            return redirect('main:news_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = NewsForm()
    return render(request, 'news/news_form.html', {'form': form, 'mode': 'create'})


@login_required
@user_passes_test(is_admin)
def news_update(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            news = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': news.id})
            return redirect('main:news_detail', news_id=news.id)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = NewsForm(instance=news)
    return render(request, 'news/news_form.html', {'form': form, 'mode': 'edit'})


@login_required
@user_passes_test(is_admin)
def news_delete(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        news.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('main:news_list')
    return render(request, 'news/news_confirm_delete.html', {'news': news})
