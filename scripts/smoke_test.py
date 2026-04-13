"""Run a deterministic workflow smoke test without local or cloud LLM dependencies."""

from clinical_coder.eval.smoke import run_smoke_test


def main() -> None:
    summary = run_smoke_test()
    print("Smoke test summary")
    print(f"Provider: {summary['provider']}")
    print(f"Entities: {summary['entity_count']}")
    print(f"Candidates: {summary['candidate_count']}")
    print(f"Flags: {summary['flag_count']}")
    print(f"Errors: {summary['error_count']}")
    print(f"Codes: {', '.join(summary['codes'])}")


if __name__ == "__main__":
    main()
