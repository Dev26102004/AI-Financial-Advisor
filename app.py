import streamlit as st
import requests
import matplotlib.pyplot as plt
import time
import re
import numpy as np

# ----------------------------
BACKEND_URL = "http://127.0.0.1:5000"

def check_backend_server():
    try:
        res = requests.get(f"{BACKEND_URL}/get_sessions?limit=1")
        return res.status_code == 200
    except:
        return False

# ----------------------------
st.set_page_config(page_title="AI Financial Advisor", layout="wide")
st.title("💼 AI Financial Advisor")

if check_backend_server():
    st.success("✅ Connected to Backend Server")
else:
    st.error("❌ Cannot connect to Backend Server. Make sure Flask server is running.")
    st.stop()

# ---------------------------- INPUT SECTION ----------------------------
with st.expander("📝 Enter Your Financial Details", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        income = st.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0)
        expenses = st.number_input("Monthly Expenses (₹)", min_value=0.0, step=1000.0)
        investments_raw = st.text_area("Existing Investments (comma-separated, e.g., Tesla, Infosys)")
        emergency_status = st.selectbox("Emergency Fund Status", ["Not Started", "In Progress", "Completed"])

        # Emergency fund logic
        if emergency_status == "Not Started":
            emergency_goal = 6 * expenses
            emergency_completed_amount = 0
            suggested_monthly_saving = emergency_goal / 12
            st.info(f"⚠ Emergency Fund Goal: ₹{emergency_goal} | Suggested Monthly Saving: ₹{suggested_monthly_saving:.0f}")

        elif emergency_status == "In Progress":
            emergency_goal = st.number_input("Emergency Fund Goal (₹)", min_value=0.0, step=1000.0, value=6 * expenses)
            emergency_completed_amount = st.number_input("Amount Completed (₹)", min_value=0.0, step=1000.0)
            remaining_amount = max(0, emergency_goal - emergency_completed_amount)
            suggested_monthly_saving = remaining_amount / 12
            st.info(f"⚠ Suggested Monthly Saving to complete in 12 months: ₹{suggested_monthly_saving:.0f}")

        else:
            emergency_goal = st.number_input("Emergency Fund Goal (₹)", min_value=0.0, step=1000.0, value=6 * expenses)
            emergency_completed_amount = emergency_goal
            suggested_monthly_saving = 0

    with col2:
        risk = st.selectbox("Risk Tolerance", ["low", "medium", "high"])
        years = st.slider("Projection Horizon (Years)", min_value=1, max_value=30, value=10)
        show_llm = st.checkbox("Show AI Advice", value=True)
        save_session_flag = st.checkbox("Save This Session", value=True)

    investments = [x.strip() for x in investments_raw.split(",") if x.strip()]

# ---------------------------- MAIN ACTION ----------------------------
if st.button("🚀 Run Financial Analysis"):

    payload = {
        "income": income,
        "expenses": expenses,
        "risk": risk,
        "years": years,
        "investments": investments,
        "emergency_goal": emergency_goal,
        "emergency_status": emergency_status,
        "emergency_completed_amount": emergency_completed_amount,
    }

    # ---------------------------- MONTE CARLO CALL ----------------------------
    with st.spinner("Running Financial Projections..."):
        try:
            mc_data = requests.post(f"{BACKEND_URL}/run_projection", json=payload).json()
        except Exception as e:
            st.error(f"Failed to fetch projections: {e}")
            st.stop()

    # ---------------------------- MONTE CARLO GRAPH ----------------------------
    projections = mc_data["mc_projection"]

    st.subheader("📈 Monte Carlo Simulation (Future Scenarios)")

    plt.figure(figsize=(8, 5))

    # Plot only first 50 simulations for clarity
    for path in projections[:50]:
        plt.plot(path, alpha=0.3)

    plt.title("Monte Carlo Simulation")
    plt.xlabel("Years")
    plt.ylabel("Growth")
    st.pyplot(plt.gcf())

    # ---------------------------- SAVINGS ----------------------------
    monthly_savings = income - expenses
    if emergency_status != "Completed":
        monthly_savings -= suggested_monthly_saving

    monthly_investment_capacity = max(0, monthly_savings)

    st.write(f"💰 Monthly Investment Capacity: ₹{monthly_investment_capacity:.0f}")

    # ---------------------------- CURRENT PORTFOLIO ----------------------------
    allocation = {}

    if investments:
        equal_weight = 1.0 / len(investments)
        for inv in investments:
            allocation[inv] = equal_weight

    if emergency_status != "Completed" and emergency_completed_amount < emergency_goal:
        emergency_weight = suggested_monthly_saving / income if income > 0 else 0
        allocation["Emergency Fund"] = emergency_weight

    total_weight = sum(allocation.values())
    if total_weight > 0:
        allocation = {k: v / total_weight for k, v in allocation.items()}

    plt.figure(figsize=(6, 6))
    plt.pie(allocation.values(), labels=allocation.keys(), autopct='%1.1f%%', startangle=90)
    plt.title("💹 Current Portfolio Allocation")
    st.pyplot(plt.gcf())

    # ---------------------------- AI ADVICE ----------------------------
    advice = ""

    if show_llm:
        st.subheader("🧠 Personalized Financial Advice")

        prompt_text = f"""
        You are a financial advisor AI.

        Income: ₹{income}
        Expenses: ₹{expenses}
        Investment Capacity: ₹{monthly_investment_capacity}
        Risk: {risk}
        Years: {years}
        Investments: {investments}
        Emergency Fund: {emergency_status}

        Suggest:
        1. Portfolio allocation (percentages)
        2. Monthly investment plan
        3. Saving tips
        """

        summary = {
            "income": income,
            "expenses": expenses,
            "investments": investments,
            "mc_projection": mc_data,
            "allocation": allocation,
            "prompt": prompt_text,
        }

        with st.spinner("Generating AI advice..."):
            try:
                response = requests.post(f"{BACKEND_URL}/generate_advice", json=summary).json()
                advice = response.get("advice", "No advice returned")
                st.markdown(advice)
            except Exception as e:
                st.error(f"LLM Error: {e}")

    # ---------------------------- EXTRACT ALLOCATION ----------------------------
    def extract_allocations(text):
        pattern = r"([A-Za-z ]+)[\:\-]\s*(\d{1,2})\s*%"
        matches = re.findall(pattern, text)

        result = {}
        for name, percent in matches:
            result[name.strip()] = float(percent)

        return result

    suggested_alloc = extract_allocations(advice)

    st.subheader("📊 Suggested Portfolio")

    if suggested_alloc:
        total = sum(suggested_alloc.values())
        suggested_alloc = {k: (v / total) * 100 for k, v in suggested_alloc.items()}

        plt.figure(figsize=(6, 6))
        plt.pie(suggested_alloc.values(), labels=suggested_alloc.keys(), autopct='%1.1f%%')
        plt.title("💼 AI Suggested Portfolio")
        st.pyplot(plt.gcf())

    # ---------------------------- SAVE SESSION ----------------------------
    if save_session_flag:
        session_data = {
            "timestamp": int(time.time()),
            "input": payload,
            "summary": summary,
            "llm_reply": advice
        }

        try:
            requests.post(f"{BACKEND_URL}/store_session", json=session_data)
            st.success("Session saved successfully!")
        except:
            st.error("Failed to save session")
