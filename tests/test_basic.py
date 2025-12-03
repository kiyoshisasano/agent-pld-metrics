import sys
import os
import pytest

# ---------------------------------------------------------
# Path Setup: Add the parent directory to sys.path.
# This allows importing 'pld_runtime' without installing the package.
# ---------------------------------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pld_runtime import SimpleObserver

def test_pld_runtime_is_alive():
    """
    [Survival Check]
    Verifies that the library can be imported and the main class initialized.
    If this fails, the installation is broken.
    """
    print("\n💡 Testing PLD Runtime initialization...")
    
    # 1. Create an Observer with an agent name
    observer = SimpleObserver(agent_name="test_agent")
    
    # 2. Assert that the instance is created correctly
    assert observer is not None
    assert observer.agent_name == "test_agent"
    
    print("✅ PLD Runtime is ALIVE and working!")

if __name__ == "__main__":
    # Allow running this file directly via python
    test_pld_runtime_is_alive()
