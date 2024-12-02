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

#expose port 8000 for running the app
EXPOSE 8000

# Starte die Anwendung mit uvicorn
CMD ["uvicorn", "main:app", "--host=0.0.0.0"]
