from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from effectkernelbench_artifact import hash_artifact
hash_artifact(Path(__file__).resolve().parents[1])
