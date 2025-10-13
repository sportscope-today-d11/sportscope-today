from django.db import models

# Create your models here.

class TeamStats(models.Model):
    team = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    players = models.PositiveIntegerField()
    age = models.FloatField()
    possession = models.FloatField()
    goals = models.PositiveIntegerField()
    assists = models.PositiveIntegerField()
    penalty_kicks = models.PositiveIntegerField()
    penalty_kick_attempts = models.PositiveIntegerField()
    yellows = models.PositiveIntegerField()
    reds = models.PositiveIntegerField()
    expected_goals = models.FloatField(null=True)
    expected_assists = models.FloatField()
    progressive_carries = models.PositiveIntegerField()
    progressive_passes = models.PositiveIntegerField()

    class Meta:
        db_table = "team_stats"
        verbose_name = "Team Statistics"
        verbose_name_plural = "Teams Statistics"

    def __str__(self):
        return self.team