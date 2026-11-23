import json
import subprocess  # nosec B404
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "harness-log.md"
JSON_PATH = ROOT / ".harness" / "last-run.json"


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def run_gate(name: str, command: list[str]) -> dict[str, object]:
    started = utc_now()
    completed = subprocess.run(  # nosec B603
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    finished = utc_now()
    output = completed.stdout
    if completed.stderr:
        output += ("\n" if output else "") + completed.stderr
    return {
        "name": name,
        "command": command,
        "started_at": started,
        "finished_at": finished,
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "output": output,
    }


def markdown_output(output: str) -> str:
    if not output:
        return "(no output)"
    return output.rstrip()


def append_markdown(results: list[dict[str, object]], overall_passed: bool) -> None:
    run_started = str(results[0]["started_at"])
    run_finished = str(results[-1]["finished_at"])
    status = "PASS" if overall_passed else "FAIL"
    lines = [
        "",
        f"## Harness Run - {run_started}",
        "",
        f"- Run started: `{run_started}`",
        f"- Run finished: `{run_finished}`",
        f"- Overall result: **{status}**",
        "",
    ]

    for result in results:
        command = " ".join(str(part) for part in result["command"])
        result_status = "PASS" if result["passed"] else "FAIL"
        lines.extend(
            [
                f"### {result['name']} - {result_status}",
                "",
                f"- Started: `{result['started_at']}`",
                f"- Finished: `{result['finished_at']}`",
                f"- Exit code: `{result['exit_code']}`",
                f"- Command: `{command}`",
                "",
                "```text",
                markdown_output(str(result["output"])),
                "```",
                "",
            ]
        )

    with LOG_PATH.open("a", encoding="utf-8") as log:
        log.write("\n".join(lines))


def main() -> int:
    gates = [
        (
            "Python syntax validation",
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "src",
                "tests",
                ".harness",
            ],
        ),
        (
            "Ruff lint",
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "src",
                "tests",
                ".harness",
                "src/main.py",
                "src/models.py",
                "src/task_manager.py",
                "src/storage.py",
            ],
        ),
        (
            "Bandit security scan",
            [
                sys.executable,
                "-m",
                "bandit",
                "-q",
                "-r",
                "src",
                ".harness",
            ],
        ),
        (
            "Pytest unit tests",
            [sys.executable, "-m", "pytest", "tests/unit", "-q"],
        ),
        (
            "Pytest contract tests",
            [sys.executable, "-m", "pytest", "tests/contract", "-q"],
        ),
    ]

    results = [run_gate(name, command) for name, command in gates]
    overall_passed = all(bool(result["passed"]) for result in results)
    append_markdown(results, overall_passed)

    JSON_PATH.write_text(
        json.dumps(
            {
                "started_at": results[0]["started_at"],
                "finished_at": results[-1]["finished_at"],
                "overall_passed": overall_passed,
                "gates": results,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status}: {result['name']} (exit {result['exit_code']})")
    print(f"Overall: {'PASS' if overall_passed else 'FAIL'}")
    print(f"Log: {LOG_PATH.relative_to(ROOT)}")
    print(f"Machine-readable result: {JSON_PATH.relative_to(ROOT)}")
    return 0 if overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
