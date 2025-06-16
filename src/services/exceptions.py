from typing import Optional


class ResumeNotFoundError(Exception):
    """
    Exception raised when a resume is not found in the database.
    """

    def __init__(self, resume_id: Optional[str] = None, message: Optional[str] = None):
        if resume_id and not message:
            message = f"Resume with ID {resume_id} not found."
        elif not message:
            message = "Resume not found."
        super().__init__(message)
        self.resume_id = resume_id


class ResumeParsingError(Exception):
    """
    Exception raised when a resume processing and storing in the database failed.
    """

    def __init__(self, resume_id: Optional[str] = None, message: Optional[str] = None):
        if resume_id and not message:
            message = f"Parsing of resume with ID {resume_id} failed."
        elif not message:
            message = "Parsed resume not found."
        super().__init__(message)
        self.resume_id = resume_id