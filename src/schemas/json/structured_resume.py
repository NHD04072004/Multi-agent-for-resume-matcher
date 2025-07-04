SCHEMA = {
    "UUID": "string",
    "Personal Data": {
        "fullName": "string",
        "email": "string",
        "phone": "string",
        "linkedin": "string",
        "portfolio": "string",
        "location": {"city": "string", "country": "string"},
    },
    "Experiences": [
        {
            "jobTitle": "string",
            "company": "string",
            "location": "string",
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD or Present",
            "description": ["string", "..."],
            "technologiesUsed": ["string", "..."],
        }
    ],
    "Projects": [
        {
            "projectName": "string",
            "description": "string",
            "technologiesUsed": ["string", "..."],
            "link": "string",
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD",
        }
    ],
    "Skills": [{"category": "string", "skillName": "string"}],
    "Research Work": [
        {
            "title": "string",
            "publication": "string",
            "date": "YYYY-MM-DD",
            "link": "string",
            "description": "string",
        }
    ],
    "Achievements": ["string", "..."],
    "Education": [
        {
            "institution": "string",
            "degree": "string",
            "fieldOfStudy": "string",
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD",
            "grade": "string",
            "description": "string",
        }
    ],
    "Extracted Keywords": ["string", "..."],
}
