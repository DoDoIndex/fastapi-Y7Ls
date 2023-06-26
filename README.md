## Features

- FastAPI
- Python 3

## Prerequisite

- Install Python
- Install Poetry [Mac](https://formulae.brew.sh/formula/poetry) | [Linux](https://python-poetry.org/docs/) globally
- Clone this repo locally
- `poetry install` to install all dependencies inside `pyproject.toml`
- `poetry shell` to get into virtual env, isolate from global env

## To Run

- `uvicorn src.stl_builder.main:app --reload`

## Add Dependency

- `poetry add firebase-admin`
- `poetry export --format=requirements.txt --without-hashes > requirements.txt`

## Before Push run the following

- `ruff .` linter
- `black .` formater
