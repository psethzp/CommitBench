from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from effectkernelbench_artifact import build_baselines_cli
raise SystemExit(build_baselines_cli(Path(__file__).resolve().parents[1]))
