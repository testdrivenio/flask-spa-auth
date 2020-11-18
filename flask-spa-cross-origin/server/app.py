from flask import Flask, request, jsonify
from flask import session
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_cors import CORS


app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY="secret_sauce",
)

cors = CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": "http://localhost:8080"}},
)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

# database
users = [
    {
        "id": 1,
        "username": "test",
        "password": "test",
    }
]


class User(UserMixin):
    ...


def get_user(user_id: int):
    for user in users:
        if int(user["id"]) == int(user_id):
            return user
    return None


@login_manager.user_loader
def user_loader(id: int):
    user = get_user(id)
    if user:
        user_model = User()
        user_model.id = user["id"]
        return user_model
    return None


@app.route("/api/getsession")
def check_session():
    if current_user.is_authenticated:
        return jsonify({"login": True})
    return jsonify({"login": False})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    for user in users:
        if user["username"] == username and user["password"] == password:
            user_model = User()
            user_model.id = user["id"]
            login_user(user_model)
            return jsonify({"login": True})
    return jsonify({"login": False})


@app.route("/api/data", methods=["GET"])
@login_required
def user_data():
    user = get_user(current_user.id)

    return jsonify({"name": user["username"]})


@app.route("/api/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"logout": True})


if __name__ == "__main__":
    app.run(debug=True, load_dotenv=True)
