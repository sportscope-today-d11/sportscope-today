import json
from main.models import News

with open('dataset/json/news_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for item in data:
    News.objects.create(
        title=item.get("title", "No Title"),
        link=item.get("link", ""),
        author=item.get("author", ""),
        source=item.get("source", ""),
        publish_time=item.get("publish_time", "2000-01-01"),
        content=item.get("content", ""),
        thumbnail=item.get("thumbnail", "default"),
    )

print("News data loaded successfully!")
