from django.db import models
from django.utils.text import slugify
import os

# Create your models here.

class Team(models.Model):
    slug = models.SlugField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    players = models.IntegerField()
    age = models.FloatField()
    possession = models.FloatField()
    goals = models.IntegerField()
    assists = models.IntegerField()
    penalty_kicks = models.IntegerField()
    penalty_kick_attempts = models.IntegerField()
    yellows = models.IntegerField()
    reds = models.IntegerField()
    image = models.ImageField(upload_to="teams/", null=True, blank=True)

    # override fungsi save agar membuat slug otomatis dari nama tim
    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        static_path = f"/static/images/teams/{self.slug}.png" if self.slug else None
        default_path = "/static/images/teams/default.png"
        static_file = f"static/images/teams/{self.slug}.png" if self.slug else None
        if static_file and os.path.exists(static_file):
            return static_path
        return default_path

    def __str__(self):
        return self.name or "Unnamed Team"

class News(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    author = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    publish_time = models.DateField()
    content = models.TextField()
    thumbnail = models.URLField(
        default="https://akcdn.detik.net.id/community/media/visual/2020/02/25/3833496a-a1b8-428f-9202-79f8671928b7_169.jpeg?w=700&q=90",
        blank=True
    )

    def __str__(self):
        return self.title
