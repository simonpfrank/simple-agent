"""Test script for LiteLLM Azure OpenAI authentication.

This script tests direct LiteLLM usage with Azure OpenAI to isolate
authentication issues before integrating with smolagents.

Based on:
- https://docs.litellm.ai/docs/providers/azure
- https://github.com/BerriAI/litellm/issues/4859
- https://stackoverflow.com/questions/79538205/connecting-azureopenai-via-litellm-returning-authentication-error-401

Run: python utils/test_litellm_azure.py
"""

import os
import sys
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Test configuration
AZURE_ENDPOINT = "https://api.lab.ai.wtwco.com/"
DEPLOYMENT_NAME = "gpt-4o-mini"
API_VERSION = "2024-02-01"  # Correct API version from column-matcher


def test_1_basic_litellm_azure():
    """Test 1: Basic LiteLLM Azure OpenAI with azure_ad_token_provider."""
    print("\n" + "="*80)
    print("TEST 1: LiteLLM with azure_ad_token_provider")
    print("="*80)
    
    try:
        import litellm
        
        # Enable verbose logging
        litellm.set_verbose = True
        
        print(f"LiteLLM version: {litellm.__version__}")
        print(f"Azure endpoint: {AZURE_ENDPOINT}")
        print(f"Deployment: {DEPLOYMENT_NAME}")
        print(f"API version: {API_VERSION}")
        print()
        
        # Create token provider
        print("Creating Azure AD token provider...")
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential,
            f"{AZURE_ENDPOINT}/.default"
        )
        print(f"Token provider created: {token_provider}")
        print(f"Token provider callable: {callable(token_provider)}")
        print()
        
        # Try to get a token
        print("Getting token from provider...")
        token = token_provider()
        print(f"Token received: {token[:50]}..." if token else "No token")
        print()
        
        # Test LiteLLM completion
        print("Calling LiteLLM completion...")
        response = litellm.completion(
            model=f"azure/{DEPLOYMENT_NAME}",
            api_base=AZURE_ENDPOINT,
            api_version=API_VERSION,
            azure_ad_token_provider=token_provider,
            messages=[{"role": "user", "content": "Say 'test successful' in 2 words"}],
            max_tokens=10,
        )
        
        print("\n✅ SUCCESS!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_static_token():
    """Test 2: LiteLLM with static azure_ad_token (not provider)."""
    print("\n" + "="*80)
    print("TEST 2: LiteLLM with static azure_ad_token")
    print("="*80)
    
    try:
        import litellm
        
        print("Creating token...")
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential,
            f"{AZURE_ENDPOINT}/.default"
        )
        token = token_provider()
        print(f"Token: {token[:50]}...")
        print()
        
        print("Calling LiteLLM with static token...")
        response = litellm.completion(
            model=f"azure/{DEPLOYMENT_NAME}",
            api_base=AZURE_ENDPOINT,
            api_version=API_VERSION,
            azure_ad_token=token,  # Static token, not provider
            messages=[{"role": "user", "content": "Say 'test successful' in 2 words"}],
            max_tokens=10,
        )
        
        print("\n✅ SUCCESS!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"Error: {e}")
        return False


def test_3_check_deployment():
    """Test 3: Check if deployment exists and is accessible."""
    print("\n" + "="*80)
    print("TEST 3: Check deployment accessibility")
    print("="*80)
    
    try:
        from azure.identity import DefaultAzureCredential
        import requests
        
        print("Getting Azure AD token...")
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential,
            f"{AZURE_ENDPOINT}/.default"
        )
        token = token_provider()
        
        # Try to list deployments
        print(f"\nQuerying Azure endpoint for deployments...")
        url = f"{AZURE_ENDPOINT}/openai/deployments?api-version={API_VERSION}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            deployments = response.json()
            print(f"\n✅ Successfully listed deployments")
            print(f"Response: {deployments}")
            return True
        else:
            print(f"\n❌ Failed to list deployments")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"Error: {e}")
        return False


def test_4_alternative_model_format():
    """Test 4: Try different model ID formats."""
    print("\n" + "="*80)
    print("TEST 4: Alternative model formats")
    print("="*80)
    
    model_formats = [
        f"azure/{DEPLOYMENT_NAME}",
        DEPLOYMENT_NAME,
        f"azure_openai/{DEPLOYMENT_NAME}",
    ]
    
    try:
        import litellm
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential,
            f"{AZURE_ENDPOINT}/.default"
        )
        
        for model_format in model_formats:
            print(f"\nTrying model format: {model_format}")
            try:
                response = litellm.completion(
                    model=model_format,
                    api_base=AZURE_ENDPOINT,
                    api_version=API_VERSION,
                    azure_ad_token_provider=token_provider,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5,
                )
                print(f"✅ SUCCESS with format: {model_format}")
                return True
            except Exception as e:
                print(f"❌ Failed with {model_format}: {e}")
                continue
        
        return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"Error: {e}")
        return False


def test_5_direct_openai_sdk():
    """Test 5: Direct OpenAI SDK (your working example)."""
    print("\n" + "="*80)
    print("TEST 5: Direct OpenAI SDK (baseline)")
    print("="*80)
    
    try:
        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        
        print("Creating Azure OpenAI client...")
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential,
            f"{AZURE_ENDPOINT}/.default"
        )
        
        client = AzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=API_VERSION,
        )
        
        print(f"Calling deployment: {DEPLOYMENT_NAME}")
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,  # Note: direct deployment name, no azure/ prefix
            messages=[{"role": "user", "content": "Say 'test successful' in 2 words"}],
            max_tokens=10,
        )
        
        print("\n✅ SUCCESS with direct OpenAI SDK!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*80)
    print("LiteLLM Azure OpenAI Authentication Test Suite")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Endpoint: {AZURE_ENDPOINT}")
    print(f"  Deployment: {DEPLOYMENT_NAME}")
    print(f"  API Version: {API_VERSION}")
    
    results = {}
    
    # Run all tests
    results["Test 1: azure_ad_token_provider"] = test_1_basic_litellm_azure()
    results["Test 2: static azure_ad_token"] = test_2_static_token()
    results["Test 3: deployment check"] = test_3_check_deployment()
    results["Test 4: alternative formats"] = test_4_alternative_model_format()
    results["Test 5: direct OpenAI SDK"] = test_5_direct_openai_sdk()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*80)
    total_passed = sum(results.values())
    print(f"Total: {total_passed}/{len(results)} tests passed")
    print("="*80)
    
    sys.exit(0 if total_passed > 0 else 1)
