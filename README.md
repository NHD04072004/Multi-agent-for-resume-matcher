# Multi-agent for Resume Matcher

## Setup

- Python 3.12+

- Create virtual environment

```commandline
# pip
python -m venv nameEnv
source nameEnv/bin/activate  # Linux/MaxOS
nameEnv\Scripts\activate  # Windows

# Conda
conda create -n nameEnv python=x.x anaconda
conda activate nameEnv
```

- Install library/framework

```commandline
pip install -r requirements.txt
```

## Run

```commandline
fastapi dev main.py
```

## Error
- Stored none-unicode (Postgresql)