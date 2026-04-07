# Calculus Calculator with Chatbot

A Django-based calculus tutor application with an integrated ML-powered chatbot.

## Requirements

- Python 3.9+ (tested with Python 3.12)
- pip

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Download NLTK data** (for WordNetLemmatizer and word_tokenize):
   ```bash
   python chatbot/nltk_packages.py
   ```

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## Tech Stack

- **Backend:** Django 4.2
- **ML/AI:** TensorFlow 2.16, Keras, NLTK
- **Math:** SymPy, NumPy, SciPy
- **Database:** SQLite by default for development; PostgreSQL (psycopg2) as an optional deployment choice


https://user-images.githubusercontent.com/59368349/159202148-65619603-7f24-47d9-bf71-4aedc3883eb4.mov

