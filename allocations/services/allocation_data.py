from dataclasses import dataclass, field


@dataclass(frozen=True)
class StudentData:
    """A representation of a student containing its identifying data"""

    first_name: str
    last_name: str
    email: str


@dataclass
class TeamData:
    """A representation of a team made up of students"""

    name: str
    members: list[StudentData] = field(default_factory=list)
