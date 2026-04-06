import argparse
from src.pipeline.orchestrator import execute_pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, choices=["azure_url", "file", "text"])
    parser.add_argument("--value", required=True)
    parser.add_argument("--enable-suite-splitter", action="store_true")

    args = parser.parse_args()

    def progress(msg: str):
        print(msg + "...")

    print("Resolving requirement and running pipeline...")
    result = execute_pipeline(
        source=args.source,
        value=args.value,
        enable_suite_splitter=args.enable_suite_splitter,
        progress_callback=progress,
    )

    print("\n=== FINAL CSV PREVIEW ===")
    print(result["final_csv_text"][:1200])

    print(f"\nSaved full pipeline run to: {result['json_path']}")
    print(f"Saved final CSV to: {result['csv_path']}")

    if result["suite_files"]:
        print("\nSaved suite files:")
        for name, path in result["suite_files"].items():
            print(f"{name}: {path}")


if __name__ == "__main__":
    main()