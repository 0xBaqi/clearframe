import json
import sys
from pathlib import Path

# Permit `python backend/run_demo.py` from a fresh checkout.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.agent import StrandsClearanceAgent
from backend.seed import NIGHT_SHIFT_INTENT, night_shift_repository

results = StrandsClearanceAgent(night_shift_repository()).run(NIGHT_SHIFT_INTENT)
print(json.dumps([result.as_dict() for result in results], indent=2))
