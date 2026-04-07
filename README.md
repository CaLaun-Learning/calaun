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

## Testing

Run all tests:
```bash
python manage.py test
```

Or run specific test modules with pytest:
```bash
python -m pytest logic/tests.py -v
```

## Tech Stack

- **Backend:** Django 4.2
- **ML/AI:** TensorFlow 2.15–2.16, Keras, NLTK
- **Math:** SymPy, NumPy, SciPy
- **Database:** SQLite by default for development; PostgreSQL (psycopg2) as an optional deployment choice

## Demo

https://user-images.githubusercontent.com/59368349/159202148-65619603-7f24-47d9-bf71-4aedc3883eb4.mov

---

## Changelog

### Branch: `math-chatbot`
Replaces the neural network chatbot with a simpler TF-IDF retrieval-based system.

- **New:** `chatbot/math_chat.py` - MathChatbot class using TF-IDF + cosine similarity
- **New:** `chatbot/data/math_intents.json` - 22 intent categories for calculus Q&A
- Only answers math questions, politely deflects off-topic queries
- Added scikit-learn dependency
- 8 new chatbot tests

### Branch: `redesign-pages`
Redesigns the homepage and reference page for better UX.

- Homepage: hero section with icon, quick examples grid, features, tabbed examples
- Reference: formula sections for derivatives, integrals, limits with "try it" links
- Relaxed, friendly copy throughout
- Removed image-based reference tables

### Branch: `limitsteps`
Adds step-by-step limit evaluation.

- **New:** `logic/limitsteps.py` - LimitPrinter class for step-by-step limit solutions
- Support for direct substitution, factoring, L'Hôpital's rule, limits at infinity
- Added limit cards to result sets
- 9 new limit tests
- Limit examples on homepage

### Branch: `modernize-frontend`
Modernizes the frontend stack.

- HTML5 semantic markup
- MathJax 2 → MathJax 3 migration
- jQuery removed, vanilla ES6 JavaScript
- CSS custom properties, BEM naming
- Responsive layouts, lazy loading
- Improved accessibility

### Fixes (on `modernize-frontend`)
- Fixed MathJax format in stepprinter and intsteps
- Fixed "Show/Hide answer" collapsibles
- Fixed misleading "I don't know the steps" message
- Fixed LaTeX hiding in collapsible steps
