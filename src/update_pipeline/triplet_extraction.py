import argparse

from add_document_pipeline import DocumentPipeline


def main():
    parser = argparse.ArgumentParser(description="Step 3: extract knowledge graph triplets")
    parser.add_argument("--so-hieu", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()

    pipeline = DocumentPipeline(
        output_dir=args.output_dir,
        resume=not args.no_resume,
        force=args.force,
    )
    pipeline.initialize()
    pipeline.step3_extract_triplets(args.so_hieu)


if __name__ == "__main__":
    main()
