import sqlite3

from flask import Blueprint, jsonify, request

from aceest import services
from aceest.db import get_db

bp = Blueprint("main", __name__)


def error(message, status):
    return jsonify({"error": message}), status


def get_client(name):
    row = get_db().execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    return dict(row) if row else None


def json_body():
    # silent=True so a bad body gives us None instead of a 400 html page
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


@bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "aceest-fitness-gym"})


# ---------- programs ----------

@bp.get("/programs")
def list_programs():
    out = [
        {"code": code, "name": p["name"], "calorie_factor": p["factor"]}
        for code, p in services.PROGRAMS.items()
    ]
    return jsonify(out)


@bp.get("/programs/<code>")
def program_detail(code):
    program = services.PROGRAMS.get(code.upper())
    if program is None:
        return error("program not found", 404)
    return jsonify({"code": code.upper(), **program})


# ---------- clients ----------

@bp.post("/clients")
def create_client():
    data = json_body()
    if data is None:
        return error("request body must be a JSON object", 400)

    clean, errors = services.validate_client(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        db = get_db()
        db.execute(
            "INSERT INTO clients (name, age, height, weight, program, calories,"
            " target_weight, target_adherence, membership_end)"
            " VALUES (:name, :age, :height, :weight, :program, :calories,"
            " :target_weight, :target_adherence, :membership_end)",
            clean,
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error("client already exists", 409)

    return jsonify(get_client(clean["name"])), 201


@bp.get("/clients")
def list_clients():
    rows = get_db().execute("SELECT * FROM clients ORDER BY name").fetchall()
    return jsonify([dict(r) for r in rows])


@bp.get("/clients/<name>")
def read_client(name):
    client = get_client(name)
    if client is None:
        return error("client not found", 404)
    return jsonify(client)


@bp.put("/clients/<name>")
def update_client(name):
    existing = get_client(name)
    if existing is None:
        return error("client not found", 404)

    data = json_body()
    if data is None:
        return error("request body must be a JSON object", 400)

    # merge the changes over what we already have and validate the whole thing,
    # name stays fixed because it is the lookup key
    merged = {**existing, **data, "name": existing["name"]}
    clean, errors = services.validate_client(merged)
    if errors:
        return jsonify({"errors": errors}), 400

    db = get_db()
    db.execute(
        "UPDATE clients SET age=:age, height=:height, weight=:weight, program=:program,"
        " calories=:calories, target_weight=:target_weight,"
        " target_adherence=:target_adherence, membership_end=:membership_end"
        " WHERE name=:name",
        clean,
    )
    db.commit()
    return jsonify(get_client(name))


@bp.delete("/clients/<name>")
def delete_client(name):
    if get_client(name) is None:
        return error("client not found", 404)

    db = get_db()
    # no foreign keys in the schema, so clean up the child rows by hand
    for table in ("progress", "workouts", "metrics"):
        db.execute(f"DELETE FROM {table} WHERE client_name = ?", (name,))
    db.execute("DELETE FROM clients WHERE name = ?", (name,))
    db.commit()
    return "", 204


# ---------- calculations ----------

@bp.get("/clients/<name>/calories")
def client_calories(name):
    client = get_client(name)
    if client is None:
        return error("client not found", 404)
    if not client["weight"]:
        return error("client has no weight recorded", 422)

    return jsonify({
        "client": name,
        "program": client["program"],
        "weight": client["weight"],
        "calories": services.calculate_calories(client["weight"], client["program"]),
    })


@bp.get("/clients/<name>/bmi")
def client_bmi(name):
    client = get_client(name)
    if client is None:
        return error("client not found", 404)
    if not client["height"] or not client["weight"]:
        return error("client needs height and weight for BMI", 422)

    bmi = services.calculate_bmi(client["height"], client["weight"])
    return jsonify({"client": name, "bmi": bmi, "category": services.bmi_category(bmi)})


@bp.get("/clients/<name>/membership")
def client_membership(name):
    client = get_client(name)
    if client is None:
        return error("client not found", 404)
    info = services.membership_info(client["membership_end"])
    return jsonify({"client": name, **info})


# ---------- progress / workouts / metrics ----------

def add_record(name, validator, table, columns):
    # shared by the three POST endpoints below, they only differ in the columns
    if get_client(name) is None:
        return error("client not found", 404)

    data = json_body()
    if data is None:
        return error("request body must be a JSON object", 400)

    clean, errors = validator(data)
    if errors:
        return jsonify({"errors": errors}), 400

    if table == "progress":
        clean["week"] = services.week_label()

    cols = ["client_name"] + columns
    values = [name] + [clean[c] for c in columns]
    marks = ", ".join("?" for _ in cols)
    db = get_db()
    db.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({marks})", values)
    db.commit()
    return jsonify(dict(zip(cols, values))), 201


def list_records(name, table, order):
    if get_client(name) is None:
        return error("client not found", 404)
    rows = get_db().execute(
        f"SELECT * FROM {table} WHERE client_name = ? ORDER BY {order}", (name,)
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.post("/clients/<name>/progress")
def add_progress(name):
    return add_record(name, services.validate_progress, "progress", ["week", "adherence"])


@bp.get("/clients/<name>/progress")
def get_progress(name):
    return list_records(name, "progress", "id")


@bp.post("/clients/<name>/workouts")
def add_workout(name):
    return add_record(
        name, services.validate_workout, "workouts",
        ["date", "workout_type", "duration_min", "notes"],
    )


@bp.get("/clients/<name>/workouts")
def get_workouts(name):
    return list_records(name, "workouts", "date DESC, id DESC")


@bp.post("/clients/<name>/metrics")
def add_metrics(name):
    return add_record(
        name, services.validate_metrics, "metrics", ["date", "weight", "waist", "bodyfat"]
    )


@bp.get("/clients/<name>/metrics")
def get_metrics(name):
    return list_records(name, "metrics", "date DESC, id DESC")
