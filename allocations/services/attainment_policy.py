from typing import override

from allocations.services.allocation_data import TeamData
from allocations.services.policies import (
    AllocationPolicy,
    PolicyEvaluation,
    PolicyViolation,
)


class AttainmentPolicy(AllocationPolicy):
    def __init__(self, priority: int, max_spread: int, hard_condition: bool = False):
        if not 0 <= max_spread <= 100:
            raise ValueError("max_spread must be between 0 and 100.")
        super().__init__("Attainment policy", priority, hard_condition)
        self.max_spread: int = max_spread

    @override
    def evaluate_team(self, team: TeamData) -> PolicyEvaluation:
        scores = [
            student.c_score for student in team.members if student.c_score is not None
        ]

        # Teams with 1 or no members have zero attainment spread by default
        if len(scores) < 2:
            return PolicyEvaluation(1.0)

        lowest_score = min(scores)
        highest_score = max(scores)
        score_spread = highest_score - lowest_score

        violations: list[PolicyViolation] = []

        if score_spread > self.max_spread:
            violations.append(
                PolicyViolation(
                    f"{team.name} has a c-score spread of {score_spread} "
                    + f", exceeding the maximum of {self.max_spread}."
                )
            )
        return PolicyEvaluation(score=(1 - (score_spread / 100)), violations=violations)

    @override
    def evaluate_teams(self, teams: list[TeamData]) -> PolicyEvaluation:
        if not teams:
            return PolicyEvaluation(1)

        team_evaluations = [self.evaluate_team(team) for team in teams]
        average_score = sum(evaluation.score for evaluation in team_evaluations) / len(
            team_evaluations
        )
        violations = [
            violation
            for evaluation in team_evaluations
            for violation in evaluation.violations
        ]

        return PolicyEvaluation(score=average_score, violations=violations)
