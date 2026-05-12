from flask import Flask, render_template_string, request, redirect, session, send_file # type: ignore
import sqlite3
import pandas as pd # type: ignore
import io

app = Flask(__name__)
app.secret_key = "ultimate_secret"

# ---------------- CONFIG ----------------
START_USER = 228
END_USER = 275

CARS = ["V-1", "V-2", "AutoV-3", "V-4"]

MAX_USERS_PER_CAR = 15

# ---------------- DATABASE ----------------
conn = sqlite3.connect("car.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    user_id INTEGER,
    car_name TEXT
)
""")

conn.commit()

# ---------------- ADMINS ----------------
ADMINS = {
    "admin": "1234",
    "boss": "0000"
}


# ---------------- FUNCTIONS ----------------
def get_all():
    cur.execute("SELECT * FROM assignments")
    return cur.fetchall()


def car_count(car):
    cur.execute(
        "SELECT COUNT(*) FROM assignments WHERE car_name=?",
        (car,)
    )

    return cur.fetchone()[0]


def user_has_car(user):
    cur.execute(
        "SELECT * FROM assignments WHERE user_id=?",
        (user,)
    )

    return cur.fetchone()


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        u = request.form["user"]
        p = request.form["pass"]

        if u in ADMINS and ADMINS[u] == p:

            session["user"] = u
            return redirect("/")

        return "❌ Wrong Login"

    return """
   

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>

    body{
        /*background:#111;*/
        color:white;
        height:100vh;
        display:flex;
        justify-content:center;
        align-items:center;
    }

    .login-box{
        width:350px;
        /*background:#1e1e1e;*/
        padding:30px;
        border-radius:15px;
        box-shadow:0 0 20px rgba(0,0,0,0.5);
    }

    h2{
        text-align:center;
        margin-bottom:25px;
        color:#111;
    }

    label{
        color:#111;
    }

    .form-control{
        background:#e8f0fe;
        color:white;
        border:none;
    }

    .form-control:focus{
        background:#e8f0fe;
        /*color:white;*/
        box-shadow:none;
    }

    .btn-custom{
        width:100%;
        background:green;
        color:white;
        font-weight:bold;
    }

    .btn-custom:hover{
        background:darkgreen;
    }

    </style>

    <div class="login-box">

        <h2>🚗 ADMIN LOGIN</h2>

        <form method="post">

            <div class="mb-3">

                <label>User</label>

                <input
                    class="form-control"
                    name="user"
                    placeholder="Enter username"
                >

            </div>

            <div class="mb-3">

                <label>Password</label>

                <input
                    class="form-control"
                    type="password"
                    name="pass"
                    placeholder="Enter password"
                >

            </div>

            <button class="btn btn-custom">
                LOGIN
            </button>

        </form>

    </div>
    """


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


# ---------------- ASSIGN ----------------
@app.route("/assign/<int:user>/<car>")
def assign(user, car):

    if "user" not in session:
        return redirect("/login")

    # User already used a car
    if user_has_car(user):
        return redirect("/")

    # Car full
    if car_count(car) >= MAX_USERS_PER_CAR:
        return redirect("/")

    cur.execute(
        "INSERT INTO assignments VALUES (?, ?)",
        (user, car)
    )

    conn.commit()

    return redirect("/")


# ---------------- REMOVE ----------------
@app.route("/remove/<int:user>")
def remove(user):

    if "user" not in session:
        return redirect("/login")

    cur.execute(
        "DELETE FROM assignments WHERE user_id=?",
        (user,)
    )

    conn.commit()

    return redirect("/")


# ---------------- RESET ----------------
@app.route("/reset")
def reset():

    if "user" not in session:
        return redirect("/login")

    cur.execute("DELETE FROM assignments")

    conn.commit()

    return redirect("/")


# ---------------- EXPORT CSV ----------------
@app.route("/export")
def export():

    data = get_all()

    df = pd.DataFrame(
        data,
        columns=["User", "Car"]
    )

    output = io.StringIO()

    df.to_csv(output, index=False)

    mem = io.BytesIO()

    mem.write(output.getvalue().encode())

    mem.seek(0)

    return send_file(
        mem,
        download_name="car_report.csv",
        as_attachment=True
    )


# ---------------- DASHBOARD ----------------
@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    data = get_all()

    used = [(u, c) for u, c in data]

    total_used = len(data)

    car_usage = {}

    for car in CARS:
        car_usage[car] = car_count(car)

    html = """

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>

        h2{
           text-align:center;
           margin-bottom:25px;
        }

        p{
           text-align:center;
           margin-bottom:15px;
        }

    </style>

    <div class="container mt-4">

        <h2>🚗 CAR MANAGEMENT SYSTEM</h2>

        <p>Made By &#127802 Md. Shamsul Arefin &#127802</p>

        <p>
            👤 Logged in as:
            <b>{{user}}</b>
        </p>

        <p>
            <a class="btn btn-danger btn-sm" href="/logout">
                Logout
            </a>

            <a class="btn btn-warning btn-sm" href="/reset">
                Reset
            </a>

            <a class="btn btn-success btn-sm" href="/export">
                Export CSV
            </a>
        </p>

        <hr>

        <h5>
            📊 Total Used:
            {{total}}
        </h5>

        <div class="row mb-3">

            {% for car in cars %}

            <div class="col-md-3">

                <div class="card text-center shadow">

                    <div class="card-body">

                        <h4>{{car}}</h4>

                        <h5>
                            {{car_usage[car]}} / 15
                        </h5>

                    </div>

                </div>

            </div>

            {% endfor %}

        </div>

        <table class="table table-bordered text-center align-middle">

            <tr class="table-dark">

                <th>Student</th>

                {% for car in cars %}
                    <th>{{car}}</th>
                {% endfor %}

                <th>Action</th>

            </tr>

            {% for user in users %}

            <tr>

                {% set assigned = false %}

                {% for u, c in used %}
                    {% if u == user %}
                        {% set assigned = true %}
                    {% endif %}
                {% endfor %}

                <td
                    style="
                        background:
                        {% if assigned %}
                            red
                        {% else %}
                            green
                        {% endif %};

                        color:white;
                        font-weight:bold;
                    "
                >

                    {{user}}

                    {% if assigned %}
                        <br>
                        DONE
                    {% endif %}

                </td>

                {% for car in cars %}

                <td>

                    {% if (user, car) in used %}

                        <span class="badge bg-danger">
                            DONE
                        </span>

                    {% elif assigned %}

                        <span class="badge bg-dark">
                            LOCKED
                        </span>

                    {% elif car_usage[car] >= 15 %}

                        <span class="badge bg-warning text-dark">
                            FULL
                        </span>

                    {% else %}

                        <a
                            class="btn btn-success btn-sm"
                            href="/assign/{{user}}/{{car}}"
                        >
                            Select
                        </a>

                    {% endif %}

                </td>

                {% endfor %}

                <td>

                    <a
                        class="btn btn-danger btn-sm"
                        href="/remove/{{user}}"
                    >
                        Remove
                    </a>

                </td>

            </tr>

            {% endfor %}

        </table>

    </div>
    """

    return render_template_string(
        html,

        users=range(START_USER, END_USER + 1),

        cars=CARS,

        used=used,

        total=total_used,

        car_usage=car_usage,

        user=session["user"]
    )


# ---------------- RUN ----------------
if __name__ == "__main__":

    app.run(debug=True)