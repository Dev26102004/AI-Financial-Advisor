import streamlit as st
import requests
import matplotlib.pyplot as plt
import time
import re
import numpy as np

MCP_URL = "http://127.0.0.1:5000"

# ----------------------------
def check_mcp_server():
    try:
        res = requests.get(f"{MCP_URL}/get_sessions?limit=1")
        return res.status_code == 200
    except:
        return False

st.set_page_config(page_title="AI Financial Advisor", layout="wide")
st.title("💼 AI Financial Advisor")

if check_mcp_server():
    st.success("✅ Connected to MCP Server")
else:
    st.error("❌ Cannot connect to MCP Server. Make sure MCP is running at 127.0.0.1:5000")
    st.stop()

# ---------------------------- INPUT SECTION ----------------------------
with st.expander("📝 Enter Your Financial Details", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0)
        expenses = st.number_input("Monthly Expenses (₹)", min_value=0.0, step=1000.0)
        investments_raw = st.text_area("Existing Investments (comma-separated, e.g., Tesla, Infosys)")
        emergency_status = st.selectbox("Emergency Fund Status", ["Not Started", "In Progress", "Completed"])

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
        #show_plot = st.checkbox("Show Monte Carlo Plot", value=True)
        show_llm = st.checkbox("Show LLM Advice", value=True)
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

    with st.spinner("Running Monte Carlo Projections..."):
        try:
            mc_data = requests.post(f"{MCP_URL}/run_projection", json=payload).json()
        except Exception as e:
            st.error(f"Failed to fetch projections: {e}")
            st.stop()

    monthly_savings = income - expenses
    if emergency_status != "Completed":
        monthly_savings -= suggested_monthly_saving
    monthly_investment_capacity = max(0, monthly_savings)

    # ---------------------------- PORTFOLIO PIE ----------------------------
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
    plt.title("💹 Portfolio Allocation (Current)")
    st.pyplot(plt.gcf())

    # ---------------------------- LLM ADVICE ----------------------------
    advice = ""
    if show_llm:
        st.subheader("🧠 Personalized Financial Advice")

        investment_options = {
            "Stocks": "High risk, high return",
            "Equity Mutual Funds": "Medium-High risk, long-term growth",
            "Debt Mutual Funds": "Low-Medium risk, stable returns",
            "Liquid Funds": "Very low risk, highly liquid",
            "Fixed Deposits": "Low risk, fixed returns",
        }

        prompt_text = f"""
        You are a financial advisor AI. Based on the user's financial data below, provide actionable advice and a suggested portfolio allocation:

        User Data:
        - Monthly Income: ₹{income}
        - Monthly Expenses: ₹{expenses}
        - Monthly Investment Capacity: ₹{monthly_investment_capacity}
        - Risk Tolerance: {risk}
        - Investment Horizon: {years} years
        - Existing Investments: {', '.join(investments) if investments else 'None'}
        - Emergency Fund Status: {emergency_status} (Completed ₹{emergency_completed_amount} / Goal ₹{emergency_goal})
        - Suggested Monthly Emergency Fund Saving: ₹{suggested_monthly_saving:.0f}

        Available Investment Options: {investment_options}

        Tasks:
        1. Advise how to complete the emergency fund in 12 months.
        2. Suggest a diversified portfolio allocation (percentages for Stocks, Equity MFs, Debt MFs, Liquid Funds, FDs) based on user's capacity, risk, and horizon.
        3. Provide monthly investment amounts for each instrument after reserving emergency fund contribution.
        4. Provide tips to maximize savings and reduce unnecessary expenses.

        Format the advice clearly with steps, percentages, and monthly amounts.
        """

        summary = {
            "income": income,
            "expenses": expenses,
            "investments": investments,
            "mc_projection": mc_data,
            "allocation": allocation,
            "prompt": prompt_text,
        }

        with st.spinner("Generating LLM advice..."):
            try:
                advice_response = requests.post(f"{MCP_URL}/generate_advice", json=summary).json()
                advice = advice_response.get("advice", "No advice returned.")
                st.markdown(advice)
            except Exception as e:
                st.error(f"Failed to get LLM advice: {e}")

    # ---------------------------- FIXED ALLOCATION EXTRACTION ----------------------------
    st.subheader("📊 Suggested Portfolio Allocation (Based on LLM Advice)")

    def extract_allocations_from_text(text):
        # Handles formats like “Debt Mutual Funds: 30% (₹14250)” or “Stocks - 40%”
        pattern = r"([A-Za-z ]+)[\:\-]\s*(\d{1,2})\s*%[^\n]*"
        matches = re.findall(pattern, text)
        allocations = {}
        for name, percent in matches:
            clean_name = name.strip()
            if clean_name.lower() not in ["rule", "tips", "step", "emergency fund", "expenses"]:
                allocations[clean_name] = float(percent)
        return allocations

    suggested_alloc = extract_allocations_from_text(advice)

    if suggested_alloc:
        total = sum(suggested_alloc.values())
        if total > 0:
            suggested_alloc = {k: (v / total) * 100 for k, v in suggested_alloc.items()}
        plt.figure(figsize=(6, 6))
        plt.pie(suggested_alloc.values(), labels=suggested_alloc.keys(), autopct='%1.1f%%', startangle=90, shadow=True)
        plt.title("💼 Suggested Investment Portfolio")
        st.pyplot(plt.gcf())
    else:
        st.warning("⚠ Could not extract valid investment allocation percentages from model advice. Showing default allocation.")
        default_alloc = {"Stocks": 30, "Equity Mutual Funds": 25, "Debt Mutual Funds": 20, "Liquid Funds": 15, "Fixed Deposits": 10}
        plt.figure(figsize=(6, 6))
        plt.pie(default_alloc.values(), labels=default_alloc.keys(), autopct='%1.1f%%', startangle=90, shadow=True)
        plt.title("💼 Default Investment Portfolio")
        st.pyplot(plt.gcf())

    # ---------------------------- SAVE SESSION ----------------------------
    if save_session_flag:
        st.subheader("💾 Save This Session")
        session_data = {"timestamp": int(time.time()), "input": payload, "summary": summary, "llm_reply": advice}
        try:
            status = requests.post(f"{MCP_URL}/store_session", json=session_data).json()
            if status.get("status") == "success":
                st.success("Session saved successfully! ✅")
            else:
                st.warning(f"Could not save session: {status.get('message')}")
        except Exception as e:
            st.error(f"Failed to save session: {e}")
