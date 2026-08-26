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
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/terms-and-conditions")
def terms():
    return render_template("terms.html")

@app.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")

if __name__=="__main__":
    app.run(debug=True) 