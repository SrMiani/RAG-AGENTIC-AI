# BeeAI vs AG2 — Code Cheatsheet

> Notas de referencia con ejemplos de código reales de ambos frameworks,
> para comparar cómo se resuelve lo mismo en cada uno.

---

## BeeAI framework

**Qué es:** plataforma open-source para agentes de IA listos para
producción, desarrollada bajo el programa Linux Foundation AI & Data.

**Key features**
- **Production-ready:** caching, monitoring, integración con
  OpenTelemetry ya incorporados
- **Provider-agnostic:** soporta 10+ proveedores de LLM (OpenAI,
  watsonx.ai, Groq, Ollama)
- **Advanced patterns:** razonamiento ReAct, "systematic thinking",
  coordinación multi-agente

### Imports clave

```python
import asyncio
from beeai_framework.backend import ChatModel, ChatModelParameters, SystemMessage, UserMessage
from beeai_framework.agents.experimental import RequirementAgent
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.tools.search.wikipedia import WikipediaTool
from beeai_framework.agents.experimental.requirements.conditional import ConditionalRequirement
from beeai_framework.tools.think import ThinkTool
from beeai_framework.agents.experimental.requirements.ask_permission import AskPermissionRequirement
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.tools import Tool
```

### Uso básico (chat directo, sin agente)

```python
llm = ChatModel.from_name("watsonx:ibm/granite-4-h-small", ChatModelParameters(temperature=0))

messages = [
    SystemMessage(content="You are a helpful AI assistant."),
    UserMessage(content="Explain machine learning in simple terms.")
]

async def main():
    response = await llm.create(messages=messages)
    print(response.get_text_content())

asyncio.run(main())
```

### Salidas estructuradas (Pydantic)

```python
class BusinessPlan(BaseModel):
    business_name: str = Field(description="Catchy name for the business")
    elevator_pitch: str = Field(description="30-second description")
    revenue_streams: List[str] = Field(description="Ways to make money")

async def main():
    llm = ChatModel.from_name("openai:gpt-5-nano", ChatModelParameters(temperature=0))
    response = await llm.create_structure(
        schema=BusinessPlan,
        messages=[
            SystemMessage("You are a business consultant."),
            UserMessage("Create a business plan for a food delivery app.")
        ]
    )
    print(response.object)  # objeto BusinessPlan tipado

asyncio.run(main())
```

### Agente básico

```python
llm = ChatModel.from_name("watsonx:ibm/granite-4-h-small", ChatModelParameters(temperature=0))

agent = RequirementAgent(
    llm=llm,
    memory=UnconstrainedMemory(),
    instructions="You are an AI assistant specialized in data analysis."
)

async def main():
    result = await agent.run("What is machine learning?")
    print(f"Answer: {result.answer.text}")

asyncio.run(main())
```

### Agente con tool (patrón común)

```python
agent = RequirementAgent(
    llm=llm,
    memory=UnconstrainedMemory(),
    instructions="You are a research assistant.",
    tools=[WikipediaTool()],
    requirements=[ConditionalRequirement(WikipediaTool, max_invocations=1)]
)
```

### Agente ReAct (Think → Act → Think → Act)

```python
agent = RequirementAgent(
    llm=llm,
    memory=UnconstrainedMemory(),
    instructions="You are a helpful assistant.",
    tools=[ThinkTool(), WikipediaTool()],
    requirements=[ConditionalRequirement(
        ThinkTool,
        force_at_step=1,           # piensa primero
        force_after=Tool,          # piensa después de cada uso de tool
        consecutive_allowed=False, # no puede pensar dos veces seguidas
        max_invocations=3          # límite de ciclos de pensamiento
    )]
)
```

### Human-in-the-loop

```python
agent = RequirementAgent(
    llm=llm,
    memory=UnconstrainedMemory(),
    instructions="You are a helpful assistant.",
    tools=[WikipediaTool(), ThinkTool()],
    requirements=[
        AskPermissionRequirement(WikipediaTool),  # pide permiso antes de usar Wikipedia
        ConditionalRequirement(ThinkTool, force_at_step=1, max_invocations=3)
    ]
)
```

### Multi-agente con handoffs (mockup — sustituir los `...`)

```python
specialist_agent1 = RequirementAgent(...)
specialist_agent2 = RequirementAgent(...)

handoff_to_agent1 = HandoffTool(
    specialist_agent1,
    name="DataAnalyst",
    description="Consult the data analysis specialist"
)

handoff_to_agent2 = HandoffTool(
    specialist_agent2,
    name="ReportWriter",
    description="Consult the report writing specialist"
)

coordinator = RequirementAgent(
    llm=llm,
    memory=UnconstrainedMemory(),
    instructions="You coordinate tasks between specialists.",
    tools=[handoff_to_agent1, handoff_to_agent2, ThinkTool()]
)

async def main():
    result = await coordinator.run(...)
    print(f"Answer: {result.answer.text}")

asyncio.run(main())
```

---

## AG2 framework (antes AutoGen)

**Qué es:** framework open-source para colaboración multi-agente
mediante interacciones estructuradas.

**Core strengths**
- **Simple multi-agent setup:** colaboración entre agentes fácil de
  montar
- **Human integration:** supervisión y control humano sin fricción
- **Proven patterns:** métodos de orquestación ya probados en
  producción

### Setup

```bash
pip install ag2[openai]
```

```python
from autogen import ConversableAgent, AssistantAgent, UserProxyAgent
from autogen import GroupChat, GroupChatManager
from autogen.llm_config import LLMConfig

llm_config = LLMConfig(api_type="openai", model="gpt-5-nano")
```

### Two-agent conversation (patrón más simple)

```python
with llm_config:
    student = ConversableAgent(
        name="student",
        system_message="You are a curious student who asks clear questions",
        human_input_mode="NEVER"
    )

    tutor = ConversableAgent(
        name="tutor",
        system_message="You are a helpful tutor with clear explanations",
        human_input_mode="NEVER"
    )

chat_result = student.initiate_chat(
    recipient=tutor,
    message="Can you explain what a neural network is?",
    max_turns=2,
    summary_method="reflection_with_llm"
)

print("Final Summary:")
print(chat_result.summary)
```

### Generación y ejecución de código

```python
assistant = AssistantAgent(
    name="assistant",
    system_message="Helpful assistant who writes clear Python code"
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=5,
    code_execution_config={
        "executor": LocalCommandLineCodeExecutor(work_dir="coding")
    }
)

user_proxy.initiate_chat(
    recipient=assistant,
    message="Plot a sine wave using matplotlib and save as sine_wave.png"
)
```

### Group chat (varios agentes)

```python
lesson_planner = ConversableAgent(
    name="planner_agent",
    system_message="Create lesson plans for 4th graders",
    description="Makes lesson plans"
)

lesson_reviewer = ConversableAgent(
    name="reviewer_agent",
    system_message="Review plans and suggest up to 3 brief edits",
    description="Reviews lesson plans and suggests edits"
)

teacher = ConversableAgent(
    name="teacher_agent",
    system_message="Suggest topics and reply DONE when satisfied",
    is_termination_msg=lambda x: "DONE" in x.get("content", "").upper()
)

groupchat = GroupChat(
    agents=[teacher, lesson_planner, lesson_reviewer],
    speaker_selection_method="auto"
)

manager = GroupChatManager(
    name="group_manager",
    groupchat=groupchat,
    llm_config=llm_config
)

teacher.initiate_chat(
    recipient=manager,
    message="Make a simple lesson about the moon.",
    max_turns=6,
    summary_method="reflection_with_llm"
)
```

### Supervisión humana

`human_input_mode`:
- `"ALWAYS"` — el humano aprueba cada respuesta
- `"NEVER"` — totalmente autónomo
- `"TERMINATE"` — el humano decide cuándo terminar

```python
triage_bot = ConversableAgent(
    name="triage_bot",
    system_message="""You are a bug triage assistant. For each bug report:
    - Urgent issues (crash, security, data loss): escalate and ask for confirmation
    - Minor issues (cosmetic, typos): suggest closing but ask for review
    - Otherwise: classify as medium priority and ask for review""",
    llm_config=llm_config
)

human = ConversableAgent(
    name="human",
    human_input_mode="ALWAYS"  # revisa cada decisión
)
```

### Tools personalizadas

```python
def is_prime(n: int) -> str:
    """Check if a number is prime"""
    if n < 2: return "No"
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return "No"
    return "Yes"

register_function(
    is_prime,
    caller=math_asker,      # agente que pide la tool
    executor=math_checker,  # agente que la ejecuta
    description="Check if a number is prime. Returns Yes or No."
)
```

### Salidas estructuradas

```python
from pydantic import BaseModel

class TicketSummary(BaseModel):
    customer_name: str
    issue_type: str
    urgency_level: str
    recommended_action: str

llm_config = LLMConfig(
    api_type="openai",
    model="gpt-5-nano",
    response_format=TicketSummary  # fuerza la estructura
)
```

---

## Guía rápida de decisión

| Necesidad | Usa BeeAI cuando... | Usa AG2 cuando... |
|---|---|---|
| Despliegue en producción | Necesitas features enterprise, monitoring | Con patrones simples y probados basta |
| Supervisión humana | Workflows de aprobación complejos | Basta un human-in-the-loop básico |
| Coordinación multi-agente | Necesitas control fino | Quieres colaboración simple en grupo |
| Integración de tools | Tools con requirements custom | Registro básico de funciones |
| Punto de partida | Tienes necesidades de producción concretas | Quieres prototipar rápido |

---

## Buenas prácticas esenciales

**Seguridad**
- Nunca hardcodees API keys — usa variables de entorno
- Configura `max_consecutive_auto_reply` para evitar bucles infinitos
- Usa supervisión humana para decisiones de alto riesgo

**Diseño de agentes**
- Escribe `system_message`/`instructions` claras, definiendo rol y
  límites
- Usa agentes especializados para tareas concretas, no generalistas
- Define condiciones de terminación para acabar conversaciones de
  forma limpia

**Producción**
- Prueba primero con `max_turns` bajo para no disparar el coste en
  tokens
- Usa `temperature=0` para salidas consistentes
- Monitoriza la calidad de la conversación e interviene si hace falta

---

## En una frase

**BeeAI:** producción, features enterprise, control fino.
**AG2:** simple, probado, ideal para prototipar y para educación.
