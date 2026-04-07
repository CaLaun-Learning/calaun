# Math Chatbot

A retrieval-based chatbot that only answers calculus questions. Non-math questions are politely deflected.

## Topics Covered (55+ intents)

**Derivative Rules**
- Power, chain, product, quotient, sum, constant multiple
- Trig derivatives (sin, cos, tan, sec, csc, cot)
- Inverse trig derivatives
- Exponential and logarithmic

**Integration Techniques**
- U-substitution, integration by parts
- Trig substitution, partial fractions
- Definite vs indefinite, +C constant

**Limits**
- Definition, L'Hôpital's rule
- Squeeze theorem, one-sided limits
- Limits at infinity, indeterminate forms

**Series & Sequences**
- Geometric, p-series, harmonic
- Ratio test, comparison test
- Taylor/Maclaurin series, power series

**Applications**
- Optimization, critical points
- Related rates, linear approximation
- Area under curve, volume of revolution

**Theorems & Concepts**
- Fundamental Theorem of Calculus
- Mean Value Theorem, Rolle's Theorem
- Continuity, differentiability

## How it works

Uses TF-IDF vectorization to match user questions against predefined intents:

1. Preprocess text (lowercase, remove punctuation)
2. Convert to TF-IDF vector
3. Find most similar pattern using cosine similarity
4. Return a random response from that intent

If confidence is low or question isn't math-related, returns a fallback response.

## Files

- `math_chat.py` - MathChatbot class using scikit-learn
- `data/intents.json` - 55+ intent categories with patterns and responses

## Usage

```python
from chatbot.math_chat import chatbot_response

answer = chatbot_response("what is the chain rule")
# "The chain rule is for composite functions: d/dx[f(g(x))] = f'(g(x)) · g'(x)..."

answer = chatbot_response("what's the weather")
# "I only know about calculus! Try asking about derivatives, integrals, or limits."
```
