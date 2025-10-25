from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import DatabasePersistence

app = Flask(__name__)
app.secret_key = "supersecretkey"
db = DatabasePersistence()

# ---------------------- Web Pages ----------------------

@app.route("/")
def home():
    return render_template("carebridge_home.html")


@app.route("/client/register", methods=["GET", "POST"])
def show_client_form():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        phone_number = request.form.get("phone_number")
        date_of_birth = request.form.get("date_of_birth")
        address = request.form.get("address")

        try:
            client_id = db.insert_client(full_name, phone_number, date_of_birth, address)
            flash(f"Client registered successfully. ID: {client_id}")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Error saving client: {e}")
            return redirect(url_for("show_client_form"))

    return render_template("client_form.html")


@app.route("/caretaker/register", methods=["GET", "POST"])
def show_caretaker_form():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        phone_number = request.form.get("phone_number")
        date_of_birth = request.form.get("date_of_birth")

        try:
            caretaker_id = db.insert_caretaker(full_name, phone_number, date_of_birth)
            flash(f"Caretaker registered successfully. ID: {caretaker_id}")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Error saving caretaker: {e}")
            return redirect(url_for("show_caretaker_form"))

    return render_template("caretaker_form.html")


# ---------------------- API Endpoints ----------------------

@app.route("/api/client", methods=["POST"])
def api_create_client():
    data = request.get_json()
    try:
        client_id = db.insert_client(
            data.get("full_name"),
            data.get("phone_number"),
            data.get("date_of_birth"),
            data.get("address"),
        )
        return jsonify({"status": "success", "id": client_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/caretaker", methods=["POST"])
def api_create_caretaker():
    data = request.get_json()
    try:
        caretaker_id = db.insert_caretaker(
            data.get("full_name"),
            data.get("phone_number"),
            data.get("date_of_birth"),
        )
        return jsonify({"status": "success", "id": caretaker_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ---------------------- Run ----------------------

if __name__ == "__main__":
    app.run(debug=True, port=5003)
