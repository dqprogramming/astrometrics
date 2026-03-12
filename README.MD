# Astrometrics

The journal catalogue and search platform for the [Open Journals Collective](https://www.openjournalscollective.org/) (OJC).

OJC is a UK-based Community Interest Company (CIC #16431892) of libraries, scholarly societies, and non-profit publishers working to shift academic publishing from a profit-driven model to a community-governed one — keeping high-quality research freely accessible without author fees or embargoes.

Astrometrics provides a searchable catalogue of OJC member journals with PostgreSQL full-text search, filtering by publisher, subject, language, and indexing status (DOAJ, Scopus), and an admin interface for journal data management and CSV import/export.

## Requirements

- Python 3.12+
- PostgreSQL 16+ (with `pg_trgm` extension)
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
# Clone the repository
git clone git@github.com:dqprogramming/astrometrics.git
cd astrometrics

# Install dependencies
uv sync

# Create the PostgreSQL database
createdb astrometrics

# Run migrations
uv run python manage.py migrate

# (Optional) Load sample data
uv run python manage.py import_journals sample_data.csv

# Create a superuser for the admin interface
uv run python manage.py createsuperuser
```

## Running

```bash
uv run python manage.py runserver
```

The site will be available at `http://localhost:8000/` and the admin interface at `http://localhost:8000/admin/`.

## Testing

```bash
uv run python manage.py test
```

## Linting

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Check formatting
uv run ruff format --check .

# Apply formatting
uv run ruff format .
```

Pre-commit hooks run ruff and the test suite automatically on each commit. To install them:

```bash
uv run pre-commit install
```
