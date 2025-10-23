from django.test import TestCase
from django.urls import reverse
from .models import Team, Match
import datetime
import uuid

class MatchViewsTest(TestCase):
    def setUp(self):
        self.team1 = Team.objects.create(
            slug="team-a",
            name="Team A",
            players=11,
            age=25.0,
            possession=55.0,
            goals=10,
            assists=5,
            penalty_kicks=2,
            penalty_kick_attempts=3,
            yellows=1,
            reds=0
        )
        self.team2 = Team.objects.create(
            slug="team-b",
            name="Team B",
            players=11,
            age=24.5,
            possession=45.0,
            goals=8,
            assists=4,
            penalty_kicks=1,
            penalty_kick_attempts=2,
            yellows=2,
            reds=1
        )

        self.match = Match.objects.create(
            id=uuid.uuid4(),
            season="2025",
            match_date=datetime.date.today(),
            league="Premier League",
            home_team=self.team1,
            away_team=self.team2,
            full_time_home_goals=2,
            full_time_away_goals=1,
            full_time_result="H",
            half_time_home_goals=1,
            half_time_away_goals=1,
            half_time_result="D",
            home_shots=10,
            away_shots=8,
            home_shots_on_target=5,
            away_shots_on_target=3,
            home_corners=6,
            away_corners=4,
            home_fouls=8,
            away_fouls=9,
            home_yellow_cards=1,
            away_yellow_cards=2,
            home_red_cards=0,
            away_red_cards=0
        )

    def test_history_page_loads(self):
        url = reverse('main:match_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_match_detail_loads(self):
        url = reverse('main:match_detail', args=[self.match.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

