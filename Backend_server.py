from flask import Flask, request, jsonify
import json, numpy as np, mysql.connector
from datetime import datetime
from config import DB_CONFIG
from llm_agent import ask_llm

app = Flask(__name__)

# ---------------------------- DB CONNECTION ----------------------------
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------------------------- MONTE CARLO PROJECTION ----------------------------
@app.route("/run_projection", methods=["POST"])
def run_projection():
    data = request.get_json()
    income = data.get("income", 0)
    expenses = data.get("expenses", 0)
    years = int(data.get("years", 10))
    risk = data.get("risk", "medium")

    risk_params = {
        "low": {"return": 0.05, "volatility": 0.05},
        "medium": {"return": 0.08, "volatility": 0.10},
        "high": {"return": 0.12, "volatility": 0.18}
    }
    params = risk_params.get(risk, risk_params["medium"])

    np.random.seed(42)
    n_simulations = 500
    projections = []
    for _ in range(n_simulations):
        yearly_returns = np.random.normal(params["return"], params["volatility"], years)
        growth = np.cumprod(1 + yearly_returns)
        projections.append(growth.tolist())

    return jsonify({
        "mc_projection": projections,
        "expected_return": params["return"],
        "volatility": params["volatility"]
    })

# ---------------------------- LLM ADVICE ----------------------------
@app.route("/generate_advice", methods=["POST"])
def generate_advice_endpoint():
    summary = request.get_json()
    prompt = summary.get("prompt", str(summary))
    try:
        advice_text = ask_llm(prompt)
        return jsonify({"advice": advice_text})
    except Exception as e:
        return jsonify({"advice": f"Error generating advice: {e}"})

# ---------------------------- STORE SESSION ----------------------------
@app.route("/store_session", methods=["POST"])
def store_session_endpoint():
    session = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO sessions 
        (Time_stamp, Income, Expenses, Investments, Risk, Projection_years, 
         Monthly_savings, Allocation, Simple_projection, Mc_projection, Llm_reply)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        income = session["input"].get("income", 0)
        expenses = session["input"].get("expenses", 0)
        investments = json.dumps(session["input"].get("investments", []))
        risk = session["input"].get("risk", "medium")
        projection_years = session["input"].get("years", 10)
        monthly_savings = income - expenses
        allocation = json.dumps(session["summary"].get("allocation", {}))
        simple_projection = 0
        mc_projection = json.dumps(session["summary"].get("mc_projection", {}))
        llm_reply = session.get("llm_reply", "")

        cursor.execute(
            query,
            (
                datetime.now(),
                income,
                expenses,
                investments,
                risk,
                projection_years,
                monthly_savings,
                allocation,
                simple_projection,
                mc_projection,
                llm_reply,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)})

# ---------------------------- GET SESSIONS ----------------------------
@app.route("/get_sessions", methods=["GET"])
def get_sessions_endpoint():
    limit = int(request.args.get("limit", 5))
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM sessions ORDER BY ID DESC LIMIT {limit}")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)})

# ---------------------------- RUN SERVER ----------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
