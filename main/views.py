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
from main.models import Player, Person
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator

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

    # helpers to coerce types safely
    def to_int(v):
        try:
            if v is None:
                return None
            s = str(v).strip()
            if s == '':
                return None
            return int(float(s))
        except Exception:
            return None

    def to_float(v):
        try:
            if v is None:
                return None
            s = str(v).strip()
            if s == '':
                return None
            return float(s)
        except Exception:
            return None

    preferred_foot = (payload.get('preferred_foot') or '').strip()
    if preferred_foot not in ('Left', 'Right'):
        preferred_foot = None

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
