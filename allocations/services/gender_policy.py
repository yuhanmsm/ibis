from collections import Counter
from typing import ClassVar, override

from allocations.services.allocation_data import TeamData
from allocations.services.policies import (
    AllocationPolicy,
    PolicyEvaluation,
    PolicyViolation,
)


class GenderRepresentationPolicy(AllocationPolicy):
    GENDER_IDENTITES: ClassVar[dict[int, str]] = {
        0: "Unspecified",
        1: "Woman",
        2: "Man",
        3: "other/non-binary",
    }

    def __init__(self, priority: int, hard_condition: bool = False):
        super().__init__("Gender representation policy", priority, hard_condition)

    def _sole_member(self, team: TeamData):
        gender_counts = Counter(
            member.gender for member in team.members if member.gender != 0
        )
        return [
            PolicyViolation(
                f"{team.name} has only one {self.GENDER_IDENTITES.get(gender)} student."
            )
            for gender, count in gender_counts.items()
            if count == 1
        ]

    @override
    def evaluate_teams(self, teams: list[TeamData]) -> PolicyEvaluation:
        violations = [
            violation for team in teams for violation in self._sole_member(team)
        ]
        number_of_disclosed = sum(
            1 for team in teams for member in team.members if member.gender != 0
        )
        score = (
            1
            if number_of_disclosed == 0 and len(violations) == 0
            else 1 - (len(violations) / number_of_disclosed)
        )
        return PolicyEvaluation(score, violations)

    @override
    def _evaluate_team(self, team: TeamData) -> PolicyEvaluation:
        return super()._evaluate_team(team)
