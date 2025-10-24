# load_players.py
import os
import django
import json
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sportscope_today.settings")
django.setup()

from main.models import Player

base_path = Path("dataset/json")

# ---------------------- PLAYERS ----------------------
with open(base_path / "fifa_players.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    # Handle any data transformation if needed
    Player.objects.update_or_create(
        slug=item.get("slug"), 
        defaults=item
    )
    
print(f"✅ {Player.objects.count()} Players loaded.")