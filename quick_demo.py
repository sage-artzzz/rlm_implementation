"""
Quick demo of fast-rlm
Run: uv run python quick_demo.py
"""

import fast_rlm

print("🚀 Running fast-rlm demo...\n")

# Example 1: Simple query
print("Example 1: Simple counting")
print("-" * 50)

result = fast_rlm.run(
    "Count the letter 'r' in: apple, orange, raspberry",
    prefix="demo_simple"
)

print(f"✅ Result: {result['results']}")
print(f"💰 Cost: ${result['usage']['cost']:.6f}")
print(f"📝 Log: {result['log_file']}\n")

# Example 2: With configuration
print("Example 2: With custom configuration")
print("-" * 50)

config = fast_rlm.RLMConfig()
config.primary_agent = "minimax/minimax-m2.5"
config.max_completion_tokens = 1000

result = fast_rlm.run(
    "Generate 5 animal names and count 'a' in each",
    config=config,
    prefix="demo_config"
)

print(f"✅ Result: {result['results']}")
print(f"💰 Cost: ${result['usage']['cost']:.6f}")
print(f"📝 Log: {result['log_file']}\n")

print("🎉 Demo complete! Check the logs/ folder for execution traces.")
print("\n📚 Read HOW_TO_USE.md for more examples!")
