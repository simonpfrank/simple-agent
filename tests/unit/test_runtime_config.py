"""Unit tests for runtime_config module - TDD approach."""

import concurrent.futures
import threading
import pytest


class TestRuntimeConfig:
    """Test runtime configuration access."""

    def test_runtime_config_module_exists(self):
        """Test that runtime_config module can be imported."""
        from simple_agent.core import runtime_config
        assert runtime_config is not None

    def test_set_and_get_config(self):
        """Test that config can be set and retrieved."""
        from simple_agent.core.runtime_config import set_config, get_config
        
        test_config = {
            "app": {"name": "Test"},
            "verify_certificates": False,
        }
        
        set_config(test_config)
        retrieved = get_config()
        
        assert retrieved == test_config
        assert retrieved["verify_certificates"] is False

    def test_get_config_returns_empty_dict_when_not_set(self):
        """Test that get_config returns empty dict when config not set."""
        from simple_agent.core.runtime_config import get_config, _reset_config
        
        # Reset to ensure clean state
        _reset_config()
        
        config = get_config()
        assert config == {}
        assert isinstance(config, dict)

    def test_set_config_overwrites_previous(self):
        """Test that setting config multiple times overwrites."""
        from simple_agent.core.runtime_config import set_config, get_config
        
        set_config({"value": 1})
        assert get_config()["value"] == 1
        
        set_config({"value": 2})
        assert get_config()["value"] == 2

    def test_get_config_value_with_key(self):
        """Test getting a specific config value by key."""
        from simple_agent.core.runtime_config import set_config, get_config_value
        
        test_config = {
            "verify_certificates": True,
            "debug": {"enabled": False},
        }
        
        set_config(test_config)
        
        assert get_config_value("verify_certificates") is True
        assert get_config_value("debug") == {"enabled": False}

    def test_get_config_value_with_default(self):
        """Test that get_config_value returns default when key missing."""
        from simple_agent.core.runtime_config import set_config, get_config_value
        
        set_config({"some_key": "value"})
        
        result = get_config_value("nonexistent_key", default="default_value")
        assert result == "default_value"

    def test_get_config_value_when_config_not_set(self):
        """Test that get_config_value returns default when config not set."""
        from simple_agent.core.runtime_config import get_config_value, _reset_config
        
        _reset_config()
        
        result = get_config_value("any_key", default="fallback")
        assert result == "fallback"

    def test_config_is_independent_per_test(self):
        """Test that config doesn't leak between test cases."""
        from simple_agent.core.runtime_config import set_config, get_config, _reset_config
        
        _reset_config()
        
        # First usage
        set_config({"test": "value1"})
        assert get_config()["test"] == "value1"
        
        # Reset and verify it's gone
        _reset_config()
        assert get_config() == {}

    def test_set_config_with_none_clears_config(self):
        """Test that setting None clears the config."""
        from simple_agent.core.runtime_config import set_config, get_config
        
        set_config({"some": "data"})
        assert get_config() != {}
        
        set_config(None)
        assert get_config() == {}

    def test_get_config_value_nested_dict_access(self):
        """Test getting nested config values."""
        from simple_agent.core.runtime_config import set_config, get_config_value
        
        test_config = {
            "llm": {
                "provider": "openai",
                "openai": {
                    "model": "gpt-4"
                }
            }
        }
        
        set_config(test_config)
        
        # Get top-level nested dict
        llm_config = get_config_value("llm")
        assert llm_config["provider"] == "openai"

        # Note: For deeper nesting, user needs to chain:
        # config = get_config(); value = config.get("llm", {}).get("openai", {}).get("model")


class TestRuntimeConfigThreadSafety:
    """Test thread-safety of runtime configuration."""

    def test_concurrent_set_and_get_config(self):
        """Test concurrent access to set_config and get_config is thread-safe."""
        from simple_agent.core.runtime_config import set_config, get_config, _reset_config

        _reset_config()
        errors = []
        success_count = {"value": 0}

        def writer(thread_id: int) -> None:
            """Write config with thread ID."""
            try:
                for _ in range(100):
                    set_config({"thread_id": thread_id, "data": "value"})
                    success_count["value"] += 1
            except Exception as e:
                errors.append(f"Writer {thread_id}: {e}")

        def reader(thread_id: int) -> None:
            """Read config repeatedly."""
            try:
                for _ in range(100):
                    config = get_config()
                    # Config should be either empty dict or valid config
                    assert isinstance(config, dict)
                    success_count["value"] += 1
            except Exception as e:
                errors.append(f"Reader {thread_id}: {e}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(5):
                futures.append(executor.submit(writer, i))
                futures.append(executor.submit(reader, i))

            # Wait for all threads to complete
            concurrent.futures.wait(futures)

        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert success_count["value"] > 0, "No operations completed"

    def test_concurrent_get_config_value(self):
        """Test concurrent access to get_config_value is thread-safe."""
        from simple_agent.core.runtime_config import set_config, get_config_value, _reset_config

        _reset_config()
        test_config = {"key1": "value1", "key2": "value2", "key3": 123}
        set_config(test_config)

        errors = []

        def reader(key: str, expected: str) -> None:
            """Read specific config value repeatedly."""
            try:
                for _ in range(100):
                    value = get_config_value(key, default="missing")
                    # Value should be consistent
                    assert value == expected, f"Expected {expected}, got {value}"
            except Exception as e:
                errors.append(f"Reader {key}: {e}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(reader, "key1", "value1"),
                executor.submit(reader, "key1", "value1"),
                executor.submit(reader, "key2", "value2"),
                executor.submit(reader, "key2", "value2"),
                executor.submit(reader, "key3", 123),
                executor.submit(reader, "key3", 123),
            ]
            concurrent.futures.wait(futures)

        assert len(errors) == 0, f"Thread safety errors: {errors}"
