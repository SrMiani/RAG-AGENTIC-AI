# MCP Servers — Módulo 2
### Cheat Sheet — Transportes, componentes y Context

---

## Transportes — cliente vs transporte

- El **cliente**: entiende qué necesita la aplicación, formatea las peticiones correctamente, interpreta las respuestas, y asegura que la comunicación sigue las reglas de MCP. Es la lógica y el protocolo.
- El **transporte**: es solo el canal por el que viajan los mensajes (ej. un WebSocket o un pipe). No entiende el significado de los mensajes, solo los entrega de forma fiable de un lado a otro.

> **Cliente = lógica y protocolo. Transporte = entrega de mensajes de bajo nivel.**

MCP se comunica usando el formato **JSON-RPC**. Soporta dos transportes estandarizados: **STDIO** y **HTTP**.

---

## STDIO

- Los mensajes JSON-RPC se intercambian a través de **stdin** (entrada estándar) y **stdout** (salida estándar) del sistema
- Estos streams son las "tuberías" de datos de un programa, gestionadas por el sistema operativo
- **No requiere conexión de red** — ideal para implementación y desarrollo local
- Es como una conexión directa tipo "plug-in" entre cliente y servidor
- El cliente escribe requests en el stdin del servidor, el servidor responde por stdout

---

## HTTP

- Los mensajes JSON-RPC se intercambian mediante requests y responses HTTP
- El cliente envía un request JSON-RPC en el body de un HTTP POST; el servidor responde con una respuesta codificada en JSON
- Permite comunicación **en red** (entre máquinas, a través de Internet) — ideal para servidores MCP remotos, con soporte de autenticación, encriptación y enrutamiento
- Es como enviar "cartas" estructuradas por Internet: cada "carta" es un HTTP request con un mensaje JSON-RPC dentro
- El cliente envuelve el mensaje con headers HTTP (la dirección y el sello del sobre); el servidor lee, procesa y responde con otra "carta" JSON

---

## SSE (Server-Sent Events) — deprecado

- Transporte para streaming de mensajes del servidor al cliente sobre HTTP
- Conexión **unidireccional**: el cliente podía recibir actualizaciones continuas pero no enviar datos de la misma forma
- Dependía de que el servidor mantuviera una conexión HTTP abierta para enviar actualizaciones
- **Deprecado** en favor de STDIO y HTTP, que soportan comunicación bidireccional completa
- Es como una "radio antigua": el servidor habla, el cliente solo escucha

---

## Componentes principales (primitives) de un servidor MCP

### 🔧 Tools

- Permiten interacciones con sistemas externos — son **funciones activas** que realizan acciones
- Se usan cuando algo necesita **hacer** trabajo o **causar** un cambio (ej. consultar una BD, llamar a una API, hacer cálculos)
- Tienen identificadores únicos y metadata (descripción, parámetros) que el cliente puede leer
- Tienen schemas de input/output definidos, para comportamiento seguro y predecible
- Son **model-controlled**: el LLM las descubre e invoca automáticamente según su comprensión contextual y el prompt del usuario

### 📁 Resources

- Proveen acceso **pasivo** a datos — información estructurada que el modelo puede leer, referenciar u observar, **pero no modificar directamente**
- Ejemplo: leer un documento, obtener configuración guardada, acceder a archivos de proyecto
- El acceso activo a datos se maneja mejor con una tool
- Siguen una convención URI (ej. `mcp://resource/secret`)
- Los **resource templates** definen patrones para generar múltiples resources relacionados (ej. `mcp://resource/{userId}/settings`)
- Son **application-driven**: la aplicación host decide cómo incorporarlos según sus necesidades (ej. triggers configurados)

### 💬 Prompts

- Plantillas que definen instrucciones reutilizables, workflows, o arranques de conversación
- Ejemplo: "Resume este documento", "Genera un esquema de informe", "Redacta una respuesta de email"
- Contienen parámetros de input estructurados que el usuario o el sistema pueden rellenar
- El cliente puede descubrir prompts disponibles, obtener su contenido, y rellenarlos con parámetros personalizados
- Son **user-controlled**: se centran en guiar el razonamiento del modelo, no en ejecutar acciones

---

## MCP Context

Da acceso a la sesión MCP activa y sus capacidades, permitiendo que los primitives interactúen con el servidor durante la ejecución. Tres funciones vistas:

| Función | Qué hace |
|---|---|
| **Logging** | Registra mensajes informativos, warnings o errores desde dentro de tools/resources, para debugging o monitorización |
| **Progress reporting** | Comunica el progreso o estado de finalización de una tarea al cliente en tiempo real |
| **User elicitation** | Pide input o confirmación al usuario cuando se necesita información adicional durante la ejecución |

---

## Implementación con FastMCP

### Instanciar el servidor

```python
from fastmcp import FastMCP
mcp = FastMCP("MCP Server Name")
```

### Definir los componentes primitivos

```python
@mcp.tool()
async def mcp_tool(input_parameter: str):
    # hacer algo
    return "Return something"

@mcp.resource("uri://uniform/resource/identifier/{parameter}")
async def mcp_resource(parameter: str):
    # obtener el resource
    return "The resource"

@mcp.prompt()
async def mcp_prompt(input_parameter: str):
    return f"Prompt template with {input_parameter}"
```

### Usar el MCP Context

```python
from fastmcp import Context
from pydantic import BaseModel

class ElicitSchema(BaseModel):
    field: str

@mcp.tool()
async def context_tool(ctx: Context):
    await ctx.info("Logging message")
    await ctx.warning("Warning message")
    await ctx.error("Error message")
    await ctx.elicit(
        message="Please provide information",
        response_type=ElicitSchema
    )
    return "Tool return"
```

---

## Llamadas manuales a tools (Manual Tool Calling)

### Vía STDIO — con FastMCP

```python
from fastmcp.client.transport import StdioTransport
from fastmcp import Client

transport_stdio = StdioTransport(
    command="python",
    args=["path/to/server/script"]
)
stdio_transport_client = Client(transport_stdio)

async with client:
    tools = await client.list_tools()
    result = await client.call_tool("tool_name", {"tool_param": "param_value"})
```

### Vía STDIO — con la librería `mcp` de bajo nivel

```python
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

server_params = StdioServerParameters(
    command="python",
    args=["path/to/server/script"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool(
            name="tool_name",
            arguments={"tool_param": "param_value"},
        )
```

### Vía HTTP — con FastMCP

```python
from fastmcp.client.transport import StreamableHttpTransport
from fastmcp import Client

transport_http = StreamableHttpTransport(
    url="url_of_http_mcp_server/mcp"
)
http_transport_client = Client(transport_http)

async with client:
    tools = await client.list_tools()
    result = await client.call_tool("tool_name", {"tool_param": "param_value"})
```

### Vía HTTP — con la librería `mcp` de bajo nivel

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async with streamablehttp_client("url_of_http_mcp_server/mcp") as (read, write, _sid):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool(
            name="tool_name",
            arguments={"tool_param": "param_value"},
        )
```

---

## Resumen mental rápido

> **STDIO para local, HTTP para remoto. Tools = acciones (model-controlled). Resources = datos pasivos (application-driven). Prompts = plantillas de instrucciones (user-controlled). Context = logging + progreso + elicitation dentro de una tool en ejecución.**
