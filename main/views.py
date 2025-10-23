from django.shortcuts import render, get_object_or_404, redirect
from .models import Team, Match
from django.utils.timezone import localtime
from collections import defaultdict
from .models import News
from .forms import NewsForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q

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
 
def match_list(request):
    # Ambil tanggal hari ini
    today = localtime().date()
    matches = Match.objects.filter(match_date__date=today).order_by('league', 'match_date')

    # Kelompokkan berdasarkan liga
    matches_by_league = defaultdict(list)
    for match in matches:
        matches_by_league[match.league].append(match)

    context = {
        'match_date': today,
        'matches_by_league': dict(matches_by_league)
    }
    return render(request, 'main/matches.html', context)

def match_detail(request, match_id):
    """Tampilkan detail satu pertandingan"""
    match = get_object_or_404(Match.objects.select_related('home_team', 'away_team'), id=match_id)
    return render(request, 'matches/match_detail.html', {'match': match})

# ------------------------------
# NEWS VIEWS
# ------------------------------

def is_admin(user):
    return user.is_staff  # hanya admin/staff Django

def news_list(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    news_qs = News.objects.all().order_by('-publish_time')

    if q:
        news_qs = news_qs.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(source__icontains=q))
    if category:
        news_qs = news_qs.filter(category=category)

    paginator = Paginator(news_qs, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/news_list.html', {'news_items': page_obj, 'q': q, 'category': category})


def news_detail(request, news_id):
    """Menampilkan detail satu berita"""
    news = get_object_or_404(News, id=news_id)
    return render(request, 'news/news_detail.html', {'news': news})

@login_required
@user_passes_test(is_admin)
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:news_list')
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
            form.save()
            return redirect('main:news_detail', news_id=news.id)
    else:
        form = NewsForm(instance=news)
    return render(request, 'news/news_form.html', {'form': form, 'mode': 'edit'})

@login_required
@user_passes_test(is_admin)
def news_delete(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        news.delete()
        return redirect('main:news_list')
    return render(request, 'news/news_confirm_delete.html', {'news': news})
