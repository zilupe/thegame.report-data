"""
This depends on https://github.com/zilupe/unicorn

so should first install dependencies of that (assuming you're under src):

    pip install -r ../../unicorn/requirements.txt

set season_id= below

and then run this from src directory:

    python -m tgr_data.prepare_season_games_list

"""
import csv
import sys

sys.path.append("../../unicorn")

from unicorn.v2.season_page import SeasonParse

season_id = 25

season = SeasonParse()
with open(f"/Users/jazeps/Desktop/s{season_id}-standings.html") as f:
    season.parse_standings_page(f.read())

with open(f"/Users/jazeps/Desktop/s{season_id}-fixtures.html") as f:
    season.parse_fixtures_page(f.read())

teams_by_id = {t["id"]: t["name"].lower().replace(" ", "") for t in season.teams.values()}

rows = []
for game_day in season.game_days:
    for g in game_day.games:
        g_id = (
            f"{g['starts_at'].strftime('%Y%m%d-%H%M')}-"
            f"{teams_by_id[g['home_team_id']]}-"
            f"{teams_by_id[g['away_team_id']]}"
        )
        rows.append({
            "id": g_id,
            "home_team_id": teams_by_id[g["home_team_id"]],
            "away_team_id": teams_by_id[g["home_team_id"]],
            "scheduled_time": g["starts_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "season_id": season_id,
        })

filename = f"s{season_id}-games.csv"
with open(filename, "w") as f:
    csv_writer = csv.DictWriter(f, fieldnames=["id", "scheduled_time", "home_team_id", "away_team_id", "season_id"])
    csv_writer.writeheader()
    csv_writer.writerows(rows)

print(f"Games list written to {filename}")
