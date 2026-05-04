# CaLaun

A Django-based calculus tutor that shows step-by-step solutions for derivatives, integrals, and limits. Includes an AI chatbot powered by Groq's free LLM API.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Features

- **Step-by-step solutions** for derivatives, integrals, and limits
- **AI chatbot sidebar** that explains calculus concepts (powered by Groq/Llama 3.1)
- **Reference page** with common formulas and "try it" links

## Screenshots

The results page shows step-by-step solutions with an AI chatbot sidebar:
- Click any step to expand/collapse details
- Ask the chatbot to explain concepts or clarify steps
- Chatbot is context-aware and sees the current solution

## Requirements

- Python 3.9+ (tested with Python 3.12)
- pip
- (Optional) Groq API key for AI chatbot

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

3. **Set up the AI chatbot (optional but recommended):**
   ```bash
   # Get a free API key at https://console.groq.com/keys
   export GROQ_API_KEY="gsk_your_key_here"
   ```

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

5. **Visit** http://127.0.0.1:8000

## Usage

Enter calculus expressions like:

**Derivatives:**
- `diff(x^5, x)` - Power rule
- `diff(sin(x^2), x)` - Chain rule
- `diff(x^2 * ln(x), x)` - Product rule

**Integrals:**
- `integrate(x^3, x)` - Power rule
- `integrate(x*exp(x), x)` - Integration by parts
- `integrate(1/(x^2 - 1), x)` - Partial fractions

**Limits:**
- `limit(sin(x)/x, x, 0)` - Fundamental trig limit
- `limit((1 + 1/x)^x, x, oo)` - Definition of e
- `limit((x^2 - 4)/(x - 2), x, 2)` - Indeterminate form

## AI Chatbot

The chatbot uses Groq's free API to run Llama 3.1. It:
- Explains calculus concepts and rules
- Understands the current solution steps as context
- Uses proper LaTeX formatting in responses
- Never solves problems directly (encourages learning)

See [chatbot/README.md](chatbot/README.md) for more details.

## Testing

```bash
python manage.py test        # Run all tests (85 tests)
python -m pytest logic/      # Run logic tests only
python -m pytest chatbot/    # Run chatbot tests only
```

## Tech Stack

- **Backend:** Django 4.2
- **Math Engine:** SymPy
- **AI Chatbot:** Groq API (Llama 3.1)
- **Frontend:** Vanilla ES6 JavaScript, MathJax 3, CSS custom properties
- **Database:** SQLite (dev) / PostgreSQL (prod via DATABASE_URL)

## Project Structure

```
├── app/                 # Django app (views, URLs, template tags)
├── chatbot/             # AI chatbot module
│   ├── llm_chat.py      # Groq/Llama chatbot
│   └── README.md        # Chatbot documentation
├── logic/               # Math solving logic
│   ├── diffsteps.py     # Derivative steps
│   ├── intsteps.py      # Integral steps  
│   ├── limitsteps.py    # Limit steps (including exponential forms)
│   └── resultsets.py    # Result card definitions
├── static/
│   ├── css/modern.css   # Modern CSS with custom properties
│   └── js/app.js        # ES6 JavaScript (ChatSidebar, Collapsible)
├── templates/           # HTML5 templates
└── mathtutor/           # Django settings
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Sponsors

If you find this project helpful, consider [sponsoring on GitHub](https://github.com/sponsors)!
