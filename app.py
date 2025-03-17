from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb+srv://Sanjay:Welcome%40123@cluster0.7ef1h.mongodb.net/agriculture_ai?retryWrites=true&w=majority&appName=Cluster0"

mongo = PyMongo(app)

# Enable CORS for all origins (Modify if needed)
CORS(app, resources={r"/*": {"origins": "*"}})

# CORS Headers for Preflight Requests (Fixes OPTIONS Issues)
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Health Check Route
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "API is running"}), 200

# User Registration
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        mobile_number = data.get("mobile_number")
        password = data.get("password")

        if not (username and mobile_number and password):
            return jsonify({"error": "Missing required fields"}), 400

        # Check if user already exists
        if mongo.db.users.find_one({"mobile_number": mobile_number}):
            return jsonify({"error": "User already exists"}), 409

        hashed_pw = generate_password_hash(password)
        user_id = mongo.db.users.insert_one({
            "username": username.strip(),
            "mobile_number": mobile_number.strip(),
            "password": hashed_pw,
            "created_at": datetime.utcnow()
        }).inserted_id

        return jsonify({"message": "User registered successfully", "user_id": str(user_id)}), 201
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

# User Login
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        mobile_number = data.get("mobile_number")
        password = data.get("password")

        if not (mobile_number and password):
            return jsonify({"error": "Missing required fields"}), 400

        user = mongo.db.users.find_one({"mobile_number": mobile_number.strip()})
        if user and check_password_hash(user["password"], password):
            return jsonify({"message": "Login successful", "user_id": str(user["_id"])}), 200

        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

# Get Crop Recommendations by Month
@app.route("/crop_recommendations/<string:month>", methods=["GET"])
def get_crop_recommendations(month):
    try:
        month = month.capitalize()
        crops = mongo.db.crop_recommendations.find_one({"month": month})
        
        if not crops:
            return jsonify({"error": f"No recommendations found for {month}"}), 404

        return jsonify({"month": crops["month"], "recommended_crops": crops["recommended_crops"]}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch crop recommendations: {str(e)}"}), 500

# Get User Information by Mobile Number
@app.route("/user/<string:mobile_number>", methods=["GET"])
def get_user_info(mobile_number):
    try:
        user = mongo.db.users.find_one({"mobile_number": mobile_number.strip()}, {"_id": 0, "password": 0})
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch user information: {str(e)}"}), 500


# Get Pesticide Recommendations by Disease
@app.route("/pesticide_recommendations/<string:disease>", methods=["GET"])
def get_pesticide_recommendations(disease):
    try:
        disease = disease.capitalize()
        pesticides = mongo.db.pesticide_recommendations.find_one({"disease": disease})
        
        if not pesticides:
            return jsonify({"error": f"No recommendations found for {disease}"}), 404

        return jsonify({"disease": pesticides["disease"], "recommended_pesticides": pesticides["recommended_pesticides"]}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch pesticide recommendations: {str(e)}"}), 500

# Save Farmer Logs
@app.route("/farmer_logs", methods=["POST"])
def save_farmer_logs():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        farmer_id = data.get("farmer_id")
        recommended_crops = data.get("recommended_crops")
        pesticide_recommendations = data.get("pesticide_recommendations")

        if not (farmer_id and recommended_crops and pesticide_recommendations):
            return jsonify({"error": "Missing required fields"}), 400

        log_id = mongo.db.farmer_logs.insert_one({
            "farmer_id": farmer_id.strip(),
            "recommended_crops": recommended_crops,
            "pesticide_recommendations": pesticide_recommendations,
            "timestamp": datetime.utcnow()
        }).inserted_id

        return jsonify({"message": "Log saved successfully", "log_id": str(log_id)}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to save farmer log: {str(e)}"}), 500

# Get Farmer Logs by User ID
@app.route("/farmer_logs/<string:farmer_id>", methods=["GET"])
def get_farmer_logs(farmer_id):
    try:
        logs = list(mongo.db.farmer_logs.find({"farmer_id": farmer_id.strip()}))
        if not logs:
            return jsonify({"error": "No logs found"}), 404

        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log["_id"])

        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch farmer logs: {str(e)}"}), 500

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, port=3500)
