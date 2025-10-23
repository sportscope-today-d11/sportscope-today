import json
from main.models import News
from datetime import datetime

with open('dataset/json/news_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for item in data:
    # convert timestamp ke tanggal
    timestamp = item.get("publish_time")
    if isinstance(timestamp, int):
        publish_date = datetime.fromtimestamp(timestamp / 1000).date()
    else:
        publish_date = datetime.strptime("2000-01-01", "%Y-%m-%d").date()

    News.objects.create(
        title=item.get("title", "No Title"),
        link=item.get("link", ""),
        author=item.get("author", ""),
        source=item.get("source", ""),
        publish_time=publish_date,
        content=item.get("content", ""),
        thumbnail=item.get("thumbnail", ""),
        category=item.get("category", "Other"),
    )

print("News data loaded successfully!")
