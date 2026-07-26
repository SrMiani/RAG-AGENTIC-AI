# CrewAI: Fundamentos y Arquitectura

## 1. ¿Qué es CrewAI?

Framework para orquestar **agentes de IA autónomos**, permitiéndoles colaborar en tareas complejas. Permite construir una "crew" (tripulación) de agentes, cada uno con un rol, objetivo y tools específicos, que trabajan juntos para lograr un objetivo — de forma similar a un equipo humano. Ideal para automatizar workflows multi-paso: investigación, análisis, creación de contenido, servicio al cliente.

---

## 2. Componentes core: Agents, Tasks y Crew

### AI Agents

Los trabajadores individuales de la crew — cada uno es una IA autónoma con un propósito definido.

| Atributo | Descripción |
|---|---|
| **Role** | El puesto/función del agente (ej. "Nutrition Analyst") |
| **Goal** | El objetivo específico que el agente debe lograr |
| **Backstory** | Contexto o personalidad que moldea el comportamiento del agente |
| **Tools** | Lista de funciones/capacidades que el agente puede usar (ej. búsqueda web, lector de PDF) |
| **llm** | El modelo de lenguaje que impulsa el razonamiento del agente |
| **verbose** | Booleano; si es `True`, activa logging detallado del proceso de pensamiento del agente |

```python
from crewai import Agent
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()

research_agent = Agent(
    role='Senior Research Analyst',
    goal='Uncover cutting-edge information on a given topic',
    backstory='An expert researcher skilled at synthesizing data.',
    tools=[search_tool],
    llm=my_llm,
    verbose=True
)
```

### Tasks

Las asignaciones concretas dadas a los agentes — definen qué hay que hacer y cuál es el resultado esperado.

| Atributo | Descripción |
|---|---|
| **Description** | Explicación clara de la asignación, a menudo con placeholders como `{topic}` para inputs dinámicos |
| **Expected Output** | Descripción de cómo debería ser un resultado exitoso |
| **Agent** | El agente asignado para completar la task |
| **Context** | Lista de otras tasks de las que depende el output de esta |
| **Tools** | Lista de tools específicas provistas para esta task |
| **output_pydantic** | Un modelo Pydantic para estructurar el output de la task |

```python
from crewai import Task

research_task = Task(
    description='Analyze the major trends in {topic}.',
    expected_output='A detailed report on key trends and technologies.',
    agent=research_agent
)
```

### Crews

El `Crew` junta todo, gestionando agentes y tasks según un proceso definido.

| Atributo | Descripción |
|---|---|
| **Agents** | Lista de todos los agentes de la crew |
| **Tasks** | Lista de todas las tasks a ejecutar |
| **Process** | Estrategia de ejecución: `Process.sequential` (tasks una tras otra) o `Process.hierarchical` (workflows más complejos, basados en delegación) |

```python
from crewai import Crew, Process

content_crew = Crew(
    agents=[research_agent, writer_agent],
    tasks=[research_task, writer_task],
    process=Process.sequential,
    verbose=True
)

result = content_crew.kickoff(inputs={'topic': 'AI in Healthcare'})
print(result)
```

---

## 3. Estructurar workflows: Agent-Centric vs. Task-Centric

Decisión clave de diseño en CrewAI: cómo proporcionar tools a los agentes. Esto impacta la eficiencia y fiabilidad del sistema.

### El generalista (Agent-Centric)

Método estándar: le das al agente una "caja de herramientas" completa con todas las tools que podría necesitar. El agente usa su propio razonamiento para decidir cuál usar.

- ✅ **Pro:** simple de configurar
- ❌ **Con:** puede ser ineficiente e impredecible — el agente puede elegir la tool equivocada o tardar más en decidir

```python
generalist_agent = Agent(
    role='Inquiry Specialist',
    goal='Answer all customer questions.',
    tools=[pdf_search_tool, web_search_tool]  # El agente debe elegir
)
```

### El especialista (Task-Centric)

Enfoque más avanzado y robusto: asignas las tools directamente a las tasks que las necesitan. **Al asignar tools a una task, CrewAI sobreescribe completamente las tools del agente para esa task específica** — solo se usan las tools necesarias para ese trabajo.

- ✅ **Pro:** más eficiente, predecible y seguro. Elimina la ambigüedad y enfoca el esfuerzo del agente
- ❌ **Con:** requiere un workflow más estructurado, con múltiples tasks

```python
specialist_agent = Agent(
    role='Customer Service Specialist',
    goal='Follow a step-by-step process to answer questions.',
    tools=[]  # Sin tools asignadas directamente; si las hubiera, serían sobreescritas
)

faq_search_task = Task(
    description="Search the FAQ PDF for the query: '{customer_query}'",
    expected_output="Relevant info from the PDF.",
    tools=[pdf_search_tool],  # Tool específica de ESTA task
    agent=specialist_agent
)
```

---

## 4. Estructurar datos de salida con Pydantic

Para asegurar que los agentes produzcan datos consistentes, fiables y estructurados (como JSON), se usan modelos Pydantic. Definir un `BaseModel` crea una plantilla para el output del agente.

```python
from pydantic import BaseModel, Field
from typing import List

# 1. Definir la estructura de datos
class GroceryShoppingPlan(BaseModel):
    """Complete simplified shopping plan"""
    total_budget: str = Field(description="Total planned budget")
    meal_plans: List[str] = Field(description="Planned meals")
    shopping_tips: List[str] = Field(description="Money-saving tips")

# 2. Asignar el modelo al output de una task
shopping_task = Task(
    description="Organize a shopping list for {meal_name}.",
    expected_output="An organized shopping plan.",
    agent=shopping_organizer,
    output_pydantic=GroceryShoppingPlan
)
```

---

## 5. Gestión avanzada con @CrewBase y YAML

Para proyectos grandes/de producción, CrewAI permite organizar agentes y tasks usando el decorador **`@CrewBase`** y archivos de configuración **YAML**.

| Elemento | Función |
|---|---|
| **`@CrewBase`** | Decorador de clase Python que automatiza el setup de la crew, descubriendo métodos marcados con `@agent` y `@task` |
| **`@crew`** | Decorador opcional (usado dentro de una clase `@CrewBase`) que marca el método responsable de ensamblar agentes y tasks en un objeto `Crew` final; define qué agentes/tasks forman parte de la crew y el proceso de ejecución (ej. `Process.sequential`) |
| **YAML Configuration** | Permite definir las propiedades de agentes y tasks (role, goal, description) en archivos `agents.yaml` y `tasks.yaml` separados — separa configuración de código, dejando el proyecto más limpio |

### ⚠️ Nota crucial

La clase `@CrewBase` depende del módulo `inspect` de Python para encontrar rutas de archivo, lo cual **no funciona correctamente dentro de un Jupyter Notebook**. Por eso, las clases `@CrewBase` deben definirse siempre en **archivos `.py` separados** e importarse en la aplicación principal.

### Ejemplo de estructura conceptual (en un archivo `.py`)

```python
# En un archivo llamado 'my_crew_defs.py'
from crewai.project import CrewBase, agent, task, crew
from crewai import Agent, Task, Crew, Process

@CrewBase
class FinancialCrew:
    """A class to manage the financial analysis crew."""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def market_analyst(self) -> Agent:
        return Agent(config=self.agents_config['market_analyst'])

    @task
    def analysis_task(self) -> Task:
        return Task(config=self.tasks_config['analysis_task'])

    @crew
    def crew(self) -> Crew:
        """Assembles the agents and tasks into a crew."""
        return Crew(
            agents=[self.market_analyst()],
            tasks=[self.analysis_task()],
            process=Process.sequential,
            verbose=True
        )
```

---

## Resumen ejecutivo

- **CrewAI** organiza agentes autónomos con roles claros (`Agent`), les asigna trabajo concreto (`Task`), y coordina todo en un `Crew` con un proceso de ejecución (`sequential` o `hierarchical`)
- **Agent-centric** = flexible pero menos predecible; **Task-centric** = más control y fiabilidad, mejor para producción
- **Pydantic** (`output_pydantic`) fuerza que el output de cada task sea estructurado y validado
- **YAML + `@CrewBase`** separan configuración de código para proyectos grandes — pero solo funciona en archivos `.py`, nunca en notebooks
