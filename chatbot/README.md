# Math Chatbot

A retrieval-based chatbot that answers calculus questions.

## What it can help with

- **Derivative rules:** power rule, chain rule, product rule, quotient rule
- **Trig derivatives:** sin, cos, tan and their derivatives
- **Exponential & log:** derivatives of e^x and ln(x)
- **Integration:** by parts, u-substitution, definite vs indefinite
- **Limits:** definition, L'Hôpital's rule, indeterminate forms
- **Other:** implicit differentiation, partial derivatives, the +C constant

## How it works

Uses TF-IDF vectorization to match user questions against predefined intents. When a question comes in:

1. Preprocess the text (lowercase, remove punctuation)
2. Convert to TF-IDF vector
3. Find the most similar pattern using cosine similarity
4. Return a random response from that intent

If the question doesn't match any math topic, the bot politely redirects to calculus topics.

## Files

- `math_chat.py` - The chatbot class and API
- `data/math_intents.json` - Question patterns and responses

## Usage

```python
from chatbot.math_chat import chatbot_response

answer = chatbot_response("what is the chain rule")
```
