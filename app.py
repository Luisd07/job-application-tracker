"""Flask app for the Job Application Tracker.

Each route only renders its template for now. The real logic is TODO.
"""
import os

from dotenv import load_dotenv
from flask import Flask, render_template

# Load settings from the .env file into environment variables.
load_dotenv()

app = Flask(__name__)

# Flask needs a secret key to use flash messages (they are stored in the session).
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")


@app.route("/")
def dashboard():
    # TODO: query the database for dashboard stats and pass them to the template
    return render_template("dashboard.html")


@app.route("/companies")
def companies():
    # TODO: CRUD for companies
    return render_template("companies.html")


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
