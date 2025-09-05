# review_core.py
import os, tempfile, subprocess, json, sys
from dataclasses import dataclass
from typing import List, Optional, Dict, Set
from radon.complexity import cc_visit  # type: ignore
from unidiff import PatchSet

@dataclass
class Issue:
    file: str
    line: int                 # ✅ was str; must be int for comparisons
    severity: str
    tool: str
    rule: str
    message: str
    suggestion: Optional[str] = None

def _write_temp_code(code: str, suffix: str = ".py") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(code)
    return path

def run_flake8(code: str, filename_hint: str = "snippet.py") -> List[Issue]:
    tmp = _write_temp_code(code)
    try:
        fmt = "%(row)d|%(col)d|%(code)s|%(text)s"
        cmd = [sys.executable, "-m", "flake8", "--format", fmt, tmp]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            return [Issue(filename_hint, 1, "LOW", "flake8", "INSTALL",
                          "flake8 not found. Did you install requirements?")]
        issues: List[Issue] = []
        for line in out.stdout.strip().splitlines():
            try:
                row, col, code_id, text = line.split("|", 3)
                issues.append(Issue(filename_hint, int(row), "LOW", "flake8", code_id, text))
            except ValueError:
                # ignore malformed lines / plugin chatter
                pass
        return issues
    finally:
        try: os.unlink(tmp)
        except OSError: pass

def run_bandit(code: str, filename_hint: str = "snippet.py") -> List[Issue]:
    tmp = _write_temp_code(code)
    try:
        cmd = [sys.executable, "-m", "bandit", "-q", "-f", "json", tmp]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            return [Issue(filename_hint, 1, "LOW", "bandit", "INSTALL",
                          "bandit not found. Did you install requirements?")]
        issues: List[Issue] = []
        try:
            data = json.loads(out.stdout or "{}")
            for res in data.get("results", []):
                line = int(res.get("line_number", 1))
                sev = (res.get("issue_severity") or "LOW").upper()
                rule = res.get("test_id", "BXXX")
                msg = res.get("issue_text", "Security issue")
                issues.append(Issue(filename_hint, line, sev, "bandit", rule, msg))
        except json.JSONDecodeError:
            # ignore non-JSON output
            pass
        return issues
    finally:
        try: os.unlink(tmp)
        except OSError: pass

def run_complexity(code: str, filename_hint: str = "snippet.py", cc_threshold: int = 3) -> List[Issue]:
    issues: List[Issue] = []
    for block in cc_visit(code):
        if block.complexity >= cc_threshold:
            msg = f"Function '{block.name}' is too complex (CC={block.complexity})."
            issues.append(Issue(filename_hint, int(block.lineno), "MEDIUM", "complexity", "CC", msg))
    return issues

def _normalize_path(p: str) -> str:
    # strip leading a/ b/ and reduce to basename to improve matching
    if p.startswith(("a/", "b/")):
        p = p[2:]
    return os.path.basename(p)

def _changed_lines_from_diff(diff_text: str) -> Dict[str, Set[int]]:
    changed: Dict[str, Set[int]] = {}
    ps = PatchSet(diff_text)
    for patched_file in ps:
        if patched_file.is_removed_file:
            continue
        added: Set[int] = set()
        for hunk in patched_file:
            for line in hunk:
                if line.is_added and line.target_line_no is not None:
                    added.add(int(line.target_line_no))
        if added:
            changed[_normalize_path(patched_file.target_file)] = added
    return changed

def filter_issues_to_changed_lines(issues: List[Issue], diff_text: str) -> List[Issue]:
    changed = _changed_lines_from_diff(diff_text)
    if not changed:
        return issues
    return [
        i for i in issues
        if _normalize_path(i.file) in changed and i.line in changed[_normalize_path(i.file)]
    ]

def friendly_suggestion(issue: Issue) -> Optional[str]:
    if issue.tool == "complexity":
        return "Extract smaller functions; reduce nesting/branches."
    if issue.tool == "bandit":
        return "Avoid unsafe functions (e.g., eval); validate and sanitize inputs."
    if issue.tool == "flake8":
        return "Follow PEP 8 (naming, spacing, line length) for readability."
    return None

def review_code_string(code: str, filename_hint: str = "snippet.py", debug: bool = False) -> List[Issue]:
    f8 = run_flake8(code, filename_hint)
    bd = run_bandit(code, filename_hint)
    cx = run_complexity(code, filename_hint)
    issues = f8 + bd + cx
    for i in issues:
        i.suggestion = friendly_suggestion(i)
    if debug:
        print(f"flake8 issues: {len(f8)}; bandit: {len(bd)}; complexity: {len(cx)}")
    return issues

def issues_to_markdown(issues):
    # If someone accidentally passed a string, just return it.
    if isinstance(issues, str):
        return issues

    if not issues:
        return "✅ No issues found. Great job!"

    lines = ["### Review Comments"]
    for iss in issues:
        # Skip anything that isn't shaped like an Issue
        if not hasattr(iss, "tool"):
            continue
        tip = f" Tip: {iss.suggestion}" if getattr(iss, "suggestion", None) else ""
        lines.append(
            f"- **{iss.tool.upper()} {iss.rule}** ({iss.severity}) "
            f"at `{iss.file}:{iss.line}` — {iss.message}{tip}"
        )
    return "\n".join(lines)

