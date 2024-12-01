from datetime import datetime

class Election:
    DEPARTMENT_CHOICES = [
        ("CS", "Computer Science"),
        ("IT", "Information Technology"),
        ("CE", "Civil Engineering"),
        ("EE", "Electrical Engineering"),
        ("ME", "Mechanical Engineering"),
        ("BS", "Business Studies"),
        ("HRM", "Hospitality and Restaurant Management"),
        ("AB", "Accountancy"),
        ("ED", "Education"),
        ("Nursing", "Nursing"),
        ("Architecture", "Architecture"),
        ("Marine", "Marine Engineering"),
        ("Chemistry", "Chemistry"),
        ("Biology", "Biology"),
        ("Physics", "Physics"),
        ("Math", "Mathematics"),
        ("Communication", "Communication Arts"),
        ("Arts", "Fine Arts"),
        ("Music", "Music"),
        ("Law", "Law"),
        ("ALL", "ALL"),
    ]

    def __init__(self, title, description, departments, open_date, close_date, image=None):
        self.title = title
        self.image = image
        self.description = description
        self.departments = departments  # Expected to be a list of department codes
        self.open_date = open_date
        self.close_date = close_date

    def __str__(self):
        return f"{self.title} - Departments: {', '.join(self.departments or [])}"

    def clean(self):
        if not self.departments:
            raise ValueError("At least one department must be selected.")


class Position:
    def __init__(self, title, election, max_selection):
        self.title = title
        self.election = election  # Link to an Election object
        self.max_selection = max_selection

    def __str__(self):
        return self.title


class Student:
    DEPARTMENT_CHOICES = Election.DEPARTMENT_CHOICES

    def __init__(self, student_id, name, department):
        self.student_id = student_id
        self.name = name
        self.department = department  # Expected to match one of the department codes

    def __str__(self):
        return f"{self.name} ({self.department})"


class Candidate:
    YEAR_CHOICES = [
        ("1st Year", "1st Year"),
        ("2nd Year", "2nd Year"),
        ("3rd Year", "3rd Year"),
        ("4th Year", "4th Year"),
    ]

    def __init__(self, name, partylist, year, course, election, position, vote_count=0, image=None, platforms=None):
        self.name = name
        self.partylist = partylist
        self.year = year
        self.course = course
        self.election = election  # Link to an Election object
        self.position = position  # Link to a Position object
        self.vote_count = vote_count
        self.image = image
        self.platforms = platforms
        self.is_winner = False

    def __str__(self):
        return self.name


class VoteSlip:
    def __init__(self, student, election, candidates):
        self.student = student  # Link to a Student object
        self.election = election  # Link to an Election object
        self.candidates = candidates  # List of Candidate objects

    def __str__(self):
        return f"{self.student} ({self.election})"

    def clean(self, existing_vote_slips):
        """
        Ensure the student hasn't already submitted a vote slip for the same election.
        `existing_vote_slips` is a list of existing VoteSlip objects for validation.
        """
        if any(vote_slip.student == self.student and vote_slip.election == self.election for vote_slip in existing_vote_slips):
            raise ValueError("Each student can only submit one VoteSlip per election.")

    def save(self, existing_vote_slips):
        """
        Saves the vote slip and updates candidate vote counts.
        """
        self.clean(existing_vote_slips)  # Validate before saving

        # Update vote counts for each selected candidate
        for candidate in self.candidates:
            candidate.vote_count += 1
