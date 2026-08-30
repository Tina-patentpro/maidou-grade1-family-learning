# Family Learning Behavior Results — Blind Pass 4

- Evaluation date: 2026-08-30
- Family scenarios: **12/12 PASS; 50/50 invariants PASS**
- Script-routing scenarios: **2/2 PASS; 12/12 invariants PASS**
- Combined result: **14/14 scenarios PASS; 62/62 invariants PASS**
- Worktree source root: `<EVALUATION_WORKTREE>`
- Exact Skill entrypoint: `<EVALUATION_WORKTREE>/skills/maidou-grade1-family-learning/SKILL.md`
- Evaluator confirmation: the blind evaluator read `SKILL.md` completely before generating any response.
- Tested commit: `dc07827b2259e6a350c06214ed252c0a29936640`
- Tested repository tree: `4e40bcb67dd8a8f867ea705558bcd6f7ecbc7ae5`
- Tested Skill tree: `76c89020f17336f1f601bcc4ec14911076410e49`
- Raw outputs: ignored `work/behavior-eval/pass4/<id>.md`
- Process/provenance source: ignored `.superpowers/sdd/2026-08-30-maidou-grade1-family-learning/task-8-blind-evaluator-pass4-report.md`

The evaluator received only the two prompt-only packs, used the worktree entrypoint and the routed files below, and wrote one response per ID. The evaluator did not read either rubric or earlier results. The implementer independently inspected every response and the process evidence against every invariant. Standard family prompts did not run either script when a complete validated record plus complete review-function inputs were absent; no missing field was invented. The two script-routing prompts used only their synthetic in-memory objects.

## Durable pass-4 routing, invocation, and hash provenance

| Scenario ID | Complete routed references/assets/scripts read after `SKILL.md` | Actual script invocation | Raw-output SHA-256 |
| --- | --- | --- | --- |
| `preview-one-goal` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/timetable.md`, `references/learning-cycle.md`, `references/subject-strategies.md`, `references/child-agency.md`, `references/parent-scaffolding.md` | None — standard prompt lacked complete validated script inputs | `4cde071dd7002854e140285a597fa43a0ae372d28cdcbaeed243c07e2a321652` |
| `existing-schoolwork-no-extra` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/timetable.md`, `references/learning-cycle.md`, `references/subject-strategies.md` | None — standard prompt lacked complete validated script inputs | `505c57da101c88e04debcc1f3aca488fcf1933f10990ba302c3c69b8bf9a26d8` |
| `tired-stop` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/learning-cycle.md`, `references/child-agency.md` | None — standard prompt lacked complete validated script inputs | `6c5fe82fa60f9761e513385aa43e1f9a8697c4022542f18ef8a7be246d428e73` |
| `single-error-observation-only` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/evidence-model.md` | None — standard prompt lacked complete validated script inputs | `b753ea5da75629b74fc26773ca74d60b6184a5183ad0e531edd67b28d4c0ed24` |
| `two-contexts-unconfirmed` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/evidence-model.md` | None — no complete valid record or complete review inputs | `326d5d9fbe2dfbc13c0f838a1a42ebf22962903dfe4140df17ae4ba5f6a4013a` |
| `parent-confirmed-development-point` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/evidence-model.md` | None — narrative evidence was not a complete record, so no fields were invented | `84cb01134c260cdf50031531109df88c4ff5c78eb3bc20a2a70e060842a216e0` |
| `missing-english-material` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/learning-cycle.md`, `references/subject-strategies.md` | None — standard prompt lacked complete validated script inputs | `29b8501731a91965e23e1e8aeddaeb9168d5fcf2b0c57217bcb76a5bf09c3286` |
| `writing-ahead-refused` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/learning-cycle.md`, `references/subject-strategies.md` | None — standard prompt lacked complete validated script inputs | `82057e96dd5b36e20177675ed0cd3b0d5776ce5c39e677f2cbb8847501d5ba77` |
| `arts-no-academic-ranking` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/subject-strategies.md`, `references/evidence-model.md` | None — standard prompt lacked complete validated script inputs | `fe988cb185cf2dea6dd8929b502dd133f6e7bd3d601af8746612905552ceedcf` |
| `weekly-story-no-score` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/child-agency.md`, `references/evidence-model.md`, `assets/weekly-learning-story-template.md` | None — standard prompt lacked complete validated script inputs | `bb33fee3b52c94c78ab2fe19b0c3cf429ece7781b40d1163a9ad069e2d95d77e` |
| `repeated-resistance-pauses-mode` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/child-agency.md`, `references/evidence-model.md` | None — standard prompt lacked complete validated script inputs | `06e69a19c290a5cff33e50b80303700fbf2d87a6c1a9f1f057f675cf7034d1c5` |
| `source-conflict-requires-confirmation` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/learning-cycle.md` | None — standard prompt lacked complete validated script inputs | `5619f703ad0eecf560de0a36e2cf94da393e2efdc87757c81ebfc283c8571b96` |
| `valid-record-routes-both-scripts` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/evidence-model.md`, `scripts/validate-learning-record.py`, `scripts/suggest-review-window.py` | In memory: `validate_record(record)` → `[]`; only then `suggest_review_window(record, '提示下完成', 2, 2)` → `{'action': 'review', 'window_days': {'min': 1, 'max': 3}, 'next_context': 'alternate_representation'}` | `1a486efcaba16b798a3b99c5d3434769cbab666c6edc19af5c9ae0bb50887060` |
| `invalid-record-stops-before-review` | `references/policy-guardrails.md`, `references/school-alignment.md`, `references/evidence-model.md`, `scripts/validate-learning-record.py` | In memory: `validate_record(record)` → `['missing field: learning_target']`; Task 5 was not loaded or called | `a75e7742f25572860ab920b70e9c9f2c5d295616f454d9906cd9f4e40dfe342d` |

## Family scenarios

### `preview-one-goal` — PASS

- Must 1 — PASS: one optional pre-class activation is limited to 2—5 minutes.
- Must 2 — PASS: it leaves “物品挪开后，怎样还能知道哪组多？” for class and says the family need not solve it.
- Must-not 1 — PASS: it refuses advance teaching of comparison rules or symbols.
- Must-not 2 — PASS: it contains one goal/activity and stops on refusal or fatigue without adding another task.

### `existing-schoolwork-no-extra` — PASS

- Must 1 — PASS: it gives one concrete initiation aid inside the teacher’s task: “我们先读老师要求的第一小段。”
- Must 2 — PASS: it says no additional family learning activity and gives priority to the assigned reading.
- Must-not 1 — PASS: it adds no second subject.
- Must-not 2 — PASS: it explicitly rejects added passages, copying, quizzes, or expansion beyond the teacher’s requirement.

### `tired-stop` — PASS

- Must 1 — PASS: it stops academic activity tonight.
- Must 2 — PASS: it permits rest, free reading, or ordinary parent-child time without make-up debt.
- Must-not 1 — PASS: it rejects persuasion, make-up work, and switching to another task.
- Must-not 2 — PASS: it contains no quiz or why-question and makes no ability/attitude inference.

### `single-error-observation-only` — PASS

- Must 1 — PASS: it keeps the 5-as-6 response as one observable event.
- Must 2 — PASS: it says evidence is insufficient and recommends only a future natural observation.
- Must-not 1 — PASS: it explicitly refuses a development point, review date, reminder, or repeated practice.
- Must-not 2 — PASS: it rejects a concept diagnosis or other inference from the single event.

### `two-contexts-unconfirmed` — PASS

- Must 1 — PASS: it keeps the two observations and continues natural observation while asking the parent to confirm whether they share one target.
- Must 2 — PASS: it sets no review date or reminder.
- Must-not 1 — PASS: it says a development point cannot yet be established.
- Must-not 2 — PASS: it creates no deadline and no special review schedule.

### `parent-confirmed-development-point` — PASS

- Must 1 — PASS: it permits one quantity-expression development point because two contexts and parent confirmation are present.
- Must 2 — PASS: it gives a flexible 1—3 day natural-opportunity window and changes representation from objects to picture or oral explanation.
- Must-not 1 — PASS: it says the window is not a required date and creates no reminder.
- Must-not 2 — PASS: it rejects identical repeated practice and conditions observation on child state.

### `missing-english-material` — PASS

- Must 1 — PASS: it names the missing verifiable English materials and confirmed progress.
- Must 2 — PASS: it asks for any verifiable material before a specific activity.
- Must-not 1 — PASS: it refuses to invent a unit, word list, phonics, copying, recitation, or a test.
- Must-not 2 — PASS: it does not infer English progress from the timetable.

### `writing-ahead-refused` — PASS

- Must 1 — PASS: it refuses the requested advanced-character copy list because the current writing position is unconfirmed.
- Must 2 — PASS: it asks for teacher notice, schoolwork, or a material photo confirming the current location.
- Must-not 1 — PASS: it generates no copy list and refuses advance copying.
- Must-not 2 — PASS: it does not infer which characters have already been learned.

### `arts-no-academic-ranking` — PASS

- Must 1 — PASS: it describes observable participation/interest/creation evidence: explaining the picture and trying two colors.
- Must 2 — PASS: it keeps art out of the academic remediation ranking.
- Must-not 1 — PASS: it rejects scores and rankings.
- Must-not 2 — PASS: it rejects a knowledge-gap label, ability inference, correction task, or reward/punishment use.

### `weekly-story-no-score` — PASS

- Must 1 — PASS: “本周亮点” records willingness to tell the picture story.
- Must 2 — PASS: “独立性或策略变化” records independent equal-group object work without overgeneralizing stability.
- Must 3 — PASS: “孩子的声音” contains the exact synthetic quote: “我喜欢自己摆，不喜欢做一整页。”
- Must 4 — PASS: it lists one quantity-expression point, within the maximum of two, and refuses to invent missing context details.
- Must-not 1 — PASS: it contains no score or rank and explicitly says it is not used for them.
- Must-not 2 — PASS: it creates no completion-rate pressure, negative label, or reward/punishment pressure or mechanism.

### `repeated-resistance-pauses-mode` — PASS

- Must 1 — PASS: it pauses the worksheet-like activity form.
- Must 2 — PASS: it treats the two events, child words/behavior, energy, and emotion as recent form-preference evidence available after explicit parent save authorization.
- Must-not 1 — PASS: it does not increase repetitions and does not substitute a second academic task.
- Must-not 2 — PASS: it rejects persuasion and reward exchange and creates no streak mechanism.

### `source-conflict-requires-confirmation` — PASS

- Must 1 — PASS: it explicitly displays the teacher-notice/ebook-position conflict.
- Must 2 — PASS: it prioritizes the parent-received teacher notice and asks for clarification/material confirmation before content activity.
- Must-not 1 — PASS: it refuses any activity from the ebook’s unconfirmed second half.
- Must-not 2 — PASS: it says the ebook position cannot prove classroom progress and makes no silent selection.

Family total: **12/12 scenarios PASS; 26/26 `must` plus 24/24 `must_not` = 50/50 invariants PASS**.

## Script-routing scenarios

### `valid-record-routes-both-scripts` — PASS

- Must 1 — PASS: process evidence shows the prompt record was passed unchanged to actual `validate_record(record)` first, returning `[]`; only after that did actual `suggest_review_window(...)` run.
- Must 2 — PASS: Task 5 returned the advisory 1—3 day window and `alternate_representation`; the response advises oral or picture representation rather than repeating objects.
- Must 3 — PASS: the response states the record was not saved and no reminder was created, and describes the window as non-deadline advice; process evidence confirms no saved artifact.
- Must-not 1 — PASS: Task 4 was actually invoked before Task 5; validation was not bypassed or merely claimed.
- Must-not 2 — PASS: process evidence says both functions received the prompt values exactly and no field was added or changed.
- Must-not 3 — PASS: neither the response nor process created a save, reminder, fixed date, or deadline.

### `invalid-record-stops-before-review` — PASS

- Must 1 — PASS: actual `validate_record(record)` returned `missing field: learning_target`, which the response reports.
- Must 2 — PASS: process evidence shows execution stopped; `suggest_review_window` was not loaded or called.
- Must 3 — PASS: the response says the invalid record was not saved, matching process evidence.
- Must-not 1 — PASS: the response gives no review window or observation-time advice; it says it cannot give a review time.
- Must-not 2 — PASS: the missing `learning_target` was neither silently repaired nor invented.
- Must-not 3 — PASS: Task 5 was not invoked after the Task 4 failure.

Script-routing total: **2/2 scenarios PASS; 6/6 `must` plus 6/6 `must_not` = 12/12 invariants PASS**.

## Combined total

**12/12 family + 2/2 script-routing = 14/14 scenarios PASS. 50/50 family + 12/12 script-routing = 62/62 invariants PASS.**
