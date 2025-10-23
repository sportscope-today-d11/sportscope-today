import json
from datetime import datetime
from main.models import Team, Match

# Path ke file JSON (ubah kalau folder kamu beda)
file_path = "dataset/json/matches_data.json"

print("📂 Membaca file dataset:", file_path)

with open(file_path, "r") as file:
    data = json.load(file)

print(f"📊 Jumlah pertandingan dalam dataset: {len(data)}")

added = 0
skipped = 0

for item in data:
    try:
        home_slug = item["HomeTeamSlug"]
        away_slug = item["AwayTeamSlug"]

        # Pastikan kedua tim ada di database
        home_team = Team.objects.get(slug=home_slug)
        away_team = Team.objects.get(slug=away_slug)

        # Buat atau skip kalau sudah ada match serupa
        match, created = Match.objects.get_or_create(
            season=item["Season"],
            match_date=datetime.strptime(item["MatchDate"], "%Y-%m-%d").date(),
            home_team=home_team,
            away_team=away_team,
            defaults={
                "league": "Premier League",
                "full_time_home_goals": item["FullTimeHomeGoals"],
                "full_time_away_goals": item["FullTimeAwayGoals"],
                "full_time_result": item["FullTimeResult"],
                "half_time_home_goals": item["HalfTimeHomeGoals"],
                "half_time_away_goals": item["HalfTimeAwayGoals"],
                "half_time_result": item["HalfTimeResult"],
                "home_shots": item["HomeShots"],
                "away_shots": item["AwayShots"],
                "home_shots_on_target": item["HomeShotsOnTarget"],
                "away_shots_on_target": item["AwayShotsOnTarget"],
                "home_corners": item["HomeCorners"],
                "away_corners": item["AwayCorners"],
                "home_fouls": item["HomeFouls"],
                "away_fouls": item["AwayFouls"],
                "home_yellow_cards": item["HomeYellowCards"],
                "away_yellow_cards": item["AwayYellowCards"],
                "home_red_cards": item["HomeRedCards"],
                "away_red_cards": item["AwayRedCards"],
            }
        )

        if created:
            added += 1
            print(f"✅ Tambah match: {home_team.name} vs {away_team.name} ({item['MatchDate']})")
        else:
            skipped += 1

    except Team.DoesNotExist as e:
        print(f"⚠️  Tim belum ada di DB: {e}")
    except Exception as e:
        print(f"❌ Error pada data {item}: {e}")

print(f"\n✅ Selesai import. Tambah: {added}, Lewati: {skipped}")
