from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
import json
from main.models import Person, Team
from django.utils.html import strip_tags
from django.contrib.auth import logout as auth_logout

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

# ========================== VIEWS MODUL TEAM ==========================
# List semua teams
@csrf_exempt
def team_list(request):
    try:
        teams = Team.objects.all()
        
        # Build full URL untuk images
        base_url = request.build_absolute_uri('/')[:-1]  # Removes trailing slash
        
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
        
        return JsonResponse({
            'status': 'success',
            'data': teams_data
        }, safe=False)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


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
        
        return JsonResponse({
            'status': 'success',
            'data': team_data
        })
    
    except Team.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Team not found'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ========================== VIEWS MODUL NEWS ==========================


# ========================== VIEWS MODUL PLAYER ==========================


# ========================== VIEWS MODUL MATCH RESULTS ==========================


# ========================== VIEWS MODUL FORUM ==========================