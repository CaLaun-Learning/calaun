# Math Chatbot

This module contains two chatbot implementations:

1. **TF-IDF Chatbot** (`math_chat.py`) - Fast, retrieval-based for common questions
2. **LLM Step Helper** (`llm_chat.py`) - AI-powered assistant for understanding solution steps

## LLM Step Helper (Ollama)

An AI-powered chatbot that helps students understand calculus solution steps. Uses **Ollama** to run open-source LLMs locally - completely free, no API keys, no data sent to third parties.

### Features

- **100% Free & Private**: Runs locally using open-source models
- **Step-aware**: Receives the current solution steps as context
- **Calculus-focused**: Only answers calculus-related questions
- **Conversation memory**: Remembers previous messages in the chat
- **LaTeX support**: Responds with mathematical notation

### Setup

1. **Install Ollama** (free, open-source):
   ```bash
   # macOS
   brew install ollama
   
   # Or download from https://ollama.com/download
   ```

2. **Pull a model** (Llama 3.2 recommended):
   ```bash
   ollama pull llama3.2
   ```

3. **Start the server**:
   ```bash
   ollama serve
   ```

Optional environment variables:
- `OLLAMA_URL` - Server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL` - Model to use (default: `llama3.2`)

### Supported Models

Any Ollama model works! Some good options for calculus tutoring:
- `llama3.2` - Fast, good for most questions (default)
- `llama3.1` - More capable, slower
- `mistral` - Good balance of speed and quality
- `phi3` - Lightweight, fast responses

### Usage

```python
from chatbot.llm_chat import llm_response

# With solution steps context
steps_html = "<div>Step 1: Apply power rule...</div>"
answer = llm_response("Why do we multiply by 2 here?", steps_html=steps_html)

# With conversation history
history = [
    {"role": "user", "content": "What is a derivative?"},
    {"role": "assistant", "content": "A derivative measures..."}
]
answer = llm_response("Can you give an example?", conversation_history=history)
```

---

## TF-IDF Chatbot (Original)

A retrieval-based chatbot that only answers calculus questions. Non-math questions are politely deflected.

### Topics Covered (55+ intents)

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
