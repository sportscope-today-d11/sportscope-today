from django.shortcuts import render, get_object_or_404, redirect
from .models import Team, Match, News, Player
from django.utils.timezone import localtime
from datetime import datetime
from collections import defaultdict
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import MatchForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json

# ------------------------------
# TEAM VIEWS
# ------------------------------

def team_list(request):
    """Tampilkan daftar semua tim"""
    teams = Team.objects.all().order_by('name')
    return render(request, 'teams/team_list.html', {'teams': teams})


def team_detail(request, slug):
    """Tampilkan detail tim tertentu"""
    team = get_object_or_404(Team, slug=slug)

    # Ambil semua pertandingan di mana tim ini terlibat
    home_matches = team.home_matches.all()
    away_matches = team.away_matches.all()

    # Gabungkan keduanya (bisa dipakai untuk riwayat pertandingan)
    matches = home_matches.union(away_matches).order_by('-match_date')

    return render(request, 'teams/team_detail.html', {
        'team': team,
        'matches': matches
    })


# ------------------------------
# MATCH VIEWS
# ------------------------------

def match_detail(request, match_id):
    """Tampilkan detail satu pertandingan"""
    match = get_object_or_404(Match.objects.select_related('home_team', 'away_team'), id=match_id)
    return render(request, 'match_detail.html', {'match': match})

def match_history(request):
    # Ambil semua data pertandingan, urutkan dari terbaru
    matches = Match.objects.all().order_by('-match_date')

    # Ambil parameter filter dari query GET
    competition = request.GET.get('competition')
    date = request.GET.get('date')

    # Terapkan filter kalau ada input dari user
    if competition:
        matches = matches.filter(league__iexact=competition)
    if date:
        matches = matches.filter(match_date=date)

    # Pagination
    paginator = Paginator(matches, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ambil daftar kompetisi unik untuk dropdown
    competitions = Match.objects.values_list('league', flat=True).distinct()

    context = {
        'page_obj': page_obj,
        'competitions': competitions,
        'request': request,  # biar bisa akses di template
    }

    # Kalau AJAX (filter via JS), kirim partial HTML aja
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/match_list_partial.html', context, request=request)
        return JsonResponse({'html': html})

    # Render normal (HTML utuh)
    return render(request, 'match_history.html', context)

def matches_by_date(request, date):
    """Tampilkan semua pertandingan berdasarkan tanggal (format YYYY-MM-DD)"""
    try:
        # Parse tanggal dari URL (misal "2025-10-24")
        match_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        # Kalau format salah, fallback ke hari ini
        match_date = localtime().date()

    # Ambil match sesuai tanggal
    matches = Match.objects.filter(match_date=match_date).select_related('home_team', 'away_team')

    # Kelompokkan berdasarkan liga
    matches_by_league = {}
    for match in matches:
        matches_by_league.setdefault(match.league, []).append(match)

    # Render ke template
    return render(request, "matches.html", {
        "matches_by_league": matches_by_league,
        "match_date": match_date,
    })


# ------------------------------
# Admin Views for Match Management
# ------------------------------

def is_admin(user):
    return user.is_staff  # cuma admin yang bisa lewat

@user_passes_test(is_admin)
def match_list_admin(request):
    matches = Match.objects.all().order_by('-match_date')
    paginator = Paginator(matches, 10)  # 10 pertandingan per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'match_list_admin.html', {'page_obj': page_obj})

@user_passes_test(is_admin)
def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pertandingan berhasil ditambahkan!')
            return redirect('main:admin_match_list')
    else:
        form = MatchForm()
    return render(request, 'match_form.html', {'form': form, 'title': 'Tambah Pertandingan'})

@user_passes_test(is_admin)
def edit_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data pertandingan berhasil diperbarui!')
            return redirect('main:admin_match_list')
    else:
        form = MatchForm(instance=match)
    return render(request, 'match_form.html', {'form': form, 'title': 'Edit Pertandingan'})

@user_passes_test(is_admin)
def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    match.delete()
    messages.success(request, 'Pertandingan berhasil dihapus!')
    return redirect('main:admin_match_list')

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

    if len(hero_featured) >= 8:
        hero_main = hero_featured[0]
        hero_bottom = hero_featured[1:3]
        hero_right = hero_featured[3:8]
    elif len(hero_featured) >= 3:
        hero_main = hero_featured[0]
        hero_bottom = hero_featured[1:3]
        hero_right = hero_featured[3:]
    elif len(hero_featured) > 0:
        hero_main = hero_featured[0]
        hero_bottom = []
        hero_right = []
    else:
        hero_main = None
        hero_bottom = []
        hero_right = []

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
            response.set_cookie('last_login', str(datetime.now()))
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
