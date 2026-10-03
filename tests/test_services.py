from datetime import date

import pytest

from aceest import services


# ---------- calories ----------

@pytest.mark.parametrize("program, weight, expected", [
    ("FL", 70, 1540),
    ("MG", 80, 2800),
    ("BG", 60, 1560),
])
def test_calories_uses_program_factor(program, weight, expected):
    assert services.calculate_calories(weight, program) == expected


def test_calories_truncates_to_int():
    # 72.5 * 22 = 1595.0, 72.55 * 22 = 1596.1 -> int() drops the decimals
    assert services.calculate_calories(72.55, "FL") == 1596


def test_calories_unknown_program():
    with pytest.raises(ValueError):
        services.calculate_calories(70, "XX")


# ---------- bmi ----------

def test_bmi_value():
    assert services.calculate_bmi(170, 65) == 22.5


@pytest.mark.parametrize("height, weight", [(0, 70), (170, 0), (-5, 70)])
def test_bmi_rejects_non_positive(height, weight):
    with pytest.raises(ValueError):
        services.calculate_bmi(height, weight)


@pytest.mark.parametrize("bmi, category", [
    (17.0, "Underweight"),
    (18.5, "Normal"),      # boundary values belong to the higher band
    (24.9, "Normal"),
    (25.0, "Overweight"),
    (29.9, "Overweight"),
    (30.0, "Obese"),
    (40.0, "Obese"),
])
def test_bmi_category_boundaries(bmi, category):
    assert services.bmi_category(bmi) == category


# ---------- membership ----------

def test_membership_active():
    info = services.membership_info("2026-06-30", today=date(2026, 6, 1))
    assert info["status"] == "Active"
    assert info["days_left"] == 29


def test_membership_last_day_is_still_active():
    info = services.membership_info("2026-06-01", today=date(2026, 6, 1))
    assert info["status"] == "Active"
    assert info["days_left"] == 0


def test_membership_expired():
    info = services.membership_info("2026-05-01", today=date(2026, 6, 1))
    assert info["status"] == "Expired"
    assert info["days_left"] < 0


def test_membership_not_set():
    info = services.membership_info(None)
    assert info["status"] == "Inactive"
    assert info["days_left"] is None


def test_membership_bad_date():
    with pytest.raises(ValueError):
        services.membership_info("31/12/2026")


# ---------- small helpers ----------

def test_week_label_format():
    assert services.week_label(date(2026, 1, 15)) == "Week 02 - 2026"


def test_parse_date():
    assert services.parse_date("2026-02-03") == date(2026, 2, 3)
    assert services.parse_date("not a date") is None
    assert services.parse_date(None) is None


def test_every_program_has_plan_details():
    for code, program in services.PROGRAMS.items():
        assert program["factor"] > 0, code
        assert program["workout"], code
        assert program["diet"], code


# ---------- validate_client ----------

def test_validate_client_ok(sample_client):
    clean, errors = services.validate_client(sample_client)
    assert errors == []
    assert clean["calories"] == 1540
    assert clean["name"] == "Asha Rao"


def test_validate_client_trims_name():
    clean, errors = services.validate_client({"name": "  Ravi  ", "program": "BG"})
    assert errors == []
    assert clean["name"] == "Ravi"
    assert clean["calories"] is None  # no weight given, so nothing to calculate


def test_validate_client_missing_required():
    _, errors = services.validate_client({})
    assert "name is required" in errors
    assert any("program" in e for e in errors)


@pytest.mark.parametrize("field, value", [
    ("age", 5),
    ("age", 150),
    ("age", 25.5),
    ("age", "twenty"),
    ("height", 10),
    ("weight", 500),
    ("weight", True),
    ("target_adherence", 101),
    ("membership_end", "2026/01/01"),
])
def test_validate_client_bad_values(sample_client, field, value):
    sample_client[field] = value
    _, errors = services.validate_client(sample_client)
    assert errors, f"{field}={value!r} should have been rejected"


# ---------- other validators ----------

def test_validate_progress():
    assert services.validate_progress({"adherence": 75})[1] == []
    assert services.validate_progress({})[1]
    assert services.validate_progress({"adherence": 120})[1]


def test_validate_workout_defaults_date_to_today():
    clean, errors = services.validate_workout({"workout_type": "Cardio", "duration_min": 30})
    assert errors == []
    assert clean["date"] == date.today().isoformat()


def test_validate_workout_errors():
    _, errors = services.validate_workout(
        {"workout_type": "Yoga", "duration_min": 0, "date": "yesterday", "notes": 5}
    )
    assert len(errors) == 4


def test_validate_metrics_needs_one_value():
    assert services.validate_metrics({})[1]
    assert services.validate_metrics({"waist": 80})[1] == []
    assert services.validate_metrics({"bodyfat": 99})[1]


def test_validate_metrics_bad_date():
    _, errors = services.validate_metrics({"weight": 70, "date": "12-03-2026"})
    assert errors == ["date must be YYYY-MM-DD"]
