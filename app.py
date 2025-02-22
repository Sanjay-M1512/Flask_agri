from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/agriculture_ai"
mongo = PyMongo(app)

# User Registration (No Email Required, Mobile Number Added)
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_pw = generate_password_hash(data["password"])
    user_id = mongo.db.users.insert_one({
        "username": data["username"],
        "mobile_number": data["mobile_number"],
        "password": hashed_pw
    }).inserted_id
    return jsonify({"message": "User registered successfully!", "user_id": str(user_id)})

# User Login (Either by Username & Password or Mobile Number & Password)
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = mongo.db.users.find_one({"$or": [
        {"username": data.get("username")},
        {"mobile_number": data.get("mobile_number")}
    ]})
    
    if user and check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Login successful!", "user_id": str(user["_id"])});
    return jsonify({"message": "Invalid credentials"}), 401

# Get Crop Recommendations by Month
@app.route("/crop_recommendations/<month>", methods=["GET"])
def get_crop_recommendations(month):
    crops = mongo.db.crop_recommendations.find_one({"month": month.capitalize()})
    if crops:
        return jsonify({"month": crops["month"], "recommended_crops": crops["recommended_crops"]})
    return jsonify({"message": "No recommendations available for this month."}), 404

# Get Pesticide Recommendations by Disease
@app.route("/pesticide_recommendations/<disease>", methods=["GET"])
def get_pesticide_recommendations(disease):
    pesticides = mongo.db.pesticide_recommendations.find_one({"disease": disease.capitalize()})
    if pesticides:
        return jsonify({"disease": pesticides["disease"], "recommended_pesticides": pesticides["recommended_pesticides"]})
    return jsonify({"message": "No recommendations available for this disease."}), 404

# Save Farmer Logs
@app.route("/farmer_logs", methods=["POST"])
def save_farmer_logs():
    data = request.json
    log_id = mongo.db.farmer_logs.insert_one({
        "farmer_id": data["farmer_id"],
        "recommended_crops": data["recommended_crops"],
        "pesticide_recommendations": data["pesticide_recommendations"],
        "timestamp": datetime.utcnow()
    }).inserted_id
    return jsonify({"message": "Log saved successfully!", "log_id": str(log_id)})

# Get Farmer Logs by User ID
@app.route("/farmer_logs/<farmer_id>", methods=["GET"])
def get_farmer_logs(farmer_id):
    logs = list(mongo.db.farmer_logs.find({"farmer_id": farmer_id}))
    for log in logs:
        log["_id"] = str(log["_id"])
    return jsonify(logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
