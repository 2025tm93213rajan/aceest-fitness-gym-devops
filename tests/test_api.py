from urllib.parse import quote


def url(name, suffix=""):
    # client names can have spaces, so encode them like a real client would
    return f"/clients/{quote(name)}{suffix}"


# ---------- health and programs ----------

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_list_programs(client):
    res = client.get("/programs")
    assert res.status_code == 200
    codes = {p["code"] for p in res.get_json()}
    assert codes == {"FL", "MG", "BG"}


def test_program_detail_is_case_insensitive(client):
    res = client.get("/programs/mg")
    assert res.status_code == 200
    body = res.get_json()
    assert body["code"] == "MG"
    assert body["factor"] == 35
    assert body["workout"]


def test_program_not_found(client):
    assert client.get("/programs/ZZ").status_code == 404


# ---------- create ----------

def test_create_client(client, sample_client):
    res = client.post("/clients", json=sample_client)
    assert res.status_code == 201
    body = res.get_json()
    assert body["name"] == "Asha Rao"
    assert body["calories"] == 1540
    assert body["id"] == 1


def test_create_duplicate_client(client, sample_client):
    client.post("/clients", json=sample_client)
    res = client.post("/clients", json=sample_client)
    assert res.status_code == 409


def test_create_client_validation_errors(client):
    res = client.post("/clients", json={"name": "", "program": "nope", "age": 3})
    assert res.status_code == 400
    assert len(res.get_json()["errors"]) >= 3


def test_create_client_body_not_json(client):
    res = client.post("/clients", data="hello", content_type="text/plain")
    assert res.status_code == 400


def test_create_client_body_not_an_object(client):
    res = client.post("/clients", json=[1, 2, 3])
    assert res.status_code == 400


# ---------- read ----------

def test_list_clients_sorted_by_name(client):
    for name in ("Zoya", "Arun", "Meena"):
        client.post("/clients", json={"name": name, "program": "BG"})
    names = [c["name"] for c in client.get("/clients").get_json()]
    assert names == ["Arun", "Meena", "Zoya"]


def test_get_client(client, saved_client):
    res = client.get(url(saved_client))
    assert res.status_code == 200
    assert res.get_json()["program"] == "FL"


def test_get_missing_client(client):
    assert client.get("/clients/Nobody").status_code == 404


# ---------- update / delete ----------

def test_update_recalculates_calories(client, saved_client):
    res = client.put(url(saved_client), json={"weight": 80})
    assert res.status_code == 200
    assert res.get_json()["calories"] == 1760


def test_update_program_changes_calories(client, saved_client):
    res = client.put(url(saved_client), json={"program": "MG"})
    assert res.get_json()["calories"] == 2450  # 70kg * 35


def test_update_cannot_rename(client, saved_client):
    res = client.put(url(saved_client), json={"name": "Someone Else"})
    assert res.status_code == 200
    assert res.get_json()["name"] == saved_client


def test_update_invalid_value(client, saved_client):
    res = client.put(url(saved_client), json={"age": 500})
    assert res.status_code == 400


def test_update_missing_client(client):
    assert client.put("/clients/Nobody", json={"weight": 60}).status_code == 404


def test_update_bad_body(client, saved_client):
    res = client.put(url(saved_client), data="x", content_type="text/plain")
    assert res.status_code == 400


def test_delete_client_removes_related_rows(client, saved_client):
    client.post(url(saved_client, "/progress"), json={"adherence": 70})
    client.post(url(saved_client, "/workouts"), json={"workout_type": "Cardio", "duration_min": 20})

    assert client.delete(url(saved_client)).status_code == 204
    assert client.get(url(saved_client)).status_code == 404

    # re-create the same name, old history must not come back
    client.post("/clients", json={"name": saved_client, "program": "BG"})
    assert client.get(url(saved_client, "/progress")).get_json() == []
    assert client.get(url(saved_client, "/workouts")).get_json() == []


def test_delete_missing_client(client):
    assert client.delete("/clients/Nobody").status_code == 404


# ---------- calories / bmi / membership ----------

def test_calories_endpoint(client, saved_client):
    body = client.get(url(saved_client, "/calories")).get_json()
    assert body["calories"] == 1540
    assert body["program"] == "FL"


def test_calories_without_weight(client):
    client.post("/clients", json={"name": "NoWeight", "program": "FL"})
    assert client.get(url("NoWeight", "/calories")).status_code == 422


def test_bmi_endpoint(client, saved_client):
    body = client.get(url(saved_client, "/bmi")).get_json()
    assert body["bmi"] == 25.7
    assert body["category"] == "Overweight"


def test_bmi_without_height(client):
    client.post("/clients", json={"name": "NoHeight", "program": "FL", "weight": 70})
    assert client.get(url("NoHeight", "/bmi")).status_code == 422


def test_membership_active_endpoint(client, saved_client):
    body = client.get(url(saved_client, "/membership")).get_json()
    assert body["status"] == "Active"
    assert body["days_left"] > 0


def test_membership_expired_endpoint(client):
    client.post("/clients", json={"name": "Old", "program": "BG", "membership_end": "2020-01-01"})
    assert client.get(url("Old", "/membership")).get_json()["status"] == "Expired"


def test_membership_not_set_endpoint(client):
    client.post("/clients", json={"name": "New", "program": "BG"})
    assert client.get(url("New", "/membership")).get_json()["status"] == "Inactive"


def test_calculation_endpoints_unknown_client(client):
    for suffix in ("/calories", "/bmi", "/membership"):
        assert client.get(url("Ghost", suffix)).status_code == 404


# ---------- progress ----------

def test_progress_log_and_list(client, saved_client):
    res = client.post(url(saved_client, "/progress"), json={"adherence": 80})
    assert res.status_code == 201
    assert res.get_json()["week"].startswith("Week")

    client.post(url(saved_client, "/progress"), json={"adherence": 90})
    rows = client.get(url(saved_client, "/progress")).get_json()
    assert [r["adherence"] for r in rows] == [80, 90]


def test_progress_validation(client, saved_client):
    assert client.post(url(saved_client, "/progress"), json={}).status_code == 400
    assert client.post(url(saved_client, "/progress"), json={"adherence": 101}).status_code == 400


# ---------- workouts ----------

def test_workout_log_and_list_newest_first(client, saved_client):
    for day in ("2026-03-01", "2026-03-05", "2026-03-03"):
        res = client.post(url(saved_client, "/workouts"), json={
            "date": day, "workout_type": "Strength", "duration_min": 60, "notes": "leg day",
        })
        assert res.status_code == 201

    dates = [w["date"] for w in client.get(url(saved_client, "/workouts")).get_json()]
    assert dates == ["2026-03-05", "2026-03-03", "2026-03-01"]


def test_workout_validation(client, saved_client):
    res = client.post(url(saved_client, "/workouts"), json={"workout_type": "Yoga"})
    assert res.status_code == 400


# ---------- metrics ----------

def test_metrics_log_and_list(client, saved_client):
    res = client.post(url(saved_client, "/metrics"), json={"weight": 69.5, "waist": 80})
    assert res.status_code == 201
    rows = client.get(url(saved_client, "/metrics")).get_json()
    assert rows[0]["weight"] == 69.5
    assert rows[0]["bodyfat"] is None


def test_metrics_validation(client, saved_client):
    assert client.post(url(saved_client, "/metrics"), json={}).status_code == 400


# ---------- shared behaviour of the sub-resources ----------

def test_sub_resources_unknown_client(client):
    for suffix in ("/progress", "/workouts", "/metrics"):
        assert client.get(url("Ghost", suffix)).status_code == 404
        assert client.post(url("Ghost", suffix), json={}).status_code == 404


def test_sub_resources_bad_body(client, saved_client):
    for suffix in ("/progress", "/workouts", "/metrics"):
        res = client.post(url(saved_client, suffix), data="x", content_type="text/plain")
        assert res.status_code == 400
