# MCP — Model Context Protocol
### Cheat Sheet — Conceptos básicos

---

## ¿Qué es MCP?

**Model Context Protocol (MCP)** es un estándar open-source que permite que aplicaciones de IA se conecten con sistemas externos. Usando MCP, LLMs como ChatGPT pueden:

- **Ejecutar tareas** (ej. enviar un email)
- **Recuperar datos** (ej. leer del sistema de archivos local)
- **Realizar workflows especializados** (ej. revisión de código iterativa)

---

## La analogía clave

> **MCP es como un puerto USB para aplicaciones de IA.**

Proporciona una interfaz estandarizada que permite que las aplicaciones de IA se conecten con sistemas externos — igual que USB ofrece una forma universal de que los dispositivos se conecten y comuniquen entre sí.

---

## ¿Por qué existe MCP?

| Razón | Descripción |
|---|---|
| **Integración estandarizada** | Un protocolo único para conectar IA con sistemas externos — patrones de desarrollo consistentes y simples, mejor escalabilidad |
| **Interoperabilidad** | Soporte amplio para distintos clientes y modelos de IA; es modular |
| **Seguridad** | Usa OAuth 2.0 y autenticación basada en tokens |
| **Minimiza alucinaciones** | Conecta a sistemas externos actualizados → datos limpios y precisos → menos respuestas incorrectas |
| **Soporte de workflows agénticos** | Permite que agentes de IA ejecuten tareas dinámicas de múltiples pasos |

---

## Arquitectura de MCP

### Arquitectura de tres capas

- Comunicación **bidireccional** usando **JSON-RPC 2.0** como formato de mensajes
- Los mensajes se envían por **STDIO** o **HTTP** (transportes)

### Ciclo de vida de la conexión

**1. Inicialización**
- El cliente envía un request `initialize` con versión de protocolo y capacidades
- El servidor responde con sus propias capacidades
- El cliente envía una notificación `initialized` → handshake completo

**2. Operación**
- Comienza la comunicación bidireccional
- El cliente descubre e invoca **tools**, **resources** y **prompts** que ofrece el servidor
- El servidor puede enviar notificaciones, logs y otros requests al cliente

**3. Shutdown**
- El cliente envía un request `shutdown`
- El servidor responde y cierra la conexión

---

## Multi-server client

- Un **host process** gestiona múltiples instancias de cliente MCP a la vez
- Cada cliente maneja su propia sesión con un servidor (ciclo de vida y capacidades independientes)
- El host process **agrega las capacidades** de todos los servidores y **enruta** los resultados de cada tool al cliente correcto

---

## Interactuando con un servidor MCP — con FastMCP

### 1. Importar cliente y transportes

```python
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport, StdioTransport
```

### 2. Crear los transportes (STDIO o HTTP)

```python
stdio_transport = StdioTransport(
    command="npx",
    args=["-y", "@upstash/context7-mcp"]
)

http_transport = StreamableHttpTransport(
    url="https://mcp.context7.com/mcp"
)
```

### 3. Crear un cliente por cada transporte

```python
stdio_client = Client(stdio_transport)
http_client = Client(http_transport)
```

### 4. Usar el cliente dentro de un context manager asíncrono

```python
async with stdio_client as client:
    # Lista de tools que ofrece el servidor
    tools = await client.list_tools()

    # Llamar a una tool con parámetros
    response = await client.call_tool("resolve-library-id", {
        "libraryName": "fastmcp"
    })
```

Lo mismo aplica para el cliente HTTP:

```python
async with http_client as client:
    tools = await client.list_tools()
    response = await client.call_tool("resolve-library-id", {
        "libraryName": "fastmcp"
    })
```

---

## Métodos clave del cliente

| Método | Qué hace |
|---|---|
| `client.list_tools()` | Lista todas las tools disponibles: nombre, descripción y metadata (incluye el input schema) |
| `client.call_tool("nombre", {params})` | Ejecuta una tool concreta pasándole los parámetros necesarios |

---

## Resumen mental rápido

> **MCP estandariza cómo un agente de IA descubre y usa herramientas externas — el cliente MCP traduce las peticiones a un formato común (JSON-RPC), gestiona la sesión con el servidor, y permite que el mismo agente hable con múltiples servidores distintos sin tener que programar una integración custom para cada uno.**
