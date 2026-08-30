import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "maidou-grade1-family-learning" / "scripts" / "suggest-review-window.py"

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
    spec = importlib.util.spec_from_file_location("review_window", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cli(payload):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "review-input.json"
        path.write_text(payload, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )


class ReviewWindowTests(unittest.TestCase):
    def test_unconfirmed_or_single_context_only_continues_observation(self):
        result = load_module().suggest_review_window(VALID, "正在形成", 1, 1)
        self.assertEqual(result["action"], "continue_observing")
        self.assertIsNone(result["window_days"])

    def test_light_prompt_after_confirmation_uses_one_to_three_day_window(self):
        record = copy.deepcopy(VALID)
        record.update(parent_confirmed=True, support_level="light_prompt")
        result = load_module().suggest_review_window(record, "提示下完成", 2, 2)
        self.assertEqual(result["window_days"], {"min": 1, "max": 3})
        self.assertEqual(result["next_context"], "alternate_representation")

    def test_independent_work_uses_changed_context(self):
        record = copy.deepcopy(VALID)
        record["parent_confirmed"] = True
        result = load_module().suggest_review_window(record, "独立完成", 2, 2)
        self.assertEqual(result["window_days"], {"min": 3, "max": 7})
        self.assertEqual(result["next_context"], "changed_real_context")

    def test_transfer_uses_natural_observation_and_stable_archives(self):
        record = copy.deepcopy(VALID)
        record["parent_confirmed"] = True
        transfer = load_module().suggest_review_window(record, "能够迁移", 2, 2)
        stable = load_module().suggest_review_window(record, "延迟后稳定", 2, 2)
        self.assertEqual(transfer["window_days"], {"min": 7, "max": 14})
        self.assertEqual(transfer["next_context"], "natural_observation")
        self.assertEqual(stable["action"], "archive")
        self.assertIsNone(stable["window_days"])

    def test_modelled_work_waits_for_related_classroom_instruction(self):
        record = copy.deepcopy(VALID)
        record.update(parent_confirmed=True, support_level="modelled")
        result = load_module().suggest_review_window(record, "正在形成", 2, 2)
        self.assertEqual(result["action"], "wait_for_related_instruction")
        self.assertIsNone(result["window_days"])

    def test_not_observed_does_not_suggest_a_review(self):
        record = copy.deepcopy(VALID)
        record.update(parent_confirmed=True, support_level="not_observed")
        result = load_module().suggest_review_window(record, "正在形成", 2, 2)
        self.assertEqual(
            result,
            {"action": "no_review", "window_days": None, "next_context": "natural_opportunity"},
        )

    def test_not_observed_waits_for_a_natural_opportunity_even_without_confirmation(self):
        record = copy.deepcopy(VALID)
        record["support_level"] = "not_observed"
        result = load_module().suggest_review_window(record, "正在形成", 1, 1)
        self.assertEqual(
            result,
            {"action": "no_review", "window_days": None, "next_context": "natural_opportunity"},
        )

    def test_stable_stage_cannot_bypass_evidence_gate(self):
        result = load_module().suggest_review_window(VALID, "延迟后稳定", 1, 1)
        self.assertEqual(
            result,
            {"action": "continue_observing", "window_days": None, "next_context": "distinct_context"},
        )

    def test_stable_stage_archives_only_independent_evidence(self):
        module = load_module()
        expected_by_support = {
            "independent": {"action": "archive", "window_days": None, "next_context": "none"},
            "not_observed": {
                "action": "no_review",
                "window_days": None,
                "next_context": "natural_opportunity",
            },
            "modelled": {
                "action": "wait_for_related_instruction",
                "window_days": None,
                "next_context": "after_related_class",
            },
            "light_prompt": {
                "action": "review",
                "window_days": {"min": 1, "max": 3},
                "next_context": "alternate_representation",
            },
        }
        for support_level, expected in expected_by_support.items():
            with self.subTest(support_level=support_level):
                record = copy.deepcopy(VALID)
                record.update(parent_confirmed=True, support_level=support_level)
                self.assertEqual(
                    module.suggest_review_window(record, "延迟后稳定", 2, 2),
                    expected,
                )

    def test_invalid_stage_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid stage: 完成"):
            load_module().suggest_review_window(VALID, "完成", 1, 1)

    def test_invalid_evidence_counts_are_rejected_predictably(self):
        module = load_module()
        cases = (
            (True, 1, "invalid evidence_count: expected non-negative integer"),
            (-1, 0, "invalid evidence_count: expected non-negative integer"),
            (2, False, "invalid distinct_contexts: expected non-negative integer"),
            (1, 2, "invalid distinct_contexts: cannot exceed evidence_count"),
        )
        for evidence_count, distinct_contexts, message in cases:
            with self.subTest(evidence_count=evidence_count, distinct_contexts=distinct_contexts):
                with self.assertRaisesRegex(ValueError, message):
                    module.suggest_review_window(VALID, "正在形成", evidence_count, distinct_contexts)

    def test_cli_validates_nested_record_and_prints_utf8_json(self):
        record = copy.deepcopy(VALID)
        record.update(parent_confirmed=True, support_level="light_prompt")
        payload = json.dumps(
            {"record": record, "stage": "提示下完成", "evidence_count": 2, "distinct_contexts": 2},
            ensure_ascii=False,
        )
        result = run_cli(payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {"action": "review", "window_days": {"min": 1, "max": 3}, "next_context": "alternate_representation"},
        )
        self.assertIn("review", result.stdout)
        self.assertNotIn("\\u6570", result.stdout)

    def test_cli_rejects_invalid_nested_record_without_traceback(self):
        record = copy.deepcopy(VALID)
        del record["learning_target"]
        result = run_cli(
            json.dumps(
                {"record": record, "stage": "正在形成", "evidence_count": 2, "distinct_contexts": 2},
                ensure_ascii=False,
            )
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid record: missing field: learning_target", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_rejects_malformed_json_without_traceback(self):
        result = run_cli('{"record":')
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid JSON", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_rejects_bad_counts_with_field_specific_errors(self):
        payload = {"record": VALID, "stage": "正在形成", "evidence_count": True, "distinct_contexts": 1}
        result = run_cli(json.dumps(payload, ensure_ascii=False))
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid evidence_count: expected non-negative integer", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_missing_input_returns_a_concise_exit_one_error(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid arguments:", result.stderr)
        self.assertIn("--input", result.stderr)
        self.assertNotIn("usage:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
