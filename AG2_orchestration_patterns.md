# AG2 (AutoGen) — Orchestration Patterns

> Notas de referencia sobre los patrones de orquestación de agentes en AG2
> (antes AutoGen). Fuente: documentación oficial de AG2.

## Learning objectives

- Describe the key orchestration patterns in AG2
- Identify use cases and methods for implementing orchestration patterns

## Overview

AG2 provides a flexible architecture for orchestrating AI agents through
structured interaction patterns, safeguards, and termination controls.

---

## 1. Two-Agent Chat

**Definition:** the simplest orchestration — two agents in a direct
back-and-forth conversation.

**How it works**
- An agent initiates the conversation with `initiate_chat()`, specifying
  a recipient, an initial message, and optional settings (`max_turns`,
  a summarizer method)
- The two agents exchange messages until `max_turns` is reached
- The interaction is summarized afterward (e.g. LLM-based reflection)

**Use case:** a student agent asks a teacher agent to explain the
triangle inequality theorem; a few clarifications, then a summary.

---

## 2. Sequential Chat

**Definition:** chains multiple two-agent chats in order, passing the
result (**carryover**) from one chat to the next.

**How it works**
- The initiating agent calls `initiate_chats()` with a list of
  recipient agents and their message settings
- Each interaction happens in sequence
- The output summary of each step feeds forward as context to the next

**Use case:** a document goes through ideation → drafting → formatting,
each stage building on the previous result.

---

## 3. Nested Chat

**Definition:** encapsulates a complex multi-agent workflow under a
single "trigger" agent — reusable and modular.

**How it works**
- The main agent registers the nested workflow via
  `register_nested_chats()`
- When triggered, the nested interaction (itself sequential or a group
  chat) runs internally
- The final result is returned/summarized to the outer context

**Use case:** a `curriculum_planner` agent delegates subject-specific
planning to sub-agents like `math_planner` and `history_planner`.

---

## 4. Group Chats

**Definition:** multiple agents interact within a shared conversation
space managed by a `GroupChatManager`.

**How it works**
- A `GroupChat` is instantiated with participating agents and a
  speaking strategy (pattern)
- `GroupChatManager` controls turn-taking based on the chosen pattern
- The conversation proceeds until a termination condition is met

**Use case:** a support chat with `triage_agent`, `tech_support_agent`,
`general_support_agent` — issues escalate or resolve dynamically.

### 4a. Orchestration patterns

| Pattern | Description | When to use |
|---|---|---|
| `DefaultPattern` | Requires explicit agent handoffs | Strict workflows, predictable transitions |
| `AutoPattern` | LLM selects next speaker from context | Adaptive, dynamic conversations |
| `RoundRobinPattern` | Rotates turns in fixed sequence | Structured updates, status meetings |
| `RandomPattern` | Random agent selection (excluding current) | Brainstorming, varied input |
| `ManualPattern` | Prompts user to choose next speaker | Educational settings, human oversight needed |

### 4b. Tools & functions

Agents can invoke tools/functions and use `ReplyResult` to structure
the reply and guide the next step.

`ReplyResult` includes:
- a response message
- a transition target (controls the next speaker)
- optional updates to shared `context_variables`

**Use case:** a classifier function assesses a query's topic and routes
it to `finance_agent` or `hr_agent`.

### 4c. Context variables

Shared memory for group workflows, via the `ContextVariables` class.

- Maintained as a key-value store
- Accessible across agents and orchestration patterns
- **Not** automatically injected into LLM prompts unless explicitly
  referenced
- Persisted across tool calls and interactions

**Use case:** `issue_severity` gets updated as agents assess a problem;
past a threshold, routing changes to involve an escalation agent.

### 4d. Handoffs & routing

Defines which agent speaks next, via rules on context or message
content.

| Routing method | How it decides |
|---|---|
| LLM-based (`OnCondition`) | Evaluates the message via LLM |
| Context-based (`OnContextCondition`) | Checks values in `context_variables` |
| After-Work / Default | Fallback when no condition matches |
| Tool-based | Tool returns `ReplyResult` with a transition value |

**Use case:** the phrase "urgent outage" triggers `OnCondition`,
transitioning control to an `escalation_agent`.

---

## 5. Guardrails

**Definition:** safety mechanisms that intercept conversations based on
rules, redirecting control when needed.

**Types**
- `RegexGuardrail` — pattern matching (phone numbers, SSNs, etc.)
- `LLMGuardrail` — semantic filtering via LLM for unsafe/inappropriate
  content

**Behavior**
- Can be registered on agent inputs or outputs
- On detection, control redirects to a designated safety/compliance
  agent

---

## Ending a chat

| Mechanism | How |
|---|---|
| Maximum turns | `max_turns` (two-agent) or `max_round` (group chat) |
| Termination message | e.g. `"DONE!"` triggers `is_termination_msg` |
| Max auto-replies | `max_consecutive_auto_reply` avoids infinite loops |
| User-initiated exit | `human_input_mode="ALWAYS"/"TERMINATE"` + typing `"exit"` |
| No next agent | Pattern returns `None` → conversation halts |
| `TerminateTarget` transition | Fallback when no further handoff possible |
| Custom reply logic | Agent returns `(True, None)` to signal intentional end |

---

## Summary table

| Architecture | Ideal use case | Core method/component |
|---|---|---|
| Two-Agent Chat | Quick Q&A or task delegation | `initiate_chat()` + `max_turns` |
| Sequential Chat | Pipelines, multi-step workflows | `initiate_chats()` + carryover |
| Nested Chat | Encapsulating reusable workflows | `register_nested_chats()` |
| Group Chat | Multi-role collaboration | `GroupChatManager` + orchestration patterns |
| Tools & Functions | Custom logic, branching control | `ReplyResult` |
| Context Variables | Shared state, routing decisions | `ContextVariables` |
| Handoffs & Routing | Conditional speaker transitions | `OnCondition`, `OnContextCondition` |

---

## Conclusión rápida

AG2 combina patrones de interacción reutilizables, enrutamiento
condicional, memoria contextual, integración de tools y terminaciones
estructuradas — desde un diálogo simple (Two-Agent Chat) hasta un
pipeline de automatización por capas (Group Chat + Handoffs +
Guardrails).
