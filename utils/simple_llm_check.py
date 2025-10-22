"""
Simple OpenAI API check script.

Uses .env file to load API key and makes a basic LLM call.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file
print("Loading .env file...")
loaded = load_dotenv()
print(f"load_dotenv() returned: {loaded}")

# Get API key from environment
api_key = os.environ.get("OPENAI_API_KEY", "")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment")
    exit(1)

print(f"API Key loaded: {api_key[:10]}...")
print(f"API Key ends with: ...{api_key[-4:]}")
print(f"API Key length: {len(api_key)}")

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Simple prompt
prompt = "Say 'Hello! The API key is working.' in exactly those words."

print("\nSending prompt to OpenAI...")
print(f"Prompt: {prompt}")

# Make API call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=50,
    temperature=0.7
)

# Print response
print("\n" + "="*60)
print("RESPONSE:")
print("="*60)
print(response.choices[0].message.content)
print("="*60)
print("\n✅ OpenAI API is working correctly!")
