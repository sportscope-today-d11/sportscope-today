import json
from main.models import Team

# Buka file dataset matches
with open('dataset/json/matches_data.json', 'r') as f:
    data = json.load(f)

# Ambil semua tim unik dari dataset
team_slugs = set()
teams = {}

for item in data:
    home_slug = item['HomeTeamSlug']
    away_slug = item['AwayTeamSlug']
    home_name = item['HomeTeam']
    away_name = item['AwayTeam']

    team_slugs.add(home_slug)
    team_slugs.add(away_slug)
    teams[home_slug] = home_name
    teams[away_slug] = away_name

# Buat entri tim di database
for slug in team_slugs:
    name = teams.get(slug, slug.replace('-', ' ').title())

    obj, created = Team.objects.get_or_create(
        slug=slug,
        defaults={
            "name": name,
            "players": 0,
            "age": 0,
            "possession": 0,
            "goals": 0,
            "assists": 0,
            "penalty_kicks": 0,
            "penalty_kick_attempts": 0,
            "yellows": 0,
            "reds": 0,
        },
    )

    if created:
        print(f"✅ Team ditambahkan: {name} ({slug})")
    else:
        print(f"ℹ️ Team sudah ada: {name}")

print("\nSelesai menambahkan tim dari dataset.")
