# config.py

# Ollama Local Configuration
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3:latest"

# Risk-return assumptions
RISK_RETURNS = {
    "low": 0.04,
    "medium": 0.07,
    "high": 0.12
}

# MySQL config
DB_CONFIG = {
    "host": "localhost",
    "user": "your_mysql_username",
    "password": "your_mysql_password",
    "database": "financial_advisor"
}
