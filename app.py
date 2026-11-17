"""Flask app for the Job Application Tracker.

Routes for the dashboard, CRUD pages for each table, and the job-match feature.
"""

import json
import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from database import execute, fetch_all, fetch_one

# Load settings from the .env file into environment variables.
load_dotenv()

app = Flask(__name__)

# Flask needs a secret key to use flash messages (they are stored in the session).
app.secret_key = os.getenv("SECRET_KEY")

# Allowed values for the ENUM columns in schema.sql.
JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]
STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]

# VARCHAR sizes from schema.sql. MySQL rejects longer values with an error.
MAX_LENGTHS = {
    "companies": {
        "company_name": 100,
        "industry": 50,
        "website": 200,
        "city": 50,
        "state": 50,
    },
    "jobs": {"job_title": 100, "job_url": 300},
    "applications": {"resume_version": 50},
    "contacts": {
        "contact_name": 100,
        "title": 100,
        "email": 100,
        "phone": 20,
        "linkedin_url": 200,
    },
}
MAX_INT = 2_147_483_647  # largest value a MySQL INT column can hold


def clean(value):
    """Clean a value that arrives as '' when empty. Store NULL"""
    value = (value or "").strip()
    return value or None


def to_int(value):
    """Convert a form value to an int, or None when empty. Raises ValueError if not a number."""
    value = clean(value)
    return int(value) if value is not None else None


def to_date(value):
    """Convert a YYYY-MM-DD form value to a date, or None when empty. Raises ValueError if invalid."""
    value = clean(value)
    return date.fromisoformat(value) if value is not None else None


def load_json(value):
    """Parse a JSON column (MySQL returns it as a string), or None when NULL."""
    return json.loads(value) if value else None


def lookup_id(value, sql):
    """Return the id as an int if a row exists for it (sql selects by id), else None."""
    try:
        record_id = to_int(value)
    except ValueError:
        return None
    if record_id is None or not fetch_one(sql, (record_id,)):
        return None
    return record_id


def length_errors(r, table):
    """Return an error for each form field longer than its VARCHAR column allows."""
    errors = []
    for field, limit in MAX_LENGTHS[table].items():
        value = clean(r.get(field))
        if value and len(value) > limit:
            label = field.replace("_", " ").capitalize()
            errors.append(f"{label} must be {limit} characters or fewer.")
    return errors


def flash_errors(errors):
    for error in errors:
        flash(error, "danger")


def company_choices():
    """Companies for the <select> dropdown on the job and contact forms."""
    return fetch_all(
        "SELECT company_id, company_name FROM companies ORDER BY company_name"
    )


def job_choices():
    """Jobs for the <select> dropdown on the application form."""
    return fetch_all(
        "SELECT j.job_id, j.job_title, c.company_name FROM jobs j "
        "JOIN companies c ON j.company_id = c.company_id "
        "ORDER BY c.company_name, j.job_title"
    )


@app.route("/")
def dashboard():
    counts = fetch_one(
        "SELECT (SELECT COUNT(*) FROM companies) AS companies, "
        "(SELECT COUNT(*) FROM jobs) AS jobs, "
        "(SELECT COUNT(*) FROM applications) AS applications, "
        "(SELECT COUNT(*) FROM contacts) AS contacts"
    )
    by_status = fetch_all(
        "SELECT status, COUNT(*) AS count FROM applications "
        "GROUP BY status ORDER BY count DESC"
    )
    recent = fetch_all(
        "SELECT a.application_date, a.status, j.job_title, c.company_name FROM applications a "
        "JOIN jobs j ON a.job_id = j.job_id JOIN companies c ON j.company_id = c.company_id "
        "ORDER BY a.application_date DESC LIMIT 5"
    )
    return render_template(
        "dashboard.html", counts=counts, by_status=by_status, recent=recent
    )


@app.route("/companies")
def companies():
    rows = fetch_all("SELECT * FROM companies ORDER BY company_name")
    return render_template("companies.html", companies=rows)


@app.route("/companies/add", methods=["GET", "POST"])
def company_add():
    if request.method == "POST":
        r = request.form
        errors = length_errors(r, "companies")
        if not clean(r.get("company_name")):
            errors.insert(0, "Company name is required.")
        if errors:
            flash_errors(errors)
            return render_template("company_form.html", company=r)
        execute(
            "INSERT INTO companies (company_name, industry, website, city, state, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                clean(r.get("company_name")),
                clean(r.get("industry")),
                clean(r.get("website")),
                clean(r.get("city")),
                clean(r.get("state")),
                clean(r.get("notes")),
            ),
        )
        flash("Company added successfully.", "success")
        return redirect(url_for("companies"))
    return render_template("company_form.html", company={})


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def company_edit(company_id):
    company = fetch_one("SELECT * FROM companies WHERE company_id = %s", (company_id,))
    if not company:
        flash("Company not found.", "danger")
        return redirect(url_for("companies"))
    if request.method == "POST":
        r = request.form
        errors = length_errors(r, "companies")
        if not clean(r.get("company_name")):
            errors.insert(0, "Company name is required.")
        if errors:
            flash_errors(errors)
            return render_template("company_form.html", company=r)
        execute(
            "UPDATE companies SET company_name=%s, industry=%s, website=%s, city=%s, "
            "state=%s, notes=%s WHERE company_id=%s",
            (
                clean(r.get("company_name")),
                clean(r.get("industry")),
                clean(r.get("website")),
                clean(r.get("city")),
                clean(r.get("state")),
                clean(r.get("notes")),
                company_id,
            ),
        )
        flash("Company updated successfully.", "success")
        return redirect(url_for("companies"))
    return render_template("company_form.html", company=company)


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def company_delete(company_id):
    execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
    flash("Company deleted successfully.", "success")
    return redirect(url_for("companies"))


def job_form_values(r):
    """Validate the job form. Returns (params, errors); params match the INSERT/UPDATE column order."""
    errors = length_errors(r, "jobs")
    company_id = lookup_id(
        r.get("company_id"), "SELECT company_id FROM companies WHERE company_id = %s"
    )
    if company_id is None:
        errors.append("Choose a valid company.")
    job_title = clean(r.get("job_title"))
    if not job_title:
        errors.append("Job title is required.")
    job_type = r.get("job_type")
    if job_type not in JOB_TYPES:
        errors.append("Choose a valid job type.")
    try:
        salary_min = to_int(r.get("salary_min"))
        salary_max = to_int(r.get("salary_max"))
    except ValueError:
        errors.append("Salaries must be whole numbers.")
        salary_min = salary_max = None
    if (salary_min is not None and salary_min < 0) or (
        salary_max is not None and salary_max < 0
    ):
        errors.append("Salaries cannot be negative.")
    if (salary_min is not None and salary_min > MAX_INT) or (
        salary_max is not None and salary_max > MAX_INT
    ):
        errors.append(f"Salaries cannot be more than {MAX_INT:,}.")
    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        errors.append("Minimum salary cannot be greater than maximum salary.")
    try:
        date_posted = to_date(r.get("date_posted"))
    except ValueError:
        errors.append("Date posted must be a valid date.")
        date_posted = None
    # Skills are typed as "Python, SQL, Flask" and stored as a JSON array.
    # Duplicates are dropped ignoring case, keeping the first spelling typed.
    skills = []
    seen = set()
    for s in (r.get("requirements") or "").split(","):
        s = s.strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            skills.append(s)
    params = (
        company_id,
        job_title,
        job_type,
        salary_min,
        salary_max,
        clean(r.get("job_url")),
        date_posted,
        json.dumps(skills),
    )
    return params, errors


@app.route("/jobs")
def jobs():
    rows = fetch_all(
        "SELECT j.*, c.company_name FROM jobs j "
        "JOIN companies c ON j.company_id = c.company_id "
        "ORDER BY j.date_posted DESC, j.job_title"
    )
    for row in rows:
        row["requirements"] = load_json(row["requirements"]) or []
    return render_template("jobs.html", jobs=rows)


@app.route("/jobs/add", methods=["GET", "POST"])
def job_add():
    if request.method == "POST":
        r = request.form
        params, errors = job_form_values(r)
        if errors:
            flash_errors(errors)
            return render_template("job_form.html", job=r, companies=company_choices())
        execute(
            "INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, "
            "job_url, date_posted, requirements) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            params,
        )
        flash("Job added successfully.", "success")
        return redirect(url_for("jobs"))
    return render_template("job_form.html", job={}, companies=company_choices())


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def job_edit(job_id):
    job = fetch_one("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("jobs"))
    if request.method == "POST":
        r = request.form
        params, errors = job_form_values(r)
        if errors:
            flash_errors(errors)
            return render_template("job_form.html", job=r, companies=company_choices())
        execute(
            "UPDATE jobs SET company_id=%s, job_title=%s, job_type=%s, salary_min=%s, "
            "salary_max=%s, job_url=%s, date_posted=%s, requirements=%s WHERE job_id=%s",
            params + (job_id,),
        )
        flash("Job updated successfully.", "success")
        return redirect(url_for("jobs"))
    # Show the stored JSON array as "Python, SQL, Flask" in the text box.
    job["requirements"] = ", ".join(load_json(job["requirements"]) or [])
    return render_template("job_form.html", job=job, companies=company_choices())


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def job_delete(job_id):
    execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
    flash("Job deleted successfully.", "success")
    return redirect(url_for("jobs"))


def application_form_values(r, existing_interview_data=None):
    """Validate the application form. Returns (params, errors).

    The form edits only the "notes" key of interview_data; any other keys
    already stored in the JSON are kept.
    """
    errors = length_errors(r, "applications")
    job_id = lookup_id(r.get("job_id"), "SELECT job_id FROM jobs WHERE job_id = %s")
    if job_id is None:
        errors.append("Choose a valid job.")
    try:
        application_date = to_date(r.get("application_date"))
        if application_date is None:
            errors.append("Application date is required.")
    except ValueError:
        errors.append("Application date must be a valid date.")
        application_date = None
    status = r.get("status")
    if status not in STATUSES:
        errors.append("Choose a valid status.")
    # An unchecked checkbox is not sent with the form at all.
    cover_letter_sent = "cover_letter_sent" in r
    interview_data = dict(existing_interview_data or {})
    notes = clean(r.get("interview_notes"))
    if notes:
        interview_data["notes"] = notes
    else:
        interview_data.pop("notes", None)
    params = (
        job_id,
        application_date,
        status,
        clean(r.get("resume_version")),
        cover_letter_sent,
        json.dumps(interview_data) if interview_data else None,
    )
    return params, errors


@app.route("/applications")
def applications():
    rows = fetch_all(
        "SELECT a.*, j.job_title, c.company_name FROM applications a "
        "JOIN jobs j ON a.job_id = j.job_id "
        "JOIN companies c ON j.company_id = c.company_id "
        "ORDER BY a.application_date DESC"
    )
    for row in rows:
        row["interview_data"] = load_json(row["interview_data"]) or {}
    return render_template("applications.html", applications=rows)


@app.route("/applications/add", methods=["GET", "POST"])
def application_add():
    if request.method == "POST":
        r = request.form
        params, errors = application_form_values(r)
        if errors:
            flash_errors(errors)
            return render_template(
                "application_form.html",
                application=r,
                jobs=job_choices(),
                statuses=STATUSES,
            )
        execute(
            "INSERT INTO applications (job_id, application_date, status, resume_version, "
            "cover_letter_sent, interview_data) VALUES (%s, %s, %s, %s, %s, %s)",
            params,
        )
        flash("Application added successfully.", "success")
        return redirect(url_for("applications"))
    return render_template(
        "application_form.html", application={}, jobs=job_choices(), statuses=STATUSES
    )


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def application_edit(application_id):
    application = fetch_one(
        "SELECT * FROM applications WHERE application_id = %s", (application_id,)
    )
    if not application:
        flash("Application not found.", "danger")
        return redirect(url_for("applications"))
    existing_interview_data = load_json(application["interview_data"]) or {}
    if request.method == "POST":
        r = request.form
        params, errors = application_form_values(r, existing_interview_data)
        if errors:
            flash_errors(errors)
            return render_template(
                "application_form.html",
                application=r,
                jobs=job_choices(),
                statuses=STATUSES,
            )
        execute(
            "UPDATE applications SET job_id=%s, application_date=%s, status=%s, "
            "resume_version=%s, cover_letter_sent=%s, interview_data=%s "
            "WHERE application_id=%s",
            params + (application_id,),
        )
        flash("Application updated successfully.", "success")
        return redirect(url_for("applications"))
    application["interview_notes"] = existing_interview_data.get("notes", "")
    return render_template(
        "application_form.html",
        application=application,
        jobs=job_choices(),
        statuses=STATUSES,
    )


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def application_delete(application_id):
    execute("DELETE FROM applications WHERE application_id = %s", (application_id,))
    flash("Application deleted successfully.", "success")
    return redirect(url_for("applications"))


def contact_form_values(r):
    """Validate the contact form. Returns (params, errors)."""
    errors = length_errors(r, "contacts")
    company_id = lookup_id(
        r.get("company_id"), "SELECT company_id FROM companies WHERE company_id = %s"
    )
    if company_id is None:
        errors.append("Choose a valid company.")
    contact_name = clean(r.get("contact_name"))
    if not contact_name:
        errors.append("Contact name is required.")
    email = clean(r.get("email"))
    if email and "@" not in email:
        errors.append("Email address is not valid.")
    params = (
        company_id,
        contact_name,
        clean(r.get("title")),
        email,
        clean(r.get("phone")),
        clean(r.get("linkedin_url")),
        clean(r.get("notes")),
    )
    return params, errors


@app.route("/contacts")
def contacts():
    rows = fetch_all(
        "SELECT ct.*, c.company_name FROM contacts ct "
        "JOIN companies c ON ct.company_id = c.company_id "
        "ORDER BY ct.contact_name"
    )
    return render_template("contacts.html", contacts=rows)


@app.route("/contacts/add", methods=["GET", "POST"])
def contact_add():
    if request.method == "POST":
        r = request.form
        params, errors = contact_form_values(r)
        if errors:
            flash_errors(errors)
            return render_template(
                "contact_form.html", contact=r, companies=company_choices()
            )
        execute(
            "INSERT INTO contacts (company_id, contact_name, title, email, phone, "
            "linkedin_url, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            params,
        )
        flash("Contact added successfully.", "success")
        return redirect(url_for("contacts"))
    return render_template("contact_form.html", contact={}, companies=company_choices())


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def contact_edit(contact_id):
    contact = fetch_one("SELECT * FROM contacts WHERE contact_id = %s", (contact_id,))
    if not contact:
        flash("Contact not found.", "danger")
        return redirect(url_for("contacts"))
    if request.method == "POST":
        r = request.form
        params, errors = contact_form_values(r)
        if errors:
            flash_errors(errors)
            return render_template(
                "contact_form.html", contact=r, companies=company_choices()
            )
        execute(
            "UPDATE contacts SET company_id=%s, contact_name=%s, title=%s, email=%s, "
            "phone=%s, linkedin_url=%s, notes=%s WHERE contact_id=%s",
            params + (contact_id,),
        )
        flash("Contact updated successfully.", "success")
        return redirect(url_for("contacts"))
    return render_template(
        "contact_form.html", contact=contact, companies=company_choices()
    )


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def contact_delete(contact_id):
    execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))
    flash("Contact deleted successfully.", "success")
    return redirect(url_for("contacts"))


@app.route("/job-match")
def job_match():
    # TODO: implement the job-matching algorithm
    return render_template("job_match.html")


if __name__ == "__main__":
    # debug=True auto-reloads on code changes. Turn it off in production.
    app.run(debug=True)
