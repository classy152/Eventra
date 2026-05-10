from flask import Blueprint, request, jsonify
from extension import db
from model import User, Event
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.decorators import role_required
import bcrypt

auth_bp = Blueprint('auth', __name__)

# ---------------- REGISTER ---------------- #
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    if role not in ["student", "faculty", "admin"]:
        return jsonify({"error": "Invalid role"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        new_user = User(
            name=name,
            email=email,
            password=hashed_password.decode('utf-8'),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ---------------- LOGIN ---------------- #
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)

    return jsonify({
        "message": "Login successful",
        "token": token
    }), 200


# ---------------- PROFILE ---------------- #
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })


# ---------------- CREATE EVENT ---------------- #
@auth_bp.route('/create-event', methods=['POST'])
@jwt_required()
@role_required(['student'])
def create_event():
    data = request.get_json()
    user_id = get_jwt_identity()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    event = Event(
        title=title,
        description=description,
        created_by=user_id,
        status="pending"
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Event created successfully"}), 201


# ---------------- APPROVE EVENT ---------------- #
@auth_bp.route('/approve-event/<int:event_id>', methods=['PUT'])
@jwt_required()
@role_required(['faculty', 'admin'])
def approve_event(event_id):
    event = Event.query.get(event_id)

    if not event:
        return jsonify({"error": "Event not found"}), 404

    event.status = "approved"
    db.session.commit()

    return jsonify({"message": "Event approved"})


# ---------------- ADMIN ONLY ---------------- #
@auth_bp.route('/admin-only', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def admin_only():
    return jsonify({"message": "Admin access granted"})