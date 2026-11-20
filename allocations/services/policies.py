from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from allocations.services.allocation_data import TeamData


@dataclass(frozen=True)
class PolicyViolation:
    """Human-readable feedback of unmet policy conditions

    :param message: A message describing the violation that occured
    """

    message: str


@dataclass(frozen=True)
class PolicyEvaluation:
    """Holds the result of a policy evaluation

    :param score: A normalised score from 0 to 1 of how well the allocation
    satisfied the policy
    :param violations: A list of policy violations that occured
    :param satisfied: Whether the policy was free of any violations
    """

    score: float
    violations: list[PolicyViolation] = field(default_factory=list)

    @property
    def satisfied(self) -> bool:
        """Whether any violations occured"""
        return len(self.violations) == 0


class AllocationPolicy(ABC):
    """Base class for an allocation policy

    :param name: The name of the policy
    :param priority: The priority that this policy should have
    :param hard_condition: Whether the policy must be satisfied fully
    """

    def __init__(self, name: str, priority: int, hard_condition: bool = False):
        if priority < 0:
            raise ValueError("Priority can not be negative.")
        self.name: str = name
        self.priority: int = priority
        self.hard_condition: bool = hard_condition

    @abstractmethod
    def evaluate_teams(self, teams: list[TeamData]) -> PolicyEvaluation:
        """Evaluates to what extent the policy has been met in the created teams

        :param teams: A list of allocated teams
        :returns: An evaluation of how much the policy has been satisfies in the
        team allocations
        """
        ...

    def evaluate_team(self, team: TeamData) -> PolicyEvaluation:
        """Evaluates to what extent the policy has been met per team

        Not always possible depending on the policy, so not mandatory to implement

        :param team: The team to evaluate
        :returns: An evaluation of to what extent the policy has been satisfied
        by the team allocation
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement per-team evaluation."
        )
