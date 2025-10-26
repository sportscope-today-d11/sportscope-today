from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.templatetags.static import static
from urllib.parse import urlparse
from django.template.loader import render_to_string

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
    sort = request.GET.get('sort', 'latest')

    news_qs = News.objects.all()

    if q:
        news_qs = news_qs.filter(
            Q(title__icontains=q) | Q(content__icontains=q) | Q(source__icontains=q)
        )

    if category:
        news_qs = news_qs.filter(category__iexact=category)

    # Sorting
    if sort == 'oldest':
        news_qs = news_qs.order_by('publish_time')
    else:
        news_qs = news_qs.order_by('-publish_time')

    paginator = Paginator(news_qs, 9)
    page = request.GET.get('page')
    all_news = paginator.get_page(page)

    bookmarks = request.session.get('bookmarks', [])
    context = {
        'all_news': all_news,
        'sort': sort,
        'category': category,
        'bookmarked_ids': [int(x) for x in bookmarks],
    }
    return render(request, 'news_list.html', context)

def news_list_ajax(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'latest')
    bookmarked = request.GET.get('bookmarked', '')

    news_qs = News.objects.all()

    # Jika user klik "My Bookmarks"
    if bookmarked:
        bookmark_ids = request.session.get('bookmarks', [])
        news_qs = news_qs.filter(id__in=bookmark_ids)
    else:
        if q:
            news_qs = news_qs.filter(
                Q(title__icontains=q) | Q(content__icontains=q) | Q(source__icontains=q)
            )
        if category:
            news_qs = news_qs.filter(category__iexact=category)

    # Sorting
    news_qs = news_qs.order_by('publish_time' if sort == 'oldest' else '-publish_time')

    paginator = Paginator(news_qs, 9)
    page = request.GET.get('page')
    all_news = paginator.get_page(page)

    html = render_to_string('news_cards.html', {
        'all_news': all_news,
        'bookmarked_ids': [int(x) for x in request.session.get('bookmarks', [])],
        'user': request.user,
    })

    return JsonResponse({'html': html})

def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'news_detail.html', {'news': news})

def toggle_bookmark(request, news_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Login required'}, status=401)

    bookmarks = request.session.get('bookmarks', [])
    news_id = str(news_id)

    if news_id in bookmarks:
        bookmarks.remove(news_id)
        status = 'removed'
    else:
        bookmarks.append(news_id)
        status = 'added'

    request.session['bookmarks'] = bookmarks
    request.session.modified = True
    return JsonResponse({'success': True, 'status': status})

def bookmarked_news(request):
    bookmarks = request.session.get('bookmarks', [])
    news_qs = News.objects.filter(id__in=bookmarks)
    return render(request, 'news_list.html', {
        'all_news': news_qs,
        'is_bookmark_page': True,
        'bookmarked_ids': [int(x) for x in bookmarks],
    })

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
    return render(request, 'news_form.html', {'form': form, 'mode': 'create'})


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
    return render(request, 'news_form.html', {'form': form, 'mode': 'edit'})


@login_required
@user_passes_test(is_admin)
def news_delete(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        news.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('main:news_list')
    return render(request, 'news_confirm_delete.html', {'news': news})
