# Calc Tutor

A Django-based calculus tutor that shows step-by-step solutions for derivatives, integrals, and limits. Includes an AI chatbot for answering calculus questions.

## Features

- **Step-by-step solutions** for derivatives, integrals, and limits
- **AI chatbot** that answers calculus questions
- **Reference page** with common formulas and "try it" links
- **Modern responsive UI** with MathJax 3 for beautiful math rendering

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

3. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

4. **Visit** http://127.0.0.1:8000

## Usage

Enter calculus expressions like:
- `diff(sin(x)*cos(x), x)` - Derivative
- `integrate(x*exp(x), x)` - Integral  
- `limit(sin(x)/x, x, 0)` - Limit

## Testing

```bash
python manage.py test
```

## Tech Stack

- **Backend:** Django 4.2
- **Math Engine:** SymPy
- **Chatbot:** scikit-learn (TF-IDF + cosine similarity)
- **Frontend:** Vanilla ES6 JavaScript, MathJax 3, CSS custom properties
- **Database:** SQLite (dev) / PostgreSQL (prod)

## Project Structure

```
├── app/                 # Django app (views, URLs)
├── chatbot/             # AI chatbot module
│   ├── math_chat.py     # TF-IDF chatbot
│   └── data/intents.json
├── logic/               # Math solving logic
│   ├── diffsteps.py     # Derivative steps
│   ├── intsteps.py      # Integral steps
│   ├── limitsteps.py    # Limit steps
│   └── resultsets.py    # Result card definitions
├── static/              # CSS, JS, images
├── templates/           # HTML templates
└── mathtutor/           # Django settings
```
