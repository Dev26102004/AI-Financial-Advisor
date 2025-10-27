import numpy as np
from config import RISK_RETURNS

def calculate_savings(income, expenses):
    savings = max(income - expenses, 0)
    savings_rate = (savings / income) if income > 0 else 0.0
    return {"savings": savings, "savings_rate": round(savings_rate, 2)}

def recommend_allocation(risk, current_savings, emergency_goal):
    """
    Allocates fully to emergency fund if not completed.
    Otherwise returns base allocation depending on risk.
    """
    base_alloc = {
        "low": {"stocks":0.1, "mutual_funds":0.3, "gold":0.1, "debt_funds":0.3, "fd":0.1, "liquid_fund":0.1},
        "medium": {"stocks":0.3, "mutual_funds":0.3, "gold":0.1, "debt_funds":0.2, "fd":0.05, "liquid_fund":0.05},
        "high": {"stocks":0.5, "mutual_funds":0.2, "gold":0.1, "debt_funds":0.1, "fd":0.05, "liquid_fund":0.05}
    }
    if current_savings < emergency_goal:
        return {"emergency_fund": 1.0}  # prioritize emergency fund
    return base_alloc.get(risk.lower(), base_alloc["medium"])

def future_value_series(monthly_investment, years, annual_return):
    months = years * 12
    monthly_rate = annual_return / 12
    if monthly_rate == 0:
        return monthly_investment * months
    fv = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    return round(fv, 2)

def simulate_projection_series(current_savings, monthly_investment, years, risk, runs=300):
    expected = RISK_RETURNS.get(risk.lower(), 0.07)
    sigma = {"low":0.03, "medium":0.08, "high":0.20}.get(risk.lower(),0.08)
    median_series, p10_series, p90_series = [], [], []

    for year in range(1, years+1):
        totals=[]
        for _ in range(runs):
            value=current_savings
            for _ in range(year*12):
                monthly_r = np.random.normal(expected, sigma)/12
                value = value*(1+monthly_r)+monthly_investment
            totals.append(value)
        totals_sorted = sorted(totals)
        median_series.append(float(np.percentile(totals_sorted,50)))
        p10_series.append(float(np.percentile(totals_sorted,10)))
        p90_series.append(float(np.percentile(totals_sorted,90)))

    return {"median":median_series,"p10":p10_series,"p90":p90_series,"expected_return_rate":expected}

def summarize_finance(income, expenses, investments, risk, goal_years, emergency_goal=0, emergency_completed_amount=0):
    calc = calculate_savings(income, expenses)
    monthly_savings = calc["savings"]

    # Emergency Fund Status
    if emergency_completed_amount >= emergency_goal:
        emergency_completed = True
    else:
        emergency_completed = False

    allocation = recommend_allocation(risk, current_savings=monthly_savings + emergency_completed_amount, emergency_goal=emergency_goal)

    annual_return = RISK_RETURNS.get(risk.lower(),0.07)
    fv = future_value_series(monthly_savings, goal_years, annual_return)
    mc_projection = simulate_projection_series(0, monthly_savings, goal_years, risk)

    return {
        "income": income,
        "expenses": expenses,
        "monthly_savings": monthly_savings,
        "savings_rate": calc["savings_rate"],
        "allocation": allocation,
        "simple_projection_fv": fv,
        "mc_projection": mc_projection,
        "annual_return_used": annual_return,
        "investments_list": investments,
        "emergency_goal": emergency_goal,
        "emergency_completed": emergency_completed,
        "emergency_completed_amount": emergency_completed_amount
    }
