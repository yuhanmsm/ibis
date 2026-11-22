from django.test import SimpleTestCase

from allocations.services.attainment_policy import AttainmentPolicy
from allocations.tests.helpers import make_team


class AttainmentPolicyTestCase(SimpleTestCase):
    """Tests of the AttainmentPolicy class."""

    def test_out_of_bounds_max_spread_raises_value_error(self):
        """Negative spread or spread larger than 100 (the maximum c_score) should be rejected."""
        with self.assertRaises(ValueError):
            _ = AttainmentPolicy(priority=50, max_spread=-1)
            _ = AttainmentPolicy(priority=50, max_spread=101)

    def test_perfect_score_policy_evaluation(self):
        """0 spread should raise 0 policy violations."""
        policy = AttainmentPolicy(priority=50, max_spread=15)
        team = make_team("Team 1", 75, 75, 75, 75)

        result = policy.evaluate_teams([team])

        self.assertEqual(result.score, 1.0)
        self.assertTrue(result.satisfied)
        self.assertEqual(result.violations, [])

    def test_maximum_spread_policy_evaluation(self):
        """Maximum spread should raise a policy violation."""
        policy = AttainmentPolicy(priority=50, max_spread=15)
        team = make_team("Team 1", 0, 100)

        result = policy.evaluate_teams([team])

        self.assertEqual(result.score, 0.0)
        self.assertFalse(result.satisfied)
        self.assertEqual(len(result.violations), 1)

    def test_spread_within_max_spread_policy_evaluation(self):
        """If there is a spread but it is within the max_spread,
        it should be accepted without violations.
        """
        policy = AttainmentPolicy(priority=50, max_spread=15)
        team = make_team("Team 1", 60, 75)

        result = policy.evaluate_teams([team])

        self.assertAlmostEqual(result.score, 0.85)
        self.assertTrue(result.satisfied)

    def test_too_large_spread_policy_evaluation(self):
        """If the spread is larger than the allowed spread a violation should be raised."""
        policy = AttainmentPolicy(priority=50, max_spread=15)
        team = make_team("Team 1", 60, 76)

        result = policy.evaluate_teams([team])

        self.assertFalse(result.satisfied)
        self.assertEqual(len(result.violations), 1)
        self.assertIn("Team 1", result.violations[0].message)
        self.assertIn("16", result.violations[0].message)

    def test_missing_c_scores_policy_evaluation(self):
        """None type scores should be ignored from spread calculations."""
        policy = AttainmentPolicy(priority=50, max_spread=10)
        team = make_team("Team 1", 80, None, 85, None)

        result = policy.evaluate_teams([team])

        self.assertAlmostEqual(result.score, 0.95)
        self.assertTrue(result.satisfied)

    def test_teams_with_one_member_policy_evaluation(self):
        """Teams with only 1 student should automatically get a max score."""
        policy = AttainmentPolicy(priority=50, max_spread=10)
        team = make_team("Team 1", 80, None, None)

        result = policy.evaluate_teams([team])

        self.assertEqual(result.score, 1.0)
        self.assertTrue(result.satisfied)

    def test_empty_team_policy_evaluation(self):
        """Empty teams should automatically get a max score."""
        policy = AttainmentPolicy(priority=50, max_spread=10)

        result = policy.evaluate_teams([])

        self.assertEqual(result.score, 1.0)
        self.assertTrue(result.satisfied)

    def test_multiple_team_policy_evaluation(self):
        """Test that multiple teams have the overall score be an average."""
        policy = AttainmentPolicy(priority=50, max_spread=15)
        team_a = make_team("Team A", 80, 80)
        team_b = make_team("Team B", 50, 70)

        result = policy.evaluate_teams([team_a, team_b])

        self.assertAlmostEqual(result.score, 0.9)
        self.assertFalse(result.satisfied)
        self.assertEqual(len(result.violations), 1)
        self.assertIn("Team B", result.violations[0].message)
