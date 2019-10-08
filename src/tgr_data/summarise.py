import csv
import itertools
import logging
from pathlib import Path
from typing import Generator, Dict, Type, List, Tuple

from cached_property import cached_property

from tgr_data.base import Player, Team, Game, PlayerGameRecord, GameRecord, TeamGameRecord, TeamGameStats, \
    PlayerGameStats, Stats

log = logging.getLogger(__name__)

raw_data_dir = Path(Path.cwd().parent) / "raw_data"


def get_input_files(input_dirs: List[Path]) -> Generator[Path, None, None]:
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
        record.fgm, record.fga = [int(x) for x in r.pop("fg*").split("-")]
    if "ft" in r and "-" in r["ft"]:
        record.ftm, record.fta = [int(x) for x in r.pop("ft").split("-")]
    if "3pt" in r and "-" in r["3pt"]:
        record.tpm, record.tpa = [int(x) for x in r.pop("3pt").split("-")]

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


class League:
    def __init__(self):
        pass

    @cached_property
    def players(self) -> Dict[str, Player]:
        players = {}
        with (raw_data_dir / "sk_player_ids.csv").open("r") as f:
            for row in csv.DictReader(f):
                player = Player(**row)
                players[player.id] = player
        return players

    @cached_property
    def teams(self) -> Dict[str, Team]:
        teams = {}
        with (raw_data_dir / "sk_team_ids.csv").open("r") as f:
            for row in csv.DictReader(f):
                team = Team(**row)
                teams[team.id] = team
        return teams

    @cached_property
    def games(self) -> Dict[str, Game]:
        games = {}
        with (raw_data_dir / "sk_game_ids.csv").open("r") as f:
            for row in csv.DictReader(f):
                game = Game(**row)
                games[game.id] = game
        return games

    def get_all_records(self, input_dirs: List[Path]) -> Generator[GameRecord, None, None]:
        for path in get_input_files(input_dirs):
            log.info(f"Processing {path}")

            game = self.games[path.stem]

            with path.open("r") as f:
                reader = csv.DictReader(f)
                for row in reader:

                    player_id = row.pop("player")
                    team = self.teams[row["team"]]
                    side_id = game.team_ids.index(team.id)
                    opponent_id = game.opponent_of(team.id)

                    if player_id in self.teams:
                        record: TeamGameRecord = row_to_record(dict(row), record_cls=TeamGameRecord)
                        record.team_id = team.id
                    else:
                        record: PlayerGameRecord = row_to_record(dict(row), record_cls=PlayerGameRecord)
                        player = self.players[player_id]
                        record.player_id = player.id
                        record.team_id = team.id

                    record.game_id = game.id
                    record.side_id = side_id
                    record.opponent_id = opponent_id

                    yield record

    def _record_sort_key(self, record: GameRecord):
        return record.game_id, record.side_id, getattr(record, "player_id", "")

    def get_game_records(self, input_dirs: List[Path]) -> Generator[Tuple[TeamGameRecord, List[PlayerGameRecord]], None, None]:
        """
        Generate TeamGameRecord, one for each side of each game, along with a list of player records.
        """
        records_by_game = itertools.groupby(
            sorted(self.get_all_records(input_dirs), key=self._record_sort_key),
            key=lambda r: (r.game_id, r.side_id),
        )
        for (game_id, side_id), records_iter in records_by_game:
            records = list(records_iter)
            team_record = records[0]
            if not isinstance(team_record, TeamGameRecord):
                player_records = records
                team_record = TeamGameRecord(
                    game_id=game_id,
                    side_id=side_id,
                    team_id=records[0].team_id,
                    opponent_id=self.games[game_id].opponent_of(records[0].team_id),
                )
                for f in GameRecord.raw_stat_fields:
                    setattr(team_record, f, sum(getattr(r, f) for r in records))
            else:
                player_records = records[1:]
            yield team_record, player_records

    def get_game_stats(self, input_dirs: List[Path]) -> Generator[TeamGameStats, None, None]:

        records_by_game = itertools.groupby(
            self.get_game_records(input_dirs=input_dirs),
            key=lambda gr: gr[0].game_id,
        )
        for game_id, records_iter in records_by_game:
            team_records = []

            for gr in records_iter:
                team_records.append(gr[0])
                for pr in gr[1]:
                    yield PlayerGameStats(record=pr)

            if len(team_records) == 2:
                team_records[0].opponent_pts = team_records[1].pts
                team_records[1].opponent_pts = team_records[0].pts
                yield TeamGameStats(record=team_records[0])
                yield TeamGameStats(record=team_records[1])
            else:
                log.warning(f"Incomplete data for game {game_id}, excluding")


def main():
    path: Path

    logging.basicConfig(level=logging.DEBUG)

    input_dirs = [
        raw_data_dir / "easystats",
        raw_data_dir / "statastic",
        raw_data_dir / "sk.v3",
        raw_data_dir / "sk.v4",
    ]

    league = League()

    team_stats = []
    player_stats = []
    for stats in league.get_game_stats(input_dirs):
        if isinstance(stats, TeamGameStats):
            team_stats.append(stats)
        else:
            player_stats.append(stats)

    outputs: Dict[str, List[Stats]] = {
        "team-logs.csv": team_stats,
        "player-logs.csv": player_stats,
    }

    for filename, stats_objects in outputs.items():
        output_path = Path(f"../reports/{filename}")
        with output_path.open("w") as f:
            writer = csv.DictWriter(f, fieldnames=stats_objects[0].to_dict().keys())
            writer.writeheader()
            for stats in stats_objects:
                writer.writerow(stats.to_dict())
        log.info(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
