# Structured Outputs con Pydantic en CrewAI

## Por qué importan los structured outputs en workflows de IA

El texto libre de un LLM es difícil de parsear, ambiguo y arriesgado para tareas downstream. Los **structured outputs** (JSON, objetos con campos definidos) aseguran consistencia y facilitan extraer/usar los datos.

CrewAI permite definir **schemas** para las respuestas de las tasks, lo que da resultados más fiables y predecibles. En workflows multi-agente, esto asegura que el output de un agente pueda ser interpretado limpiamente por el siguiente, reduciendo malentendidos, pérdida de datos y alucinaciones.

---

## Introducción a Pydantic para modelado de datos

CrewAI se apoya en **Pydantic** para habilitar structured outputs. Un modelo Pydantic es una clase que hereda de `BaseModel` y define campos con tipos.

Al crear una instancia, Pydantic **valida automáticamente** que los datos coincidan con los tipos esperados (y los convierte cuando es posible). Si faltan campos requeridos o el tipo es incorrecto, lanza un `ValidationError`.

---

## Características clave de Pydantic

### 1. Data validation
Asegura que los inputs coincidan con los tipos esperados.

```python
from pydantic import BaseModel

class Person(BaseModel):
    age: int

Person(age="twenty")  # Raises ValidationError
```

### 2. Automatic type conversion
Pydantic intenta convertir el input al tipo esperado cuando es posible.

```python
from datetime import date
from pydantic import BaseModel

class Event(BaseModel):
    date: date

e = Event(date="2025-07-24")
print(e.date)  # Outputs: 2025-07-24
```

### 3. Nested models y tipos complejos
Los modelos pueden incluir otros modelos, listas y campos opcionales — ideal para datos estructurados tipo JSON.

```python
from typing import List
from pydantic import BaseModel

class Item(BaseModel):
    name: str

class Cart(BaseModel):
    items: List[Item]

cart = Cart(items=[{"name": "Apple"}])
```

### 4. Serialización fácil
Convertir modelos a diccionarios o JSON strings para almacenamiento o respuestas de API.

```python
user = Person(age=30)
print(user.dict())   # {'age': 30}
print(user.json())   # '{"age": 30}'
```

---

## Implementar structured output en una task de CrewAI

### Paso 1: Definir un modelo Pydantic

```python
from pydantic import BaseModel

class BlogSummary(BaseModel):
    title: str
    content: str
```

Esto fuerza un schema con dos campos obligatorios: `title` y `content`.

### Paso 2: Nested Pydantic models

Para datos jerárquicos/agrupados:

```python
from typing import List
from pydantic import BaseModel

class Ingredient(BaseModel):
    name: str
    quantity: str

class MealPlan(BaseModel):
    meal_name: str
    ingredients: List[Ingredient]
```

CrewAI valida automáticamente cada campo dentro de cada modelo anidado.

### Paso 3: Vincular el modelo a la task

Usando el parámetro `output_pydantic` (o `output_json`):

```python
blog_task = Task(
    description="Generate a catchy blog title and a short content about a topic.",
    expected_output="A JSON object with 'title' and 'content' fields.",
    agent=blog_agent,
    output_pydantic=BlogSummary
)
```

- `output_pydantic` → devuelve un objeto Pydantic
- `output_json` → devuelve un dict plano de Python

### Paso 4: Usar YAML junto con Pydantic

No se puede referenciar una clase Pydantic directamente en YAML, pero se puede definir la config de la task en YAML y adjuntar el modelo en Python vía `CrewBase`:

```python
@task
def blog_task(self) -> Task:
    return Task(
        config=self.tasks_config['blog_task'],  # Desde YAML
        output_json=BlogSummary                 # Definido en Python
    )
```

Esto combina la facilidad de edición de YAML con la validación estricta de schema de Python.

### Paso 5: Ejecutar la crew

```python
result = crew.kickoff()
```

El resultado incluye datos estructurados:
- `result.raw` → output crudo del modelo
- `result.json_dict` → dict (si se usó `output_json`)
- `result.pydantic` → objeto Pydantic (si se usó `output_pydantic`)

También se puede acceder como diccionario: `result["title"]` (soporte de `__getitem__` implementado).

### Paso 6: Usar los datos estructurados

```python
title = result.pydantic.title           # si se usó output_pydantic
title = result.json_dict.get("title")   # si se usó output_json
```

Esto hace que el output de la IA sea una parte fiable del pipeline de datos del programa — sin parseo ni adivinanzas.

---

## Por qué importa el structured output en CrewAI

| Beneficio | Cómo ayuda en workflows de CrewAI |
|---|---|
| **Type safety y validación** | CrewAI valida el output del LLM contra el schema definido. Si el modelo devuelve tipos incorrectos o falta algún campo, te enteras al instante — evita bugs sutiles |
| **Contratos de datos claros** | Un modelo Pydantic actúa como un acuerdo formal: "esta task siempre devuelve estos campos, con estos tipos" — facilita entender el código en proyectos colaborativos |
| **Integración de sistemas** | Ya sea enviar el output a una API, guardarlo en BBDD, o mostrarlo en una UI, los structured outputs hacen la integración fluida, sin parsear manualmente la respuesta del LLM |
| **Menos post-procesamiento** | Sin structured outputs, se suele escribir parsing manual o regex para extraer info de texto crudo. Con CrewAI + Pydantic, ese trabajo ya viene validado y listo |
| **Handoffs consistentes entre agentes** | En workflows multi-agente, la estructura asegura transiciones fluidas: el output de un agente se convierte en el input del siguiente sin ambigüedad, evitando formatos alucinados |
| **Alineación del comportamiento del LLM** | Al pedirle al LLM que siga un schema estructurado (ej. "devuelve un JSON con campos A, B y C"), tiende a mantenerse más enfocado y preciso — funciona como un "soft prompting" o function-calling que constriñe el espacio de outputs posibles |

---

## Resumen

Los structured outputs en CrewAI combinan la flexibilidad de los LLMs con la fiabilidad de formatos de datos definidos. Usando modelos Pydantic, se crea una estructura clara que CrewAI hace cumplir, facilitando validar, reutilizar e integrar los outputs. Esto ayuda a construir workflows más fiables, conectar múltiples agentes sin fricción, y conectar los resultados de IA directamente con sistemas reales — un paso clave para convertir IA experimental en aplicaciones production-ready.
