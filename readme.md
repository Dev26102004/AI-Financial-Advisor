💼 AI-Powered Financial Advisor

This project is an AI-driven personal financial assistant that helps users analyze income, expenses, and investments to provide actionable insights and portfolio advice.

It uses Flask for backend processing, Streamlit for visualization, and Ollama (Llama3) as the local LLM model to generate smart investment recommendations.

🧩 Features

✅ Collects user financial inputs (income, expenses, goals, risk level)\n
✅ Runs Monte Carlo simulations for investment projection
✅ Provides AI-generated financial advice via backend Server & Llama3
✅ Shows interactive charts using Matplotlib
✅ Stores session data in MySQL database
✅ Clean and modern Streamlit dashboard

🏗️ Tech Stack

Frontend: Streamlit

Backend: Flask 

AI Model: Llama3 via Ollama

Database: MySQL Workbench

Libraries: NumPy, Matplotlib, Requests

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/Dev26102004/AI-Financial-Advisor.git
cd AI-Financial-Advisor

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Set Up MySQL Database

Open MySQL Workbench

Create a database:

CREATE DATABASE financial_advisor;


Create a table:

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


Update your MySQL credentials in config.py.

4️⃣ Start Backend Server (Flask)
python backend_server.py

5️⃣ Run Streamlit Frontend
streamlit run app.py

6️⃣ Make sure Ollama is running
ollama serve


Check Ollama is running at http://127.0.0.1:11434

📊 Outputs

Personalized financial advice

Suggested portfolio pie charts

Savings vs expenses visualization
