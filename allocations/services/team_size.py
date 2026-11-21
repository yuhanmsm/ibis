from policies import *

class TeamSizePolicy(AllocationPolicy):
    def __init__(self, name: str, priority: int, hard_condition: bool = False):
        super().__init__(name, priority, hard_condition)

    def evaluate_teams(self, teams: list[TeamData]) -> PolicyEvaluation:
        return PolicyEvaluation()
    
    def evaluate_team(self, team: TeamData) -> PolicyEvaluation:
        return PolicyEvaluation()