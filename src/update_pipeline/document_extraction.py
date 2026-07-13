import argparse

from add_document_pipeline import DocumentPipeline


def main():
    parser = argparse.ArgumentParser(description="Step 1: extract and parse a legal document")
    parser.add_argument("--so-hieu", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--effective-date", required=True)
    parser.add_argument("--file", dest="files", action="append", required=True)
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
    pipeline.step1_extract_document(
        {
            "so_hieu": args.so_hieu,
            "title": args.title,
            "effective_date": args.effective_date,
            "files": args.files,
        }
    )


if __name__ == "__main__":
    main()
