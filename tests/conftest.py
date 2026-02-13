"""
Test configuration and shared fixtures.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import sys
from pathlib import Path


# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
