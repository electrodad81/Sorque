"""
LLM client stub for Sorque.

All calls to language models are routed through this module. During
development and testing this stub returns a canned string that begins
with ``LLM stub`` so that callers can detect and fallback to static
content. To integrate a real model, replace the implementation of
``complete`` with a call to OpenAI's chat completion API or another
provider. Remember to pass appropriate system prompts and user
messages and to handle JSON output if needed.
"""

# Example shape:
# from openai import OpenAI
# client = OpenAI()
# def complete(prompt: str) -> str:
#     response = client.chat.completions.create(...)
#     return response.choices[0].message.content


def complete(prompt: str) -> str:
    """Return a placeholder response from the LLM.

    The prefix 'LLM stub' is intentionally added so that callers can
    detect when a real model is not configured and provide fallback
    content instead.
    """
    return "LLM stub: replace with real completion."