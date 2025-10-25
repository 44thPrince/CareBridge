from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from database import DatabasePersistence
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"
db = DatabasePersistence()

# ---------------------- Authentication Helpers ----------------------

def login_required(f):
    """Decorator to require login for protected routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Check if password matches hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ---------------------- Web Pages ----------------------

@app.route("/")
def home():
    return render_template("carebridge_home.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        next_page = request.form.get("next") or url_for('dashboard')
        
        # Check if user exists
        user = db.find_user_by_username(username)
        if user and check_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {username}!")
            return redirect(next_page)
        else:
            flash("Invalid username or password. Please try again.")
            return redirect(url_for('signin'))
    
    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard after login"""
    username = session.get('username', 'User')
    
    # Get user-specific data based on role
    # For now, show all caretakers as demo data
    caretakers = db.get_all_caretakers()
    
    return render_template("dashboard.html", 
                         username=username, 
                         caretakers=caretakers)


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
    app.run(debug=True, port=5004)
