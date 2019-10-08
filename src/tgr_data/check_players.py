"""
Go through all CSV files in raw_data and find any unknown players.
A player is unknown if they are not listed in raw_data/sk_player_ids.csv
"""
import csv
import logging
from pathlib import Path
from typing import Generator

from tgr_data.base import Player, Team, Game

log = logging.getLogger(__name__)

raw_data_dir = Path(Path.cwd().parent) / "raw_data"

input_dirs = [
    raw_data_dir / "easystats",
    raw_data_dir / "statastic",
    raw_data_dir / "sk.v3",
    raw_data_dir / "sk.v4",
]


def get_registered_players() -> Generator[Player, None, None]:
    with (raw_data_dir / "sk_player_ids.csv").open("r") as f:
        for row in csv.DictReader(f):
            yield Player(**row)


def get_registered_teams() -> Generator[Team, None, None]:
    with (raw_data_dir / "sk_team_ids.csv").open("r") as f:
        for row in csv.DictReader(f):
            yield Team(**row)


def get_registered_games() -> Generator[Game, None, None]:
    with (raw_data_dir / "sk_game_ids.csv").open("r") as f:
        for row in csv.DictReader(f):
            yield Game(**row)


def get_input_files() -> Generator[Path, None, None]:
    for input_dir in input_dirs:
        for item in input_dir.iterdir():
            if item.suffix == ".csv":
                yield item


def main():
    path: Path

    logging.basicConfig(level=logging.DEBUG)

    teams = {team.id: team for team in get_registered_teams()}
    players = {player.id: player for player in get_registered_players()}
    games = {game.id: game for game in get_registered_games()}

    log.info(f"Found {len(players)} registered players")
    log.info(f"Found {len(teams)} registered teams")
    log.info(f"Found {len(games)} registered games")

    for path in get_input_files():
        log.info(f"Processing {path}")

        # game = games[path.stem]

        with path.open("r") as f:
            reader = csv.DictReader(f)
            for row in reader:

                r = dict(row)

                if r["player"] in teams:
                    # TODO team stats!
                    continue

                player = players[r["player"]]
                team = teams[r["team"]]

    for path in get_input_files():
        print(path.stem)



if __name__ == "__main__":
    main()
