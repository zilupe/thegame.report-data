import csv
import itertools
import logging
from pathlib import Path
from typing import Generator, Dict, Type

from tgr_data.base import Player, Team, Game, PlayerGameRecord, GameRecord, TeamGameRecord

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


def row_to_record(row: Dict, record_cls: Type[GameRecord] = GameRecord):
    r = dict(row)
    record: GameRecord = record_cls(
        game_id=r.pop("game_id", None),
    )

    if "2fga" in r and ("3fga" in r and "fga" in r):
        r.pop("2fga")
        r.pop("2fgm")

    # Easystats
    if "fg*" in r and "-" in r["fg*"]:
        record.fga, record.fgm = [int(x) for x in r.pop("fg*").split("-")]
    if "ft" in r and "-" in r["ft"]:
        record.fta, record.ftm = [int(x) for x in r.pop("ft").split("-")]
    if "3pt" in r and "-" in r["3pt"]:
        record.tpa, record.tpm = [int(x) for x in r.pop("3pt").split("-")]

    for f in ("dreb", "oreb", "reb", "ast", "stl", "tov", "blk", "pts", "fta", "ftm", "fga", "fgm", "tpa", "tpm", "pf"):
        if f in r:
            v = r.pop(f)
            setattr(record, f, int(v or 0))

    ignored = (
        "team",
        "player",
        "",
        "a!",
        "eff",
        "pir",
        "tim",
        "+/-",
        "min",
        "fg%",
        "3fg%",
        "3p%",
        "2fg%",
        "ft%",
        "treb",
        "fd",
        "blka",
        "scheduled_time",
    )

    for k in ignored:
        if k in r:
            r.pop(k)

    mapped = {
        "asst": "ast",
        "foul": "pf",
        "fol": "pf",
        "fc": "pf",
        "to": "tov",
        "3fga": "tpa",
        "3fgm": "tpm",
        "3pa": "tpa",
        "3pm": "tpm",
        "orb": "oreb",
        "drb": "dreb",
    }

    for k, v in mapped.items():
        if k in r:
            setattr(record, v, int(r.pop(k)))

    assert not r, (r, record)
    return record


def get_all_records() -> Generator[GameRecord, None, None]:

    teams = {team.id: team for team in get_registered_teams()}
    players = {player.id: player for player in get_registered_players()}
    games = {game.id: game for game in get_registered_games()}

    log.info(f"Found {len(players)} registered players")
    log.info(f"Found {len(teams)} registered teams")
    log.info(f"Found {len(games)} registered games")

    for path in get_input_files():
        log.info(f"Processing {path}")

        game = games[path.stem]

        with path.open("r") as f:
            reader = csv.DictReader(f)
            for row in reader:

                player_id = row.pop("player")
                team = teams[row["team"]]

                if player_id in teams:
                    record: TeamGameRecord = row_to_record(dict(row), record_cls=TeamGameRecord)
                    record.team_id = team.id
                else:
                    record: PlayerGameRecord = row_to_record(dict(row), record_cls=PlayerGameRecord)
                    player = players[player_id]
                    record.player_id = player.id
                    record.team_id = team.id

                record.game_id = game.id
                record.side_id = [game.home_side_id, game.away_side_id].index(record.team_id)
                assert record.game_id
                yield record


def record_sort_key(record: GameRecord):
    return record.game_id, record.side_id, getattr(record, "player_id", "")


def main():
    path: Path

    logging.basicConfig(level=logging.DEBUG)

    records_by_game = itertools.groupby(sorted(get_all_records(), key=record_sort_key), key=lambda r: (r.game_id, r.side_id))
    for (game_id, side_id), records_iter in records_by_game:
        records = list(records_iter)
        if not isinstance(records[0], TeamGameRecord):
            print(f"Need a team summary for {game_id}, {records[0].team_id}")
        else:
            print(records[0])


if __name__ == "__main__":
    main()
