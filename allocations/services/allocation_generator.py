import random
import time
from dataclasses import dataclass, field
from enum import Enum

from allocations.services.allocation_data import StudentData, TeamData
from allocations.services.policies import AllocationPolicy, PolicyEvaluation
from allocations.services.team_size_policy import TeamSizePolicy


def plan_team_sizes(number_of_students: int, min_size: int, max_size: int) -> list[int] | None:
  
    #Plan the sizes of teams for a given number of students.

    n = number_of_students

    for k in range(1, n + 1):

        # Check whether k is valid
        if not (k * min_size <= n <= k * max_size):
            continue

        base = n // k
        remainder = n % k

        teams = []
        for i in range(k):
            size = base + (1 if i < remainder else 0)
            teams.append(size)

       
        return teams  # Returns the first valid arrangement

                       
    return None # No valid arrangement exists

    

    raise NotImplementedError


def make_initial_teams(students: list[StudentData], sizes: list[int],
                       rng: random.Random) -> list[TeamData]: #Shuffle the students and split them into teams of the given sizes.
    raise NotImplementedError


# Step 3: AllocationStatus and AllocationResult go here

# Step 4: evaluate(teams, policies)

# Step 5: is_better(a, b)

# Step 6: generate_allocation(students, policies, time_limit, seed)