"""Allow running as python -m qmeter_analyzer."""
import sys
from .cli import main

sys.exit(main())
