import argparse
import csv
import logging
import sys
from pathlib import Path
from typing import Dict

log = logging.getLogger(__name__)

sys.path.append("../../unicorn")
from unicorn.v2.season_page import SeasonParse


def extract_scores(input_dir: Path, output_dir: Path):
    log.info(f"Extracting scores from {input_dir}")

    seasons: Dict[int, SeasonParse] = {}

    # Standings should be parsed before fixtures in order to get the teams list first
    # so we are sorting items in reverse order.
    for item in sorted(input_dir.iterdir(), reverse=True):
        if item.suffix != ".html":
            log.debug(f"Skipping {item}")
            continue

        log.info(f"Parsing {item}")

        parts = item.name.split("-")
        gm_season_id = int(parts[1])
        is_fixtures = parts[2] == "fixtures.html"
        if gm_season_id not in seasons:
            seasons[gm_season_id] = SeasonParse()

        if is_fixtures:
            seasons[gm_season_id].parse_fixtures_page(item.read_text())
        else:
            seasons[gm_season_id].parse_standings_page(item.read_text())

    seasons_rows = []
    games_rows = []
    team_rows = []

    for season in seasons.values():

        seasons_rows.append({
            "id": season.season_id,
            "league_id": season.league_id,
            "division_id": season.division_id,
            "name": season.season_name,
            "first_week_date": sorted(season.game_days, key=lambda gd: gd.date)[0].date if season.game_days else None,
            "last_week_date": sorted(season.game_days, key=lambda gd: gd.date)[-1].date if season.game_days else None,
        })

        for team in season.teams.values():
            team_rows.append({
                "id": team.id,
                "incorrect_name": team.name,
            })

        for game_day in season.game_days:
            for g in game_day.games:
                games_rows.append({
                    "id": g.id,
                    "scheduled_time": g.starts_at,
                    "season_id": season.season_id,
                    "season_stage": g.season_stage,
                    "home_team_id": g.home_team_id,
                    "home_team_pts": g.home_team_score,
                    "home_team_outcome": g.home_team_outcome,
                    "away_team_id": g.away_team_id,
                    "away_team_pts": g.away_team_score,
                    "away_team_outcome": g.away_team_outcome,
                })

    for i, season_row in enumerate(sorted(seasons_rows, key=lambda s: s["first_week_date"])):
        season_row["sequence_number"] = i + 1

    output_path = output_dir / "gm_seasons.csv"
    with output_path.open("w") as f:
        csv_writer = csv.DictWriter(
            f,
            fieldnames=[
                "sequence_number",
                "id",
                "league_id",
                "division_id",
                "name",
                "first_week_date",
                "last_week_date",
            ],
        )
        csv_writer.writeheader()
        csv_writer.writerows(sorted(seasons_rows, key=lambda s: s["first_week_date"]))
    log.info(f"{len(seasons_rows)} seasons written to {output_path}")

    output_path = output_dir / "gm_teams.csv"
    with output_path.open("w") as f:
        csv_writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "incorrect_name",
            ],
        )
        csv_writer.writeheader()
        csv_writer.writerows(team_rows)
    log.info(f"{len(team_rows)} teams written to {output_path}")

    output_path = output_dir / "gm_games.csv"
    with output_path.open("w") as f:
        csv_writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "scheduled_time",
                "season_id",
                "season_stage",
                "home_team_id",
                "home_team_pts",
                "home_team_outcome",
                "away_team_id",
                "away_team_pts",
                "away_team_outcome",
            ],
        )
        csv_writer.writeheader()
        csv_writer.writerows(games_rows)
    log.info(f"{len(games_rows)} games written to {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", help="Directory that contains scraped HTML files", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--log-level", choices=("info", "warn", "warning", "error", "debug"), default="info")

    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper()),
        stream=sys.stdout,
    )

    extract_scores(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
