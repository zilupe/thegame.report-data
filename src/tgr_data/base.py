import collections
import dataclasses
import datetime as dt
from typing import ClassVar, List, Dict, Tuple


@dataclasses.dataclass
class Team:
    id: str
    name: str


@dataclasses.dataclass
class Game:
    id: str
    scheduled_time: dt.datetime
    home_side_id: str
    away_side_id: str

    @property
    def team_ids(self) -> Tuple[str, str]:
        return self.home_side_id, self.away_side_id

    def opponent_of(self, team_id: str) -> str:
        """
        returns the id of the opponent team to the team specified by team_id
        """
        return self.team_ids[abs(self.team_ids.index(team_id) - 1)]


@dataclasses.dataclass
class Player:
    id: str
    name: str
    gender: str = "u"


@dataclasses.dataclass
class GameRecord:
    game_id: str = None
    side_id: int = None
    team_id: str = None
    opponent_id: str = None

    fgm: int = 0
    fga: int = 0
    tpm: int = 0
    tpa: int = 0
    ftm: int = 0
    fta: int = 0
    pts: int = 0
    oreb: int = 0
    dreb: int = 0
    reb: int = 0
    ast: int = 0
    stl: int = 0
    tov: int = 0
    blk: int = 0
    pf: int = 0

    raw_stat_fields: ClassVar[List[str]] = (
        "fgm",
        "fga",
        "tpm",
        "tpa",
        "ftm",
        "fta",
        "pts",
        "oreb",
        "dreb",
        "reb",
        "ast",
        "stl",
        "tov",
        "blk",
        "pf",
    )

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self, dict_factory=collections.OrderedDict)


@dataclasses.dataclass
class PlayerGameRecord(GameRecord):
    player_id: str = None


@dataclasses.dataclass
class TeamGameRecord(GameRecord):
    opponent_pts: int = 0


class Stats:
    stats_fields: List[str] = ()

    def __init__(self, record: GameRecord):
        self.record = record

    def to_dict(self) -> Dict:
        return {
            **self.record.to_dict(),
            **{k: getattr(self, k) for k in self.stats_fields},
        }


class TeamGameStats(Stats):
    record: TeamGameRecord

    stats_fields = (
        "possessions",
        "defensive_eff",
        "offensive_eff",
    )

    @property
    def possessions(self) -> float:
        # https://www.nbastuffer.com/analytics101/possession/
        return 0.96 * (
            self.record.fga + self.record.tov + .44 * self.record.fta - self.record.oreb
        )

    @property
    def defensive_eff(self) -> float:
        # https://www.nbastuffer.com/analytics101/defensive-efficiency/
        return 100 * (self.record.opponent_pts / self.possessions)

    @property
    def offensive_eff(self) -> float:
        # https://www.nbastuffer.com/analytics101/offensive-efficiency/
        return 100 * (self.record.pts / self.possessions)


class PlayerGameStats(Stats):
    record: PlayerGameRecord

    stats_fields = (
        "enthusiasm_rating",
        "pir",
    )

    @property
    def enthusiasm_rating(self) -> int:
        return (
            self.record.fga
            + self.record.fta
            + self.record.reb
            + self.record.ast
            + self.record.stl
            + self.record.blk
            + self.record.tov
            + self.record.pf
        )

    @property
    def pir(self) -> int:
        return (
            self.record.pts + self.record.reb + self.record.ast + self.record.stl + self.record.blk
            - (self.record.fta - self.record.ftm)
            - (self.record.fga - self.record.fgm)
            - self.record.tov
            - self.record.pf
        )
