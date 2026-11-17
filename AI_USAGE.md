# AI Usage

## Tools Used

- **Claude Code (Sonnet 5.5, `claude-sonnet-5-5`)** by Anthropic: used to generate the project boilerplate (framework setup and file structure only).
- **Claude Code (Opus 5.5, `claude-opus-5-5`)** by Anthropic: used to review my schema and companies routes, fix the errors it found, and write the CRUD routes for jobs, applications, and contacts.

## Key Prompts

- Asked for only the boilerplate of a Flask + MySQL Job Application Tracker: app skeleton with one route per page, a database connection helper, Jinja2 templates extending a Bootstrap base layout, an empty stylesheet, a minimal `schema.sql`, `.env.example`, and `.gitignore`. Explicitly asked for TODO stubs instead of CRUD, SQL, dashboard stats, or the job-matching algorithm, and for `requirements.txt` to be exported with uv rather than hand-written.
- "Implement the CRUD routes for the rest of app.py. Follow similar structure to the previously written companies CRUD routes." I wrote the companies routes myself first so the AI had a pattern to copy.

## What Worked Well

- `app.py` with a Flask app, `.env` loading, and six routes that just render templates.
- `database.py` with a single `get_connection()` helper using environment variables.
- `base.html` with a Bootstrap 5 navbar, flash message area, and content block; the other six templates extend it with a heading and a TODO.
- Empty `style.css`, minimal `schema.sql`, `.env.example`, and `.gitignore`.
- CRUD routes for jobs, applications, and contacts (list/add/edit/delete) that follow the same structure as my companies routes:
  - List pages use JOINs so they show company and job names instead of IDs.
  - Server-side validation: required fields, ENUM values for job type and status, valid dates, whole-number salaries with min ≤ max, and checking that the selected company or job exists.
  - The JSON columns are converted between form text and JSON (`requirements` is typed as "Python, SQL, Flask" and stored as an array; the interview notes are stored as a key inside `interview_data`).
- It caught a bug in my own `company_edit` and `company_delete` routes: they used `WHERE id = %s`, but the column is `company_id`.

## What I Modified

_TODO: fill in after I make my changes._

## Lessons Learned

Using AI for generic boilerplate code greatly increases effectiveness and speed. However that boilerplate may not be fully tailored for your use case, so checking it over is greatly recommended.
