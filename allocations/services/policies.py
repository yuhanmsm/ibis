from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PolicyAllocationScore:
    score: float


class AllocationPolicy(ABC):
    def __init__(self, name: str, priority: int, hard_condition: bool = False):
        self.name: str = name
        self.priority: int = priority
        self.hard_condition: bool = hard_condition

    @abstractmethod
    def evaluate_teams(self, teams: list) -> PolicyAllocationScore:
        """Evaluates cross-team policies"""
        raise NotImplementedError

    @abstractmethod
    def evaluate_team(self, team) -> PolicyAllocationScore:
        """Evaluates per-team policies"""
        raise NotImplementedError

