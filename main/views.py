from django.shortcuts import render, get_object_or_404, redirect
from .models import Team, Match
from django.utils.timezone import localtime
from datetime import datetime
from collections import defaultdict
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import MatchForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages

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
    matches = Match.objects.all().order_by('-match_date', '-time')

    # Ambil parameter filter dari query GET
    competition = request.GET.get('competition')
    date = request.GET.get('date')

    # Terapkan filter kalau ada input dari user
    if competition:
        matches = matches.filter(league__iexact=competition)
    if date:
        matches = matches.filter(match_date__date=date)

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
    matches = Match.objects.filter(match_date__date=match_date).select_related('home_team', 'away_team')

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

def match_list_admin(request):
    matches = Match.objects.all().order_by('-match_date')
    paginator = Paginator(matches, 10)  # 10 pertandingan per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'match_list_admin.html', {'page_obj': page_obj})

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

def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    match.delete()
    messages.success(request, 'Pertandingan berhasil dihapus!')
    return redirect('main:admin_match_list')
