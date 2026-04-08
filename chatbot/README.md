# Math Step Helper Chatbot

An AI-powered chatbot that helps students understand calculus solution steps. Uses **Groq's free API** to run open-source LLMs (Llama 3.1) with extremely fast inference.

## Features

- **Free Tier**: 30 requests/minute, no credit card needed
- **Open Source Models**: Llama 3.1, Mixtral, Gemma
- **Step-aware**: Receives the current solution steps as context
- **Calculus-focused**: Only answers calculus-related questions
- **Teaching-focused**: Explains concepts without giving direct answers
- **Conversation memory**: Remembers previous messages in the chat
- **LaTeX support**: Responds with mathematical notation

## Setup

1. **Get a free API key** at https://console.groq.com/keys

2. **Create a `.env` file** in the project root:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

3. **Restart the server**

Optional environment variables:
- `GROQ_MODEL` - Model to use (default: `llama-3.1-8b-instant`)

## Supported Models

All free on Groq:
- `llama-3.1-8b-instant` - Fast, good for most questions (default)
- `llama-3.3-70b-versatile` - More capable, slightly slower  
- `mixtral-8x7b-32768` - Great reasoning ability
- `gemma2-9b-it` - Good balance of speed and quality

## Usage

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

## How It Works

The chatbot is designed to be a helpful tutor, not a calculator:

1. **Receives context**: Gets the current solution steps being displayed
2. **Understands the question**: Uses Llama 3.1 to understand what the student is asking
3. **Explains concepts**: Provides explanations of rules and techniques
4. **Never calculates**: Won't solve problems directly - encourages learning

## Topics It Can Help With

**Derivative Rules**
- Power, chain, product, quotient rules
- Trig derivatives (sin, cos, tan, sec, csc, cot)
- Inverse trig and hyperbolic derivatives
- Exponential and logarithmic differentiation

**Integration Techniques**
- U-substitution, integration by parts
- Trig substitution, partial fractions
- Inverse hyperbolic integrals

**Limits**
- Direct substitution, factoring
- L'Hôpital's rule, rationalization
- Special limits (sin(x)/x, etc.)

**General Calculus Concepts**
- Continuity, differentiability
- Fundamental Theorem of Calculus
- Applications and word problems

## Files

- `llm_chat.py` - LLM chatbot using Groq API
