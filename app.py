from flask import Flask, redirect, render_template, request, session, jsonify
from db import SessionLocal, Engine
import models
from ai import explain_topic, generate_personalized_quiz
import uuid
from datetime import datetime


app = Flask(__name__)

app.secret_key = "study_mate_dev_secret_key_change_this"


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if "user" in session:
        return redirect("/dashboard")

    return render_template("index.html")


# ============================================================
# SIGNUP
# ============================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        name = request.form.get("name", "").strip()

        previous_score = request.form.get(
            "previous_score", ""
        ).strip()

        targeted_subject = request.form.get(
            "target_subject", ""
        ).strip()

        student_class = request.form.get(
            "student_class", ""
        ).strip()

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

            existing_user = (
                db.query(models.User)
                .filter_by(email=email)
                .first()
            )

            if existing_user:
                return "User already exists. Please login."

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


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()

        try:

            user = (
                db.query(models.User)
                .filter_by(
                    email=email,
                    password=password
                )
                .first()
            )

            if user:

                session["user"] = user.id

                return redirect("/dashboard")

            return "Invalid credentials"

        finally:

            db.close()

    return render_template("login.html")


# ============================================================
# TERMS
# ============================================================

@app.route("/terms-and-conditions")
def terms():

    return render_template("terms.html")


# ============================================================
# PRIVACY
# ============================================================

@app.route("/privacy-policy")
def privacy():

    return render_template("privacy.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

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

        schedule_entries = (
            db.query(models.Schedule)
            .filter_by(user_id=user_id)
            .all()
        )

        return render_template(
            "dashboard.html",
            user=user,
            schedule_entries=schedule_entries
        )

    finally:

        db.close()


# ============================================================
# SETTINGS
# ============================================================

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

            name = request.form.get(
                "name", ""
            ).strip()

            email = request.form.get(
                "email", ""
            ).strip()

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

            if not name or not email:
                return "Name and email are required."

            if not targeted_subject:
                return "Targeted subject is required."

            if not student_class:
                return "Class is required."

            if not previous_score:
                return "Previous score is required."

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

            user.name = name
            user.email = email
            user.Targeted_Subject = targeted_subject
            user.Class = student_class
            user.Previous_Score = previous_score

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


# ============================================================
# PROFILE
# ============================================================

@app.route("/profile")
def profile():

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

        return render_template(
            "profile.html",
            user=user
        )

    finally:

        db.close()


# ============================================================
# SCHEDULE
# ============================================================

@app.route("/schedule", methods=["GET", "POST"])
def schedule():

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
            .order_by(
                models.Schedule.Date,
                models.Schedule.Start_time
            )
            .all()
        )

        return render_template(
            "schedule.html",
            user=user,
            schedule_entries=schedule_entries
        )

    finally:

        db.close()


# ============================================================
# EDIT SCHEDULE
# ============================================================

@app.route(
    "/schedule/edit/<int:schedule_id>",
    methods=["GET", "POST"]
)
def edit_schedule(schedule_id):

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

    finally:

        db.close()


# ============================================================
# DELETE SCHEDULE
# ============================================================

@app.route(
    "/schedule/delete/<int:schedule_id>",
    methods=["POST"]
)
def delete_schedule(schedule_id):

    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    try:

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

    finally:

        db.close()


# ============================================================
# EXPLANATION
# ============================================================

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

            subject = request.form.get(
                "subject", ""
            ).strip()

            question = request.form.get(
                "question", ""
            ).strip()

            if not subject or not question:

                return (
                    "Subject and question are required.",
                    400
                )

            explanation_text = explain_topic(
                question=question,
                subject=subject,
                student_class=user.Class
            )

            explanation = models.Explanation(
                user_id=user_id,
                Subject=subject,
                Questions=question,
                Explanation=explanation_text
            )

            db.add(explanation)

            db.commit()

        explanations = (
            db.query(models.Explanation)
            .filter_by(user_id=user_id)
            .order_by(
                models.Explanation.id.desc()
            )
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


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():

    return render_template("about.html")


# ============================================================
# QUIZ PAGE
# ============================================================

@app.route("/quiz")
def quiz():

    if "user" not in session:
        return redirect("/login")

    return render_template("quiz.html")


# ============================================================
# GENERATE PERSONALIZED QUIZ
# ============================================================

@app.route(
    "/api/quiz/generate",
    methods=["POST"]
)
def generate_quiz():

    if "user" not in session:

        return jsonify({
            "error": "Please log in first."
        }), 401

    db = SessionLocal()

    try:

        # ------------------------------------------------
        # CURRENT USER
        # ------------------------------------------------

        user_id = session["user"]

        user = (
            db.query(models.User)
            .filter_by(id=user_id)
            .first()
        )

        if not user:

            session.pop("user", None)

            return jsonify({
                "error": "User not found."
            }), 404

        # ------------------------------------------------
        # STUDENT CLASS
        # ------------------------------------------------

        student_class = user.Class

        # ------------------------------------------------
        # COMPLETED TASKS
        # ------------------------------------------------

        completed_tasks = (
            db.query(models.Task)
            .filter_by(
                user_id=user_id,
                completed=True
            )
            .order_by(
                models.Task.id.desc()
            )
            .limit(20)
            .all()
        )

        tasks = []

        for task in completed_tasks:

            tasks.append({
                "subject": task.subject,
                "topic": task.title,
                "description": task.description or "",
                "completed": task.completed
            })

        # ------------------------------------------------
        # SCHEDULE
        # ------------------------------------------------

        schedule_entries = (
            db.query(models.Schedule)
            .filter_by(user_id=user_id)
            .order_by(
                models.Schedule.id.desc()
            )
            .limit(20)
            .all()
        )

        schedule = []

        for item in schedule_entries:

            schedule.append({
                "subject": item.Subject,
                "task": item.Task,
                "date": item.Date,
                "start_time": item.Start_time,
                "end_time": item.End_time,
                "status": item.Status
            })

        # ------------------------------------------------
        # CHECK STUDY ACTIVITY
        # ------------------------------------------------

        if not tasks and not schedule:

            return jsonify({
                "questions": [],
                "message": (
                    "Not enough study activity. "
                    "Complete some tasks or add "
                    "items to your schedule first."
                )
            })

        # ------------------------------------------------
        # GENERATE QUIZ WITH GEMINI
        # ------------------------------------------------

        quiz_data = generate_personalized_quiz(
            student_class=student_class,
            tasks=tasks,
            schedule=schedule,
            question_count=10
        )

        questions = quiz_data.get(
            "questions",
            []
        )

        if not questions:

            return jsonify({
                "error": "Gemini did not generate any questions."
            }), 500

        # ------------------------------------------------
        # VALIDATE QUESTIONS
        # ------------------------------------------------

        valid_questions = []

        for question in questions:

            if not isinstance(question, dict):
                continue

            options = question.get(
                "options",
                []
            )

            answer = question.get(
                "answer"
            )

            if (
                not question.get("question")
                or not question.get("subject")
                or not question.get("topic")
                or len(options) != 4
                or answer is None
            ):
                continue

            try:

                answer = int(answer)

            except (TypeError, ValueError):

                continue

            if answer < 0 or answer > 3:
                continue

            valid_questions.append({
                "subject": question["subject"],
                "topic": question["topic"],
                "question": question["question"],
                "options": options,
                "answer": answer
            })

        if not valid_questions:

            return jsonify({
                "error": (
                    "Gemini returned an invalid quiz. "
                    "Please try again."
                )
            }), 500

        # ------------------------------------------------
        # QUIZ ID
        # ------------------------------------------------

        quiz_id = str(uuid.uuid4())

        # ------------------------------------------------
        # STORE ANSWERS SERVER-SIDE
        # ------------------------------------------------

        session[
            f"quiz_{quiz_id}"
        ] = {
            "questions": valid_questions,
            "created_at": datetime.utcnow().isoformat()
        }

        # ------------------------------------------------
        # SEND QUESTIONS WITHOUT ANSWERS
        # ------------------------------------------------

        client_questions = []

        for question in valid_questions:

            client_questions.append({
                "subject": question["subject"],
                "topic": question["topic"],
                "question": question["question"],
                "options": question["options"]
            })

        return jsonify({

            "quiz_id": quiz_id,

            "title": quiz_data.get(
                "title",
                "Your Personalized Quiz"
            ),

            "description": quiz_data.get(
                "description",
                "Generated from your Study_Mate activity."
            ),

            "questions": client_questions
        })

    except Exception as e:

        print(
            "QUIZ GENERATION ERROR:",
            repr(e)
        )

        return jsonify({
            "error": (
                "Unable to generate your quiz right now."
            )
        }), 500

    finally:

        db.close()


# ============================================================
# SUBMIT QUIZ
# ============================================================

@app.route(
    "/api/quiz/submit",
    methods=["POST"]
)
def submit_quiz():

    if "user" not in session:

        return jsonify({
            "error": "Please log in first."
        }), 401

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "Invalid request."
            }), 400

        quiz_id = data.get("quiz_id")

        submitted_answers = data.get(
            "answers",
            {}
        )

        if not quiz_id:

            return jsonify({
                "error": "Missing quiz ID."
            }), 400

        quiz_key = f"quiz_{quiz_id}"

        stored_quiz = session.get(
            quiz_key
        )

        if not stored_quiz:

            return jsonify({
                "error": (
                    "Quiz expired. "
                    "Please generate a new quiz."
                )
            }), 400

        questions = stored_quiz.get(
            "questions",
            []
        )

        correct = 0

        subject_breakdown = {}

        # ------------------------------------------------
        # CHECK EACH ANSWER
        # ------------------------------------------------

        for index, question in enumerate(questions):

            submitted = submitted_answers.get(
                str(index)
            )

            correct_answer = question["answer"]

            subject = question.get(
                "subject",
                "General"
            )

            if subject not in subject_breakdown:

                subject_breakdown[subject] = {
                    "correct": 0,
                    "total": 0
                }

            subject_breakdown[
                subject
            ]["total"] += 1

            if submitted is not None:

                try:

                    submitted = int(submitted)

                except (TypeError, ValueError):

                    submitted = None

            if (
                submitted is not None
                and submitted == correct_answer
            ):

                correct += 1

                subject_breakdown[
                    subject
                ]["correct"] += 1

        # ------------------------------------------------
        # RESULTS
        # ------------------------------------------------

        total = len(questions)

        incorrect = total - correct

        percentage = (
            round(
                (correct / total) * 100
            )
            if total
            else 0
        )

        # ------------------------------------------------
        # REMOVE QUIZ FROM SESSION
        # ------------------------------------------------

        session.pop(
            quiz_key,
            None
        )

        return jsonify({

            "correct": correct,

            "incorrect": incorrect,

            "total": total,

            "percentage": percentage,

            "subject_breakdown":
                subject_breakdown
        })

    except Exception as e:

        print(
            "QUIZ SUBMISSION ERROR:",
            repr(e)
        )

        return jsonify({
            "error": (
                "Unable to calculate quiz result."
            )
        }), 500


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )