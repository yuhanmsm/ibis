from django.test import SimpleTestCase

from allocations.services.allocation_generator import plan_team_sizes


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