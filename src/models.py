from typing import Optional
from pydantic import BaseModel, Field, computed_field
import datetime as dt


class Team(BaseModel):
    id: int
    title: str
    short_title: Optional[str] = None

    # defining the __eq__ and __hash__ methods to allow for comparison of Team objects
    def __eq__(self, other):
        if not isinstance(other, Team):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        return self.id < other.id


class Fixture(BaseModel):
    id: int
    is_result: bool = Field(alias="isResult")
    h: Team
    a: Team
    goals: dict[str, int | None]
    xg: dict[str, float | None] = Field(alias="xG")
    datetime: dt.datetime
    forecast: Optional[dict[str, float]] = None


class MatchStats(BaseModel):
    match_id: Optional[int] = None
    team_id: int
    h_a: str
    xg: float = Field(alias="xG")
    xga: float = Field(alias="xGA")
    npxg: float = Field(alias="npxG")
    npxga: float = Field(alias="npxGA")
    ppda: dict[str, float]
    ppda_allowed: dict[str, float]
    deep: int
    deep_allowed: int
    scored: int
    missed: int
    xpts: float
    result: str
    date: dt.datetime
    wins: int
    draws: int
    loses: int
    pts: int
    npxgd: float = Field(alias="npxGD")

    @computed_field
    def ppda_coef(self) -> float:
        return self.ppda["att"] / self.ppda["def"] if self.ppda["def"] != 0 else 0

    @computed_field
    def ppda_allowed_coef(self) -> float:
        return (
            self.ppda_allowed["att"] / self.ppda_allowed["def"]
            if self.ppda["def"] != 0
            else 0
        )

    @computed_field
    def xg_diff(self) -> float:
        return self.xg - self.scored

    @computed_field
    def xga_diff(self) -> float:
        return self.xga - self.missed

    @computed_field
    def xpts_diff(self) -> float:
        return self.xpts - self.pts
