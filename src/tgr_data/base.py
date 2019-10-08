import dataclasses


@dataclasses.dataclass
class Team:
    id: str
    name: str


@dataclasses.dataclass
class Player:
    id: str
    name: str
    gender: str = "u"


@dataclasses.dataclass
class PlayerGameRecord:
    game_id: str
    side_id: int
    player_id: str

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


@dataclasses.dataclass
class TeamGameRecord:
    game_id: str
    side_id: int
    team_id: str

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
