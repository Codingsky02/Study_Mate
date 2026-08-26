from flask import Flask, redirect, render_template, request, session
from db import SessionLocal, Engine
import models
from ai import explain_topic

app = Flask(__name__)

app.secret_key = "study_mate_dev_secret_key_change_this"

@app.route("/")
def home():
    if "user"in session:
        return redirect("/dashboard")
    return render_template("index.html")
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        name = request.form.get("name", "").strip()

        previous_score = request.form.get("previous_score", "").strip()
        targeted_subject = request.form.get("target_subject", "").strip()
        student_class = request.form.get("student_class", "").strip()

        # Check required fields
        if not email or not password or not name:
            return "Name, email and password are required."

        if not previous_score:
            return "Previous score is required."

        if not targeted_subject:
            return "Targeted subject is required."

        if not student_class:
            return "Class is required."

        db = SessionLocal()

        try:

            # Check existing user
            existing_user = (
                db.query(models.User)
                .filter_by(email=email)
                .first()
            )

            if existing_user:
                return "User already exists. Please login."

            # Create user
            user = models.User(
                name=name,
                email=email,
                password=password,
                Previous_Score=previous_score,
                Targeted_Subject=targeted_subject,
                Class=student_class
            )

            db.add(user)
            db.commit()

            return redirect("/login")

        except Exception as e:

            db.rollback()

            print("SIGNUP ERROR:", e)

            return f"Signup error: {e}", 500

        finally:

            db.close()

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()
        user = db.query(models.User).filter_by(email=email, password=password).first()

        if user:
            session["user"] = user.id
            return redirect("/dashboard")
        else:
            return "Invalid credentials"
        
    return render_template("login.html")


@app.route("/terms-and-conditions")
def terms():
    return render_template("terms.html")

@app.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()
    user_id = session["user"]
    user = db.query(models.User).filter_by(id=user_id).first()

    if request.method == "POST":
        subject = request.form.get("subject")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        task = request.form.get("task")
        status = request.form.get("status")

        schedule_entry = models.Schedule(
            user_id=user_id,
            Subject=subject,
            Date=date,
            Start_time=start_time,
            End_time=end_time,
            Task=task,
            Status=status
        )
        db.add(schedule_entry)
        db.commit()

    schedule_entries = db.query(models.Schedule).filter_by(user_id=user_id).all()
    return render_template("dashboard.html", user=user, schedule_entries=schedule_entries)


@app.route("/settings", methods=["GET", "POST"])
def settings():

    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    try:

        user_id = session["user"]

        user = (
            db.query(models.User)
            .filter_by(id=user_id)
            .first()
        )

        if not user:
            session.pop("user", None)
            return redirect("/login")

        if request.method == "POST":

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            targeted_subject = request.form.get(
                "targeted_subject", ""
            ).strip()
            student_class = request.form.get(
                "student_class", ""
            ).strip()
            previous_score = request.form.get(
                "previous_score", ""
            ).strip()

            new_password = request.form.get(
                "new_password", ""
            ).strip()

            # Basic validation
            if not name or not email:
                return "Name and email are required."

            if not targeted_subject:
                return "Targeted subject is required."

            if not student_class:
                return "Class is required."

            if not previous_score:
                return "Previous score is required."

            # Check if another user already has this email
            existing_user = (
                db.query(models.User)
                .filter(
                    models.User.email == email,
                    models.User.id != user_id
                )
                .first()
            )

            if existing_user:
                return "That email is already being used."

            # Update profile
            user.name = name
            user.email = email
            user.Targeted_Subject = targeted_subject
            user.Class = student_class
            user.Previous_Score = previous_score

            # Update password only if entered
            if new_password:
                user.password = new_password

            db.commit()

            return redirect("/settings")

        return render_template(
            "settings.html",
            user=user
        )

    except Exception as e:

        db.rollback()

        print("SETTINGS ERROR:", e)

        return f"Settings error: {e}", 500

    finally:

        db.close()


@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    user_id = session["user"]

    user = db.query(models.User).filter_by(id=user_id).first()

    if not user:
        session.pop("user", None)
        return redirect("/login")

    return render_template("profile.html", user=user)


@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    user_id = session["user"]

    user = db.query(models.User).filter_by(id=user_id).first()

    if not user:
        session.pop("user", None)
        return redirect("/login")

    if request.method == "POST":

        subject = request.form.get("subject")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        task = request.form.get("task")
        status = request.form.get("status")

        schedule_entry = models.Schedule(
            user_id=user_id,
            Subject=subject,
            Date=date,
            Start_time=start_time,
            End_time=end_time,
            Task=task,
            Status=status
        )

        db.add(schedule_entry)
        db.commit()

        return redirect("/schedule")

    schedule_entries = (
        db.query(models.Schedule)
        .filter_by(user_id=user_id)
        .order_by(models.Schedule.Date, models.Schedule.Start_time)
        .all()
    )

    return render_template(
        "schedule.html",
        user=user,
        schedule_entries=schedule_entries
    )

@app.route("/schedule/edit/<int:schedule_id>", methods=["GET", "POST"])
def edit_schedule(schedule_id):

    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    user_id = session["user"]

    user = db.query(models.User).filter_by(id=user_id).first()

    if not user:
        session.pop("user", None)
        return redirect("/login")

    entry = (
        db.query(models.Schedule)
        .filter_by(
            id=schedule_id,
            user_id=user_id
        )
        .first()
    )

    if not entry:
        return "Schedule entry not found", 404

    if request.method == "POST":

        entry.Subject = request.form.get("subject")
        entry.Date = request.form.get("date")
        entry.Start_time = request.form.get("start_time")
        entry.End_time = request.form.get("end_time")
        entry.Task = request.form.get("task")
        entry.Status = request.form.get("status")

        db.commit()

        return redirect("/schedule")

    return render_template(
        "edit_schedule.html",
        user=user,
        entry=entry
    )

@app.route("/schedule/delete/<int:schedule_id>", methods=["POST"])
def delete_schedule(schedule_id):

    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    user_id = session["user"]

    entry = (
        db.query(models.Schedule)
        .filter_by(
            id=schedule_id,
            user_id=user_id
        )
        .first()
    )

    if not entry:
        return "Schedule entry not found", 404

    db.delete(entry)
    db.commit()

    return redirect("/schedule")


@app.route("/explain", methods=["GET", "POST"])
def explain():

    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    try:
        user_id = session["user"]

        user = (
            db.query(models.User)
            .filter_by(id=user_id)
            .first()
        )

        if not user:
            session.pop("user", None)
            return redirect("/login")

        if request.method == "POST":

            subject = request.form.get("subject", "").strip()
            question = request.form.get("question", "").strip()

            if not subject or not question:
                return "Subject and question are required.", 400

            # Generate explanation using Gemini
            explanation_text = explain_topic(
                question=question,
                subject=subject,
                student_class=user.Class
            )

            # Save explanation
            explanation = models.Explanation(
                user_id=user_id,
                Subject=subject,
                Questions=question,
                Explanation=explanation_text
            )

            db.add(explanation)
            db.commit()

        # Get user's explanation history
        explanations = (
            db.query(models.Explanation)
            .filter_by(user_id=user_id)
            .order_by(models.Explanation.id.desc())
            .all()
        )

        latest_explanation = (
            explanations[0]
            if explanations
            else None
        )

        return render_template(
            "explain.html",
            user=user,
            explanations=explanations,
            latest_explanation=latest_explanation
        )

    finally:
        db.close()

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True) 