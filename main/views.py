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

def user_login(request):
    return 

def user_register(request):
    return 