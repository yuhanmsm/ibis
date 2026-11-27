import random

from django.test import SimpleTestCase

from allocations.services.allocation_generator import make_initial_teams, plan_team_sizes
from allocations.tests.helpers import make_student

class PlanTeamSizesTestCase(SimpleTestCase):
    """Tests of plan_team_sizes()."""

    def test_mixed_sizes_when_not_exactly_divisible(self):
        """23 students in teams of 4-5 should give three 5s and two 4s."""
        sizes = plan_team_sizes(23, 4, 5)
        self.assertEqual(sizes, [5, 5, 5, 4, 4])

    def test_20_students(self):
        """20 students in teams of 4-5 should give the fewest teams: four teams of 5."""
        sizes = plan_team_sizes(20, 4, 5)
        self.assertEqual(sizes, [5, 5, 5, 5])

    def test_7_students_impossible(self):
        """7 students cannot form teams of 4-5."""
        sizes = plan_team_sizes(7, 4, 5)
        self.assertIsNone(sizes)


    def test_12_students(self):
        """12 students should give three teams of 4."""
        sizes = plan_team_sizes(12, 4, 5)
        self.assertEqual(sizes, [4, 4, 4])


    def test_300_students(self):
       """300 students should give sixty teams of 5."""
       sizes = plan_team_sizes(300, 4, 5)
       self.assertEqual(sizes, [5] * 60)

class MakeInitialTeamsTestCase(SimpleTestCase):
    """Tests of make_initial_teams()."""

    def setUp(self):
        """Runs before every test: 23 students and the sizes from plan_team_sizes."""
        self.students = [make_student(email=f"s{i}@example.org") for i in range(23)]
        self.sizes = [5, 5, 5, 4, 4]

    def emails_in(self, teams):
        """Helper: a list of every member's email across all teams."""
        return [student.email for team in teams for student in team.members]

    def test_team_sizes_match_planned_sizes(self):
        """Each team should have exactly the planned number of members."""
        teams = make_initial_teams(self.students, self.sizes, random.Random(1))
        self.assertEqual([len(team.members) for team in teams], self.sizes)

    def test_every_student_allocated_exactly_once(self):
        """All 23 students appear, and nobody appears twice."""
        teams = make_initial_teams(self.students, self.sizes, random.Random(1))
        emails = self.emails_in(teams)
        self.assertEqual(len(emails), 23)
        self.assertEqual(len(set(emails)), 23)
        self.assertEqual(set(emails), {s.email for s in self.students})

    def test_original_student_list_is_not_changed(self):
        """Shuffling must happen on a copy, not the caller's list."""
        original = list(self.students)
        make_initial_teams(self.students, self.sizes, random.Random(1))
        self.assertEqual(self.students, original)

    def test_same_seed_gives_same_teams(self):
        """The same seed should give identical teams, so runs are repeatable."""
        teams_a = make_initial_teams(self.students, self.sizes, random.Random(42))
        teams_b = make_initial_teams(self.students, self.sizes, random.Random(42))
        self.assertEqual(self.emails_in(teams_a), self.emails_in(teams_b))

    def test_teams_are_named_in_order(self):
        """Teams should be called Team 1, Team 2, ..."""
        teams = make_initial_teams(self.students, self.sizes, random.Random(1))
        self.assertEqual([team.name for team in teams],
                         ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5"])