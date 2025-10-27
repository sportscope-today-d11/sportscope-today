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
from django.templatetags.static import static
from urllib.parse import urlparse
import json

# ------------------------------
# NEWS VIEWS
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
    match = get_object_or_404(
        Match.objects.select_related('home_team', 'away_team'), 
        id=match_id
    )

    # Fallback kalau league kosong
    if not match.league or match.league.strip() == "":
        match.league = "Premier League"

    context = {
        "match": match,
    }
    return render(request, "match_detail.html", context)

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
    return render(request, 'admin/match_list_admin.html', {'page_obj': page_obj})

@user_passes_test(is_admin)
def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match successfully added!')
            return redirect('main:admin_match_list')
    else:
        form = MatchForm()
    return render(request, 'admin/match_form.html', {'form': form, 'title': 'Add Match'})

@user_passes_test(is_admin)
def edit_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match data successfully updated!')
            return redirect('main:admin_match_list')
    else:
        form = MatchForm(instance=match)
    return render(request, 'admin/match_form.html', {'form': form, 'title': 'Match Edit'})

@user_passes_test(is_admin)
def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    match.delete()
    messages.success(request, 'This match is deleted!')
    return redirect('main:admin_match_list')
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import News, Team, Player, Person
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .forms import RegisterForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.utils.text import slugify

# View untuk halaman home yang menampilkan daftar pemain
def player_list(request):
    player_list = Player.objects.all().order_by('-likes')
    paginator = Paginator(player_list, 12)  # 12 pemain per halaman

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # pass both page_obj (for pagination controls) and players (iterable used in template)
    context = {'page_obj': page_obj, 'players': page_obj.object_list}
    context = {'page_obj': page_obj, 'players': page_obj.object_list, 'request':request}
    
    return render(request, 'player.html', context)

def player_detail(request, slug):
    player = get_object_or_404(Player, slug=slug)
    context = {'player': player}
    return render(request, 'player_detail.html', context)


@login_required
@require_POST
def player_add_ajax(request):
    """Add a Player via AJAX (expects JSON). Admin-only (Person.role == 'admin')."""
    # role check
    try:
        person = Person.objects.get(user=request.user)
    except Person.DoesNotExist:
        return JsonResponse({"status": "error", "message": "No role assigned"}, status=403)
    if person.role != 'admin':
        return JsonResponse({"status": "error", "message": "Admin only"}, status=403)

    import json
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    name = (payload.get('name') or '').strip()
    if not name:
        return JsonResponse({"status": "error", "message": "Name is required"}, status=400)

    from unidecode import unidecode
    from django.utils.text import slugify

    base = slugify(unidecode(name)) or 'player'
    slug = base
    i = 1
    while Player.objects.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1

    defaults = {
        'slug': slug,
        'name': name,
        'full_name': (payload.get('full_name') or '')[:255],
        'positions': (payload.get('positions') or '')[:100],
        'nationality': (payload.get('nationality') or '')[:100],
        'overall_rating': to_int(payload.get('overall_rating')),
        'age': to_int(payload.get('age')),
        'preferred_foot': preferred_foot,
        'height_cm': to_float(payload.get('height_cm')),
        'weight_kgs': to_float(payload.get('weight_kgs')),
        'international_reputation': to_int(payload.get('international_reputation')),
        # Shooting
        'finishing': to_int(payload.get('finishing')),
        'long_shots': to_int(payload.get('long_shots')),
        'penalties': to_int(payload.get('penalties')),
        # Passing
        'short_passing': to_int(payload.get('short_passing')),
        'long_passing': to_int(payload.get('long_passing')),
        'vision': to_int(payload.get('vision')),
        # Dribbling
        'dribbling': to_int(payload.get('dribbling')),
        'ball_control': to_int(payload.get('ball_control')),
        'agility': to_int(payload.get('agility')),
        # Pace
        'acceleration': to_int(payload.get('acceleration')),
        'sprint_speed': to_int(payload.get('sprint_speed')),
        # Physical
        'stamina': to_int(payload.get('stamina')),
        'strength': to_int(payload.get('strength')),
        'jumping': to_int(payload.get('jumping')),
        # Defending
        'marking': to_int(payload.get('marking')),
        'standing_tackle': to_int(payload.get('standing_tackle')),
        'sliding_tackle': to_int(payload.get('sliding_tackle')),
        # Market
        'value_euro': to_float(payload.get('value_euro')),
        'wage_euro': to_float(payload.get('wage_euro')),
        'release_clause_euro': to_float(payload.get('release_clause_euro')),
        # Likes (optional)
        'likes': max(0, to_int(payload.get('likes')) or 0),
    }

    player = Player.objects.create(**defaults)

    return JsonResponse({
        'status': 'success',
        'player': {
            'slug': player.slug,
            'name': player.name,
            'positions': player.positions,
            'nationality': player.nationality,
            'overall_rating': player.overall_rating,
            'age': player.age,
            'likes': player.likes,
            'image_url': player.image_url,
            'detail_url': reverse('main:player_detail', kwargs={'slug': player.slug}),
        }
    }, status=201)


# View untuk halaman home yang menampilkan daftar pemain
def player_list(request):
    player_list = Player.objects.all().order_by('-likes')
    paginator = Paginator(player_list, 12)  # 12 pemain per halaman

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # pass both page_obj (for pagination controls) and players (iterable used in template)
    context = {'page_obj': page_obj, 'players': page_obj.object_list, 'request':request}
    
    return render(request, 'player.html', context)

def player_detail(request, slug):
    player = get_object_or_404(Player, slug=slug)
    context = {'player': player}
    return render(request, 'player_detail.html', context)


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
    role = request.user.person.role
    return HttpResponse('<span>Role: </span>' + role)

def news_detail(request, news_id):
    role = request.user.person.role
    return HttpResponse('<span>Role: </span>' + role)


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

@require_POST
def ajax_login(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        errors = {}
        if not username:
            errors['username'] = 'Username is required'
        if not password:
            errors['password'] = 'Password is required'
            
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': f'Welcome back, {user.username}!',
                'redirect_url': reverse('main:homepage')
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': {'non_field_errors': 'Invalid username or password.'}
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def user_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)  # ← Ganti jadi RegisterForm
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    else:
        form = RegisterForm()  # ← Ganti jadi RegisterForm

    context = {'form': form}
    return render(request, 'register.html', context)

@require_POST
def ajax_register(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = RegisterForm(request.POST)  
        
        if form.is_valid():
            user = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Your account has been successfully created!',
            })
        else:
            # Collect all errors
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            
            return JsonResponse({
                'success': False,
                'errors': errors
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

# Tambahkan di views.py yang sudah ada

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

#  Helper decorator untuk check admin role
def admin_required(view_func):
    """Decorator untuk memastikan user adalah admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        
        try:
            if request.user.person.role != 'admin':
                return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)
        except Person.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User profile not found'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
@require_POST
def add_team(request):
    """Add new team - Admin only"""
    try:
        name = request.POST.get('name')
        goals = request.POST.get('goals')
        assists = request.POST.get('assists')
        yellows = request.POST.get('yellows')
        reds = request.POST.get('reds')
        possession = request.POST.get('possession')
        image = request.FILES.get('image')  # Get uploaded image
        
        # Validasi
        if not all([name, goals, assists, yellows, reds, possession]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required'
            })
        
        # Auto-generate slug dari nama
        slug = slugify(name)
        
        # Check if slug already exists
        if Team.objects.filter(slug=slug).exists():
            return JsonResponse({
                'success': False,
                'message': f'Team with name "{name}" already exists (slug: {slug})'
            })
        
        # Create team
        team = Team.objects.create(
            name=name,
            slug=slug,
            goals=int(goals),
            assists=int(assists),
            yellows=int(yellows),
            reds=int(reds),
            possession=float(possession),
            players=0,  # Set default value
            age=0.0,    # Set default value
            penalty_kicks=0,  # Set default value
            penalty_kick_attempts=0  # Set default value
        )
        
        # Handle image upload
        if image:
            # Generate filename: slug.extension (e.g., manchester-united.png)
            ext = os.path.splitext(image.name)[1]  # Get extension (.png, .jpg, etc)
            filename = f"{slug}{ext}"
            
            # Save to media/teams/ directory
            file_path = default_storage.save(f'teams/{filename}', ContentFile(image.read()))
            team.image = file_path
            team.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Team "{name}" has been added successfully!',
            'team_slug': team.slug
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': 'Invalid number format in one of the fields'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })


@login_required
@admin_required
@require_POST
def edit_team(request, team_slug):
    """Edit existing team - Admin only (NO IMAGE EDIT)"""
    try:
        # Gunakan slug sebagai identifier
        team = get_object_or_404(Team, slug=team_slug)
        
        name = request.POST.get('name')
        goals = request.POST.get('goals')
        assists = request.POST.get('assists')
        yellows = request.POST.get('yellows')
        reds = request.POST.get('reds')
        possession = request.POST.get('possession')
        
        # Validasi
        if not all([name, goals, assists, yellows, reds, possession]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required'
            })
        
        # Update team (SLUG dan IMAGE TIDAK BERUBAH)
        team.name = name
        team.goals = int(goals)
        team.assists = int(assists)
        team.yellows = int(yellows)
        team.reds = int(reds)
        team.possession = float(possession)
        team.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Team "{name}" has been updated successfully!'
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': 'Invalid number format in one of the fields'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })

@login_required
@admin_required
@require_POST
def delete_team(request, team_slug):
    """Delete team - Admin only"""
    try:
        team = get_object_or_404(Team, slug=team_slug)
        team_name = team.name
        
        # Delete image if exists
        if team.image:
            if default_storage.exists(team.image.name):
                default_storage.delete(team.image.name)
        
        team.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Team "{team_name}" has been deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })

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