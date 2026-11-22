from django.urls import reverse

from allocations.models import User
from allocations.services.allocation_data import StudentData, TeamData

PASSWORD = "Allocation123"


def create_user(
    username="johndoe", first_name="John", last_name="Doe", is_superuser=False
):
    """Create a user with the given details and the password PASSWORD."""
    return User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=f"{username}@example.org",
        password=PASSWORD,
        is_superuser=is_superuser,
    )


def create_superuser():
    """Create the superuser Jane Doe, as in the seed command."""
    return create_user("janedoe", "Jane", "Doe", is_superuser=True)


def logged_in_user_id(client):
    """Return the id of the user logged in on a test client, or None."""
    user_id = client.session.get("_auth_user_id")
    if user_id is None:
        return None
    return int(user_id)


def log_in_url_for(url):
    """Return the log in URL that @login_required redirects to from url."""
    return f"{reverse('log_in')}?next={url}"


def messages_in(response):
    """Return the texts of the messages shown in a response."""
    return [str(message) for message in response.context["messages"]]


def make_student(
    email: str = "student@example.org",
    first_name: str = "Test",
    last_name: str = "Student",
    gender: int = 0,
    ethnicity: int = 0,
    c_score: int | None = 70,
) -> StudentData:
    """Create a StudentData instance with defaults for unit tests."""
    return StudentData(
        first_name=first_name,
        last_name=last_name,
        email=email,
        gender=gender,
        ethnicity=ethnicity,
        c_score=c_score,
    )


def make_team(name: str = "Team 1", *c_scores: int | None) -> TeamData:
    """Create a TeamData populated with students having the given c-scores."""
    members = [
        make_student(
            email=f"{name.lower().replace(' ', '')}_s{i}@example.org", c_score=score
        )
        for i, score in enumerate(c_scores, start=1)
    ]
    return TeamData(name=name, members=members)
