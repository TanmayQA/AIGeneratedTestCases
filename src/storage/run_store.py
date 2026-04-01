from pathlib import Path
from datetime import datetime
import json


def save_full_pipeline_run(normalized, mode: str, stage_outputs: dict) -> str:
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"{normalized.requirement_id}_{mode}_{timestamp}"

    run_data = {
        "run_id": run_id,
        "mode": mode,
        "requirement": normalized.model_dump(),
        "stages": stage_outputs
    }

    file_path = output_dir / f"{run_id}.json"
    file_path.write_text(json.dumps(run_data, indent=2), encoding="utf-8")

    return str(file_path)


def save_csv_output(requirement_id: str, csv_text: str, mode: str) -> str:
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"{requirement_id}_{mode}_{timestamp}.csv"

    file_path.write_text(csv_text, encoding="utf-8")
    return str(file_path)