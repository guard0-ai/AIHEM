import os
import sys

# Make the service root importable so `import app.x` works from tests.
sys.path.insert(0, os.path.dirname(__file__))
