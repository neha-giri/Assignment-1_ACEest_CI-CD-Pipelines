"""ACEest Fitness & Gym - Flask service (converted from the Tkinter versions)."""
from flask import Flask, jsonify, request

app = Flask(__name__)

PROGRAMS = {
    "FL": {
        "name": "Fat Loss (FL)",
        "workout": "Mon: 5x5 Back Squat + AMRAP | Tue: EMOM 20min Assault Bike | "
                   "Wed: Bench Press + 21-15-9 | Thu: 10RFT Deadlifts/Box Jumps | "
                   "Fri: 30min Active Recovery",
        "diet": "B: Egg Whites + Oats Idli | L: Grilled Chicken + Brown Rice | "
                "D: Fish Curry + Millet Roti",
        "calorie_factor": 22,
    },
    "MG": {
        "name": "Muscle Gain (MG)",
        "workout": "Mon: Squat 5x5 | Tue: Bench 5x5 | Wed: Deadlift 4x6 | "
                   "Thu: Front Squat 4x8 | Fri: Incline Press 4x10 | Sat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats | L: Chicken Biryani | D: Mutton Curry + Jeera Rice",
        "calorie_factor": 35,
    },
    "BG": {
        "name": "Beginner (BG)",
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups. Focus: Technique & Form",
        "diet": "Balanced Meals: Idli-Sambar, Rice-Dal, Chapati. Protein: 120g/day",
        "calorie_factor": 26,
    },
}

clients = {}  # in-memory store: name -> client dict


def calculate_calories(weight, program_code):
    """Estimated daily calories = weight (kg) * program calorie factor."""
    if program_code not in PROGRAMS:
        raise ValueError("Unknown program")
    if weight <= 0:
        raise ValueError("Weight must be positive")
    return int(weight * PROGRAMS[program_code]["calorie_factor"])


@app.route("/")
def home():
    return jsonify({"service": "ACEest Fitness & Gym", "status": "running"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/programs")
def list_programs():
    return jsonify({code: p["name"] for code, p in PROGRAMS.items()})


@app.route("/programs/<code>")
def get_program(code):
    program = PROGRAMS.get(code.upper())
    if not program:
        return jsonify({"error": "Program not found"}), 404
    return jsonify(program)


@app.route("/calories", methods=["POST"])
def calories():
    data = request.get_json(silent=True) or {}
    try:
        value = calculate_calories(float(data.get("weight", 0)),
                                   str(data.get("program", "")).upper())
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"calories": value})


@app.route("/clients", methods=["GET"])
def list_clients():
    return jsonify(list(clients.values()))


@app.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    program = str(data.get("program", "")).upper()
    if not name or program not in PROGRAMS:
        return jsonify({"error": "Valid name and program are required"}), 400
    try:
        age = int(data.get("age", 0))
        weight = float(data.get("weight", 0))
        adherence = int(data.get("adherence", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "age, weight, adherence must be numbers"}), 400
    if not 0 <= adherence <= 100:
        return jsonify({"error": "Adherence must be between 0 and 100"}), 400
    if name in clients:
        return jsonify({"error": "Client already exists"}), 409
    client = {
        "name": name, "age": age, "weight": weight, "program": program,
        "adherence": adherence,
        "calories": calculate_calories(weight, program) if weight > 0 else None,
    }
    clients[name] = client
    return jsonify(client), 201


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    client = clients.get(name)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(client)


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    if clients.pop(name, None) is None:
        return jsonify({"error": "Client not found"}), 404
    return jsonify({"message": "Client deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
