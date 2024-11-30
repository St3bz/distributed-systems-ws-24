# Dockerfile für FastAPI

FROM python:3.12-slim

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Kopiere die requirements.txt
COPY requirements.txt .

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Codes
COPY . .

# Starte die Anwendung mit uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
