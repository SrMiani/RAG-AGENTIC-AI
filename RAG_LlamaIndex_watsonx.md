# RAG con LlamaIndex y IBM watsonx

## Conceptos base

**LLMs (Large Language Models)**: modelos de IA entrenados con grandes corpus de texto, basados en arquitectura **Transformer**, pre-entrenados en varias tareas de lenguaje para generar respuestas similares a las humanas.

**IBM watsonx**: suite de herramientas/servicios de IA para construir y desplegar apps con IA — APIs para NLP, visión por computador y reconocimiento de voz. Modelos foundation usados en este contexto: **`ibm/granite-4-h-small`** y **`meta-llama/llama-3-3-70b-instruct`**, intercambiables para comparar rendimiento.

**LlamaIndex**: plataforma open-source de orquestación de datos para apps LLM. Disponible en Python y TypeScript, facilita el proceso de "context augmentation" (RAG) para casos de uso de IA generativa.

**RAG (Retrieval-Augmented Generation)**: como los LLMs no incluyen tus datos específicos por defecto, RAG combina tu propia información con el conocimiento ya existente del LLM.

**Flujo general de RAG:**
1. Tus datos se cargan, procesan e indexan
2. Al llegar una query, se busca la info más relevante en el índice
3. Esa info + la query se envían al LLM
4. El LLM genera la respuesta basada en ese contexto enriquecido

---

## Las 5 etapas de RAG

| Etapa | Qué hace |
|---|---|
| **1. Loading** | Importa tus datos (PDFs, webs, BBDD, APIs...) al workflow. **LlamaHub** ofrece conectores para simplificarlo |
| **2. Splitting** | Divide los datos en chunks manejables para mejorar relevancia de retrieval y calidad de respuesta. Estrategias: ventanas de tamaño fijo, segmentación semántica, splitting recursivo por caracteres |
| **3. Indexing** | Construye una estructura de datos para consultas eficientes — típicamente **vector embeddings** (representaciones numéricas del significado) + metadata para retrieval preciso |
| **4. Storing** | Guarda el índice y su metadata para evitar tener que re-indexar más adelante |
| **5. Querying** | Consultas sobre el índice — puede incluir sub-queries, queries multi-paso, o técnicas híbridas |

### Sobre Indexing en detalle

Un **Index** en LlamaIndex es la estructura clave que permite recuperar el contexto relevante en respuesta a una query. Se construye a partir de los **Nodes** generados en el splitting, y luego se usa para construir **Retrievers** y **Query Engines** — los que realmente potencian las interacciones de pregunta-respuesta.

### Vector embeddings

Antes de indexar los nodes, hay que convertirlos en representaciones vectoriales (**embedding**) — esto permite al modelo entender mejor el texto y comparar su similitud semántica con las queries del usuario. Textos similares producen vectores similares, permitiendo búsqueda y retrieval eficientes. Se usa un modelo de embedding de IBM watsonx, y los vectores se guardan en una **vector database** para usarse durante el procesamiento de queries.

### Evaluation

Paso crucial para medir de forma objetiva precisión, relevancia y velocidad de los resultados de las queries, especialmente al comparar distintos enfoques o hacer ajustes.

---

## Ejemplo práctico: Icebreaker Bot

Aplicación real de las 5 etapas de RAG en un caso concreto — un bot que genera "icebreakers" personalizados a partir de perfiles de LinkedIn:

```
1. Loading    → Se carga la data del perfil de LinkedIn
2. Splitting  → Se convierte en chunks
3. Indexing   → Se generan embeddings de esos chunks
4. Storing    → Los embeddings se guardan en una vector database
5. Querying   → Al hacer una pregunta, se recuperan las piezas más relevantes del perfil
   Generation → Un LLM genera respuestas personalizadas basándose en ese contexto específico
```

**Mapeo directo con las etapas teóricas:**

| Etapa teórica | Aplicación en Icebreaker Bot |
|---|---|
| Loading | Cargar datos del perfil de LinkedIn |
| Splitting | Convertir el perfil en chunks manejables |
| Indexing | Generar embeddings de esos chunks |
| Storing | Guardar los embeddings en una vector database |
| Querying | Recuperar las piezas más relevantes del perfil según la pregunta del usuario |
| *(Generation, más allá de las 5 etapas de RAG)* | El LLM usa el contexto recuperado para generar una respuesta personalizada |

**Idea clave:** este ejemplo ilustra perfectamente por qué RAG es tan útil — sin RAG, un LLM genérico no sabría nada específico sobre el perfil de LinkedIn de una persona concreta. Con RAG, el sistema recupera justo los fragmentos relevantes de **ese perfil en particular** y los usa como contexto, permitiendo respuestas verdaderamente personalizadas en vez de genéricas.
