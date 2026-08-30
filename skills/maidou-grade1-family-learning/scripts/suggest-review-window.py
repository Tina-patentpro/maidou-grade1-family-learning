#!/usr/bin/env python3
import argparse
import importlib.util
import json
import sys
from pathlib import Path


STAGES = {
    "初次接触", "正在形成", "提示下完成",
    "独立完成", "能够迁移", "延迟后稳定",
}


class AdvisoryArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(f"invalid arguments: {message}")


def _validate_count(name, value):
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid {name}: expected non-negative integer")


def suggest_review_window(record: dict, stage: str, evidence_count: int, distinct_contexts: int) -> dict:
    if not isinstance(stage, str) or stage not in STAGES:
        raise ValueError(f"invalid stage: {stage}")
    _validate_count("evidence_count", evidence_count)
    _validate_count("distinct_contexts", distinct_contexts)
    if distinct_contexts > evidence_count:
        raise ValueError("invalid distinct_contexts: cannot exceed evidence_count")
    if stage == "延迟后稳定":
        if not record.get("parent_confirmed") or evidence_count < 2 or distinct_contexts < 2:
            return {"action": "continue_observing", "window_days": None, "next_context": "distinct_context"}
        if record.get("support_level") == "independent":
            return {"action": "archive", "window_days": None, "next_context": "none"}
    if record.get("support_level") == "not_observed":
        return {"action": "no_review", "window_days": None, "next_context": "natural_opportunity"}
    if not record.get("parent_confirmed") or evidence_count < 2 or distinct_contexts < 2:
        return {"action": "continue_observing", "window_days": None, "next_context": "distinct_context"}
    if record.get("support_level") == "modelled":
        return {"action": "wait_for_related_instruction", "window_days": None, "next_context": "after_related_class"}
    if record.get("support_level") == "light_prompt":
        return {"action": "review", "window_days": {"min": 1, "max": 3}, "next_context": "alternate_representation"}
    if stage == "能够迁移":
        return {"action": "review", "window_days": {"min": 7, "max": 14}, "next_context": "natural_observation"}
    return {"action": "review", "window_days": {"min": 3, "max": 7}, "next_context": "changed_real_context"}


def _load_validator():
    validator_path = Path(__file__).resolve().with_name("validate-learning-record.py")
    spec = importlib.util.spec_from_file_location("learning_record_validator", validator_path)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    return validator


def _load_input(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON: {error.msg}") from error
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    for field in ("record", "stage", "evidence_count", "distinct_contexts"):
        if field not in data:
            raise ValueError(f"missing field: {field}")
    return data


def main(argv=None):
    parser = AdvisoryArgumentParser(description="Suggest an advisory learning review window.")
    parser.add_argument("--input", required=True, type=Path, help="JSON suggestion input file")
    input_path = "<arguments>"

    try:
        args = parser.parse_args(argv)
        input_path = args.input
        data = _load_input(args.input)
        errors = _load_validator().validate_record(data["record"])
        if errors:
            raise ValueError(f"invalid record: {errors[0]}")
        result = suggest_review_window(
            data["record"], data["stage"], data["evidence_count"], data["distinct_contexts"]
        )
    except (OSError, ValueError, TypeError) as error:
        print(f"{input_path}: {error}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
