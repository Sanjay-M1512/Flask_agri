from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

# MongoDB Configuration (Properly Encoded URI)
app.config["MONGO_URI"] = "mongodb+srv://Sanjay:Welcome%40123@cluster0.7ef1h.mongodb.net/agriculture_ai?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# Enable CORS for frontend (Adjust origin as needed)
CORS(app, resources={r"/*": {"origins": "http://localhost:8081"}})

# Health Check Route
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "API is running"}), 200

# User Registration
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        if not data or not all(key in data for key in ("username", "mobile_number", "password")):
            return jsonify({"error": "Missing required fields"}), 400

        if mongo.db.users.find_one({"mobile_number": data["mobile_number"]}):
            return jsonify({"error": "User with this mobile number already exists"}), 409

        hashed_pw = generate_password_hash(data["password"])
        user_id = mongo.db.users.insert_one({
            "username": data["username"],
            "mobile_number": data["mobile_number"],
            "password": hashed_pw,
            "created_at": datetime.utcnow()
        }).inserted_id

        return jsonify({"message": "User registered successfully!", "user_id": str(user_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User Login
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data or not data.get("password"):
            return jsonify({"error": "Missing required fields"}), 400

        user = mongo.db.users.find_one({"$or": [
            {"username": data.get("username")},
            {"mobile_number": data.get("mobile_number")}
        ]})

        if user and check_password_hash(user["password"], data["password"]):
            return jsonify({"message": "Login successful!", "user_id": str(user["_id"])}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Crop Recommendations by Month
@app.route("/crop_recommendations/<string:month>", methods=["GET"])
def get_crop_recommendations(month):
    try:
        crops = mongo.db.crop_recommendations.find_one({"month": month.capitalize()})
        if crops:
            return jsonify({"month": crops["month"], "recommended_crops": crops["recommended_crops"]}), 200
        return jsonify({"error": "No recommendations available for this month"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Pesticide Recommendations by Disease
@app.route("/pesticide_recommendations/<string:disease>", methods=["GET"])
def get_pesticide_recommendations(disease):
    try:
        pesticides = mongo.db.pesticide_recommendations.find_one({"disease": disease.capitalize()})
        if pesticides:
            return jsonify({"disease": pesticides["disease"], "recommended_pesticides": pesticides["recommended_pesticides"]}), 200
        return jsonify({"error": "No recommendations available for this disease"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Save Farmer Logs
@app.route("/farmer_logs", methods=["POST"])
def save_farmer_logs():
    try:
        data = request.json
        if not data or not all(key in data for key in ("farmer_id", "recommended_crops", "pesticide_recommendations")):
            return jsonify({"error": "Missing required fields"}), 400

        log_id = mongo.db.farmer_logs.insert_one({
            "farmer_id": data["farmer_id"],
            "recommended_crops": data["recommended_crops"],
            "pesticide_recommendations": data["pesticide_recommendations"],
            "timestamp": datetime.utcnow()
        }).inserted_id

        return jsonify({"message": "Log saved successfully!", "log_id": str(log_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Farmer Logs by User ID
@app.route("/farmer_logs/<string:farmer_id>", methods=["GET"])
def get_farmer_logs(farmer_id):
    try:
        logs = list(mongo.db.farmer_logs.find({"farmer_id": farmer_id}))
        if logs:
            for log in logs:
                log["_id"] = str(log["_id"])
            return jsonify(logs), 200
        return jsonify({"error": "No logs found for this farmer"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=3500)
