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
        form = RegisterForm(request.POST)  # ← Ganti jadi RegisterForm
        
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