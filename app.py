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
        emergency_contact_name = request.form.get("emergency_contact_name")
        emergency_contact_phone = request.form.get("emergency_contact_phone")
        medical_conditions = request.form.get("medical_conditions")
        special_instructions = request.form.get("special_instructions")

        try:
            client_id = db.insert_client(
                full_name, phone_number, date_of_birth, address,
                emergency_contact_name, emergency_contact_phone,
                medical_conditions, special_instructions
            )
            flash(f"Client registered successfully! Welcome to CareBridge, {full_name}!")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Error saving client: {e}")
            return redirect(url_for("show_client_form"))

    return render_template("client_form.html")


@app.route("/caretaker/register", methods=["GET", "POST"])
def show_caretaker_form():
    if request.method == "POST":
        # Get all form fields
        full_name = request.form.get("full_name")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        date_of_birth = request.form.get("date_of_birth")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        zip_code = request.form.get("zip_code")
        bio = request.form.get("bio")
        years_experience = request.form.get("years_experience", 0)
        hourly_rate = request.form.get("hourly_rate")
        availability = request.form.get("availability")
        certifications = request.form.get("certifications")
        languages = request.form.get("languages")
        
        # Get ADL services (checkboxes)
        adl_services = request.form.getlist("adl_services")

        try:
            # Insert caretaker
            caretaker_id = db.insert_caretaker(
                full_name, phone_number, date_of_birth, email, address,
                city, state, zip_code, bio, years_experience, hourly_rate,
                availability, certifications, languages
            )
            
            # Add ADL services
            for service in adl_services:
                db.add_caretaker_adl(caretaker_id, service)
            
            flash(f"Caretaker registered successfully! Welcome to CareBridge, {full_name}! Your profile is now live.")
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
