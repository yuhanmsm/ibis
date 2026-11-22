from dataclasses import dataclass, field


@dataclass(frozen=True)
class StudentData:
    """A representation of a student containing its identifying data

    Note that gender, ethnicity and c_score default to 0 as 'Files without
    first_name, last_name, and email are invalid. Other attributes may be excluded'.

    :param c_score: The overall score of all assessments the student has completed,
    None indicates the student has no associated score
    :param gender: 1: Woman, 2: Man, 3: Other/Non-binary, or 0 (not provided).
    :param ethnicity: 1: Asian, or Asian British, 2: Black, Black British,
    Caribbean, or African, 3 : Mixed, or multiple ethic groups, 4: White,
    5: Other ethnic group (e.g. Arab), or 0 (not provided).
    """

    first_name: str
    last_name: str
    email: str
    gender: int = 0
    ethnicity: int = 0
    c_score: int | None = None


@dataclass
class TeamData:
    """A representation of a team made up of students"""

    name: str
    members: list[StudentData] = field(default_factory=list)
