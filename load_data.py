import os
import django
import json
from pathlib import Path
from django.utils.dateparse import parse_date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sportscope_today.settings")
django.setup()

from main.models import News

base_path = Path("dataset/json")

# ---------------------- NEWS ----------------------
with open(base_path / "news_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for item in data:
    if "publish_time" in item:
        item["publish_time"] = parse_date(item["publish_time"])
    News.objects.update_or_create(title=item.get("title"), defaults=item)
print(f"✅ {News.objects.count()} News loaded.")
