from flask import Flask, request, jsonify, render_template
import base64
import requests
import os
import json

app = Flask(__name__)

PLANT_ID_API_KEY = "Ge8F5JMobZg40zvRPHBiXpcMoJHF61OAwM8ot0QzhogNFLx9UG"
PLANT_ID_URL = "https://plant.id/api/v3/identification"

UPLOAD_FOLDER = "static/uploads"
RESULTS_FILE = "diagnosis_results.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    items = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)
    return render_template("index.html", items=items)

@app.route("/diagnose", methods=["POST"])
def diagnose():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    existing_files = os.listdir(UPLOAD_FOLDER)
    image_numbers = [int(f.split('.')[0]) for f in existing_files if f.endswith('.jpg') and f.split('.')[0].isdigit()]
    next_number = max(image_numbers) + 1 if image_numbers else 1

    filename = f"{next_number}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    with open(filepath, "rb") as img_file:
        image_data = base64.b64encode(img_file.read()).decode("utf-8")

    payload = {
        "images": [image_data],
        "health": "auto",
        "symptoms": True,
    }

    headers = {
        "Content-Type": "application/json",
        "Api-Key": PLANT_ID_API_KEY
    }

    response = requests.post(PLANT_ID_URL, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        print("🛑 Response Error:", response.status_code, response.text)
        return jsonify({"error": "API failed", "status": response.status_code}), 500

    result = response.json()

    # 🟢 استخراج أعلى مرض
    suggestions = result.get("result", {}).get("disease", {}).get("suggestions", [])
    disease_name = suggestions[0].get("name", "غير محدد") if suggestions else "غير محدد"
    probability = round(suggestions[0].get("probability", 0) * 100, 1) if suggestions else 0

    # 🟢 استخراج أعلى عرض
    symptoms = result.get("result", {}).get("symptom", {}).get("suggestions", [])
    if symptoms:
        top_symptom = max(symptoms, key=lambda s: s.get("score", 0))
        symptom_name = top_symptom.get("name", "غير معروف")
        symptom_score = round(top_symptom.get("score", 0) * 100, 1)
    else:
        symptom_name = "لا يوجد"
        symptom_score = 0

    # 📝 حفظ البيانات
    diagnosis = {
        "image": filename,
        "disease": disease_name,
        "probability": probability,
        "symptom": symptom_name,
        "symptom_score": symptom_score
    }

    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)

    with open(RESULTS_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(diagnosis)
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
