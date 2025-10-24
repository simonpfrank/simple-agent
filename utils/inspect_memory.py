"""
Quick script to inspect SmolAgents memory structure.
"""

import json
from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.agent_manager import AgentManager

# Load config
config = ConfigManager.load("config.yaml")
config = ConfigManager.merge_with_defaults(config)

# Create agent
agent_manager = AgentManager(config)

# Run a couple of prompts
print("Running test prompts...")
agent_manager.run_agent("default", "What is 2+2?")
agent_manager.run_agent("default", "What is the capital of France?")

# Get memory
agent = agent_manager.get_agent("default")
memory_steps = agent.agent.memory.get_full_steps()

print(f"\nTotal memory steps: {len(memory_steps)}")
print("\n" + "=" * 80)

for i, step in enumerate(memory_steps, 1):
    print(f"\nStep {i}:")
    print(f"Keys: {list(step.keys())}")
    print(f"Type: {type(step)}")
    print(f"Content (first 200 chars): {str(step)[:200]}")
    print("-" * 80)

# Save to file for inspection
with open("memory_structure.json", "w") as f:
    json.dump(memory_steps, f, indent=2, default=str)

print("\nSaved full memory to memory_structure.json")
