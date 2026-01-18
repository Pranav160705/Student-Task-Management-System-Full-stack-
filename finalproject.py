from flask import Flask, render_template, request, redirect, session
import pymysql
from datetime import date

app = Flask(__name__)
app.secret_key = "studenttasksecret"


def get_db():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="your_password",
        database="information",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )





@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/student")
        else:
            return "Invalid Login"

    return render_template("_login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        r = request.form["role"]

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (%s,%s,%s)",
                (u, p, r)
            )
            conn.commit()
            conn.close()
            return redirect("/")
        except:
            return "Username already exists"

    return render_template("_signup.html")


@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        student = request.form["student"]
        title = request.form["title"]
        due = request.form["due"]

        cur.execute(
            "INSERT INTO tasks (student, title, due_date, status) VALUES (%s,%s,%s,'In Progress')",
            (student, title, due)
        )
        conn.commit()

    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    conn.close()

    return render_template("_admindashboard.html", tasks=tasks)


@app.route("/student")
def student_dashboard():
    if "user" not in session or session["role"] != "student":
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tasks WHERE student=%s", (session["user"],))
    tasks = cur.fetchall()

    today = date.today()
    for t in tasks:
        if t["status"] != "Completed" and t["due_date"] < today:
            t["status"] = "Overdue"

    conn.close()
    return render_template("_studentsdashboard.html", tasks=tasks)


@app.route("/complete/<int:id>")
def complete_task(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='Completed' WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect("/student")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

