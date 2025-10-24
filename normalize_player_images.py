import os
import django
import json
from pathlib import Path
from django.utils.dateparse import parse_date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sportscope_today.settings")
django.setup()

from main.models import Team, Player, Match, News  # pastiin ini app lu

base_path = Path("dataset/json")

# ---------------------- TEAMS ----------------------
with open(base_path / "team_stats.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for item in data:
    Team.objects.update_or_create(slug=item.get("slug"), defaults=item)
print(f"✅ {Team.objects.count()} Teams loaded.")

# ---------------------- PLAYERS ----------------------
with open(base_path / "fifa_players.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for item in data:
    Player.objects.update_or_create(slug=item.get("slug"), defaults=item)
print(f"✅ {Player.objects.count()} Players loaded.")

# ---------------------- MATCHES ----------------------
import re
from main.models import Team

with open(base_path / "matches_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    # ubah key JSON jadi snake_case
    normalized = {}
    for key, val in item.items():
        new_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
        normalized[new_key] = val

    # parse tanggal
    if "match_date" in normalized:
        normalized["match_date"] = parse_date(normalized["match_date"])

    # ambil relasi tim dari slug
    home_slug = normalized.pop("home_team_slug", None)
    away_slug = normalized.pop("away_team_slug", None)

    if home_slug:
        normalized["home_team"] = Team.objects.filter(slug=home_slug).first()
    if away_slug:
        normalized["away_team"] = Team.objects.filter(slug=away_slug).first()

    # create / update Match
    Match.objects.update_or_create(
        id=normalized.get("id"),
        defaults=normalized
    )

print(f"✅ {Match.objects.count()} Matches loaded.")

# ---------------------- NEWS ----------------------
with open(base_path / "news_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for item in data:
    if "publish_time" in item:
        item["publish_time"] = parse_date(item["publish_time"])
    News.objects.update_or_create(title=item.get("title"), defaults=item)
print(f"✅ {News.objects.count()} News loaded.")


