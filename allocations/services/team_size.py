from policies import *

class TeamSizePolicy(AllocationPolicy):
    def __init__(self, min_size: int, max_size: int, priority: int, hard_condition: bool = False):
        if min_size < 1 or max_size < min_size:
            raise ValueError("min_size must be between 1 and max_size.")
        
        super().__init__(priority, hard_condition)
        self.min_size = min_size
        self.max_size = max_size

    def _violation(self, team: TeamData) -> PolicyViolation | None:
        number_of_members = len(team.members)
        if number_of_members < self.min_size or number_of_members > self.max_size:
            return PolicyViolation(f"{team.name} has {number_of_members} members. Member size should be {self.min_size} to {self.max_size}.")
        return None

    def evaluate_teams(self, teams: list[TeamData]) -> PolicyEvaluation:
        violations = [violation for team in teams if (violation := self._violation(team))]
        score = 1 if not teams else 1 - (len(violations) / len(teams))
        return PolicyEvaluation(score, violations)
    
    def evaluate_team(self, team: TeamData) -> PolicyEvaluation:
        return PolicyEvaluation()