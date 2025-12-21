# Create your models here.
from unidecode import unidecode
from django.db import models
from django.utils.text import slugify
import os
import uuid
from django.templatetags.static import static
from urllib.parse import urlparse
from django.contrib.staticfiles import finders
from django.contrib.auth.models import User


class Team(models.Model):
    slug = models.SlugField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    players = models.IntegerField()
    age = models.FloatField(null=True)
    possession = models.FloatField()
    goals = models.IntegerField()
    assists = models.IntegerField()
    penalty_kicks = models.IntegerField(null=True)
    penalty_kick_attempts = models.IntegerField(null=True)
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
        # Jika ada uploaded image
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

        # cek logo di static/images/logo
        static_path = f"/static/images/logo/{self.slug}.png" if self.slug else None
        static_file = f"static/images/logo/{self.slug}.png" if self.slug else None

        if static_file and os.path.exists(static_file):
            return static_path

        # kalau gak ada logo, gausah tampil apa-apa
        return None

class Person(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User '),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'

    @classmethod
    def get_user_role(cls, user):
        try:
            return cls.objects.get(user=user).role
        except cls.DoesNotExist:
            return 'user'
          
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

    bookmarked_by = models.ManyToManyField(
        Person,
        related_name="bookmarked_news",
        blank=True,
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


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.CharField(max_length=20)
    match_date = models.DateField()
    league = models.CharField(max_length=100, default="Unknown")

    home_team = models.ForeignKey(Team, related_name="home_matches", on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name="away_matches", on_delete=models.CASCADE)

    # Full-time results
    full_time_home_goals = models.IntegerField(default=0)
    full_time_away_goals = models.IntegerField(default=0)
    full_time_result = models.CharField(max_length=1, default="D")  # 'H' (home), 'A' (away), 'D' (draw)

    # Half-time results
    half_time_home_goals = models.IntegerField(default=0)
    half_time_away_goals = models.IntegerField(default=0)
    half_time_result = models.CharField(max_length=1, default="D")

    # Stats
    home_shots = models.IntegerField(default=0)
    away_shots = models.IntegerField(default=0)
    home_shots_on_target = models.IntegerField(default=0)
    away_shots_on_target = models.IntegerField(default=0)
    home_corners = models.IntegerField(default=0)
    away_corners = models.IntegerField(default=0)
    home_fouls = models.IntegerField(default=0)
    away_fouls = models.IntegerField(default=0)
    home_yellow_cards = models.IntegerField(default=0)
    away_yellow_cards = models.IntegerField(default=0)
    home_red_cards = models.IntegerField(default=0)
    away_red_cards = models.IntegerField(default=0)

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
    image = models.ImageField(upload_to="player_pictures/", null=True, blank=True)

    # override fungsi save agar membuat slug otomatis dari nama pemain
    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or "Unnamed Player"

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

class Forum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    views = models.PositiveIntegerField(default=0)

    # 👇 NEW: optional image untuk post (supaya FE bisa render image_url)
    image = models.ImageField(
        upload_to="forum_images/",
        null=True,
        blank=True,
    )

    quoted_post = models.ForeignKey(
        "self",
        related_name="quoted_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    bookmarked_by = models.ManyToManyField(
        Person,
        related_name="bookmarked_forums",
        blank=True
    )

    author = models.ForeignKey(
        Person,
        related_name="forums",
        on_delete=models.CASCADE,
    )

    liked_by = models.ManyToManyField(
        Person,
        related_name="liked_forums",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    # ---- helper counter ----
    @property
    def like_count(self):
        return self.liked_by.count()

    @property
    def bookmark_count(self):
        return self.bookmarked_by.count()

    # 👇 NEW: comment count biar UI ga perlu hitung manual
    @property
    def comment_count(self):
        return self.comments.filter(parent__isnull=True).count()

    # 👇 NEW: "reposts" / "quotes" ala X (sementara sama-sama dari quoted_by)
    @property
    def repost_count(self):
        return self.quoted_by.count()

    @property
    def quote_count(self):
        return self.quoted_by.count()

    # 👇 NEW: image_url helper untuk API response
    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return None

    
class Comment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    forum = models.ForeignKey(
        Forum,
        related_name="comments",
        on_delete=models.CASCADE,
    )

    author = models.ForeignKey(
        Person,
        related_name="comments",
        on_delete=models.CASCADE,
    )

    parent = models.ForeignKey(
        "self",
        related_name="replies",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # buat "to @username"
    reply_to = models.ForeignKey(
        Person,
        related_name="comment_replies",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # siapa aja yang nge-like comment ini
    liked_by = models.ManyToManyField(
        Person,
        related_name="liked_comments",
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.user.username}: {self.text[:30]}"

    @property
    def is_root(self):
        return self.parent is None

    @property
    def reply_to_username(self):
        if self.reply_to:
            return self.reply_to.user.username
        return None

    # 👇 NEW: helper counter like
    @property
    def like_count(self):
        return self.liked_by.count()
