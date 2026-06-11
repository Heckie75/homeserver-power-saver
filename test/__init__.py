import os
import sys

# Add the project source directory to sys.path so tests can import modules located in src/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
