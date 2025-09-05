from enum import Enum

from pydantic import BaseModel, Field


class Ranking(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class RankingThresholds(BaseModel):
    """
    Model used to convert input values into a Ranking [LOW, MEDIUM, HIGH].

    LOW := value < low;
    MEDIUM := low >= value < medium;
    HIGH := value >= high;
    """

    low: float = Field(description="Upper bound (not inclusive) of the LOW Ranking")
    medium: float = Field(
        description="Upper bound (not inclusive) of the Medium Ranking"
    )

    def ranking_for(self, value: float) -> Ranking:
        if value < self.low:
            return Ranking.LOW
        elif value < self.medium:
            return Ranking.MEDIUM
        else:
            return Ranking.HIGH


class RankingWeight(BaseModel):
    """
    Model used to map a given Rank [LOW, MEDIUM, HIGH] into a weight.
    """

    low: float = Field(description="Weight given to the lowest rank")
    medium: float = Field(description="Weight given to the middle rank")
    high: float = Field(description="Weight given to the highest rank")

    def weight_for_ranking(self, ranking: Ranking) -> float:
        if ranking == Ranking.LOW:
            return self.low
        elif ranking == ranking.MEDIUM:
            return self.medium
        else:
            return self.high
