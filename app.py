"""Flask app for the Job Application Tracker.

Routes for the dashboard, CRUD pages for each table, and the job-match feature.
"""

import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from database import execute, fetch_all, fetch_one

# Load settings from the .env file into environment variables.
load_dotenv()

app = Flask(__name__)

# Flask needs a secret key to use flash messages (they are stored in the session).
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")


def clean(value):
    """Clean a value that arrives as '' when empty. Store NULL"""
    value = (value or "").strip()
    return value or None


@app.route("/")
def dashboard():
    # TODO: query the database for dashboard stats and pass them to the template
    return render_template("dashboard.html")


@app.route("/companies")
def companies():
    rows = fetch_all("SELECT * FROM companies ORDER BY company_name")
    return render_template("companies.html", companies=rows)


@app.route("/companies/add", methods=["GET", "POST"])
def company_add():
    if request.method == "POST":
        r = request.form
        if not clean(r.get("company_name")):
            flash("Company name is required.", "danger")
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
    company = fetch_one("SELECT * FROM companies WHERE id = %s", (company_id,))
    if not company:
        flash("Company not found.", "danger")
        return redirect(url_for("companies"))
    if request.method == "POST":
        r = request.form
        if not clean(r.get("company_name")):
            flash("Company name is required.", "danger")
            return render_template("company_form.html", company=r)
        execute(
            "UPDATE companies SET company_name=%s, industry=%s, website=%s, city=%s, state=%s, notes=%s "
            "WHERE id=%s",
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
    execute("DELETE FROM companies WHERE id = %s", (company_id,))
    flash("Company deleted successfully.", "success")
    return redirect(url_for("companies"))


@app.route("/jobs")
def jobs():
    # TODO: CRUD for jobs
    return render_template("jobs.html")


@app.route("/applications")
def applications():
    # TODO: CRUD for applications
    return render_template("applications.html")


@app.route("/contacts")
def contacts():
    # TODO: CRUD for contacts
    return render_template("contacts.html")


@app.route("/job-match")
def job_match():
    # TODO: implement the job-matching algorithm
    return render_template("job_match.html")


if __name__ == "__main__":
    # debug=True auto-reloads on code changes. Turn it off in production.
    app.run(debug=True)
