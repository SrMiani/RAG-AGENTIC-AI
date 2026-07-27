# BeeAI Framework — Key Concepts

> Notas de referencia sobre BeeAI, framework open-source de IBM Research
> para construir agentes de IA listos para producción.

## Overview

- BeeAI is a cutting-edge, open-source platform for building
  production-ready AI agents.
- **Key benefits:** modularity, structured outputs, async execution,
  multi-agent support, standards compliance, and observability.

---

## 1. Creating a basic conversation

You can create an AI conversation in BeeAI by:
1. Importing the necessary modules
2. Initializing the chat model
3. Defining the conversation messages
4. Running the model **asynchronously**, using Python's `async` /
   `await` syntax

---

## 2. Prompts & structured outputs

- **Dynamic prompt templates** enable the creation of reusable prompts
  with variable data.
- BeeAI can generate **structured outputs** using **Pydantic schemas**
  — útil cuando necesitas que la respuesta del modelo tenga una forma
  concreta y validable, no solo texto libre.

---

## 3. Memory

- Conversational memory is managed with the **`UnconstrainedMemory`**
  class.
- `UnconstrainedMemory` provides a **persistent context** for an agent
  — mantiene el historial completo de la conversación sin límite (a
  diferencia de, por ejemplo, `TokenMemory`, que sí limita por número
  de tokens).

---

## 4. Agents

- Agents maintain a **persistent state**, use **external tools**, and
  follow **behavioral requirements**.
- The **`RequirementAgent`** class is used to build intelligent,
  controllable agents — es la clase recomendada para construir agentes
  en BeeAI.

### Tools

- Additional capabilities can be added to agents by **integrating
  tools**.
- Custom tools can be built for applications that require
  **domain-specific capabilities**.
- **`ThinkTool`** enables agents to engage in an explicit thinking
  process before providing answers (razonar antes de responder, no
  solo generar una respuesta directa).

### The ReAct pattern

- The **ReAct pattern** supports **reasoning and acting in cycles** —
  el agente alterna entre pensar (`Think`) y actuar (usar una tool),
  repitiendo el ciclo hasta llegar a una respuesta.

---

## 5. Requirements system

- BeeAI's **requirements system** provides **fine-grained control** of
  agent behavior — reglas declarativas que fuerzan comportamientos
  consistentes (ej. "usa siempre `ThinkTool` en el primer paso").
- **`AskPermissionRequirement`** enables **human-in-the-loop**
  workflows for improved security — el agente se detiene a pedir
  confirmación humana antes de ejecutar ciertas acciones sensibles.

---

## 6. Multi-agent systems

- Multi-agent systems can be created with BeeAI for **specialized
  agent collaboration** — varios agentes, cada uno especializado en
  una tarea, colaborando entre sí (similar en espíritu al
  `GroupChatManager` de AG2, aunque con su propia implementación).

---

## Resumen rápido

| Concepto | Clase / mecanismo |
|---|---|
| Conversación básica | `async`/`await` + chat model |
| Prompts reutilizables | Dynamic prompt templates |
| Salida estructurada | Pydantic schemas |
| Memoria persistente | `UnconstrainedMemory` |
| Agente controlable | `RequirementAgent` |
| Razonamiento explícito | `ThinkTool` |
| Ciclo razonar → actuar | ReAct pattern |
| Control fino de comportamiento | Requirements system |
| Human-in-the-loop | `AskPermissionRequirement` |
| Colaboración multi-agente | Multi-agent systems |
