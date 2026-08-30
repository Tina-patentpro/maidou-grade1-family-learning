#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


REQUIRED_FIELDS = (
    "observed_at",
    "subject",
    "source",
    "learning_target",
    "observed_behavior",
    "support_level",
    "representation",
    "energy",
    "affect",
    "possible_explanation",
    "parent_confirmed",
)

ALLOWED = {
    "support_level": {"independent", "light_prompt", "modelled", "not_observed"},
    "representation": {"oral", "object", "picture", "symbol", "real_context"},
    "energy": {"high", "medium", "tired"},
    "affect": {"engaged", "neutral", "reluctant", "distressed"},
    "possible_explanation": {"concept", "memory", "language", "attention", "motor", "unclear"},
}


class ValidationArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(f"invalid arguments: {message}")


def validate_record(record: dict) -> list[str]:
    if not isinstance(record, dict):
        return ["record must be an object"]

    errors = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing field: {field}")
    if errors:
        return errors

    for field in ("subject", "source", "learning_target", "observed_behavior"):
        if not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"invalid non-empty string: {field}")
    for field, allowed in ALLOWED.items():
        if not isinstance(record[field], str) or record[field] not in allowed:
            errors.append(f"invalid {field}: {record[field]}")
    if not isinstance(record["parent_confirmed"], bool):
        errors.append("invalid parent_confirmed: expected boolean")
    try:
        observed_at = record["observed_at"]
        if not isinstance(observed_at, str) or "T" not in observed_at:
            raise ValueError("observed_at must include a time component")
        datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        errors.append(f"invalid observed_at: {record['observed_at']}")
    return errors


def load_records(path):
    text = Path(path).read_text(encoding="utf-8")
    if not text.strip():
        return []

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        records = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at line {line_number}: {error.msg}") from error
        return records

    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("invalid JSON input: expected an object or array")


def main(argv=None):
    parser = ValidationArgumentParser(description="Validate learning-evidence JSON records.")
    parser.add_argument("--input", required=True, type=Path, help="JSON or JSONL evidence file")
    input_path = "<arguments>"

    try:
        args = parser.parse_args(argv)
        input_path = args.input
        records = load_records(args.input)
    except (OSError, ValueError) as error:
        print(f"{input_path}: {error}", file=sys.stderr)
        return 1

    has_errors = False
    for record_number, record in enumerate(records, start=1):
        for error in validate_record(record):
            print(f"{input_path}:{record_number}: {error}", file=sys.stderr)
            has_errors = True
    if has_errors:
        return 1

    print(f"valid records={len(records)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
