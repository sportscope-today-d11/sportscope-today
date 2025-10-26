from django.db import models
from django.utils.text import slugify
import os
import uuid
from unidecode import unidecode
from django.templatetags.static import static
from urllib.parse import urlparse

# Create your models here.

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
