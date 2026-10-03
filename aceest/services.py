from datetime import date, datetime

# Programs carried over from the desktop versions (v1.1 / v3.x).
# "factor" is kcal per kg of body weight, used for the calorie estimate.
PROGRAMS = {
    "FL": {
        "name": "Fat Loss (FL)",
        "factor": 22,
        "workout": [
            "Mon: Back Squat 5x5 + Core",
            "Tue: EMOM 20min Assault Bike",
            "Wed: Bench Press + 21-15-9",
            "Thu: Deadlift + Box Jumps",
            "Fri: Zone 2 Cardio 30min",
        ],
        "diet": [
            "Breakfast: Egg Whites + Oats",
            "Lunch: Grilled Chicken + Brown Rice",
            "Dinner: Fish Curry + Millet Roti",
            "Target: ~2000 kcal",
        ],
    },
    "MG": {
        "name": "Muscle Gain (MG)",
        "factor": 35,
        "workout": [
            "Mon: Squat 5x5",
            "Tue: Bench 5x5",
            "Wed: Deadlift 4x6",
            "Thu: Front Squat 4x8",
            "Fri: Incline Press 4x10",
            "Sat: Barbell Rows 4x10",
        ],
        "diet": [
            "Breakfast: Eggs + Peanut Butter Oats",
            "Lunch: Chicken Biryani",
            "Dinner: Mutton Curry + Rice",
            "Target: ~3200 kcal",
        ],
    },
    "BG": {
        "name": "Beginner (BG)",
        "factor": 26,
        "workout": [
            "Full Body Circuit: Air Squats, Ring Rows, Push-ups",
            "Focus: Technique & Consistency",
        ],
        "diet": [
            "Balanced Tamil Meals",
            "Idli / Dosa / Rice + Dal",
            "Protein Target: 120g/day",
        ],
    },
}

WORKOUT_TYPES = ["Strength", "Hypertrophy", "Cardio", "Mobility"]


def calculate_calories(weight, program_code):
    # same formula as the old save_client(): int(weight * factor)
    if program_code not in PROGRAMS:
        raise ValueError("unknown program")
    return int(weight * PROGRAMS[program_code]["factor"])


def calculate_bmi(height_cm, weight_kg):
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("height and weight must be positive")
    h = height_cm / 100.0
    return round(weight_kg / (h * h), 1)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def week_label(d=None):
    d = d or date.today()
    # keeps the "Week 05 - 2026" style the progress table used before
    return d.strftime("Week %U - %Y")


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def membership_info(end_date, today=None):
    today = today or date.today()
    if not end_date:
        return {"status": "Inactive", "membership_end": None, "days_left": None}
    end = parse_date(end_date)
    if end is None:
        raise ValueError("membership_end must be YYYY-MM-DD")
    days_left = (end - today).days
    status = "Active" if days_left >= 0 else "Expired"
    return {"status": status, "membership_end": end_date, "days_left": days_left}


def _number(data, field, lo, hi, errors, integer=False, required=False):
    value = data.get(field)
    if value is None:
        if required:
            errors.append(f"{field} is required")
        return None
    # bool is a subclass of int in python, don't let True/False slip through
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{field} must be a number")
        return None
    if integer and int(value) != value:
        errors.append(f"{field} must be a whole number")
        return None
    if not lo <= value <= hi:
        errors.append(f"{field} must be between {lo} and {hi}")
        return None
    return int(value) if integer else float(value)


def validate_client(data):
    # returns (clean_dict, errors); errors is an empty list when the data is fine
    errors = []

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name is required")
        name = None
    else:
        name = name.strip()

    program = data.get("program")
    if program not in PROGRAMS:
        errors.append("program must be one of: " + ", ".join(PROGRAMS))
        program = None

    age = _number(data, "age", 10, 100, errors, integer=True)
    height = _number(data, "height", 50, 250, errors)
    weight = _number(data, "weight", 20, 300, errors)
    target_weight = _number(data, "target_weight", 20, 300, errors)
    target_adherence = _number(data, "target_adherence", 0, 100, errors, integer=True)

    membership_end = data.get("membership_end")
    if membership_end is not None and parse_date(membership_end) is None:
        errors.append("membership_end must be YYYY-MM-DD")

    clean = {
        "name": name,
        "age": age,
        "height": height,
        "weight": weight,
        "program": program,
        "target_weight": target_weight,
        "target_adherence": target_adherence,
        "membership_end": membership_end,
        "calories": calculate_calories(weight, program) if weight and program else None,
    }
    return clean, errors


def validate_progress(data):
    errors = []
    adherence = _number(data, "adherence", 0, 100, errors, integer=True, required=True)
    return {"adherence": adherence}, errors


def validate_workout(data):
    errors = []
    d = data.get("date") or date.today().isoformat()
    if parse_date(d) is None:
        errors.append("date must be YYYY-MM-DD")
    wtype = data.get("workout_type")
    if wtype not in WORKOUT_TYPES:
        errors.append("workout_type must be one of: " + ", ".join(WORKOUT_TYPES))
    duration = _number(data, "duration_min", 1, 600, errors, integer=True, required=True)
    notes = data.get("notes", "")
    if not isinstance(notes, str):
        errors.append("notes must be text")
    return {"date": d, "workout_type": wtype, "duration_min": duration, "notes": notes}, errors


def validate_metrics(data):
    errors = []
    d = data.get("date") or date.today().isoformat()
    if parse_date(d) is None:
        errors.append("date must be YYYY-MM-DD")
    weight = _number(data, "weight", 20, 300, errors)
    waist = _number(data, "waist", 30, 250, errors)
    bodyfat = _number(data, "bodyfat", 1, 70, errors)
    if weight is None and waist is None and bodyfat is None:
        errors.append("send at least one of weight, waist, bodyfat")
    return {"date": d, "weight": weight, "waist": waist, "bodyfat": bodyfat}, errors
