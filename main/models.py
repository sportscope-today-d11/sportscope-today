from unidecode import unidecode
from django.db import models
from django.utils.text import slugify
import os
import uuid

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
        default="https://akcdn.detik.net.id/community/media/visual/2020/02/25/3833496a-a1b8-428f-9202-79f8671928b7_169.jpeg?w=700&q=90",
        blank=True
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Other"
    )

    def __str__(self):
        return self.title

class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.CharField(max_length=20)
    match_date = models.DateField()
    league = models.CharField(max_length=100, default="Unknown")

    home_team = models.ForeignKey(Team, related_name="home_matches", on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name="away_matches", on_delete=models.CASCADE)

    # Full-time results
    full_time_home_goals = models.IntegerField()
    full_time_away_goals = models.IntegerField()
    full_time_result = models.CharField(max_length=1)  # 'H' (home), 'A' (away), 'D' (draw)

    # Half-time results
    half_time_home_goals = models.IntegerField()
    half_time_away_goals = models.IntegerField()
    half_time_result = models.CharField(max_length=1)

    # Stats
    home_shots = models.IntegerField()
    away_shots = models.IntegerField()
    home_shots_on_target = models.IntegerField()
    away_shots_on_target = models.IntegerField()
    home_corners = models.IntegerField()
    away_corners = models.IntegerField()
    home_fouls = models.IntegerField()
    away_fouls = models.IntegerField()
    home_yellow_cards = models.IntegerField()
    away_yellow_cards = models.IntegerField()
    home_red_cards = models.IntegerField()
    away_red_cards = models.IntegerField()

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.match_date})"

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

    def __str__(self):
        return self.name or "Unnamed Player"