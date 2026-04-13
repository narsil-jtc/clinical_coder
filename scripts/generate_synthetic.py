"""Generate synthetic notes for demo and evaluation use."""

import argparse
import json
from pathlib import Path

from clinical_coder.data.synthetic_generator import TEMPLATES, generate_batch


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic clinical notes")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--template", choices=list(TEMPLATES.keys()), default=None)
    parser.add_argument("--output", type=str, default="data/synthetic_notes/")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    templates = [args.template] if args.template else None
    notes = generate_batch(n=args.count, templates=templates)
    for note in notes:
        filepath = output_dir / f"{note.note_id}.json"
        filepath.write_text(
            json.dumps(
                {
                    "note_id": note.note_id,
                    "note_type": note.note_type,
                    "template": note.template_name,
                    "expected_codes": note.expected_codes,
                    "expected_principal": note.expected_principal,
                    "edge_cases": note.edge_cases,
                    "text": note.text,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Written: {filepath}")


if __name__ == "__main__":
    main()
