# Agentic AI — conceptos clave para entrevista (BeeAI + AG2)

> No es para memorizar sintaxis — es para poder explicar cada concepto
> **con tus propias palabras** en 30-60 segundos si te lo preguntan.

---

## 1. Conceptos universales (independientes del framework)

Estos son los que más probablemente te pregunten, porque aplican a
cualquier framework de agentes, no solo a BeeAI o AG2.

- **Agente vs LLM a secas** — un LLM solo genera texto; un agente
  además decide *qué hacer* (usar una tool, pedir confirmación,
  terminar), mantiene estado, y puede iterar varias veces antes de dar
  la respuesta final.
- **Tool calling / function calling** — cómo un LLM "pide" ejecutar una
  función externa (buscar en Wikipedia, consultar una BD) en vez de
  inventarse la respuesta. El LLM no ejecuta nada directamente; propone
  la llamada, el framework la ejecuta y le devuelve el resultado.
- **Patrón ReAct** (Reasoning + Acting) — el agente alterna ciclos de
  "pensar" → "actuar" → "pensar" → "actuar", en vez de responder de
  un tirón. Origen: paper "ReAct: Synergizing Reasoning and Acting in
  Language Models" (2022).
- **Human-in-the-loop** — puntos donde el agente se detiene a pedir
  confirmación humana antes de una acción sensible (enviar un email,
  borrar datos, gastar dinero). Es un control de seguridad, no un
  detalle de UX.
- **Structured outputs** — forzar que la respuesta del LLM tenga una
  forma validable (normalmente vía un schema de Pydantic), en vez de
  texto libre que luego hay que parsear a mano.
- **Memoria de conversación** — corto plazo (todo el historial de esta
  sesión) vs limitada por tokens (se recorta para no reventar el
  contexto) vs persistente entre sesiones (se guarda en BD). Saber
  nombrar esta distinción es más importante que saber la clase exacta
  de cada framework.
- **Multi-agente vs agente único** — cuándo tiene sentido dividir un
  problema en varios agentes especializados (uno investiga, otro
  redacta, otro revisa) en vez de un agente generalista haciendo todo.
  Ventaja: cada uno con su propio prompt/tools optimizados. Coste:
  más complejidad de orquestación.
- **Protocolos de comunicación entre agentes** — **MCP** (Model Context
  Protocol, de Anthropic) estandariza cómo un agente habla con
  *tools y datos*. **ACP** (Agent Communication Protocol, de IBM,
  usado por BeeAI) va un paso más allá: estandariza cómo un agente
  descubre y ejecuta *a otro agente*, sin importar en qué framework
  esté construido.
- **Observabilidad** — poder ver la traza completa de lo que hizo el
  agente (qué tool llamó, en qué orden, qué pensó) — crítico en
  producción para depurar por qué un agente hizo algo inesperado.

---

## 2. BeeAI — lo específico que hay que saber

- **`RequirementAgent`** — la clase de agente recomendada. Su gracia:
  el comportamiento se define con **reglas declarativas**
  (`requirements=[...]`), no con código imperativo de control de flujo.
- **Requirements system** — en vez de escribir "si pasó X, haz Y",
  declaras restricciones (*"usa `ThinkTool` en el paso 1"*, *"pide
  permiso antes de usar esta tool"*) y el framework las hace cumplir,
  **de forma consistente sin importar qué LLM esté por debajo**. Esto
  es la propuesta de valor central de BeeAI frente a otros frameworks:
  normaliza el comportamiento entre modelos con distinta capacidad de
  razonamiento.
- **`ConditionalRequirement`** — la regla más común: fuerza cuándo/cómo
  se usa una tool (`force_at_step`, `max_invocations`,
  `consecutive_allowed`).
- **`AskPermissionRequirement`** — el mecanismo human-in-the-loop de
  BeeAI. Pausa la ejecución pidiendo aprobación antes de una tool
  concreta.
- **`UnconstrainedMemory`** — memoria sin límite de historial (existe
  también `TokenMemory`, que sí recorta por tokens — saber nombrar la
  diferencia).
- **`ThinkTool`** — fuerza un paso explícito de razonamiento antes de
  actuar; es lo que habilita el patrón ReAct dentro de BeeAI.
- **`HandoffTool`** — mecanismo de multi-agente: un agente coordinador
  "delega" en un agente especialista, envuelto como si fuera una tool
  más.
- **`GlobalTrajectoryMiddleware`** — el componente de observabilidad;
  trackea toda la ejecución (tools usadas, orden, resultados).
- **Producción / enterprise** — caching, monitoring, OpenTelemetry ya
  integrados, soporta 10+ proveedores de LLM. Este es el argumento de
  venta de BeeAI frente a AG2: pensado para *producción*, no solo para
  prototipar.

---

## 3. AG2 (antes AutoGen) — lo específico que hay que saber

- **`ConversableAgent`** — la clase base de la que heredan el resto.
  Su rol: intercambiar mensajes en lenguaje natural.
- **`AssistantAgent`** vs **`UserProxyAgent`** — el primero representa
  la parte "experta"/LLM; el segundo actúa en nombre del usuario
  (puede tener `human_input_mode` para pedir input real, o ejecutar
  código).
- **`GroupChat` + `GroupChatManager`** — varios agentes en un mismo
  espacio de conversación; el manager decide quién habla a
  continuación según el **orchestration pattern** elegido
  (`AutoPattern`, `RoundRobinPattern`, `RandomPattern`,
  `ManualPattern`, `DefaultPattern`).
- **Two-Agent Chat vs Sequential Chat vs Nested Chat** — de menos a
  más complejo: conversación directa → cadena de chats con
  *carryover* → workflow encapsulado y reutilizable bajo un agente
  "trigger".
- **`ReplyResult` + `context_variables`** — cómo una tool puede además
  de responder, decidir quién habla después (*transition target*) y
  actualizar estado compartido entre agentes.
- **Handoffs/routing** — `OnCondition` (decide vía LLM),
  `OnContextCondition` (decide mirando `context_variables`
  directamente, sin LLM de por medio).
- **Guardrails** — `RegexGuardrail` (detección por patrón, ej. números
  de tarjeta) vs `LLMGuardrail` (filtrado semántico).
- **Terminación** — `max_turns`/`max_round`, `is_termination_msg`,
  `max_consecutive_auto_reply`, `human_input_mode="TERMINATE"`.
- **Simplicidad y prototipado** — el argumento de venta de AG2 frente
  a BeeAI: patrones ya probados, fácil de montar rápido, ideal para
  educación o prototipos.

---

## 4. Preguntas típicas que te pueden hacer (y cómo enfocarlas)

- **"¿Cuándo usarías multi-agente en vez de un agente único?"** →
  cuando las tareas son lo bastante distintas como para que un prompt
  único se vuelva confuso o poco fiable (ej. investigar + redactar +
  revisar), y el coste de orquestar varios agentes compensa la
  ganancia en especialización.
- **"¿Cómo garantizas seguridad en un sistema de agentes?"** → human-in-
  the-loop en acciones sensibles (`AskPermissionRequirement` en BeeAI,
  `human_input_mode` en AG2), guardrails para contenido, límites de
  iteraciones para evitar bucles infinitos, observabilidad para poder
  auditar qué hizo el agente y por qué.
- **"¿Diferencia entre esto y simplemente encadenar prompts?"** → un
  agente decide dinámicamente su propio flujo (qué tool usar, cuándo
  parar) en vez de seguir una secuencia fija programada de antemano.
- **"¿Por qué async/await en estos frameworks?"** → las llamadas al
  LLM y a las tools son operaciones de I/O que tardan; sin async,
  cada llamada bloquearía el proceso entero mientras espera respuesta.
- **"¿Cómo evitarías que un agente entre en bucle infinito?"** →
  límites explícitos: `max_invocations`, `max_turns`,
  `max_consecutive_auto_reply`, detección de ciclos incorporada en el
  propio framework (BeeAI la menciona explícitamente en su
  `RequirementAgent`).

---

## 5. Lo más importante de todo

No es tener memorizado `ConditionalRequirement(ThinkTool, force_at_step=1)`.
Es poder decir, con tus palabras: *"esto fuerza a que el agente razone
antes de actuar, en el primer paso, para no lanzarse directo a usar una
tool sin pensar"* — sin mirar el código. Si puedes explicar el **por
qué** de cada pieza, la sintaxis exacta se busca en 10 segundos en
cualquier entrevista técnica que te deje usar documentación (y en las
que no, lo que evalúan es justo este razonamiento, no la sintaxis).
