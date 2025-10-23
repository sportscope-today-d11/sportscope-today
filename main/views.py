from django.shortcuts import render, get_object_or_404, redirect
from .models import Team, Match
from django.utils.timezone import localtime
from collections import defaultdict
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import MatchForm

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
    return render(request, 'matches.html', context)

def match_detail(request, match_id):
    """Tampilkan detail satu pertandingan"""
    match = get_object_or_404(Match.objects.select_related('home_team', 'away_team'), id=match_id)
    return render(request, 'match_detail.html', {'match': match})

def match_history(request):
    matches = Match.objects.all().order_by('-match_date')

    team = request.GET.get('team')
    competition = request.GET.get('competition')

    if team:
        matches = matches.filter(
        Q(home_team__name__icontains=team) | Q(away_team__name__icontains=team)
    )
    if competition:
        matches = matches.filter(league__icontains=competition)

    paginator = Paginator(matches, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'match_history.html', {'page_obj': page_obj})


# ------------------------------
# Admin Views for Match Management
# ------------------------------

def match_list_admin(request):
    matches = Match.objects.all().order_by('-date')
    return render(request, 'match_list_admin.html', {'matches': matches})

def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_match_list')
    else:
        form = MatchForm()
    return render(request, 'match_form.html', {'form': form, 'title': 'Tambah Pertandingan'})

def edit_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('admin_match_list')
    else:
        form = MatchForm(instance=match)
    return render(request, 'match_form.html', {'form': form, 'title': 'Edit Pertandingan'})

def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    match.delete()
    return redirect('admin_match_list')