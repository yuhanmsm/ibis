from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from allocations.services.allocation_data import TeamData


@dataclass(frozen=True)
class PolicyViolation:


    message: str


@dataclass(frozen=True)
class PolicyEvaluation:

    score: float
    violations: list[PolicyViolation] = field(default_factory=list)

    @property
    def satisfied(self) -> bool:
        """Whether any violations occured"""
        return len(self.violations) == 0


class AllocationPolicy(ABC):
    def __init__(self, name: str, priority: int, hard_condition: bool = False):
        self.name: str = name
        self.priority: int = priority
        self.hard_condition: bool = hard_condition

    @abstractmethod
    def evaluate_teams(self, teams: list[TeamData]) -> PolicyEvaluation:

        ...

    def evaluate_team(self, team: TeamData) -> PolicyEvaluation:

        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement per-team evaluation."
        )
