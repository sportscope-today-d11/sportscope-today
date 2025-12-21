from datetime import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
import json
from main.models import Person, Match, Team, News, Forum, Comment
from django.utils.html import strip_tags
from django.contrib.auth import logout as auth_logout
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator
from datetime import datetime
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.db.models import Count, F, Value
from django.db.models.functions import Coalesce

# VIEWS AUTENTIKASI
@csrf_exempt
@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            # Try to parse as JSON first
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Fallback to form-data
                data = request.POST
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({
                    "status": False,
                    "message": "Username and password are required."
                }, status=400)
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    # login: ini yang ngelink session <-> user
                    auth_login(request, user)

                    # pastikan session_key ada
                    if not request.session.session_key:
                        request.session.create()
                    session_key = request.session.session_key

                    # ambil role dari Person
                    try:
                        person = Person.objects.get(user=user)
                        role = person.role
                    except Person.DoesNotExist:
                        role = 'user'
                    
                    return JsonResponse({
                        "username": user.username,
                        "role": role,
                        "sessionid": session_key,   # ⬅️ ini yang dipakai Flutter
                        "status": True,
                        "message": "Login successful!"
                    }, status=200)
                else:
                    return JsonResponse({
                        "status": False,
                        "message": "Login failed, account is disabled."
                    }, status=401)
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Login failed, please check your username or password."
                }, status=401)
        
        except json.JSONDecodeError:
            return JsonResponse({
                "status": False,
                "message": "Invalid JSON format."
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"Login error: {str(e)}"
            }, status=500)
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    
@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            # Try to parse as JSON first, fallback to form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Fallback to form-data
                data = request.POST
            
            username = data.get('username')
            password1 = data.get('password1')
            password2 = data.get('password2')

            # Validation
            if not username or not password1 or not password2:
                return JsonResponse({
                    "status": False,
                    "message": "All fields are required."
                }, status=400)

            if password1 != password2:
                return JsonResponse({
                    "status": False,
                    "message": "Passwords do not match."
                }, status=400)
            
            if len(password1) < 8:
                return JsonResponse({
                    "status": False,
                    "message": "Password must be at least 8 characters long."
                }, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Username already exists."
                }, status=400)
            
            # Create user
            user = User.objects.create_user(username=username, password=password1)
            user.save()
            
            # Create Person with role
            Person.objects.create(user=user, role='user')
            
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "User created successfully!"
            }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({
                "status": False,
                "message": "Invalid JSON format."
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"Registration error: {str(e)}"
            }, status=500)
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)
    

@csrf_exempt
def logout(request):
    try:
        if request.user.is_authenticated:
            username = request.user.username
            auth_logout(request)
            request.session.flush()
            return JsonResponse({
                "username": username,
                "status": True,
                "message": "Logged out successfully!"
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "No user is currently logged in."
            }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Logout failed: {str(e)}"
        }, status=401)
    

# VIEWS MODUL TEAM
# List semua teams
@csrf_exempt
def team_list(request):
    try:
        teams = Team.objects.all()
        
        # FILTER (optional)
        min_goals = request.GET.get('min_goals')
        if min_goals:
            teams = teams.filter(goals__gte=int(min_goals))
        
        # SORT (optional)
        sort_by = request.GET.get('sort_by', 'goals')
        order = request.GET.get('order', 'asc')
        
        allowed_sort = ['name', 'goals', 'possession', 'age', 'players', 'yellows', 'reds']
        if sort_by in allowed_sort:
            teams = teams.order_by(f'-{sort_by}' if order == 'desc' else sort_by)
        
        # Build full URL untuk images
        base_url = request.build_absolute_uri('/')[:-1]
        
        teams_data = []
        for team in teams:
            team_dict = {
                'slug': team.slug,
                'name': team.name,
                'players': team.players,
                'age': team.age,
                'possession': team.possession,
                'goals': team.goals,
                'assists': team.assists,
                'penalty_kicks': team.penalty_kicks,
                'penalty_kick_attempts': team.penalty_kick_attempts,
                'yellows': team.yellows,
                'reds': team.reds,
                'image_url': base_url + team.image_url if team.image_url else None
            }
            teams_data.append(team_dict)
        
        # Return langsung array of objects (flat JSON)
        return JsonResponse(teams_data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Detail team by slug
@csrf_exempt
def team_detail(request, slug):
    try:
        team = Team.objects.get(slug=slug)
        
        base_url = request.build_absolute_uri('/')[:-1]
        
        team_data = {
            'slug': team.slug,
            'name': team.name,
            'players': team.players,
            'age': team.age,
            'possession': team.possession,
            'goals': team.goals,
            'assists': team.assists,
            'penalty_kicks': team.penalty_kicks,
            'penalty_kick_attempts': team.penalty_kick_attempts,
            'yellows': team.yellows,
            'reds': team.reds,
            'image_url': base_url + team.image_url if team.image_url else None
        }
        
        # Return langsung object (flat JSON)
        return JsonResponse(team_data)
    
    except Team.DoesNotExist:
        return JsonResponse({'error': 'Team not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# VIEWS MODUL NEWS
def news_to_dict(news, person):
    return {
        "id": news.id,
        "title": news.title,
        "author": news.author,
        "source": news.source,
        "content": news.content,
        "category": news.category,
        "thumbnail_url": news.thumbnail_url, # Menggunakan @property thumbnail_url di model
        "publish_time": news.publish_time.strftime("%Y-%m-%d"),
        "featured": news.featured,
        "link": news.link,
        # Logika krusial: cek apakah 'person' ada di ManyToMany bookmarked_by
        "is_bookmarked": news.bookmarked_by.filter(id=person.id).exists() if person else False,
    }

@require_GET
def api_news_list(request):
    person = get_person_from_request(request)

    q = request.GET.get("q", "")
    category = request.GET.get("category", "")
    sort = request.GET.get("sort", "latest")
    featured = request.GET.get("featured")  # optional

    news_qs = News.objects.all()

    # Search
    if q:
        news_qs = news_qs.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(source__icontains=q)
        )

    # Filter kategori
    if category:
        news_qs = news_qs.filter(category__iexact=category)

    # Filter featured
    if featured == "true":
        news_qs = news_qs.filter(featured=True)

    # Sorting
    news_qs = news_qs.order_by(
        "publish_time" if sort == "oldest" else "-publish_time"
    )

    data = [news_to_dict(n, person) for n in news_qs]

    return JsonResponse({
        "is_admin": person.is_admin() if (person is not None) else False,
        "news": data
    })

@require_GET
def api_news_detail(request, news_id):
    person = get_person_from_request(request)
    news = get_object_or_404(News, id=news_id)

    return JsonResponse(news_to_dict(news, person))

@require_GET
def api_bookmarked_news(request):
    person = get_person_from_request(request)
    if not person:
        return JsonResponse(
            {"success": False, "message": "Login required"},
            status=401
        )

    news_qs = News.objects.filter(bookmarked_by=person)
    data = [news_to_dict(n, person) for n in news_qs]

    return JsonResponse({"bookmarks": data})

@csrf_exempt
@require_POST
def api_toggle_bookmark(request, news_id):
    person = get_person_from_request(request)
    if not person:
        return JsonResponse(
            {"success": False, "message": "Login required"},
            status=401
        )

    news = get_object_or_404(News, id=news_id)

    if news.bookmarked_by.filter(id=person.id).exists():
        news.bookmarked_by.remove(person)
        status = "removed"
    else:
        news.bookmarked_by.add(person)
        status = "added"

    return JsonResponse({
        "success": True,
        "status": status,
        "is_bookmarked": status == "added"
    })

@csrf_exempt
@require_POST
def api_create_news(request):    
    person = get_person_from_request(request)

    if not person or not person.is_admin():
        user_info = str(request.user) if request.user.is_authenticated else "Anonymous"
        return JsonResponse(
            {"success": False, "message": f"Admin only. Detected as: {user_info}"}, 
            status=403
        )
    # GUNAKAN LOGIKA DARI FORUM
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    else:
        data = request.POST

    required = ["title", "author", "source", "content", "category"]
    for field in required:
        if not data.get(field):
            return JsonResponse({"success": False, "message": f"{field} is required"}, status=400)

    news = News.objects.create(
        title=data.get("title"),
        link=data.get("link", ""),
        author=data.get("author"),
        source=data.get("source"),
        content=data.get("content"),
        category=data.get("category"),
        thumbnail=data.get("thumbnail_url", ""),
        featured=data.get("featured") == "true" or data.get("featured") is True, # Handle string vs bool
        publish_time=timezone.now(),
    )

    return JsonResponse({"success": True, "news": news_to_dict(news, person)}, status=201)

@csrf_exempt
@require_POST
def api_update_news(request):
    person = get_person_from_request(request)
    if not person or not person.is_admin():
        return JsonResponse({"success": False, "message": "Admin only"}, status=403)

    if request.content_type == "application/json":
        data = json.loads(request.body)
    else:
        data = request.POST

    news_id = data.get("news_id")
    news = get_object_or_404(News, id=news_id)

    for field in ["title", "author", "source", "content", "category"]:
        if field in data:
            setattr(news, field, data.get(field))
            
    if "featured" in data:
        # Handle jika dikirim lewat Form-Data (string "true") atau JSON (bool true)
        news.featured = data.get("featured") == "true" or data.get("featured") is True

    if "thumbnail_url" in data:
        news.thumbnail = data.get("thumbnail_url")

    news.save()
    return JsonResponse({"success": True})

@csrf_exempt
@require_POST
def api_delete_news(request):
    person = get_person_from_request(request)
    if not person or not person.is_admin():
        return JsonResponse({"success": False, "message": "Admin only"}, status=403)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    news = get_object_or_404(News, id=data.get("news_id"))
    news.delete()

    return JsonResponse({"success": True})

# VIEWS MODUL PLAYER


# VIEWS MODUL MATCH 
def is_admin_request(request):
    if not request.user.is_authenticated:
        return False
    try:
        person = Person.objects.get(user=request.user)
        return person.is_admin()
    except Person.DoesNotExist:
        return False

@csrf_exempt
def api_match_history(request):
    matches = Match.objects.select_related("home_team", "away_team").all()

    # ===== QUERY PARAMS =====
    team_id = request.GET.get("team_id")
    competition_id = request.GET.get("competition_id")
    date = request.GET.get("date")           # YYYY-MM-DD
    page = int(request.GET.get("page", 1))   # 👈 pagination
    page_size = int(request.GET.get("page_size", 10))

    # ===== FILTER BY TEAM =====
    if team_id:
        if not Team.objects.filter(slug=team_id).exists():
            return JsonResponse(
                {"success": False, "message": "team_id not found"},
                status=404
            )
        matches = matches.filter(
            Q(home_team__slug=team_id) | Q(away_team__slug=team_id)
        )

    # ===== FILTER BY COMPETITION =====
    if competition_id:
        matches = matches.filter(league__iexact=competition_id)

    # ===== FILTER BY DATE =====
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            matches = matches.filter(match_date=parsed_date)
        except ValueError:
            return JsonResponse(
                {"success": False, "message": "Invalid date format (YYYY-MM-DD)"},
                status=400
            )

    # ===== ORDERING =====
    matches = matches.order_by("-match_date")

    # ===== PAGINATION =====
    paginator = Paginator(matches, page_size)
    page_obj = paginator.get_page(page)

    # ===== SERIALIZE DATA =====
    results = [
        {
            "id": str(m.id),
            "season": m.season,
            "date": m.match_date.isoformat() if m.match_date else None,
            "competition": m.league or "Premier League",

            "home_team": m.home_team.name,
            "home_team_slug": m.home_team.slug,
            "away_team": m.away_team.name,
            "away_team_slug": m.away_team.slug,

            "full_time_score": f"{m.full_time_home_goals} - {m.full_time_away_goals}",
        }
        for m in page_obj.object_list
    ]

    return JsonResponse({
        "results": results,
        "page": page_obj.number,
        "page_size": page_size,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,
        "has_next": page_obj.has_next(),
        "has_prev": page_obj.has_previous(),
    })

@csrf_exempt
def api_match_detail(request, match_id):
    try:
        # Handle UUID format with or without 'uuid:' prefix
        if match_id.startswith('uuid:'):
            match_id = match_id[5:]  # Remove 'uuid:' prefix
        
        match = Match.objects.select_related("home_team", "away_team").get(id=match_id)

        data = {
            "id": str(match.id),
            "season": match.season,
            "date": match.match_date.isoformat() if match.match_date else None,
            "competition": match.league or "Premier League",  # Default to Premier League

            "home_team": match.home_team.name,
            "home_team_slug": match.home_team.slug,
            "away_team": match.away_team.name,
            "away_team_slug": match.away_team.slug,

            "full_time_score": f"{match.full_time_home_goals} - {match.full_time_away_goals}",
            "half_time_score": f"{match.half_time_home_goals} - {match.half_time_away_goals}",

            "shots_home": match.home_shots,
            "shots_away": match.away_shots,
            "shots_on_target_home": match.home_shots_on_target,
            "shots_on_target_away": match.away_shots_on_target,

            "corners_home": match.home_corners,
            "corners_away": match.away_corners,

            "fouls_home": match.home_fouls,
            "fouls_away": match.away_fouls,

            "yellow_cards_home": match.home_yellow_cards,
            "yellow_cards_away": match.away_yellow_cards,
            "red_cards_home": match.home_red_cards,
            "red_cards_away": match.away_red_cards,
        }

        return JsonResponse(data)

    except Match.DoesNotExist:
        return JsonResponse({"detail": "Match not found"}, status=404)
    except ValueError:
        return JsonResponse({"detail": "Invalid match ID format"}, status=400)


def api_matches_by_date(request, date):
    try:
        match_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse(
        {"success": False, "message": "Invalid date format (YYYY-MM-DD)"},
        status=400,)

    matches = Match.objects.select_related("home_team", "away_team").filter(match_date=match_date)

    results = {}
    for m in matches:
        league = m.league or "Premier League"
        results.setdefault(league, []).append({
            "id": str(m.id),
            "date": m.match_date.isoformat() if m.match_date else None,
            "competition": league,
            "season": m.season,
            "home_team": m.home_team.name,
            "home_team_slug": m.home_team.slug,
            "away_team": m.away_team.name,
            "away_team_slug": m.away_team.slug,
            "full_time_score": f"{m.full_time_home_goals} - {m.full_time_away_goals}",
        })

    return JsonResponse({
        "success": True,
        "date": match_date.isoformat(),
        "matches_by_league": results,
    })

# views modul match untuk admin
@csrf_exempt
@require_GET
def api_match_list_admin(request):
    if not is_admin_request(request):
        return JsonResponse({"success": False, "message": "Admin only"}, status=403,)

    matches = Match.objects.select_related("home_team", "away_team").order_by("-match_date")

    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 10))

    paginator = Paginator(matches, page_size)
    page_obj = paginator.get_page(page)

    results = [
        {
            "id": str(m.id),
            "date": m.match_date.isoformat() if m.match_date else None,
            "competition": m.league or "Premier League",
            "season": m.season,
            "home_team": m.home_team.name,
            "away_team": m.away_team.name,
            "score": f"{m.full_time_home_goals} - {m.full_time_away_goals}",
        }
        for m in page_obj.object_list
    ]

    return JsonResponse({
        "success": True,
        "results": results,
        "page": page_obj.number,
        "has_next": page_obj.has_next(),
        "has_prev": page_obj.has_previous(),
        "total_pages": paginator.num_pages,
    })

@csrf_exempt
@require_POST
def api_add_match(request):
    if not is_admin_request(request):
        return JsonResponse({"success": False, "message": "Admin only"}, status=403,)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400,)

    try:
        match = Match.objects.create(
            home_team=Team.objects.get(slug=data["home_team_slug"]),
            away_team=Team.objects.get(slug=data["away_team_slug"]),
            league=data.get("competition", "Premier League"),
            season=data.get("season", ""),
            match_date=data.get("date"),
            full_time_home_goals=data.get("home_goals", 0),
            full_time_away_goals=data.get("away_goals", 0),
            half_time_home_goals=data.get("ht_home_goals", 0),
            half_time_away_goals=data.get("ht_away_goals", 0),
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400,)

    return JsonResponse({"success": True, "id": str(match.id)}, status=201,)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def api_edit_match(request, match_id):
    if not is_admin_request(request):
        return JsonResponse({"success": False, "message": "Admin only"}, status=403,)

    match = get_object_or_404(Match, id=match_id)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400,)

    match.league = data.get("competition", match.league)
    match.season = data.get("season", match.season)
    match.match_date = data.get("date", match.match_date)

    match.full_time_home_goals = data.get("home_goals", match.full_time_home_goals)
    match.full_time_away_goals = data.get("away_goals", match.full_time_away_goals)

    match.save()

    return JsonResponse({"success": True})

@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_match(request, match_id):
    if not is_admin_request(request):
        return JsonResponse({"success": False, "message": "Admin only"}, status=403,)

    match = get_object_or_404(Match, id=match_id)
    match.delete()

    return JsonResponse({"success": True})


# ========================== VIEWS MODUL FORUM ==========================
def get_person_from_request(request):
    if not request.user.is_authenticated:
        return None
    try:
        return Person.objects.get(user=request.user)
    except Person.DoesNotExist:
        return None

def forum_preview_to_dict(forum):
    """
    Preview ringan untuk embedded quote card (mirip X/Quora quote preview).
    Dipakai di field "quoted_post" pada forum_to_dict.
    """
    # Quote preview removed: return None for compatibility
    return None


def forum_to_dict(forum, current_person=None):
    """
    Dict utama untuk Forum List & Forum Detail.
    - Tidak pakai context (news/match) lagi.
    - Menyediakan quote_count untuk UI (tanpa repost).
    """
    is_liked = False
    if current_person is not None:
        is_liked = forum.liked_by.filter(id=current_person.id).exists()

    # aman untuk image_url
    image_url = None
    if getattr(forum, "image", None) and hasattr(forum.image, "url"):
        image_url = forum.image.url

    # quote_count/quoted_post removed

    return {
        "id": str(forum.id),
        "title": forum.title,
        "content": forum.content,
        "author": forum.author.user.username,
        "author_role": getattr(forum.author, "role", ""),
        "created_at": forum.created_at.isoformat(),
        "updated_at": forum.updated_at.isoformat(),

        # counts/stats
        "views": forum.views,
        "like_count": forum.like_count,
        "comment_count": forum.comment_count,

        # flags
        "is_liked": is_liked,

        # media
        "image_url": image_url,

        # quote preview removed
    }

def comment_to_dict(comment, current_person=None):
    is_liked = False
    if current_person is not None:
        is_liked = comment.liked_by.filter(id=current_person.id).exists()

    return {
        "id": str(comment.id),
        "forum_id": str(comment.forum.id),
        "author": comment.author.user.username,
        "author_role": comment.author.role,
        "text": comment.text,
        "created_at": comment.created_at.isoformat(),
        "parent_id": str(comment.parent.id) if comment.parent else None,
        "reply_to_username": comment.reply_to_username,
        "like_count": comment.like_count,
        "is_liked": is_liked,
    }


# POST /api/forum/add-forum/

@csrf_exempt
@require_POST
def api_add_forum(request):
    """
    API: POST /forum/add-forum/
    - Create forum baru
    - Support optional:
      - image (1 file) -> request.FILES['image']
      - quoted_post_id -> request.POST['quoted_post_id']
      - news_id / match_id
    - Return forum object via forum_to_dict
    """

    person = get_person_from_request(request)
    if person is None:
        return JsonResponse(
            {"success": False, "message": "Authentication required."},
            status=401,
        )

    # NOTE:
    # Untuk create + upload image, request harus multipart/form-data
    # Jadi kita prioritas baca dari request.POST.
    title = (request.POST.get("title") or "").strip()
    content = (request.POST.get("content") or "").strip()

    if not title or not content:
        return JsonResponse(
            {"success": False, "message": "Title and content are required."},
            status=400,
        )

    forum = Forum(
        title=title,
        content=content,
        author=person,
    )

    # Optional: image (create only)
    if "image" in request.FILES:
        forum.image = request.FILES["image"]

    # Optional: context news/match
    news_id = (request.POST.get("news_id") or "").strip()
    match_id = (request.POST.get("match_id") or "").strip()

    if news_id:
        # aman: set FK by id
        forum.news_id = news_id

    if match_id:
        forum.match_id = match_id

    # Optional: quote
    # quoted_post removed (quote feature disabled)

    forum.save()

    # Re-fetch dengan select_related biar quoted_post/author kebaca rapi
    forum = (
        Forum.objects
        .select_related("author", "author__user")
        .filter(id=forum.id)
        .first()
    )

    return JsonResponse(
        {"success": True, "forum": forum_to_dict(forum, current_person=person)}
    )

# POST /api/forum/<id_forum>/add-comment/
@csrf_exempt
@require_POST
def api_add_comment(request, forum_id):
    person = get_person_from_request(request)
    if person is None:
        return JsonResponse(
            {"success": False, "message": "Authentication required."}, status=401
        )

    forum = Forum.objects.filter(id=forum_id).first()
    if forum is None:
        return JsonResponse(
            {"success": False, "message": "Forum not found."}, status=404
        )

    try:
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON."}, status=400)

    text = data.get("text", "").strip()
    reply_to_comment_id = data.get("reply_to_comment_id")  # optional

    if not text:
        return JsonResponse(
            {"success": False, "message": "Comment text is required."}, status=400
        )

    parent = None
    reply_to_person = None

    if reply_to_comment_id:
        target_comment = Comment.objects.filter(
            id=reply_to_comment_id, forum=forum
        ).first()
        if target_comment is None:
            return JsonResponse(
                {"success": False, "message": "Target comment not found."}, status=404
            )

        # root comment (maks 1 level)
        root = target_comment
        if target_comment.parent is not None:
            root = target_comment.parent

        parent = root
        reply_to_person = target_comment.author

    comment = Comment.objects.create(
        forum=forum,
        author=person,
        parent=parent,
        reply_to=reply_to_person,
        text=text,
    )

    return JsonResponse(
        {"success": True, "comment": comment_to_dict(comment, current_person=person)},  # 👈
        status=201,
    )


# POST /api/forum/delete-forum/
@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_delete_forum(request, forum_id):
    person = get_person_from_request(request)
    if person is None:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    forum = Forum.objects.filter(id=forum_id).first()
    if forum is None:
        return JsonResponse({"success": False, "message": "Forum not found."}, status=404)

    # author boleh delete sendiri, admin boleh delete semua
    if forum.author != person and not person.is_admin():
        return JsonResponse({"success": False, "message": "Forbidden."}, status=403)

    forum.delete()
    return JsonResponse({"success": True, "message": "Forum deleted."})



# POST /api/forum/delete-comment/
@csrf_exempt
@require_http_methods(["DELETE", "POST"])  #
def api_delete_comment(request, comment_id):  
    person = get_person_from_request(request)
    if person is None:
        return JsonResponse(
            {"success": False, "message": "Authentication required."}, 
            status=401
        )

    # Fetch comment
    comment = Comment.objects.select_related(
        "author__user", 
        "forum__author__user"
    ).filter(id=comment_id).first()

    if comment is None:
        return JsonResponse(
            {"success": False, "message": "Comment not found."}, 
            status=404
        )

    # Permission check
    is_comment_author = (comment.author.id == person.id)
    is_forum_author = (comment.forum.author.id == person.id)
    is_admin = person.is_admin()

    if not (is_comment_author or is_forum_author or is_admin):
        return JsonResponse(
            {"success": False, "message": "Forbidden."}, 
            status=403
        )

    # Delete
    comment.delete()
    
    return JsonResponse({
        "success": True, 
        "message": "Comment deleted successfully."
    })

# POST /api/forum/edit-forum/
@csrf_exempt
@require_http_methods(["POST", "PUT"])
def api_edit_forum(request, forum_id):
    person = get_person_from_request(request)
    if person is None:
        return JsonResponse({"success": False, "message": "Authentication required."}, status=401)

    try:
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON."}, status=400)

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title or not content:
        return JsonResponse({"success": False, "message": "Title and content are required."}, status=400)

    forum = Forum.objects.filter(id=forum_id).first()
    if forum is None:
        return JsonResponse({"success": False, "message": "Forum not found."}, status=404)

    # hanya author boleh edit (admin gak usah bisa edit post orang kalau mau strict)
    if forum.author != person:
        return JsonResponse({"success": False, "message": "Forbidden."}, status=403)

    forum.title = title
    forum.content = content
    forum.save(update_fields=["title", "content", "updated_at"])

    return JsonResponse({"success": True, "forum": forum_to_dict(forum, current_person=person)})



# GET /api/forum/forums/
@require_GET
def api_forum_list(request):
    person = get_person_from_request(request)
    filter_by = (request.GET.get("filter") or "latest").lower()

    qs = (
        Forum.objects
        .select_related("author", "author__user")
        .annotate(
            like_count_db=Count("liked_by", distinct=True),
            comment_count_db=Count("comments", distinct=True),
        )
    )

    # ----- filter scope -----
    if filter_by == "my":
        if person is None:
            return JsonResponse(
                {"success": False, "message": "Authentication required."},
                status=401,
            )
        qs = qs.filter(author=person).order_by("-created_at")

    elif filter_by == "trending":
        week_ago = timezone.now() - timedelta(days=7)

        qs = (
            qs.filter(created_at__gte=week_ago)
            .annotate(
                trending_score=(
                    Coalesce(F("views"), Value(0), output_field=IntegerField()) +
                    Coalesce(F("like_count_db"), Value(0), output_field=IntegerField()) +
                    Coalesce(F("comment_count_db"), Value(0), output_field=IntegerField())
                )
            )
            .order_by("-trending_score", "-created_at")
        )

    else:
        # "latest" or "all" or unknown -> treat as latest
        qs = qs.order_by("-created_at")

    forums = [forum_to_dict(f, current_person=person) for f in qs]
    return JsonResponse({"success": True, "forums": forums})


# POST /api/forum/comment-like/
@csrf_exempt
@require_POST
def api_comment_like(request):
    person = get_person_from_request(request)
    if person is None:
        return JsonResponse(
            {"success": False, "message": "Authentication required."},
            status=401,
        )

    try:
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Invalid JSON."},
            status=400,
        )

    comment_id = data.get("comment_id")
    if not comment_id:
        return JsonResponse(
            {"success": False, "message": "comment_id is required."},
            status=400,
        )

    comment = Comment.objects.filter(id=comment_id).select_related("author").first()
    if comment is None:
        return JsonResponse(
            {"success": False, "message": "Comment not found."},
            status=404,
        )

    if comment.liked_by.filter(id=person.id).exists():
        comment.liked_by.remove(person)
        status_str = "unliked"
    else:
        comment.liked_by.add(person)
        status_str = "liked"

    return JsonResponse(
        {
            "success": True,
            "status": status_str,
            "like_count": comment.like_count,
            "is_liked": comment.liked_by.filter(id=person.id).exists(),
            "comment_id": str(comment.id),
        }
    )

# GET /api/forum/my-bookmark/ removed: bookmark feature disabled


# POST /api/forum/like
@csrf_exempt
@require_POST
def api_forum_like(request):
    person = get_person_from_request(request)
    if person is None:
        return JsonResponse(
            {"success": False, "message": "Authentication required."}, status=401
        )

    try:
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON."}, status=400)

    forum_id = data.get("forum_id")
    if not forum_id:
        return JsonResponse(
            {"success": False, "message": "forum_id is required."}, status=400
        )

    forum = Forum.objects.filter(id=forum_id).first()
    if forum is None:
        return JsonResponse(
            {"success": False, "message": "Forum not found."}, status=404
        )

    if forum.liked_by.filter(id=person.id).exists():
        forum.liked_by.remove(person)
        status_str = "unliked"
    else:
        forum.liked_by.add(person)
        status_str = "liked"

    return JsonResponse(
        {
            "success": True, 
            "status": status_str, 
            "like_count": forum.like_count,
            "is_liked": forum.liked_by.filter(id=person.id).exists()
        }
    )

@require_GET
def api_forum_comments(request, forum_id):
    person = get_person_from_request(request)

    forum = Forum.objects.filter(id=forum_id).first()
    if forum is None:
        return JsonResponse(
            {"success": False, "message": "Forum not found."},
            status=404,
        )

    # Ambil semua comment dalam forum (root + replies)
    # root: parent is NULL
    # reply: parent != NULL (parent = root sesuai logic kamu)
    all_comments = (
        Comment.objects
        .select_related("author", "author__user", "reply_to", "reply_to__user", "forum")
        .prefetch_related("liked_by")
        .filter(forum=forum)
        .order_by("created_at")
    )

    # Pisahkan root & reply
    roots = []
    replies_map = {}  # root_id -> list of reply Comment

    for c in all_comments:
        if c.parent_id is None:
            roots.append(c)
        else:
            replies_map.setdefault(str(c.parent_id), []).append(c)

    # Build nested JSON
    out = []
    for root in roots:
        root_dict = comment_to_dict(root, current_person=person)

        child_comments = replies_map.get(str(root.id), [])
        root_dict["replies"] = [
            comment_to_dict(child, current_person=person) for child in child_comments
        ]

        out.append(root_dict)

    return JsonResponse(
        {"success": True, "comments": out}
    )

from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def api_forum_detail(request, forum_id):
    """
    API: GET /forum/<uuid:forum_id>/
    - Return detail 1 forum
    - Increment views +1 setiap kali endpoint ini dipanggil (masuk detail)
    - Response forum memakai forum_to_dict (yang sudah include views + quoted_post + image_url)
    """
    person = get_person_from_request(request)

    forum = (
        Forum.objects
        .select_related(
            "author", "author__user",
            "quoted_post", "quoted_post__author", "quoted_post__author__user",
        )
        .filter(id=forum_id)
        .first()
    )

    if forum is None:
        return JsonResponse(
            {"success": False, "message": "Forum not found."},
            status=404,
        )

    # increment views
    forum.views = (forum.views or 0) + 1
    forum.save(update_fields=["views"])

    return JsonResponse(
        {"success": True, "forum": forum_to_dict(forum, current_person=person)}
    )


