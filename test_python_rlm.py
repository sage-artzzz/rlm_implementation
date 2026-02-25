"""Test the pure Python RLM implementation."""

import fast_rlm_py

if __name__ == "__main__":
    query = "Generate names of 10 fruits and return a dictionary of each name and the number of r in each fruit."

    config = fast_rlm_py.RLMConfig()
    config.primary_agent = "minimax/minimax-m2.5"
    config.sub_agent = "minimax/minimax-m2.5"
    config.max_completion_tokens = 2000

    data = fast_rlm_py.run(query, config=config, prefix="python_r_count")
    print("\n" + "="*60)
    print("FINAL RESULT:", data.get("results"))
    print("="*60)
    print("Log file:", data.get("log_file"))
    print("Usage:", data.get("usage"))
