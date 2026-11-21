from policies import *
from collections import Counter

class GenderRepresentationPolicy(AllocationPolicy):
    def __init__(self, priority: int, hard_condition: bool = False):    
        super().__init__(priority, hard_condition)
        self.GENDER_IDENTITES = {1: "woman", 2: "man", 3: "other/non-binary"}

    def _sole_member(self, team: TeamData):
        gender_counts = Counter(member.gender for member in team.members if member.gender != 0)
        return [PolicyViolation(f"{team.name} has only one {self.GENDER_IDENTITES.get(gender)} student.") for gender, count in gender_counts.items() if count == 1]

    def evaluate_teams(self, teams: list[TeamData]) -> PolicyEvaluation:
        violations = [violation for team in teams for violation in self._sole_member(team)]
        number_of_disclosed = sum(1 for team in teams for member in team.members if member.gender != 0)
        score = 1 if number_of_disclosed == 0 and len(violations) == 0 else 1 - (len(violations) / number_of_disclosed)
        return PolicyEvaluation(score, number_of_disclosed)
    
    def evaluate_team(self, team: TeamData) -> PolicyEvaluation:
        return PolicyEvaluation()