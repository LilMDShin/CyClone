# Utilise une image Python comme base
FROM python:3.12

# Définit le répertoire de travail
WORKDIR /app

# Copie le fichier requirements.txt et installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code de l'API
COPY . .

# COPY wait-for-db.sh /wait-for-db.sh
# RUN chmod +x /wait-for-db.sh

# CMD ["sh", "/wait-for-db.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8111"]


# Commande pour lancer l'API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8111", "--reload"]
