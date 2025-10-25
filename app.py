import bcrypt
from database import DatabasePersistence
from functools import wraps
from flask import (
    flash,
    Flask,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
import secrets
from utils import (
    validate_apartment_form,
    paginate,
    validate_tenant_form
)


app = Flask(__name__)
app.secret_key= secrets.token_hex(32)

db = DatabasePersistence()


@app.route('/')
def index():
    return redirect(url_for(''))


if __name__ == '__main__':
    app.run(debug=True, port=5003)