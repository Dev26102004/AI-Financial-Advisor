# 💼 AI-Powered Financial Advisor

This project is an AI-driven personal financial assistant that helps users analyze their income, expenses, and investments to generate actionable financial insights and personalized portfolio recommendations.

The system uses a Flask backend for processing, a Streamlit frontend for visualization, and Ollama (Llama3) to generate intelligent financial advice.

## 🧩 Features

- Collects user financial inputs (income, expenses, investments, risk level)
- Performs Monte Carlo simulations for future investment projections
- Generates AI-based financial advice using LLM
- Displays interactive visualizations using Matplotlib
- Stores user session data in MySQL database
- Provides a clean and intuitive Streamlit dashboard

## 🏗️ Tech Stack

- Frontend: Streamlit
- Backend: Flask
- AI Model: Llama3 via Ollama
- Database: MySQL
- Libraries: NumPy, Matplotlib, Requests

## ⚙️ Installation & Setup

### 1. Clone the Repository
git clone https://github.com/Dev26102004/AI-Financial-Advisor.git
cd AI-Financial-Advisor

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Set Up MySQL Database

CREATE DATABASE financial_advisor;

CREATE TABLE sessions (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Time_stamp DATETIME,
    Income FLOAT,
    Expenses FLOAT,
    Investments TEXT,
    Risk VARCHAR(10),
    Projection_years INT,
    Monthly_savings FLOAT,
    Allocation JSON,
    Simple_projection FLOAT,
    Mc_projection JSON,
    Llm_reply TEXT
);

Update your database credentials in config.py.

### 4. Start Backend Server
python backend.py

### 5. Run Streamlit Frontend
streamlit run app.py

### 6. Start Ollama
ollama serve

## 📊 Outputs

- Monte Carlo simulation graph
- Portfolio allocation charts
- AI-generated financial advice
- Savings insights
- Stored session history
