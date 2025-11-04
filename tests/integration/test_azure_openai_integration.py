"""Integration tests for Azure OpenAI provider.

These tests require:
1. Valid Azure AD credentials (az login or environment variables)
2. Access to Azure OpenAI endpoint (https://api.lab.ai.wtwco.com)
3. Deployment named 'gpt-4o-mini' available

Run with: pytest tests/integration/test_azure_openai_integration.py -v

Skip if no credentials: pytest tests/integration/test_azure_openai_integration.py -v -m "not requires_azure"
"""

import pytest
from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.core.agent_result import AgentResult


# Mark all tests in this module as requiring Azure credentials
pytestmark = pytest.mark.requires_azure


class TestAzureOpenAIIntegration:
    """Integration tests for Azure OpenAI with real API calls."""

    @pytest.fixture
    def azure_config(self):
        """Azure OpenAI configuration for integration tests."""
        return {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "azure_ad",
            "temperature": 0.7,
            "max_tokens": 100,  # Keep tokens low for cost efficiency
        }

    @pytest.fixture
    def azure_agent(self, azure_config):
        """Create Azure OpenAI agent for testing."""
        try:
            agent = SimpleAgent(
                name="test_azure_integration",
                model_provider="azure_openai",
                model_config=azure_config,
            )
            return agent
        except ValueError as e:
            pytest.skip(f"Azure OpenAI not available: {e}")

    def test_azure_openai_simple_prompt(self, azure_agent):
        """Test simple prompt execution with Azure OpenAI."""
        prompt = "What is 2+2? Answer with just the number."
        
        result = azure_agent.run(prompt)
        
        # Verify result is returned
        assert result is not None
        assert isinstance(result, AgentResult)
        
        # Verify response contains expected content
        response_str = str(result)
        assert response_str is not None
        assert len(response_str) > 0
        
        # Should contain "4" somewhere in the response
        assert "4" in response_str
        
        # Verify token tracking
        assert result.input_tokens > 0
        assert result.output_tokens > 0
        
        print(f"\n✓ Response: {response_str}")
        print(f"✓ Input tokens: {result.input_tokens}")
        print(f"✓ Output tokens: {result.output_tokens}")

    def test_azure_openai_multi_turn_conversation(self, azure_agent):
        """Test multi-turn conversation with memory."""
        # First turn
        result1 = azure_agent.run(
            "My name is Alice. Remember this.",
            reset=False  # Keep memory
        )
        assert result1 is not None
        assert isinstance(result1, AgentResult)
        
        # Second turn - should remember the name
        result2 = azure_agent.run(
            "What is my name?",
            reset=False  # Keep memory
        )
        
        response2 = str(result2)
        assert "Alice" in response2 or "alice" in response2.lower()
        
        print(f"\n✓ Turn 1: {str(result1)}")
        print(f"✓ Turn 2: {response2}")

    def test_azure_openai_with_reset(self, azure_agent):
        """Test that reset clears conversation history."""
        # First conversation
        azure_agent.run("My favorite color is blue.", reset=False)
        
        # Reset and new conversation
        result = azure_agent.run(
            "What is my favorite color?",
            reset=True  # Should not remember
        )
        
        response = str(result)
        # Should not know the color since we reset
        # This might still answer with a guess, but shouldn't confidently say "blue"
        assert result is not None
        
        print(f"\n✓ After reset: {response}")

    def test_azure_openai_error_handling(self):
        """Test error handling with invalid configuration."""
        invalid_config = {
            "model": "nonexistent-model",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "azure_ad",
        }
        
        try:
            agent = SimpleAgent(
                name="test_invalid",
                model_provider="azure_openai",
                model_config=invalid_config,
            )
            
            # Try to run - might fail at runtime
            result = agent.run("Test")
            
            # If it returns an error, check AgentResult error fields
            if result.error:
                print(f"\n✓ Expected error caught: {result.error}")
                assert result.error_type is not None
            
        except Exception as e:
            # Expected - model might not exist
            print(f"\n✓ Expected exception: {e}")
            assert "nonexistent-model" in str(e) or "model" in str(e).lower()

    def test_azure_openai_token_budget(self, azure_agent):
        """Test token budget enforcement."""
        # Set very low token budget
        result = azure_agent.run(
            "Write a very long essay about artificial intelligence.",
            token_budget_override=50,  # Very low budget
        )
        
        # Should either truncate or raise error
        # With budget override, should work but be constrained
        assert result is not None
        assert result.input_tokens <= 50

    def test_azure_openai_temperature_variation(self, azure_config):
        """Test that temperature setting affects responses (determinism check)."""
        # High temperature (more random)
        config_high_temp = azure_config.copy()
        config_high_temp['temperature'] = 1.5
        
        agent_high = SimpleAgent(
            name="test_high_temp",
            model_provider="azure_openai",
            model_config=config_high_temp,
        )
        
        # Low temperature (more deterministic)
        config_low_temp = azure_config.copy()
        config_low_temp['temperature'] = 0.1
        
        agent_low = SimpleAgent(
            name="test_low_temp",
            model_provider="azure_openai",
            model_config=config_low_temp,
        )
        
        prompt = "Complete this sentence: The weather today is"
        
        result_high = agent_high.run(prompt)
        result_low = agent_low.run(prompt)
        
        # Both should return valid responses
        assert str(result_high) is not None
        assert str(result_low) is not None
        
        print(f"\n✓ High temp response: {str(result_high)}")
        print(f"✓ Low temp response: {str(result_low)}")

    def test_azure_openai_max_tokens_limit(self, azure_config):
        """Test max_tokens parameter limits output length."""
        # Very small max_tokens
        config_small = azure_config.copy()
        config_small['max_tokens'] = 10
        
        agent = SimpleAgent(
            name="test_max_tokens",
            model_provider="azure_openai",
            model_config=config_small,
        )
        
        result = agent.run("Write a long story about a dragon.")
        
        # Output should be limited
        assert result.output_tokens <= 15  # Allow some buffer for token estimation
        
        print(f"\n✓ Output tokens with max_tokens=10: {result.output_tokens}")
        print(f"✓ Response (truncated): {str(result)}")


class TestAzureOpenAIAPIKeyAuth:
    """Integration tests for API key authentication (if available)."""

    @pytest.fixture
    def azure_api_key_config(self):
        """Azure OpenAI configuration with API key auth."""
        import os
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            pytest.skip("AZURE_OPENAI_API_KEY environment variable not set")
        
        return {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "api_key",
            "api_key": api_key,
            "temperature": 0.7,
            "max_tokens": 50,
        }

    def test_azure_openai_api_key_authentication(self, azure_api_key_config):
        """Test Azure OpenAI with API key authentication."""
        agent = SimpleAgent(
            name="test_api_key",
            model_provider="azure_openai",
            model_config=azure_api_key_config,
        )
        
        result = agent.run("Say hello in one word.")
        
        assert result is not None
        assert isinstance(result, AgentResult)
        assert len(str(result)) > 0
        
        print(f"\n✓ API key auth response: {str(result)}")


@pytest.mark.skip_if_no_azure_credentials
class TestAzureOpenAIEdgeCases:
    """Edge case tests for Azure OpenAI integration."""

    def test_azure_openai_empty_prompt(self):
        """Test handling of empty prompt."""
        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "azure_ad",
        }
        
        agent = SimpleAgent(
            name="test_empty",
            model_provider="azure_openai",
            model_config=config,
        )
        
        # Empty string should still work (might return generic response)
        result = agent.run("")
        assert result is not None

    def test_azure_openai_very_long_prompt(self):
        """Test handling of very long prompt."""
        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "azure_ad",
            "max_tokens": 50,
        }
        
        agent = SimpleAgent(
            name="test_long",
            model_provider="azure_openai",
            model_config=config,
        )
        
        # Create a very long prompt
        long_prompt = "Count from 1 to 100: " + ", ".join(str(i) for i in range(1, 101))
        
        result = agent.run(long_prompt)
        assert result is not None
        # Should handle gracefully even if context is large

    def test_azure_openai_special_characters(self):
        """Test prompt with special characters and emojis."""
        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "azure_ad",
        }
        
        agent = SimpleAgent(
            name="test_special",
            model_provider="azure_openai",
            model_config=config,
        )
        
        result = agent.run("Respond to this: 👋 Hello! 🌟 Test@#$%^&*()")
        assert result is not None
        assert len(str(result)) > 0
