from django.db import models

# Create your models here.
from unidecode import unidecode
from django.db import models
from django.utils.text import slugify
import os
import uuid
from unidecode import unidecode
from django.templatetags.static import static
from urllib.parse import urlparse
from django.contrib.auth.models import User

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

class Player(models.Model):
    slug = models.SlugField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    weight_kgs = models.FloatField(null=True, blank=True)
    positions = models.CharField(max_length=100, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    overall_rating = models.PositiveIntegerField(null=True, blank=True)
    value_euro = models.FloatField(null=True, blank=True)
    wage_euro = models.FloatField(null=True, blank=True)
    preferred_foot = models.CharField(max_length=10, null=True)
    international_reputation = models.PositiveIntegerField(null=True, blank=True)
    weak_foot = models.PositiveIntegerField(null=True, blank=True)
    skill_moves = models.PositiveIntegerField(null=True, blank=True)
    release_clause_euro = models.FloatField(null=True, blank=True)
    national_team = models.CharField(max_length=100, null=True)
    finishing = models.PositiveIntegerField(null=True, blank=True)
    heading_accuracy = models.PositiveIntegerField(null=True, blank=True)
    short_passing = models.PositiveIntegerField(null=True, blank=True)
    volleys = models.PositiveIntegerField(null=True, blank=True)
    dribbling = models.PositiveIntegerField(null=True, blank=True)
    long_passing = models.PositiveIntegerField(null=True, blank=True)
    ball_control = models.PositiveIntegerField(null=True, blank=True)
    acceleration = models.PositiveIntegerField(null=True, blank=True)
    sprint_speed = models.PositiveIntegerField(null=True, blank=True)
    agility = models.PositiveIntegerField(null=True, blank=True)
    jumping = models.PositiveIntegerField(null=True, blank=True)
    stamina = models.PositiveIntegerField(null=True, blank=True)
    strength = models.PositiveIntegerField(null=True, blank=True)
    long_shots = models.PositiveIntegerField(null=True, blank=True)
    vision = models.PositiveIntegerField(null=True, blank=True)
    penalties = models.PositiveIntegerField(null=True, blank=True)
    marking = models.PositiveIntegerField(null=True, blank=True)
    standing_tackle = models.PositiveIntegerField(null=True, blank=True)
    sliding_tackle = models.PositiveIntegerField(null=True, blank=True)
    likes = models.PositiveIntegerField(default=0)

    # override fungsi save agar membuat slug otomatis dari nama pemain
    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        # Cek apakah ada file static untuk slug tertentu
        if self.slug:
            static_file_path = f"static/images/player_pictures/{self.slug}.png"
            if os.path.exists(static_file_path):
                return f"/static/images/player_pictures/{self.slug}.png"
        
        # Fallback ke default
        return "/static/images/player_pictures/default.png"

    def __str__(self):
        return self.name or "Unnamed Player"

class News(models.Model):
    CATEGORY_CHOICES = [
        ("Transfer", "Transfer"),
        ("Injury Update", "Injury Update"),
        ("Match Result", "Match Result"),
        ("Manager News", "Manager News"),
        ("Player Award", "Player Award"),
        ("Thoughts", "Thoughts"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=255)
    link = models.URLField()
    author = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    publish_time = models.DateField()
    content = models.TextField()
    thumbnail = models.URLField(
        default="images/thumbnails/default.png",
        blank=True
    )
    featured = models.BooleanField(default=False)
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Other"
    )

    def __str__(self):
        return self.title
    
    @property
    def thumbnail_url(self):
        """
        Kembalikan URL untuk thumbnail:
        - Kalau field thumbnail isinya 'default' atau kosong → pakai default static image.
        - Kalau field thumbnail isinya URL valid (http/https) → pakai URL tersebut.
        - Kalau field thumbnail isinya path lokal (images/thumbnails/...) → pakai static().
        """
        if not self.thumbnail or self.thumbnail.lower() == "default":
            return static("images/thumbnails/default.png")

        parsed = urlparse(self.thumbnail)
        if parsed.scheme in ("http", "https"):
            return self.thumbnail
        else:
            return static(self.thumbnail)
        
class Person(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

