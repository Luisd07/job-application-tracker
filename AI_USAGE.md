# AI Usage

## Tools Used

- **Claude Code (Sonnet 5.5, `claude-sonnet-5-5`)** by Anthropic: used to generate the project boilerplate (framework setup and file structure only).

## Key Prompts

- Asked for only the boilerplate of a Flask + MySQL Job Application Tracker: app skeleton with one route per page, a database connection helper, Jinja2 templates extending a Bootstrap base layout, an empty stylesheet, a minimal `schema.sql`, `.env.example`, and `.gitignore`. Explicitly asked for TODO stubs instead of CRUD, SQL, dashboard stats, or the job-matching algorithm, and for `requirements.txt` to be exported with uv rather than hand-written.

## What Worked Well

- `app.py` with a Flask app, `.env` loading, and six routes that just render templates.
- `database.py` with a single `get_connection()` helper using environment variables.
- `base.html` with a Bootstrap 5 navbar, flash message area, and content block; the other six templates extend it with a heading and a TODO.
- Empty `style.css`, minimal `schema.sql`, `.env.example`, and `.gitignore`.

## What I Modified

_TODO: fill in after I make my changes._

## Lessons Learned

Using AI for generic boilerplate code greatly increases effectiveness and speed. However that boilerplate may not be fully tailored for your use case, so checking it over is greatly recommended.
