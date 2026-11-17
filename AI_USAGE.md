# AI Usage

## Tools Used

- **Claude Code (Sonnet 5.5)**: set up the project boilerplate.
- **Claude Code (Opus 5.5)**: everything after the boilerplate (reviews, bug fixes, routes, sample data, templates).

## What I Used AI For

1. **Boilerplate.** I asked for just the project skeleton: a Flask app with one route per page, a database connection helper, Bootstrap templates, and an empty `schema.sql`. I told it to leave TODOs instead of writing any real features.

2. **Planning.** I asked it to walk me through the project spec so I knew what to work on first.

3. **Reviewing my schema.** I wrote `schema.sql` from the spec and asked it to review it ("review schema i wrote"). It found missing semicolons, foreign keys written in SQL Server syntax instead of MySQL, and that I had used `'Interviewing'` where the spec says `'Interview'`. I asked it to fix those.

4. **The rest of the CRUD routes.** I asked it to "implement the crud routes for the rest of app.py" following the same structure as my companies routes. It wrote the jobs, applications, and contacts routes, and pointed out that my `company_edit` and `company_delete` routes used `WHERE id = %s` when the column is `company_id`.

5. **Matching the routes to the schema.** I asked it to "make sure the crud routes match my sql schema." It added checks so text that is too long for a column, or a salary too big for an INT, shows an error message instead of crashing.

6. **Templates.** I wrote `companies.html` and asked it to format it. That turned up four bugs (a duplicated `{% else %}`/`{% endfor %}` block, a stray quote in a class name, a typo in `company_name`, and a missing table header). Since the other list pages are basically the same, I had it make `jobs.html`, `applications.html`, and `contacts.html` from my `companies.html`.

7. **Form templates.** I wrote `company_form.html` and asked it to copy my style for `contact_form.html`, `job_form.html`, and `application_form.html`. These needed a few things my form didn't have: dropdowns for picking a company or job, dropdowns for job type and status, date and number fields, and a checkbox for the cover letter. It checked that the edit pages load with the saved values and that bad input shows an error without losing what was typed.

8. **Dashboard and code review.** I added the dashboard queries from its suggestion to `app.py`, but the indentation broke and the app wouldn't start, so I asked it to fix that. It then walked me through the dashboard template (count cards, applications by status, recent applications), along with matching status colors on the applications page. After that I asked it to review `applications.html`, `dashboard.html`, and `app.py`. It didn't find anything broken, but it pointed out that lists with ties (like two statuses with the same count) don't have a fixed order, that duplicate skills could be saved for a job, that deleting a record that's already gone still says it was deleted, and that the status colors are defined in two templates.

9. **Job Match.** The project spec asks us to use GenAI to help write the job-matching algorithm, so I wrote a prompt asking it to "list every job ranked by the percentage of that job's required skills I have, along with the skills I'm missing." It wrote a `match_jobs()` function in `app.py` that compares my skills to each job's skills ignoring case, works out the match percentage, and sorts the jobs best match first, with jobs that have no skills listed at the end. It also filled in `job_match.html` with a skills form and a results table showing each job's match, matched skills, and missing skills. It tested the function with the example from the spec and checked the page against my database.

## What Worked Well

- Reviews caught bugs I didn't see, like the `WHERE id` mistake and the typo that left a column blank.
- Writing one table myself and having AI copy the pattern kept the code consistent with how I wrote it.
- It tested the pages against my actual database to check each column showed data.

## What I Changed

- I kept my schema the way the project spec describes it instead of switching to the older assignment tables.
- I removed the default `SECRET_KEY` fallback in `app.py`, so the key has to come from `.env`.
- I ran a formatter on `app.py`.

## Lessons Learned

Using AI for generic boilerplate greatly speeds things up, but that boilerplate isn't fully tailored to your project, so it's worth checking it over. Writing one piece myself first and asking AI to follow it gave much better results than asking it to write everything from scratch.
