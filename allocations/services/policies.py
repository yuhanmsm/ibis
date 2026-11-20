from abc import ABC, abstractmethod
from dataclasses import dataclass

from allocations.services.allocation_data import TeamData

@dataclass
class PolicyAllocationScore:
    score: float


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
