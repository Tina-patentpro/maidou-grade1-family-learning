# 学习证据模型

学习证据只记录孩子在一次具体情境中的实际表现，用于支持家长下一步观察；它不是评分、贴标签或诊断。

## JSONL 记录架构

`learning-evidence.jsonl` 每一非空行是一个 JSON 对象，且必须包含以下字段：

```json
{
  "observed_at": "ISO-8601时间",
  "subject": "学科",
  "source": "教材页码或学校材料",
  "learning_target": "本次唯一目标",
  "observed_behavior": "孩子实际说了或做了什么",
  "support_level": "independent | light_prompt | modelled | not_observed",
  "representation": "oral | object | picture | symbol | real_context",
  "energy": "high | medium | tired",
  "affect": "engaged | neutral | reluctant | distressed",
  "possible_explanation": "concept | memory | language | attention | motor | unclear",
  "parent_confirmed": false
}
```

`observed_at` 必须是 ISO-8601 时间；`subject`、`source`、`learning_target` 和 `observed_behavior` 必须是非空文本。`source` 保留学校通知、已确认课堂进度、教材页码或材料来源，`observed_behavior` 只写可观察到的原话或动作，不把推测写成事实。

## 枚举含义

| 字段 | 可用值及含义 |
| --- | --- |
| `support_level` | `independent`：无需帮助完成；`light_prompt`：等待后的一句简短提示足够；`modelled`：需要成人示范；`not_observed`：本次没有观察到该目标。 |
| `representation` | `oral`：口头表达；`object`：实物操作；`picture`：图片或图示；`symbol`：数字、文字或符号；`real_context`：真实生活情境。 |
| `energy` | `high`：精力充足；`medium`：可以进行短时活动；`tired`：疲劳，应优先休息或停止。 |
| `affect` | `engaged`：愿意投入；`neutral`：情绪平稳；`reluctant`：不愿继续；`distressed`：痛苦或明显不适，立即停止学科活动。 |
| `possible_explanation` | `concept`、`memory`、`language`、`attention`、`motor` 分别提示可能与概念、记忆、语言理解、注意或动作有关；`unclear` 表示尚不清楚。 |

`possible_explanation` 是待验证的假设，而不是诊断；不得据此诊断学习、注意力、语言、心理或医学状况。

## 六个发展状态

状态必须由累积证据更新，依次为：

1. `初次接触`：刚有机会接触该目标。
2. `正在形成`：表现仍在变化，需要自然观察。
3. `提示下完成`：在轻提示或支持后能完成。
4. `独立完成`：在当前情境中不需帮助完成。
5. `能够迁移`：在变化的表达方式或真实情境中仍能独立完成。
6. `延迟后稳定`：间隔后在自然情境中仍能独立完成。

单次错误只保留为观察事件。只有至少两个不同情境出现同类困难，并且家长明确确认，才可以建立一个待发展点；未满足任一条件时继续观察。单次独立完成不能推断为稳定，稳定必须有间隔后的自然、独立证据。

## 复习窗口建议

复习窗口只是一项建议，帮助家长决定下一次可留意的情境；它不是日历日期、截止时间、提醒或必须完成的安排。学校已确认的进度、孩子当时的状态和自然出现的机会始终优先于任何窗口建议。

建议函数会返回以下 `action`，并始终附带 `window_days` 与 `next_context`：

| `action` | 含义 |
| --- | --- |
| `continue_observing` | 家长尚未确认、证据少于两次或情境少于两个；继续自然观察并寻找不同情境。 |
| `no_review` | 本次目标未被观察到；等待自然机会，不安排复习。 |
| `wait_for_related_instruction` | 孩子需要成人示范；等待相关课堂教学或材料出现后再观察。 |
| `review` | 可在建议范围内、结合孩子状态和自然机会，以指定的下一种情境再观察。 |
| `archive` | 只有家长确认、已有至少两条且来自两个不同情境的证据，并且 `support_level` 为 `independent` 时，`延迟后稳定` 才可归档。`not_observed`、`modelled` 和 `light_prompt` 与稳定归档不相容，必须返回各自的观察、等待或建议分支。 |

`window_days` 只能是 `null` 或建议区间：轻提示完成时为 1–3 天，并在下次观察时明确换一种表达形式（如由实物改为口头或图示），而不只是重复同一种操作；能够迁移时为 7–14 天；其他已确认且可继续观察的表现为 3–7 天。它不要求在该区间内采取行动，也不替代学校进度、孩子状态或自然机会的判断。
