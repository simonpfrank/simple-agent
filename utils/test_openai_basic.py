"""Basic OpenAI SDK test for Azure OpenAI.

Minimal test using just the OpenAI package to verify Azure setup.

Run: python utils/test_openai_basic.py
"""

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Configuration
AZURE_ENDPOINT = "https://api.lab.ai.wtwco.com/"  # Added trailing slash
DEPLOYMENT_NAME = "gpt-4o-mini"  # Changed back to gpt-4o-mini (default in column-matcher)
API_VERSION = "2024-02-01"  # Changed to 2024-02-01 (default in column-matcher)

print("="*80)
print("Basic Azure OpenAI Test")
print("="*80)
print(f"Endpoint: {AZURE_ENDPOINT}")
print(f"Deployment: {DEPLOYMENT_NAME}")
print(f"API Version: {API_VERSION}")
print()

# Create token provider
print("Creating Azure AD token provider...")
credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential,
    f"{AZURE_ENDPOINT}/.default"
)
print("✓ Token provider created")
print()

# Create Azure OpenAI client
print("Creating Azure OpenAI client...")
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    azure_ad_token_provider=token_provider,
    api_version=API_VERSION,
)
print("✓ Client created")
print()

# Make a simple request
print(f"Calling deployment '{DEPLOYMENT_NAME}'...")
try:
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "user", "content": "Say 'hello' in one word"}
        ],
        max_tokens=5,
    )
    
    print()
    print("="*80)
    print("✅ SUCCESS!")
    print("="*80)
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.usage.total_tokens}")
    
except Exception as e:
    print()
    print("="*80)
    print("❌ FAILED")
    print("="*80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print()
    import traceback
    traceback.print_exc()
