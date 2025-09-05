# review.py
import argparse
import sys
from review_core import review_code_string, issues_to_markdown, filter_issues_to_changed_lines


def _read_stream_or_file(path: str, label: str) -> str:
    """
    Read from a file path or '-' for stdin.
    Raises OSError on failure.
    """
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Static review of a Python file using flake8, bandit, and cyclomatic complexity.",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to a .py file to review, or '-' to read from stdin.",
    )
    parser.add_argument(
        "--diff",
        help="Path to a unified diff to filter issues to changed lines, or '-' for stdin (optional).",
    )
    args = parser.parse_args()

    # Load code
    try:
        code = _read_stream_or_file(args.file, "file")
    except OSError as e:
        print(f"ERROR: failed to read --file '{args.file}': {e}", file=sys.stderr)
        return 2

    # Run analysis
    issues = review_code_string(code, filename_hint=args.file)

    # Optional diff filtering
    if args.diff:
        try:
            diff_text = _read_stream_or_file(args.diff, "diff")
        except OSError as e:
            print(f"ERROR: failed to read --diff '{args.diff}': {e}", file=sys.stderr)
            return 2
        issues = filter_issues_to_changed_lines(issues, diff_text)

    # Output
    print(issues_to_markdown(issues))
    return 0


if __name__ == "__main__":
    sys.exit(main())
