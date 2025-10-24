from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import News, Team, Player

def homepage(request):
    # --- NEWS SECTION ---
    # ambil 8 berita featured random untuk layout hero
    featured_news = list(News.objects.filter(featured=True).order_by("?")[:20])

    # kategori aktif
    categories = [
        "Transfer",
        "Injury Update",
        "Match Result",
        "Manager News",
        "Thoughts",
    ]

    # berita per kategori (max 5 tiap kategori)
    news_by_category = {
        cat: News.objects.filter(category=cat).order_by("-publish_time")[:4]
        for cat in categories
    }

    # --- PREMIER LEAGUE TABLE ---
    teams = Team.objects.all().order_by("-goals")[:20]  # misal urut gol

    # --- TOP 10 MOST LOVED PLAYERS ---
    top_players = Player.objects.order_by("-likes")[:10]

    context = {
        "featured_news": featured_news,
        "categories": categories,
        "news_by_category": news_by_category,
        "teams": teams,
        "top_players": top_players,
    }
    return render(request, "homepage.html", context)
