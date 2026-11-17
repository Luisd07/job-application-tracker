# Job Application Tracker

A Flask + MySQL web app for tracking a job search. It stores companies, the jobs they posted, the applications I sent and the contacts I talked to. It can also rank jobs by how well my skills match what they require.

Pages:

- Dashboard with record counts, applications by status, and the five most recent applications
- Companies, Jobs, Applications and Contacts, each with a list page, a detail page, and add/edit/delete
- Job Match, where you enter your skills and get every job ranked by the percentage of its required skills you have, along with the ones you're missing

## Requirements

- Python 3.14 or newer (`requires-python = ">=3.14"` in `pyproject.toml`)
- MySQL 8.0 or newer (the schema uses `JSON` columns and `CHECK` constraints)

## Setup

1. Clone the repo and go into it:

   ```bash
   git clone <repo-url>
   cd job-application-tracker
   ```

2. Create a virtual environment and install the dependencies:

   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

   If you use [uv](https://docs.astral.sh/uv/), `uv sync` does the same thing (it creates `.venv` and installs from `uv.lock`).

3. Copy `.env.example` to `.env` and fill in your MySQL user and password:

   ```bash
   cp .env.example .env
   ```

   ```
   DB_HOST=localhost
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   DB_NAME=job_tracker
   SECRET_KEY=change-me
   ```

   Keep `DB_NAME=job_tracker`, since that is the database `schema.sql` creates. `SECRET_KEY` can be any random string; Flask needs it for flash messages.

4. Create the database and tables, then load the sample data:

   ```bash
   mysql -u your_mysql_user -p < schema.sql
   mysql -u your_mysql_user -p job_tracker < seed.sql
   ```

   **Warning:** `schema.sql` drops and recreates the `companies`, `jobs`, `applications` and `contacts` tables, so running it again deletes everything in `job_tracker`.

   `seed.sql` needs the tables from `schema.sql`, so run it second. It adds 6 companies, 18 jobs, 6 applications and 6 contacts.

5. Start the app:

   ```bash
   python app.py
   ```

   Then open http://127.0.0.1:5000 in a browser.

## Project structure

```
job-application-tracker/
├── app.py              # Flask routes: dashboard, CRUD for each table, job match
├── database.py         # MySQL connection and query helpers
├── schema.sql          # Creates the job_tracker database and its 4 tables
├── seed.sql            # Sample data (run after schema.sql)
├── requirements.txt    # pip dependencies
├── pyproject.toml      # Project metadata and dependencies for uv
├── .env.example        # Template for the .env settings file
├── AI_USAGE.md         # How I used AI on this project
├── static/
│   └── style.css
└── templates/
    ├── base.html                # Layout and navbar shared by every page
    ├── dashboard.html
    ├── job_match.html
    ├── companies.html           # List pages
    ├── jobs.html
    ├── applications.html
    ├── contacts.html
    ├── company_detail.html      # Detail pages
    ├── job_detail.html
    ├── application_detail.html
    ├── contact_detail.html
    ├── company_form.html        # Add/edit forms
    ├── job_form.html
    ├── application_form.html
    └── contact_form.html
```
