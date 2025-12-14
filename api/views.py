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

# VIEWS AUTENTIKASI
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
                    auth_login(request, user)
                    
                    # Get role from Person model
                    try:
                        person = Person.objects.get(user=user)
                        role = person.role
                    except Person.DoesNotExist:
                        role = 'user'
                    
                    return JsonResponse({
                        "username": user.username,
                        "role": role,
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
@require_GET
def api_news_list(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'latest')

    news_qs = News.objects.all()

    # Search
    if q:
        news_qs = news_qs.filter(
            Q(title__icontains=q) | Q(content__icontains=q) | Q(source__icontains=q)
        )

    # Filter kategori
    if category:
        news_qs = news_qs.filter(category__iexact=category)

    # Sorting
    news_qs = news_qs.order_by('publish_time' if sort == 'oldest' else '-publish_time')

    # Convert ke JSON
    data = [
        {
            "id": n.id,
            "title": n.title,
            "author": n.author,
            "source": n.source,
            "publish_time": n.publish_time,
            "category": n.category,
            "thumbnail": n.thumbnail_url,
        }
        for n in news_qs
    ]

    return JsonResponse({"news": data})

@require_GET
def api_news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)

    data = {
        "id": news.id,
        "title": news.title,
        "author": news.author,
        "source": news.source,
        "publish_time": news.publish_time,
        "content": news.content,
        "category": news.category,
        "thumbnail": news.thumbnail_url,
    }

    return JsonResponse(data)

@require_POST
def api_toggle_bookmark(request, news_id):
    bookmarks = request.session.get('bookmarks', [])

    nid = str(news_id)

    if nid in bookmarks:
        bookmarks.remove(nid)
        status = "removed"
    else:
        bookmarks.append(nid)
        status = "added"

    request.session['bookmarks'] = bookmarks
    request.session.modified = True

    return JsonResponse({"success": True, "status": status})

@require_GET
def api_bookmarked_news(request):
    bookmarks = request.session.get('bookmarks', [])
    news_qs = News.objects.filter(id__in=bookmarks)

    data = [
        {
            "id": n.id,
            "title": n.title,
            "author": n.author,
            "source": n.source,
            "publish_time": n.publish_time,
            "category": n.category,
            "thumbnail": n.thumbnail_url,
        }
        for n in news_qs
    ]

    return JsonResponse({"bookmarks": data})

# VIEWS MODUL PLAYER


# VIEWS MODUL MATCH 
@csrf_exempt
def api_match_history(request):
    matches = Match.objects.select_related("home_team", "away_team").all()

    team_id = request.GET.get("team_id")
    competition_id = request.GET.get("competition_id")
    date = request.GET.get("date")  # 👈 TAMBAH INI (YYYY-MM-DD)

    # FILTER BY TEAM
    if team_id:
        if not Team.objects.filter(slug=team_id).exists():
            return JsonResponse({"success": False, "message": "team_id not found"}, status=404)
        matches = matches.filter(
            Q(home_team__slug=team_id) | Q(away_team__slug=team_id)
        )

    # FILTER BY COMPETITION
    if competition_id:
        matches = matches.filter(league__iexact=competition_id)

    # FILTER BY DATE
    if date:
        try:
            matches = matches.filter(match_date=date)
        except ValueError:
            return JsonResponse(
                {"success": False, "message": "Invalid date format (YYYY-MM-DD)"},
                status=400
            )

    data = [
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
        for m in matches.order_by("-match_date")
    ]

    return JsonResponse(data, safe=False)

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

# ========================== VIEWS MODUL FORUM ==========================
def get_person_from_request(request):
    if not request.user.is_authenticated:
        return None
    try:
        return Person.objects.get(user=request.user)
    except Person.DoesNotExist:
        return None


def forum_to_dict(forum, current_person=None):
    is_bookmarked = False
    is_liked = False

    if current_person is not None:
        is_bookmarked = forum.bookmarked_by.filter(id=current_person.id).exists()
        is_liked = forum.liked_by.filter(id=current_person.id).exists()

    return {
        "id": str(forum.id),
        "title": forum.title,
        "content": forum.content,
        "author": forum.author.user.username,
        "author_role": forum.author.role,
        "created_at": forum.created_at.isoformat(),
        "updated_at": forum.updated_at.isoformat(),
        "context": forum.get_context_preview(),
        "like_count": forum.like_count,
        "bookmark_count": forum.bookmark_count,
        "comment_count": forum.comment_count,
        "is_bookmarked": is_bookmarked,
        "is_liked": is_liked,
    }


def comment_to_dict(comment):
    return {
        "id": str(comment.id),
        "forum_id": str(comment.forum.id),
        "author": comment.author.user.username,
        "author_role": comment.author.role,
        "text": comment.text,
        "created_at": comment.created_at.isoformat(),
        "parent_id": str(comment.parent.id) if comment.parent else None,
        "reply_to_username": comment.reply_to_username,
    }


# =============== ENDPOINT FORUM ===============

# POST /api/forum/add-forum/
@csrf_exempt
@require_POST
def api_add_forum(request):
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

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    news_id = data.get("news_id")
    match_id = data.get("match_id")

    if not title or not content:
        return JsonResponse(
            {"success": False, "message": "Title and content are required."},
            status=400,
        )

    news = None
    match = None

    if news_id:
        news = News.objects.filter(id=news_id).first()
        if news is None:
            return JsonResponse(
                {"success": False, "message": "News not found."}, status=404
            )

    if match_id:
        match = Match.objects.filter(id=match_id).first()
        if match is None:
            return JsonResponse(
                {"success": False, "message": "Match not found."}, status=404
            )

    forum = Forum.objects.create(
        title=title,
        content=content,
        author=person,
        news=news,
        match=match,
    )

    return JsonResponse(
        {"success": True, "forum": forum_to_dict(forum, current_person=person)},
        status=201,
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
        {"success": True, "comment": comment_to_dict(comment)}, status=201
    )


# POST /api/forum/delete-forum/
@csrf_exempt
@require_POST
def api_delete_forum(request):
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

    # hanya author atau admin
    if forum.author != person and not person.is_admin():
        return JsonResponse({"success": False, "message": "Forbidden."}, status=403)

    forum.delete()
    return JsonResponse({"success": True, "message": "Forum deleted."})


# POST /api/forum/delete-comment/
@csrf_exempt
@require_POST
def api_delete_comment(request):
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

    comment_id = data.get("comment_id")
    if not comment_id:
        return JsonResponse(
            {"success": False, "message": "comment_id is required."}, status=400
        )

    comment = Comment.objects.filter(id=comment_id).first()
    if comment is None:
        return JsonResponse(
            {"success": False, "message": "Comment not found."}, status=404
        )

    # boleh hapus: author comment, author forum, admin
    if (
        comment.author != person
        and comment.forum.author != person
        and not person.is_admin()
    ):
        return JsonResponse({"success": False, "message": "Forbidden."}, status=403)

    comment.delete()
    return JsonResponse({"success": True, "message": "Comment deleted."})


# POST /api/forum/add-bookmart/
@csrf_exempt
@require_POST
def api_add_bookmart(request):  # pakai nama typo sesuai spek lo
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

    if forum.bookmarked_by.filter(id=person.id).exists():
        forum.bookmarked_by.remove(person)
        status_str = "removed"
    else:
        forum.bookmarked_by.add(person)
        status_str = "added"

    return JsonResponse(
        {
            "success": True,
            "status": status_str,
            "bookmark_count": forum.bookmark_count,
        }
    )


# GET /api/forum/forums/
@require_GET
def api_forum_list(request):
    person = get_person_from_request(request)

    qs = Forum.objects.all()

    news_id = request.GET.get("news_id")
    match_id = request.GET.get("match_id")
    q = request.GET.get("q", "").strip()
    order = request.GET.get("order", "latest")

    if news_id:
        qs = qs.filter(news_id=news_id)

    if match_id:
        qs = qs.filter(match_id=match_id)

    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(content__icontains=q)
            | Q(author__user__username__icontains=q)
        )

    if order == "popular":
        qs = qs.annotate(num_likes=Count("liked_by")).order_by(
            "-num_likes", "-created_at"
        )
    elif order == "commented":
        qs = qs.annotate(num_comments=Count("comments")).order_by(
            "-num_comments", "-created_at"
        )
    else:
        qs = qs.order_by("-created_at")

    data = [forum_to_dict(f, current_person=person) for f in qs]
    return JsonResponse({"forums": data})


# GET /api/forum/<id_forum>/
@require_GET
def api_forum_detail(request, forum_id):
    person = get_person_from_request(request)
    forum = Forum.objects.filter(id=forum_id).first()
    if forum is None:
        return JsonResponse(
            {"success": False, "message": "Forum not found."}, status=404
        )

    data = forum_to_dict(forum, current_person=person)
    return JsonResponse({"success": True, "forum": data})


# GET /api/forum/<id_forum>/comments/
@require_GET
def api_forum_comments(request, forum_id):
    forum = Forum.objects.filter(id=forum_id).first()
    if forum is None:
        return JsonResponse(
            {"success": False, "message": "Forum not found."}, status=404
        )

    root_comments = (
        forum.comments.filter(parent__isnull=True)
        .order_by("created_at")
        .select_related("author", "reply_to")
    )
    all_replies = (
        forum.comments.filter(parent__isnull=False)
        .order_by("created_at")
        .select_related("author", "reply_to", "parent")
    )

    replies_map = {}
    for c in all_replies:
        replies_map.setdefault(str(c.parent_id), []).append(comment_to_dict(c))

    result = []
    for root in root_comments:
        root_dict = comment_to_dict(root)
        root_dict["replies"] = replies_map.get(str(root.id), [])
        result.append(root_dict)

    return JsonResponse({"success": True, "comments": result})


# GET /api/forum/my-bookmark/
@require_GET
def api_forum_my_bookmark(request):
    person = get_person_from_request(request)
    if person is None:
        return JsonResponse(
            {"success": False, "message": "Authentication required."}, status=401
        )

    qs = Forum.objects.filter(bookmarked_by=person).order_by("-created_at")
    data = [forum_to_dict(f, current_person=person) for f in qs]

    return JsonResponse({"success": True, "bookmarks": data})


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
        {"success": True, "status": status_str, "like_count": forum.like_count}
    )