from flask import Flask, redirect, render_template, request, session
from db import SessionLocal, Engine
import models

app = Flask(__name__)

@app.route("/")
def home():
    if "user"in session:
        return redirect("/dashboard")
    return render_template("index.html")
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        previous_score = request.form.get("previous_score")
        targeted_subject = request.form.get("targeted_subject")
        _class = request.form.get("class")

        existing_user = db.query(models.User).filter_by(email=email).first()

        if existing_user:
            return "User already exists"

        user = models.User(email=email, password=password, name=name, Previous_Score=previous_score, Targeted_Subject=targeted_subject, Class=_class)
        db.add(user)
        db.commit()
        return redirect("/login")
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


if __name__=="__main__":
    app.run(debug=True) 