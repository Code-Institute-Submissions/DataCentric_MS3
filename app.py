import os
from flask import (
    Flask, render_template,
    redirect, request, url_for, session,
    flash, Markup)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # Check for existing users
        if existing_user:
            flash("Username already cooked")
            return redirect(url_for("register"))
        # New user
        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # Starts Session
        session["user"] = request.form.get("username").lower()
        flash("Registration in the oven!")
        return redirect(url_for("dashboard", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Check if information matches
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Hey, {}!".format(request.form.get("username")))
                    return redirect(url_for(
                        "dashboard", username=session["user"]))
            else:
                # invalid information
                flash("Wrong Ingredients")
                return redirect(url_for("login"))

        else:
            # User doesn't exists
            flash("No Registered Chef")
            return redirect(url_for("login"))

    return render_template('login.html')


@app.route("/dashboard/<username>", methods=['GET', 'POST'])
def dashboard(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # Retrieves user's profile
    if session["user"]:
        return render_template("dashboard.html", username=username)

    return render_template('login.html')


@app.route("/logout")
def logout():
    # Session.pop removes user's cookie info
    flash("See you soon!")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_recipe")
def add_recipe():
    meal = list(mongo.db.dish_type.find().sort("meal_time", 1))
    return render_template('add_recipe.html', meal=meal)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
