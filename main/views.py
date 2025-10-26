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

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from main.models import Player
from django.core.paginator import Paginator

# View untuk halaman home yang menampilkan daftar pemain
def player_list(request):
    player_list = Player.objects.all().order_by('-likes')
    paginator = Paginator(player_list, 12)  # 12 pemain per halaman

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # pass both page_obj (for pagination controls) and players (iterable used in template)
    context = {'page_obj': page_obj, 'players': page_obj.object_list}
    
    return render(request, 'player.html', context)

def player_detail(request, slug):
    player = get_object_or_404(Player, slug=slug)
    context = {'player': player}
    return render(request, 'player_detail.html', context)
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from django.shortcuts import render
from .models import News, Team, Player


def homepage(request):
    # --- NEWS SECTION --- 
    # Ambil berita featured random untuk layout hero
    featured_news = list(News.objects.filter(featured=True).order_by("?"))

    # Pisahkan berita berdasarkan thumbnail (default dan bukan default)
    left_featured = [news for news in featured_news if news.thumbnail == "default"][:12]
    
    # Ambil 8 berita hero
    hero_featured = [news for news in featured_news if news.thumbnail != "default"][:8]
    hero_main = hero_featured[0]  # Hero besar
    hero_bottom = hero_featured[1:3]  # 2 berita bawah hero
    hero_right = hero_featured[3:8]  # 5 berita di kanan

    # Kategori aktif
    categories = [
        "Transfer",
        "Injury Update",
        "Match Result",
        "Manager News",
        "Thoughts",
    ]

    # Berita per kategori (max 8 tiap kategori)
    news_by_category = {
        cat: News.objects.filter(category=cat).order_by("-publish_time")[:8]
        for cat in categories
    }

    # --- PREMIER LEAGUE TABLE --- 
    teams = Team.objects.all().order_by("-goals")  # Misal urut gol

    # --- TOP 10 MOST LOVED PLAYERS --- 
    top_players = Player.objects.order_by("-likes")[:10]

    context = {
        "left_news": left_featured,
        "hero_main": hero_main,
        "hero_bottom": hero_bottom,
        "hero_right": hero_right,
        "categories": categories,
        "news_by_category": news_by_category,
        "teams": teams,
        "top_players": top_players,
    }

    return render(request, "homepage.html", context)

def news_list(request):
    return HttpResponse('info')

def news_detail(request, news_id):
    return HttpResponse('info')

def user_register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'register.html', context)

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse('main:homepage'))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            messages.success(request, f'Welcome back, {user.username}!')
            return response
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm(request)

    context = {'form': form}
    return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:homepage'))
    response.delete_cookie('last_login')
    messages.info(request, 'You have been logged out successfully.')
    return response

def login_ajax(request):
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error", 
                "message": "Invalid request format!"
            })

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({
                "status": "error",
                "message": "Username and password are required!"
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                "status": "success",
                "redirect_url": reverse("main:homepage")
            })

        return JsonResponse({
            "status": "error", 
            "message": "Invalid username or password."
        })

    return JsonResponse({
        "status": "error", 
        "message": "Only POST method allowed."
    })
def user_register(request):
    return 

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
