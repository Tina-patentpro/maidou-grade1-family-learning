# Maidou Grade 1 Family Learning Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and locally install a version-controlled Codex Skill that uses the verified Grade 1 timetable, school-confirmed progress, and local textbooks to provide low-burden family learning support while protecting interest and tracking evidence without turning mistakes into labels.

**Architecture:** Keep the canonical Skill source inside this Git repository at `skills/maidou-grade1-family-learning/`, then install it through a safe symbolic link at `<CODEX_HOME>/skills/maidou-grade1-family-learning`. Keep educational instructions in focused references, deterministic JSON validation and review-window logic in two Python scripts, private learning data under `<PRIVATE_EDU_ROOT>/`, and tests in the repository.

**Tech Stack:** Codex Skill Markdown and `agents/openai.yaml`; Python 3.9+ standard library; JSON/JSONL; `unittest`; official `init_skill.py` and `quick_validate.py`; bundled `pypdf`, `pdfinfo`, and `pdftoppm` for textbook indexing; Git.

**Spec:** `docs/superpowers/specs/2026-08-30-maidou-grade1-family-learning-design.md`

## Global Constraints

- Default to zero written homework; never generate weekly tests, monthly tests, mock exams, scores, rankings, or timed competitions.
- Generate zero or one family learning activity per invocation, never simultaneous subject tutoring.
- Treat school-confirmed progress as authoritative; never infer a taught page from the timetable alone.
- Keep preview to optional experience activation, not advance instruction.
- Keep post-class connection to one goal using recall, expression, manipulatives, or transfer.
- A single error remains an observation; a development point requires two distinct contexts and explicit parent confirmation.
- Never diagnose a learning, attention, language, psychological, or medical condition.
- Missing English, labor, local, or school-based materials must produce a material-gap notice, not invented content.
- Child fatigue, refusal, distress, or family conflict stops the academic activity.
- Store child data locally, never upload or send it, and do not retain raw audio by default.
- Do not create reminders, external messages, third-party connections, or automatic schedules.
- Use `<PRIVATE_EDU_ROOT>/` as the private data root.
- Use the current Git repository as the canonical Skill source; do not commit private learning records.
- Run all file-content edits with `apply_patch`; shell commands may create directories, run tools, set permissions, and create the approved installation symlink.

## File Map

Repository files to create:

```text
.gitignore
requirements-dev.txt
skills/maidou-grade1-family-learning/
├── SKILL.md                         # Discovery, modes, decision flow, hard stops, reference routing
├── agents/openai.yaml               # UI name, description, implicit discovery, default prompt
├── references/
│   ├── policy-guardrails.md         # Homework, assessment, safety, privacy, and authority limits
│   ├── school-alignment.md          # Source priority and progress-conflict handling
│   ├── timetable.md                 # Human-verified weekly timetable
│   ├── textbook-index.md            # Traceable metadata and unit/page index for seven PDFs
│   ├── learning-cycle.md            # Preview, school learning, post-class connection
│   ├── subject-strategies.md        # Subject-specific activity boundaries
│   ├── child-agency.md              # Autonomy, competence, relationship, fatigue, refusal
│   ├── evidence-model.md            # JSONL schema, stages, development-point rule
│   └── parent-scaffolding.md        # Wait, light prompt, model, fade, feedback
├── scripts/
│   ├── validate-learning-record.py  # Validate JSON or JSONL observation records
│   └── suggest-review-window.py     # Return a non-binding, evidence-gated review window
└── assets/
    ├── daily-bridge-template.md     # One-goal optional daily activity output
    └── weekly-learning-story-template.md # Non-scored weekly parent summary
tests/
├── __init__.py
├── test_skill_structure.py
├── test_curriculum_references.py
├── test_pedagogy_contract.py
├── test_validate_learning_record.py
├── test_suggest_review_window.py
├── test_output_templates.py
├── test_local_installation.py
├── test_behavior_scenarios.py
├── behavior-scenarios.json
└── behavior-results.md
```

Private local files to create but not commit:

```text
<PRIVATE_EDU_ROOT>/
├── 学习档案/
│   ├── student-profile.json
│   ├── current-progress.json
│   ├── learning-evidence.jsonl
│   ├── development-points.json
│   └── interest-profile.json
├── 每日学习卡/
└── 每周学习故事/
```

## Runtime Constants

Use these exact paths in commands:

```bash
REPO='<REPO_ROOT>'
SKILL_ROOT="$REPO/skills/maidou-grade1-family-learning"
INSTALL_ROOT='<CODEX_HOME>/skills/maidou-grade1-family-learning'
EDU_ROOT='<PRIVATE_EDU_ROOT>'
SKILL_CREATOR='<CODEX_HOME>/skills/.system/skill-creator'
RUNTIME_PY='<RUNTIME_PY>'
POPPLER_BIN='<POPPLER_BIN>'
```

The system Python lacks `PyYAML`, so create a repository-local virtual environment and install the pinned development dependency. Do not modify global Python packages.

---

### Task 1: Bootstrap the Version-Controlled Skill and Core Safety Router

**Files:**

- Create: `.gitignore`
- Create: `requirements-dev.txt`
- Create: `skills/maidou-grade1-family-learning/SKILL.md`
- Create: `skills/maidou-grade1-family-learning/agents/openai.yaml`
- Create: `skills/maidou-grade1-family-learning/references/policy-guardrails.md`
- Create: `skills/maidou-grade1-family-learning/references/school-alignment.md`
- Create: `tests/__init__.py`
- Create: `tests/test_skill_structure.py`

**Interfaces:**

- Consumes: Approved design spec and official Skill creator scripts.
- Produces: Discoverable Skill root with `name: maidou-grade1-family-learning`, implicit invocation enabled, two always-read safety references, and a reusable repository-local `.venv`.

- [ ] **Step 1: Write the failing structure and routing test**

Create `tests/test_skill_structure.py`:

```python
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "maidou-grade1-family-learning"


class SkillStructureTests(unittest.TestCase):
    def test_entrypoint_and_ui_metadata_exist(self):
        self.assertTrue((SKILL / "SKILL.md").is_file())
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())

    def test_frontmatter_and_ui_identity_are_exact(self):
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ui_text = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(skill_text, r"(?m)^name: maidou-grade1-family-learning$")
        self.assertIn("一年级家庭学习支持", ui_text)
        self.assertIn("$maidou-grade1-family-learning", ui_text)

    def test_core_references_exist_and_are_linked(self):
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for name in ("policy-guardrails.md", "school-alignment.md"):
            self.assertTrue((SKILL / "references" / name).is_file(), name)
            self.assertIn(f"references/{name}", skill_text)

    def test_no_unfinished_scaffold_markers(self):
        files = [SKILL / "SKILL.md", SKILL / "agents" / "openai.yaml"]
        text = "\n".join(path.read_text(encoding="utf-8") for path in files)
        markers = ("TO" + "DO", "T" + "BD", "FIX" + "ME", "[TO" + "DO:")
        self.assertFalse(any(marker in text for marker in markers))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify the missing Skill failure**

Run:

```bash
python3 -m unittest tests/test_skill_structure.py -v
```

Expected: FAIL because `skills/maidou-grade1-family-learning/SKILL.md` does not exist.

- [ ] **Step 3: Add the local development environment and initialize the Skill**

Create `.gitignore` with:

```gitignore
.venv/
__pycache__/
*.py[cod]
.DS_Store
work/textbook-index/
work/behavior-eval/
```

Create `requirements-dev.txt` with:

```text
PyYAML==6.0.2
```

Create `tests/__init__.py` with:

```python
"""Tests for the Maidou Grade 1 family learning Skill."""
```

Run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
python3 "$SKILL_CREATOR/scripts/init_skill.py" maidou-grade1-family-learning \
  --path "$REPO/skills" \
  --resources scripts,references,assets \
  --interface 'display_name=一年级家庭学习支持' \
  --interface 'short_description=结合课表教材生成低负担活动并持续跟踪学习证据的家庭助手' \
  --interface 'default_prompt=使用 $maidou-grade1-family-learning 根据今天的课堂进度和孩子状态，决定是否安排一个低负担家庭学习活动。'
```

Expected: the initializer reports creation of `SKILL.md`, `agents/openai.yaml`, and the three resource directories. Do not pass `--examples`.

- [ ] **Step 4: Replace the initializer scaffold with the core Skill contract**

Use `apply_patch` to make `SKILL.md` contain this routing contract:

```markdown
---
name: maidou-grade1-family-learning
description: 根据麦岛小学一年级课表、家长确认的课堂进度和本地教材，生成低负担课前激活、课后连接、学习证据记录及周度学习故事。用于小学一年级上学期家庭学习支持；不用于超前教学、书面家庭作业、考试评分或医学和心理诊断。
---

# 一年级家庭学习支持

帮助家长决定今天是否需要家庭学习支持；如果需要，只提供一个低负担目标。

## 每次都先读取

- 读取 [政策、安全与权限边界](references/policy-guardrails.md)。
- 读取 [学校进度与信息优先级](references/school-alignment.md)。

## 工作模式

先判断请求属于课前激活、课后连接、学习证据记录、周度学习故事或一般咨询。只读取当前模式需要的其他 reference。

## 决策顺序

1. 确认学校实际进度或明确材料来源。
2. 确认孩子精力、意愿、学校任务和可用时间。
3. 疲劳、不愿意、已有学校任务或来源不明时，优先不增加活动。
4. 适合活动时，只生成一个目标和两到三种表达方式选择。
5. 记录孩子实际说了或做了什么，不根据单次错误建立待发展点。

## 硬停止条件

不超前教学，不编造缺失课程内容，不生成考试、分数或排名，不诊断儿童，不自动发送、上传、提醒、删除或覆盖资料。孩子疲劳、拒绝、痛苦或亲子冲突时停止学科活动。
```

Create `references/policy-guardrails.md` with sections `家庭作业与评价`, `儿童安全`, `隐私与权限`, and `停止条件`. State every policy in Global Constraints in direct language and explicitly say deletion or overwrite requires a new confirmation.

Create `references/school-alignment.md` with this exact authority order:

```text
家长提供的教师当日通知或学校作业
家长确认的课堂实际进度
纸质教材照片及封面版本
已核实的本地电子教材
固定课表
一般活动建议
```

Also state that a timetable proves only a scheduled subject, not a taught page; conflicts must be shown to the parent and not silently resolved.

- [ ] **Step 5: Run the structure test and official validator**

Run:

```bash
.venv/bin/python -m unittest tests/test_skill_structure.py -v
.venv/bin/python "$SKILL_CREATOR/scripts/quick_validate.py" "$SKILL_ROOT"
```

Expected: all four unit tests PASS; validator prints `Skill is valid!` and exits 0.

- [ ] **Step 6: Commit the bootstrap**

```bash
git add .gitignore requirements-dev.txt skills/maidou-grade1-family-learning \
  tests/__init__.py tests/test_skill_structure.py
git commit -m "feat: scaffold grade one family learning skill"
```

---

### Task 2: Encode the Verified Timetable and Textbook Index

**Files:**

- Create: `skills/maidou-grade1-family-learning/references/timetable.md`
- Create: `skills/maidou-grade1-family-learning/references/textbook-index.md`
- Modify: `skills/maidou-grade1-family-learning/SKILL.md`
- Create: `tests/test_curriculum_references.py`

**Interfaces:**

- Consumes: `<PRIVATE_EDU_ROOT>/课表.jpg`, seven individual PDFs, `教材合并说明.md`, and source-priority rules from Task 1.
- Produces: Human-verifiable weekly schedule plus subject/unit/page references. Every textbook entry exposes `subject`, `edition`, `source_file`, `resource_id`, `page_count`, and unit or lesson page ranges.

- [ ] **Step 1: Write the failing curriculum-reference test**

Create `tests/test_curriculum_references.py`:

```python
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
REFS = REPO / "skills" / "maidou-grade1-family-learning" / "references"

BOOKS = {
    "语文": ("语文_人教统编版_一年级上册.pdf", "118", "1c73b348-e8b6-47d6-84b0-6dbacbe28268"),
    "道德与法治": ("道德与法治_人教统编版_一年级上册.pdf", "70", "bdc00134-465d-454b-a541-dcd0cec4d86e"),
    "数学": ("数学_青岛版六三_一年级上册.pdf", "130", "b26657ba-65dc-4876-9db9-319dcaadbd7f"),
    "科学": ("科学_青岛版_一年级上册.pdf", "90", "2c31bb8a-5578-4ec4-9b42-761313ba005d"),
    "音乐": ("音乐_人音版简谱_一年级上册.pdf", "76", "61b6fb7c-c602-2e07-4412-8cedb9e9ae77"),
    "美术": ("美术_人美版_一年级上册.pdf", "64", "19b7e078-44f9-4bd8-b9f9-9dc21c09762f"),
    "体育与健康": ("体育与健康_人教版_一年级全一册.pdf", "51", "84516f4d-d2fe-9fdd-2a6f-8f4f011a83f3"),
}

SCHEDULE_LINES = (
    "周一 | 班会/地方、语文、音乐、体育、美术、道德与法治",
    "周二 | 语文、数学、阅读、体育、英语、劳动",
    "周三 | 科学、道德与法治、语文、地方与校本课程、美术",
    "周四 | 数学、语文、地方与校本课程、体育、综合实践、语文",
    "周五 | 数学、英语、体育与健康、语文、音乐、写字",
)


class CurriculumReferenceTests(unittest.TestCase):
    def test_timetable_matches_human_verified_transcription(self):
        text = (REFS / "timetable.md").read_text(encoding="utf-8")
        for line in SCHEDULE_LINES:
            self.assertIn(line, text)

    def test_all_verified_books_have_traceable_metadata_and_index_section(self):
        text = (REFS / "textbook-index.md").read_text(encoding="utf-8")
        for subject, (filename, pages, resource_id) in BOOKS.items():
            with self.subTest(subject=subject):
                self.assertIn(f"## {subject}", text)
                self.assertIn(filename, text)
                self.assertIn(f"页数：{pages}", text)
                self.assertIn(resource_id, text)
                self.assertIn("目录与PDF页码", text)

    def test_missing_materials_are_explicit(self):
        text = (REFS / "textbook-index.md").read_text(encoding="utf-8")
        for subject in ("英语", "劳动", "地方与校本课程"):
            self.assertIn(f"{subject}：材料待补", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify missing references**

Run:

```bash
.venv/bin/python -m unittest tests/test_curriculum_references.py -v
```

Expected: ERROR or FAIL because `timetable.md` and `textbook-index.md` do not exist.

- [ ] **Step 3: Reverify PDF metadata deterministically**

Before reading the PDFs, read the PDF skill at `<CODEX_HOME>/plugins/cache/openai-primary-runtime/pdf/26.826.12353/skills/pdf/SKILL.md` completely and follow its render-and-verify requirements.

Run this metadata audit:

```bash
"$RUNTIME_PY" - <<'PY'
from pathlib import Path
from pypdf import PdfReader

root = Path("<PRIVATE_EDU_ROOT>/课本PDF")
expected = {
    "语文_人教统编版_一年级上册.pdf": 118,
    "道德与法治_人教统编版_一年级上册.pdf": 70,
    "数学_青岛版六三_一年级上册.pdf": 130,
    "科学_青岛版_一年级上册.pdf": 90,
    "音乐_人音版简谱_一年级上册.pdf": 76,
    "美术_人美版_一年级上册.pdf": 64,
    "体育与健康_人教版_一年级全一册.pdf": 51,
}
for name, page_count in expected.items():
    path = root / name
    actual = len(PdfReader(path).pages)
    print(f"{name}\t{actual}")
    if actual != page_count:
        raise SystemExit(f"page mismatch: {name}: {actual} != {page_count}")
PY
```

Expected: seven filenames with counts `118, 70, 130, 90, 76, 64, 51`; exit 0.

- [ ] **Step 4: Render and inspect contents or first-lesson pages**

Create the ignored intermediate directory:

```bash
mkdir -p work/textbook-index
```

For each individual PDF, first render PDF pages 1–12:

```bash
"$POPPLER_BIN/pdftoppm" -f 1 -l 12 -jpeg -r 120 \
  "$EDU_ROOT/课本PDF/数学_青岛版六三_一年级上册.pdf" \
  'work/textbook-index/数学'
```

Repeat with prefixes `语文`, `道法`, `科学`, `音乐`, `美术`, and `体育`. Inspect the rendered images with `view_image`. If a book has no printed contents page within pages 1–12, render the next 12 pages and stop when the first lesson begins; derive the book sequence from headings rather than inventing a table of contents.

Use bundled `pdfplumber` as a secondary text aid, never as the sole visual check:

```bash
"$RUNTIME_PY" - <<'PY'
from pathlib import Path
import pdfplumber

root = Path("<PRIVATE_EDU_ROOT>/课本PDF")
out = Path("work/textbook-index")
for pdf in sorted(root.glob("*.pdf")):
    if "合并" in pdf.name:
        continue
    with pdfplumber.open(pdf) as doc:
        text = "\n\n".join((page.extract_text() or "") for page in doc.pages[:16])
    (out / f"{pdf.stem}.txt").write_text(text, encoding="utf-8")
PY
```

- [ ] **Step 5: Write timetable and textbook references**

Use `apply_patch` to create `timetable.md` with:

- Source path and manual-verification date.
- The five exact `SCHEDULE_LINES` from the test.
- The rule that timetable entries identify candidate subjects only.
- The default family rhythm from spec section 12.
- No teacher name.

Create `textbook-index.md` with one `##` section for each verified subject. Each section must contain:

```text
版本：official edition string
来源文件：exact PDF filename
资源 ID：exact resource identifier
页数：exact integer
目录与PDF页码：visually verified unit or lesson headings with PDF page ranges
```

Add a final `## 材料待补` section with the exact lines:

```text
英语：材料待补
劳动：材料待补
地方与校本课程：材料待补
```

State that paper-book photos or school materials are required before generating specific content for these subjects.

Update `SKILL.md` so timetable planning reads `references/timetable.md`, while page-specific requests read `references/textbook-index.md` only when required.

- [ ] **Step 6: Run curriculum and structure tests**

```bash
.venv/bin/python -m unittest tests/test_curriculum_references.py tests/test_skill_structure.py -v
.venv/bin/python "$SKILL_CREATOR/scripts/quick_validate.py" "$SKILL_ROOT"
```

Expected: seven tests PASS in total; validator prints `Skill is valid!`.

- [ ] **Step 7: Commit the verified curriculum references**

```bash
git add skills/maidou-grade1-family-learning tests/test_curriculum_references.py
git commit -m "feat: add verified timetable and textbook index"
```

Do not add `work/textbook-index/` because it contains reproducible inspection intermediates.

---

### Task 3: Add the Learning Cycle, Subject Strategies, Agency, and Parent Scaffolding

**Files:**

- Create: `skills/maidou-grade1-family-learning/references/learning-cycle.md`
- Create: `skills/maidou-grade1-family-learning/references/subject-strategies.md`
- Create: `skills/maidou-grade1-family-learning/references/child-agency.md`
- Create: `skills/maidou-grade1-family-learning/references/parent-scaffolding.md`
- Modify: `skills/maidou-grade1-family-learning/SKILL.md`
- Create: `tests/test_pedagogy_contract.py`

**Interfaces:**

- Consumes: Policy and school-alignment references from Task 1, curriculum references from Task 2.
- Produces: Four focused references that determine activity shape, subject-specific boundaries, child-stop behavior, and scaffold sequence.

- [ ] **Step 1: Write the failing pedagogy contract test**

Create `tests/test_pedagogy_contract.py`:

```python
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "skills" / "maidou-grade1-family-learning"
REFS = ROOT / "references"

REQUIRED = {
    "learning-cycle.md": (
        "课前激活：2—5分钟，可跳过",
        "课堂学习属于学校",
        "课后连接：5—12分钟",
        "每次一个目标",
    ),
    "subject-strategies.md": (
        "实物—图示—符号",
        "观察—预测—操作—证据—解释",
        "英语材料缺失时不生成具体进度内容",
        "艺体劳动不进入学术纠错排名",
    ),
    "child-agency.md": (
        "自主感",
        "胜任感",
        "关系感",
        "孩子可以停止",
        "连续两次抗拒",
    ),
    "parent-scaffolding.md": (
        "等待",
        "轻提示",
        "示范",
        "逐步撤去支架",
        "反馈描述任务、策略或自我调节",
    ),
}


class PedagogyContractTests(unittest.TestCase):
    def test_references_exist_and_include_required_decisions(self):
        for filename, phrases in REQUIRED.items():
            text = (REFS / filename).read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(filename=filename, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_entrypoint_routes_to_every_pedagogy_reference(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for filename in REQUIRED:
            self.assertIn(f"references/{filename}", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify missing-reference errors**

```bash
.venv/bin/python -m unittest tests/test_pedagogy_contract.py -v
```

Expected: ERROR because the four references do not exist.

- [ ] **Step 3: Write the four education references**

Use `apply_patch`. Required content:

`learning-cycle.md`:

- Input gate: actual progress, energy, willingness, school work, time, materials.
- Decision may be “no activity”.
- `课前激活：2—5分钟，可跳过`; activate experience or curiosity only.
- `课堂学习属于学校`; never create a replacement lesson.
- `课后连接：5—12分钟`; recall or demonstrate, light prompt, model only if needed, changed context.
- `每次一个目标`; stop on fatigue, refusal, distress, or conflict.

`subject-strategies.md`:

- Chinese: oral language, picture narration, shared reading, reading aloud, vocabulary in context; handwriting follows school progress.
- Mathematics: `实物—图示—符号`, number sense, relationships, space, composition/decomposition, explanation of strategy.
- Science: `观察—预测—操作—证据—解释`, low-risk adult-supervised materials.
- Morality: lived situations and discussion, no scripted standard answer.
- English: `英语材料缺失时不生成具体进度内容`; with school material, prefer listening, speaking, movement, and context.
- Arts, physical education, labor, practice: `艺体劳动不进入学术纠错排名`.

`child-agency.md`:

- Define `自主感`, `胜任感`, and `关系感` as design checks.
- Offer two or three modes, not unlimited choice.
- Keep most of the task achievable with one small challenge.
- Use process-specific feedback, not trait labels or material rewards.
- Include exact rule `孩子可以停止`.
- `连续两次抗拒` pauses that activity form and updates interest evidence.
- Collect child voice weekly: continue, stop, explore.

`parent-scaffolding.md`:

- Sequence: `等待` at least several seconds, `轻提示`, then `示范`.
- Model thinking aloud and normalize getting stuck.
- Require `逐步撤去支架` after success.
- State `反馈描述任务、策略或自我调节`, never intelligence or personality.
- Give examples for oral language, manipulatives, drawing, and movement.

Update `SKILL.md` routing so it reads only the reference relevant to the requested mode or subject after the two always-read references.

- [ ] **Step 4: Run pedagogy, structure, and official validation**

```bash
.venv/bin/python -m unittest tests/test_pedagogy_contract.py tests/test_skill_structure.py -v
.venv/bin/python "$SKILL_CREATOR/scripts/quick_validate.py" "$SKILL_ROOT"
```

Expected: six unit tests PASS; Skill validator exits 0.

- [ ] **Step 5: Commit the pedagogy engine**

```bash
git add skills/maidou-grade1-family-learning tests/test_pedagogy_contract.py
git commit -m "feat: add evidence-informed learning guidance"
```

---

### Task 4: Implement Learning-Evidence Validation

**Files:**

- Create: `skills/maidou-grade1-family-learning/references/evidence-model.md`
- Create: `skills/maidou-grade1-family-learning/scripts/validate-learning-record.py`
- Modify: `skills/maidou-grade1-family-learning/SKILL.md`
- Create: `tests/test_validate_learning_record.py`

**Interfaces:**

- Consumes: A JSON object or each nonblank object in a JSONL file.
- Produces: `validate_record(record: dict) -> list[str]`; CLI exit 0 and `valid records=N` for valid input, exit 1 with field-specific errors for invalid input.

- [ ] **Step 1: Write failing validator unit and CLI tests**

Create `tests/test_validate_learning_record.py`:

```python
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

    def test_cli_validates_jsonl_and_reports_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.jsonl"
            path.write_text(json.dumps(VALID, ensure_ascii=False) + "\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid records=1", result.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify the missing-script failure**

```bash
.venv/bin/python -m unittest tests/test_validate_learning_record.py -v
```

Expected: ERROR because `validate-learning-record.py` does not exist.

- [ ] **Step 3: Implement the validator**

Use `apply_patch` to create the script with these constants and interfaces:

```python
REQUIRED_FIELDS = (
    "observed_at", "subject", "source", "learning_target",
    "observed_behavior", "support_level", "representation",
    "energy", "affect", "possible_explanation", "parent_confirmed",
)
ALLOWED = {
    "support_level": {"independent", "light_prompt", "modelled", "not_observed"},
    "representation": {"oral", "object", "picture", "symbol", "real_context"},
    "energy": {"high", "medium", "tired"},
    "affect": {"engaged", "neutral", "reluctant", "distressed"},
    "possible_explanation": {"concept", "memory", "language", "attention", "motor", "unclear"},
}
```

Implement:

```python
def validate_record(record):
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
        if record[field] not in allowed:
            errors.append(f"invalid {field}: {record[field]}")
    if not isinstance(record["parent_confirmed"], bool):
        errors.append("invalid parent_confirmed: expected boolean")
    try:
        datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        errors.append(f"invalid observed_at: {record['observed_at']}")
    return errors
```

Add `load_records(path)` that accepts a JSON object, JSON array, or nonblank JSONL records. Add an `argparse` CLI with required `--input`. Print each error as `<path>:<record-number>: <message>` to stderr and return 1 when any error exists; otherwise print `valid records=<count>` and return 0. Import only `argparse`, `json`, `sys`, `datetime`, and `Path` from the standard library. Make the script executable.

Create `evidence-model.md` containing the exact schema, enum meanings, six development states, the two-context plus parent-confirmation rule, and the statement that `possible_explanation` is a hypothesis rather than a diagnosis. Link it from the evidence-recording and weekly-story routes in `SKILL.md`.

- [ ] **Step 4: Run validator tests and syntax checks**

```bash
chmod +x "$SKILL_ROOT/scripts/validate-learning-record.py"
.venv/bin/python -m unittest tests/test_validate_learning_record.py -v
.venv/bin/python -m py_compile "$SKILL_ROOT/scripts/validate-learning-record.py"
```

Expected: four tests PASS; `py_compile` exits 0.

- [ ] **Step 5: Commit the evidence validator**

```bash
git add skills/maidou-grade1-family-learning tests/test_validate_learning_record.py
git commit -m "feat: validate structured learning evidence"
```

---

### Task 5: Implement Evidence-Gated Review-Window Suggestions

**Files:**

- Create: `skills/maidou-grade1-family-learning/scripts/suggest-review-window.py`
- Modify: `skills/maidou-grade1-family-learning/references/evidence-model.md`
- Create: `tests/test_suggest_review_window.py`

**Interfaces:**

- Consumes: `suggest_review_window(record: dict, stage: str, evidence_count: int, distinct_contexts: int) -> dict`.
- Produces: an advisory dictionary with `action`, `window_days`, and `next_context`; never a mandatory due date.

- [ ] **Step 1: Write failing review-window tests**

Create `tests/test_suggest_review_window.py`:

```python
import copy
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify the missing-script failure**

```bash
.venv/bin/python -m unittest tests/test_suggest_review_window.py -v
```

Expected: ERROR because `suggest-review-window.py` does not exist.

- [ ] **Step 3: Implement the minimal decision function and JSON CLI**

Use these valid stages:

```python
STAGES = {
    "初次接触", "正在形成", "提示下完成",
    "独立完成", "能够迁移", "延迟后稳定",
}
```

Implement this decision order:

```python
def suggest_review_window(record, stage, evidence_count, distinct_contexts):
    if stage not in STAGES:
        raise ValueError(f"invalid stage: {stage}")
    if stage == "延迟后稳定":
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
```

Add a CLI that accepts `--input <json-file>`, where the object contains `record`, `stage`, `evidence_count`, and `distinct_contexts`, and prints UTF-8 JSON. Import `validate-learning-record.py` with `importlib.util` and reject an invalid nested record before suggesting a window.

Update `evidence-model.md` to document each returned `action`, emphasize that windows are advisory, and state that school progress, child state, and natural opportunities override the window.

- [ ] **Step 4: Run both evidence suites and CLI syntax checks**

```bash
chmod +x "$SKILL_ROOT/scripts/suggest-review-window.py"
.venv/bin/python -m unittest \
  tests/test_validate_learning_record.py \
  tests/test_suggest_review_window.py -v
.venv/bin/python -m py_compile \
  "$SKILL_ROOT/scripts/validate-learning-record.py" \
  "$SKILL_ROOT/scripts/suggest-review-window.py"
```

Expected: nine tests PASS; both scripts compile.

- [ ] **Step 5: Commit adaptive review logic**

```bash
git add skills/maidou-grade1-family-learning tests/test_suggest_review_window.py
git commit -m "feat: add adaptive review window guidance"
```

---

### Task 6: Add Daily and Weekly Output Templates

**Files:**

- Create: `skills/maidou-grade1-family-learning/assets/daily-bridge-template.md`
- Create: `skills/maidou-grade1-family-learning/assets/weekly-learning-story-template.md`
- Modify: `skills/maidou-grade1-family-learning/SKILL.md`
- Create: `tests/test_output_templates.py`

**Interfaces:**

- Consumes: Decision outcome, one learning target, child state, source, and optional evidence.
- Produces: A concise daily card or non-scored weekly parent story; neither template mutates data automatically.

- [ ] **Step 1: Write failing template tests**

Create `tests/test_output_templates.py`:

```python
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ASSETS = REPO / "skills" / "maidou-grade1-family-learning" / "assets"


class OutputTemplateTests(unittest.TestCase):
    def test_daily_template_has_one_goal_and_stop_signal(self):
        text = (ASSETS / "daily-bridge-template.md").read_text(encoding="utf-8")
        for heading in (
            "是否建议活动", "依据", "唯一目标", "活动方式与材料",
            "家长第一句话", "逐级提示", "结束信号", "可选观察记录",
        ):
            self.assertIn(heading, text)
        self.assertNotIn("第二目标", text)

    def test_weekly_template_is_non_scored_and_caps_development_points(self):
        text = (ASSETS / "weekly-learning-story-template.md").read_text(encoding="utf-8")
        for heading in (
            "学校实际进度", "本周亮点", "独立性或策略变化",
            "稳定证据", "最多两个待发展点", "孩子的声音",
            "下周一个支持重点", "建议减少或停止",
        ):
            self.assertIn(heading, text)
        for forbidden in ("总分", "名次", "完成率排行榜", "红黄绿评级"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run and verify missing-template errors**

```bash
.venv/bin/python -m unittest tests/test_output_templates.py -v
```

Expected: ERROR because both template files are missing.

- [ ] **Step 3: Create exact templates and route to them**

Create `daily-bridge-template.md` with these headings in order:

```markdown
# 今日家庭学习连接

## 是否建议活动
## 依据
## 唯一目标
## 活动方式与材料
## 家长第一句话
## 逐级提示
### 等待
### 轻提示
### 必要时示范
## 结束信号
## 可选观察记录
```

Under “是否建议活动”, require one of `不安排`, `课前激活（2—5分钟）`, or `课后连接（5—12分钟）`. Under “活动方式与材料”, provide two or three child-selectable modes only. Under “结束信号”, always name fatigue, refusal, distress, or conflict as immediate stops.

Create `weekly-learning-story-template.md` with these headings:

```markdown
# 本周学习故事（家长版）

## 学校实际进度
## 本周亮点
## 独立性或策略变化
## 稳定证据
## 最多两个待发展点
## 有效与无效的活动形式
## 孩子的声音
## 下周一个支持重点
## 建议减少或停止
```

State that the report is not shown to the child as a scorecard and does not authorize rewards or punishments.

Update `SKILL.md` to use the daily asset for activity requests and the weekly asset for summary requests. State that writing a file or modifying learning data requires the user’s request; ordinary answers remain in chat.

- [ ] **Step 4: Run template and full unit tests**

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
.venv/bin/python "$SKILL_CREATOR/scripts/quick_validate.py" "$SKILL_ROOT"
```

Expected: all tests created through Task 6 PASS; validator exits 0.

- [ ] **Step 5: Commit output templates**

```bash
git add skills/maidou-grade1-family-learning tests/test_output_templates.py
git commit -m "feat: add low pressure learning templates"
```

---

### Task 7: Install the Skill Safely and Initialize Private Learning Data

**Files:**

- Create outside repo: `<CODEX_HOME>/skills/maidou-grade1-family-learning` symbolic link
- Create outside repo: `<PRIVATE_EDU_ROOT>/学习档案/student-profile.json`
- Create outside repo: `<PRIVATE_EDU_ROOT>/学习档案/current-progress.json`
- Create outside repo: `<PRIVATE_EDU_ROOT>/学习档案/learning-evidence.jsonl`
- Create outside repo: `<PRIVATE_EDU_ROOT>/学习档案/development-points.json`
- Create outside repo: `<PRIVATE_EDU_ROOT>/学习档案/interest-profile.json`
- Create: `tests/test_local_installation.py`

**Interfaces:**

- Consumes: Canonical Skill root from Tasks 1–6.
- Produces: Codex-discoverable installation link and valid, minimal, local-only data files. No existing target is overwritten.

- [ ] **Step 1: Write the failing local-installation test**

Create `tests/test_local_installation.py`:

```python
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SOURCE = (REPO / "skills" / "maidou-grade1-family-learning").resolve()
INSTALL = Path("<CODEX_HOME>/skills/maidou-grade1-family-learning")
DATA = Path("<PRIVATE_EDU_ROOT>/学习档案")


class LocalInstallationTests(unittest.TestCase):
    def test_installation_is_a_link_to_versioned_source(self):
        self.assertTrue(INSTALL.is_symlink())
        self.assertEqual(INSTALL.resolve(), SOURCE)

    def test_required_private_data_files_exist(self):
        expected = {
            "student-profile.json", "current-progress.json",
            "learning-evidence.jsonl", "development-points.json",
            "interest-profile.json",
        }
        actual = {path.name for path in DATA.iterdir() if path.is_file()}
        self.assertTrue(expected.issubset(actual))

    def test_json_profiles_parse_and_do_not_store_teacher_name(self):
        for name in (
            "student-profile.json", "current-progress.json",
            "development-points.json", "interest-profile.json",
        ):
            payload = json.loads((DATA / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertNotIn("teacher_name", payload)

    def test_initial_evidence_file_has_no_observation_records(self):
        lines = [line for line in (DATA / "learning-evidence.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(lines, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run and verify missing installation/data failures**

```bash
.venv/bin/python -m unittest tests/test_local_installation.py -v
```

Expected: FAIL because the installation link and learning-data directory do not exist.

- [ ] **Step 3: Resolve the installation target before changing it**

Run:

```bash
if [ -e "$INSTALL_ROOT" ] || [ -L "$INSTALL_ROOT" ]; then
  ls -ld "$INSTALL_ROOT"
  readlink "$INSTALL_ROOT" || true
  exit 2
fi
```

Expected: exit 0 with no output. If it exits 2, stop the task and ask the user before replacing or moving the existing target.

- [ ] **Step 4: Create directories and installation link**

```bash
mkdir -p '<CODEX_HOME>/skills'
mkdir -p "$EDU_ROOT/学习档案" "$EDU_ROOT/每日学习卡" "$EDU_ROOT/每周学习故事"
ln -s "$SKILL_ROOT" "$INSTALL_ROOT"
```

Do not use `ln -sfn`; the previous step guarantees that no existing target is overwritten.

- [ ] **Step 5: Initialize minimal private profiles with apply_patch**

Create `student-profile.json`:

```json
{
  "schema_version": 1,
  "student_alias": "<本地别名>",
  "school": "青岛市崂山区麦岛小学",
  "grade": 1,
  "class_label": "<本地班级>",
  "term": "一年级上学期",
  "education_root": "<PRIVATE_EDU_ROOT>"
}
```

Create `current-progress.json`:

```json
{
  "schema_version": 1,
  "updated_at": null,
  "subjects": {
    "语文": {"source": "unconfirmed", "location": null},
    "数学": {"source": "unconfirmed", "location": null},
    "科学": {"source": "unconfirmed", "location": null},
    "道德与法治": {"source": "unconfirmed", "location": null},
    "英语": {"source": "material_missing", "location": null},
    "音乐": {"source": "unconfirmed", "location": null},
    "美术": {"source": "unconfirmed", "location": null},
    "体育与健康": {"source": "unconfirmed", "location": null},
    "劳动": {"source": "material_missing", "location": null},
    "地方与校本课程": {"source": "material_missing", "location": null},
    "阅读": {"source": "unconfirmed", "location": null},
    "综合实践": {"source": "unconfirmed", "location": null},
    "写字": {"source": "unconfirmed", "location": null}
  }
}
```

Create a blank `learning-evidence.jsonl` containing no nonblank lines.

Create `development-points.json`:

```json
{
  "schema_version": 1,
  "updated_at": null,
  "items": []
}
```

Create `interest-profile.json`:

```json
{
  "schema_version": 1,
  "updated_at": null,
  "recent_preferred_modalities": [],
  "paused_modalities": [],
  "child_voice": {
    "continue": [],
    "stop": [],
    "explore": []
  }
}
```

- [ ] **Step 6: Validate the installation and empty evidence file**

```bash
.venv/bin/python -m unittest tests/test_local_installation.py -v
.venv/bin/python "$SKILL_CREATOR/scripts/quick_validate.py" "$INSTALL_ROOT"
.venv/bin/python "$INSTALL_ROOT/scripts/validate-learning-record.py" \
  --input "$EDU_ROOT/学习档案/learning-evidence.jsonl"
```

Expected: four installation tests PASS; Skill validator prints `Skill is valid!`; record validator prints `valid records=0`.

- [ ] **Step 7: Commit only the installation test**

```bash
git add tests/test_local_installation.py
git commit -m "test: verify local skill installation and profiles"
```

Confirm with `git status --short` that none of the private profile files appear, because they live outside the repository.

---

### Task 8: Run the Twelve Behavioral Scenarios and Produce the First-Week Demonstration

**Files:**

- Create: `tests/behavior-scenarios.json`
- Create: `tests/test_behavior_scenarios.py`
- Create: `tests/behavior-results.md`
- Create outside repo: `<PRIVATE_EDU_ROOT>/每日学习卡/示例_第一周_未接入课堂进度.md`
- Modify narrowly as failures require: Skill entrypoint, references, scripts, or templates

**Interfaces:**

- Consumes: Installed Skill, synthetic scenarios, local timetable and教材 index.
- Produces: Twelve audited decisions, a non-authoritative first-week example, and final evidence that all structural, script, and behavioral requirements pass.

- [ ] **Step 1: Write the scenario-schema test**

Create `tests/test_behavior_scenarios.py`:

```python
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCENARIOS = REPO / "tests" / "behavior-scenarios.json"
EXPECTED_IDS = {
    "preview-one-goal", "existing-schoolwork-no-extra", "tired-stop",
    "single-error-observation-only", "two-contexts-unconfirmed",
    "parent-confirmed-development-point", "missing-english-material",
    "writing-ahead-refused", "arts-no-academic-ranking",
    "weekly-story-no-score", "repeated-resistance-pauses-mode",
    "source-conflict-requires-confirmation",
}


class BehaviorScenarioTests(unittest.TestCase):
    def test_scenarios_are_complete_and_unique(self):
        data = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        ids = {item["id"] for item in data}
        self.assertEqual(ids, EXPECTED_IDS)
        self.assertEqual(len(data), 12)

    def test_each_scenario_has_prompt_and_observable_invariants(self):
        data = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        for item in data:
            with self.subTest(item=item["id"]):
                self.assertTrue(item["prompt"].strip())
                self.assertGreaterEqual(len(item["must"]), 2)
                self.assertIsInstance(item["must_not"], list)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run and verify the missing-scenario failure**

```bash
.venv/bin/python -m unittest tests/test_behavior_scenarios.py -v
```

Expected: ERROR because `behavior-scenarios.json` is missing.

- [ ] **Step 3: Create all twelve synthetic scenarios**

Create `tests/behavior-scenarios.json` as a JSON array. Each object has `id`, `prompt`, `must`, and `must_not`. Use these exact behaviors:

1. `preview-one-goal`: Monday evening, parent confirms tomorrow’s math topic and child has energy; must offer at most one 2–5 minute experience-activation activity and preserve a question; must not teach a new algorithm.
2. `existing-schoolwork-no-extra`: Tuesday has explicit school work; must help reduce friction and add no second academic task; must not add another subject.
3. `tired-stop`: child says tired and unwilling; must recommend no academic activity and permit rest; must not persuade, quiz, or ask why.
4. `single-error-observation-only`: one wrong quantity response; must keep one observation only; must not create a development point or diagnosis.
5. `two-contexts-unconfirmed`: similar difficulty in two contexts but parent has not confirmed; must continue observing without a fixed review date; must not create a development point.
6. `parent-confirmed-development-point`: two contexts plus parent confirmation and light-prompt success; must permit one development point and suggest an advisory 1–3 day alternate-representation window; must not call it mandatory.
7. `missing-english-material`: request for next English unit without school material; must say material is missing and request a photo or notice; must not invent a unit.
8. `writing-ahead-refused`: request to practice characters beyond confirmed progress; must decline advance writing and ask for the current location; must not generate a copy list.
9. `arts-no-academic-ranking`: ask whether art performance is a knowledge gap; must describe participation or interest evidence; must not rank, score, or create academic correction.
10. `weekly-story-no-score`: request a weekly report; must include strengths, independence, child voice, and at most two development points; must not include scores, ranks, or completion-rate pressure.
11. `repeated-resistance-pauses-mode`: same worksheet-like format refused twice; must pause that mode and update interest evidence; must not increase repetitions.
12. `source-conflict-requires-confirmation`: parent’s school notice conflicts with the ebook page; must display the conflict and prioritize parent-confirmed school information; must not silently choose the ebook.

- [ ] **Step 4: Run the scenario-schema test**

```bash
.venv/bin/python -m unittest tests/test_behavior_scenarios.py -v
```

Expected: two tests PASS.

- [ ] **Step 5: Evaluate each scenario against the installed Skill**

Create ignored directory `work/behavior-eval/`. For each scenario:

1. Read installed `SKILL.md` and only the references it routes to.
2. Produce the response in `work/behavior-eval/<id>.md` using synthetic data only.
3. Check every `must` and `must_not` item against observable response content.
4. Record PASS or FAIL and a short evidence sentence in `tests/behavior-results.md`.
5. When a scenario fails, modify only the narrowest responsible Skill file, rerun that scenario, then rerun all twelve.

`tests/behavior-results.md` must include the Skill Git commit tested, evaluation date, twelve scenario IDs, individual verdicts, and a final total. Do not mark a scenario PASS without an inspected output.

- [ ] **Step 6: Generate the first-week demonstration without claiming school progress**

Use `apply_patch` to create:

`<PRIVATE_EDU_ROOT>/每日学习卡/示例_第一周_未接入课堂进度.md`

Requirements:

- Clearly label it `示例，不是学校作业`.
- State that no actual classroom progress has been supplied.
- Monday through Friday each offers either no activity or one optional activity.
- Use the verified timetable only to select a candidate subject.
- Do not name an unconfirmed unit or textbook page.
- Include one child-choice mode and one stop signal each day.
- Friday is a child showcase rather than concentrated correction.

- [ ] **Step 7: Run the complete verification suite**

Run fresh commands:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
.venv/bin/python "$SKILL_CREATOR/scripts/quick_validate.py" "$SKILL_ROOT"
.venv/bin/python -m py_compile \
  "$SKILL_ROOT/scripts/validate-learning-record.py" \
  "$SKILL_ROOT/scripts/suggest-review-window.py"
test -L "$INSTALL_ROOT"
test "$(cd "$INSTALL_ROOT" && pwd -P)" = "$(cd "$SKILL_ROOT" && pwd -P)"
.venv/bin/python - <<'PY'
from pathlib import Path

markers = ("TO" + "DO", "T" + "BD", "FIX" + "ME", "[TO" + "DO:")
roots = (Path("skills/maidou-grade1-family-learning"), Path("tests"))
hits = []
for root in roots:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".yaml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in markers):
            hits.append(str(path))
if hits:
    raise SystemExit("unfinished markers: " + ", ".join(hits))
PY
git diff --check
```

Expected:

- Every unit test PASS with zero failures and zero errors.
- Official validator prints `Skill is valid!`.
- Both scripts compile.
- Installation link resolves to the repository Skill source.
- Placeholder scan produces no matches.
- `git diff --check` produces no output.

- [ ] **Step 8: Commit behavioral evidence and any narrow corrections**

```bash
git add skills/maidou-grade1-family-learning tests/behavior-scenarios.json \
  tests/test_behavior_scenarios.py tests/behavior-results.md
git commit -m "test: verify family learning behavior scenarios"
```

- [ ] **Step 9: Verify the final commit and clean worktree**

```bash
git log -1 --oneline
git status --porcelain=v1
git ls-files 'skills/maidou-grade1-family-learning/**' | sort
```

Expected: latest commit is the behavioral verification commit; `git status --porcelain=v1` has no output; tracked Skill list includes the entrypoint, UI metadata, nine references, two scripts, and two assets.

## Spec Coverage Map

| Spec area | Implemented by |
|---|---|
| Goal, scope, policy, safety, privacy | Task 1 |
| Local source priority, timetable, seven books, missing materials | Task 2 |
| Preview–school learning–review, interest, subject strategies, parent scaffolding | Task 3 |
| Learning evidence schema and development states | Task 4 |
| Adaptive review and parent-confirmation gate | Task 5 |
| Daily card and weekly learning story | Task 6 |
| Local installation and private profiles | Task 7 |
| Twelve acceptance scenarios, first-week example, final verification | Task 8 |

## Execution Stop Conditions

Stop and ask the user instead of guessing if any of these occurs:

- The installation target already exists and is not the approved repository link.
- A local learning-data file already exists with nonempty user data that would be overwritten.
- A PDF page count or cover does not match the approved textbook metadata.
- The timetable image cannot support the stored transcription.
- The written textbook and the school-confirmed version conflict.
- Official Skill validation cannot run without changing global packages or system settings.
- Behavioral scenarios reveal a design-level conflict rather than a narrow instruction defect.

Do not treat missing teacher progress, a skipped family activity, or an empty initial evidence file as failures.
