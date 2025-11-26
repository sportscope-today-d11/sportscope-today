from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
import json
from main.models import Person, Match, Team
from django.utils.html import strip_tags
from django.contrib.auth import logout as auth_logout
from django.db.models import Q

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


# VIEWS MODUL PLAYER


# VIEWS MODUL MATCH 
def api_match_history(request):
    matches = Match.objects.select_related("home_team", "away_team").all()

    team_id = request.GET.get("team_id")   # expecting team slug
    competition_id = request.GET.get("competition_id")

    # --------------------------
    # FILTER BY TEAM (slug)
    # --------------------------
    if team_id:
        if not Team.objects.filter(slug=team_id).exists():
            return JsonResponse({
                "success": False,
                "message": "team_id not found"
            }, status=404)

        matches = matches.filter(
            Q(home_team__slug=team_id) | Q(away_team__slug=team_id)
        )

    # --------------------------
    # FILTER BY COMPETITION
    # --------------------------
    if competition_id:
        matches = matches.filter(league__iexact=competition_id)

        if not matches.exists():
            return JsonResponse({
                "success": False,
                "message": "competition_id not found"
            }, status=404)

    # --------------------------
    # RETURN LIST
    # --------------------------
    return JsonResponse({
        "success": True,
        "count": matches.count(),
        "matches": [
            {
                "id": str(m.id),
                "date": str(m.match_date),
                "competition": m.league,
                "home_team": m.home_team.name,
                "away_team": m.away_team.name,
                "home_team_slug": m.home_team.slug,
                "away_team_slug": m.away_team.slug,
                "score": f"{m.full_time_home_goals} - {m.full_time_away_goals}",
            }
            for m in matches.order_by("-match_date")
        ]
    })

def api_match_detail(request, match_id):
    match = get_object_or_404(
        Match.objects.select_related("home_team", "away_team"),
        id=match_id
    )

    return JsonResponse({
        "success": True,
        "match": {
            "id": str(match.id),
            "season": match.season,
            "date": str(match.match_date),
            "competition": match.league,

            "home_team": match.home_team.name,
            "home_team_slug": match.home_team.slug,
            "away_team": match.away_team.name,
            "away_team_slug": match.away_team.slug,

            "full_time_score": f"{match.full_time_home_goals} - {match.full_time_away_goals}",
            "half_time_score": f"{match.half_time_home_goals} - {match.half_time_away_goals}",

            "stats": {
                "shots": {
                    "home": match.home_shots,
                    "away": match.away_shots,
                },
                "shots_on_target": {
                    "home": match.home_shots_on_target,
                    "away": match.away_shots_on_target,
                },
                "corners": {
                    "home": match.home_corners,
                    "away": match.away_corners,
                },
                "fouls": {
                    "home": match.home_fouls,
                    "away": match.away_fouls,
                },
                "cards": {
                    "yellow": {
                        "home": match.home_yellow_cards,
                        "away": match.away_yellow_cards,
                    },
                    "red": {
                        "home": match.home_red_cards,
                        "away": match.away_red_cards,
                    }
                }
            }
        }
    })


# ========================== VIEWS MODUL FORUM ==========================