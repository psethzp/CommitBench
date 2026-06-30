from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from effectkernelbench_artifact import fresh_smoke_cli
raise SystemExit(fresh_smoke_cli(Path(__file__).resolve().parents[1]))
