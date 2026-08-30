import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "maidou-grade1-family-learning" / "scripts" / "validate-learning-record.py"

VALID = {
    "observed_at": "2026-08-30T18:30:00+08:00",
    "subject": "数学",
    "source": "学校确认进度：第1课",
    "learning_target": "用实物表示5以内数量",
    "observed_behavior": "独立摆出4个积木并说明数量",
    "support_level": "independent",
    "representation": "object",
    "energy": "medium",
    "affect": "engaged",
    "possible_explanation": "unclear",
    "parent_confirmed": False,
}


def load_module():
    spec = importlib.util.spec_from_file_location("learning_record_validator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cli(path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


class LearningRecordValidatorTests(unittest.TestCase):
    def test_valid_record_has_no_errors(self):
        self.assertEqual(load_module().validate_record(VALID), [])

    def test_missing_required_field_is_rejected(self):
        record = copy.deepcopy(VALID)
        del record["learning_target"]
        self.assertIn("missing field: learning_target", load_module().validate_record(record))

    def test_invalid_enum_and_time_are_rejected(self):
        record = copy.deepcopy(VALID)
        record["energy"] = "exhausted"
        record["observed_at"] = "not-a-time"
        errors = load_module().validate_record(record)
        self.assertIn("invalid energy: exhausted", errors)
        self.assertIn("invalid observed_at: not-a-time", errors)

    def test_date_only_observed_at_is_rejected(self):
        record = copy.deepcopy(VALID)
        record["observed_at"] = "2026-08-30"
        self.assertIn(
            "invalid observed_at: 2026-08-30",
            load_module().validate_record(record),
        )

    def test_zulu_observed_at_is_accepted(self):
        record = copy.deepcopy(VALID)
        record["observed_at"] = "2026-08-30T10:30:00Z"
        self.assertEqual(load_module().validate_record(record), [])

    def test_invalid_value_in_each_enum_family_is_rejected(self):
        invalid_values = {
            "support_level": "unsupported",
            "representation": "gesture",
            "energy": "exhausted",
            "affect": "elated",
            "possible_explanation": "diagnosis",
        }
        for field, value in invalid_values.items():
            with self.subTest(field=field):
                record = copy.deepcopy(VALID)
                record[field] = value
                self.assertIn(
                    f"invalid {field}: {value}",
                    load_module().validate_record(record),
                )

    def test_unhashable_enum_value_is_rejected_as_a_field_error(self):
        record = copy.deepcopy(VALID)
        record["representation"] = []
        self.assertIn(
            "invalid representation: []",
            load_module().validate_record(record),
        )

    def test_non_object_record_is_rejected(self):
        self.assertEqual(load_module().validate_record([VALID]), ["record must be an object"])

    def test_invalid_parent_confirmation_is_rejected(self):
        record = copy.deepcopy(VALID)
        record["parent_confirmed"] = "false"
        self.assertIn(
            "invalid parent_confirmed: expected boolean",
            load_module().validate_record(record),
        )

    def test_cli_validates_json_object_and_reports_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(VALID, ensure_ascii=False), encoding="utf-8")
            result = run_cli(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid records=1", result.stdout)

    def test_cli_validates_json_array_and_reports_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps([VALID, VALID], ensure_ascii=False), encoding="utf-8")
            result = run_cli(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid records=2", result.stdout)

    def test_cli_validates_multiple_nonblank_jsonl_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.jsonl"
            path.write_text(
                "\n".join((json.dumps(VALID, ensure_ascii=False), "", json.dumps(VALID, ensure_ascii=False))) + "\n",
                encoding="utf-8",
            )
            result = run_cli(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid records=2", result.stdout)

    def test_cli_accepts_empty_jsonl_as_zero_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "learning-evidence.jsonl"
            path.write_text("\n\n", encoding="utf-8")
            result = run_cli(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid records=0", result.stdout)

    def test_cli_requires_input_without_usage_dump(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("--input", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("usage:", result.stderr.lower())

    def test_cli_help_exits_successfully(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--input", result.stdout)

    def test_cli_reports_field_specific_errors_with_record_number(self):
        record = copy.deepcopy(VALID)
        del record["learning_target"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.jsonl"
            path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
            result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{path}:1: missing field: learning_target", result.stderr)

    def test_cli_rejects_date_only_observed_at_without_traceback(self):
        record = copy.deepcopy(VALID)
        record["observed_at"] = "2026-08-30"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.jsonl"
            path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
            result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{path}:1: invalid observed_at: 2026-08-30", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_rejects_unhashable_enum_values_without_traceback(self):
        record = copy.deepcopy(VALID)
        record["representation"] = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.jsonl"
            path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
            result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{path}:1: invalid representation: []", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_rejects_invalid_json_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text('{"observed_at":', encoding="utf-8")
            result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid JSON", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
