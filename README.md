<div align="center">

[![Typing](https://readme-typing-svg.demolab.com?font=Fraunces\&weight=500\&size=30\&duration=3000\&pause=900\&color=C9A86A\&center=true\&vCenter=true\&width=960\&height=60\&lines=AIGORITMO;ARCANA+%C2%B7+ARCANO;Una+carta.+Una+presencia.;Voz+local+%C2%B7+Cerebro+intercambiable;Estudio+local+cinematogr%C3%A1fico)](http://127.0.0.1:8000/)

# **AIGORITMO**

### ARCANA · ARCANO

**Una carta. Una presencia. Una respuesta.**

Estudio local cinematográfico en español.
Dos presencias. Un solo Arcano Mayor. Voz local. Cerebro intercambiable.

<br>

[![LOCAL](https://img.shields.io/badge/RUN-LOCAL-C9A86A?style=for-the-badge\&labelColor=090909)](#-ejecución)
[![ARCANA](https://img.shields.io/badge/ARCANA-ORO_%2F_VELVET-C9A86A?style=for-the-badge\&labelColor=090909)](#-las-dos-presencias)
[![ARCANO](https://img.shields.io/badge/ARCANO-ACERO_%2F_NOCHE-8FA6B8?style=for-the-badge\&labelColor=090909)](#-las-dos-presencias)
[![PIPER](https://img.shields.io/badge/VOICE-PIPER-7DC7A8?style=for-the-badge\&labelColor=090909)](#-arquitectura)
[![OLLAMA](https://img.shields.io/badge/LLM-OLLAMA-9B8AFB?style=for-the-badge\&labelColor=090909)](#-cerebro)

</div>

---

# ✦ No es un chatbot

**Arcana** y **Arcano** son dos presencias para una misma experiencia.

No hay un catálogo infinito de personajes.
No hay un carrusel de avatares.
No hay tres cartas para fabricar una narrativa.

Hay **una presencia**, **una consulta** y **una carta**.

El sistema está diseñado para que la tecnología desaparezca detrás de la experiencia:

```text
              CONSULTA
                  │
                  ▼
        ┌─────────────────┐
        │    PRESENCIA    │
        │  Arcana / Arcano│
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  CARTA · LOCAL  │
        │   1 Arcano      │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │      LLM        │
        │ Ollama / Grok   │
        │    / ChatGPT    │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │   INTERPRETACIÓN│
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  VOZ · PIPER    │
        │    100% local   │
        └─────────────────┘
```

> **La interfaz muestra la experiencia.
> La arquitectura hace el trabajo.**

---

# ◈ Las dos presencias

No son skins.

Son dos tratamientos completos de la misma experiencia.

|                  | **ARCANA**             | **ARCANO**            |
| :--------------- | :--------------------- | :-------------------- |
| Atmósfera        | Oro · Velvet · Cálida  | Acero · Noche · Grave |
| Presencia        | Cercana                | Sobria                |
| Dirección visual | Ritual cinematográfico | Misterio tecnológico  |
| Voz              | Piper local            | Piper local           |
| Cerebro          | Intercambiable         | Intercambiable        |
| Cartas           | Arcano Mayor           | Arcano Mayor          |

### ARCANA

**Oro. Velvet. Calidez.**

Una presencia más envolvente, íntima y luminosa.

### ARCANO

**Acero. Noche. Profundidad.**

Una presencia más grave, contenida y nocturna.

El motor es común.

La personalidad visual cambia.

---

# 🃏 Una consulta → una carta

Esta es una regla estructural del proyecto:

```text
SALUDO
  │
  └── NO → tirada

CONSULTA
  │
  ▼
UNA CARTA
  │
  ▼
INTERPRETACIÓN
  │
  ▼
RESPUESTA
  │
  ▼
VOZ
```

### Nunca:

```text
❌ Pasado / Presente / Futuro
❌ Tres cartas
❌ Tiradas automáticas
❌ Carta al saludar
❌ Ruleta visible
❌ Selección manual del resultado
```

### Siempre:

```text
✓ Una consulta
✓ Una carta
✓ Una interpretación
✓ Una respuesta
```

La experiencia tiene menos elementos precisamente porque **cada elemento importa más**.

---

# ✧ Carta instantánea

La primera carta aparece **localmente**.

No depende de un servicio externo para que la experiencia pueda comenzar.

```text
LOCAL
  ↓
Carta disponible inmediatamente
```

Pollinations puede sustituir posteriormente la representación visual:

```text
Carta local
     │
     ├──────────────► inmediata
     │
     └── Pollinations ► ~8s
```

La generación remota es una mejora visual.

**No es una dependencia estructural.**

---

# ◉ Cerebro intercambiable

El sistema separa la experiencia de la inteligencia que hay detrás.

Actualmente puede trabajar con:

```text
┌──────────────────────┐
│      LLM PROVIDER    │
├──────────────────────┤
│ Ollama               │
│ Grok · xAI           │
│ ChatGPT · OpenAI     │
└──────────────────────┘
```

La interfaz no expone nombres de modelos.

El consultante ve:

> **Arcana**
> o
> **Arcano**

No:

> “Powered by [modelo que probablemente nadie pidió conocer]”.

La infraestructura puede cambiar.

**La experiencia permanece.**

---

# 🧠 LLM

Configuración mediante `.env`.

Primero:

```powershell
Copy-Item .env.example .env
```

Después configura **un proveedor**.

### 01 · Ollama

Sin claves externas.

```env
LLM_PROVIDER=ollama
```

Ideal para una ejecución completamente local del cerebro.

---

### 02 · Grok

```env
LLM_PROVIDER=spacexai
XAI_API_KEY=...
```

El YAML ya prioriza `spacexai`.

---

### 03 · ChatGPT

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=...
```

---

## Regla de oro

```text
.env
  │
  ├── nunca se versiona
  ├── nunca se pega en el chat
  └── nunca se publica
```

Las claves pertenecen a la máquina.

No al README.

No al repositorio.

Y definitivamente no a GitHub, que ya tiene suficientes secretos humanos flotando por ahí.

---

# 🔊 Voz

La voz es **100% local**.

Motor:

```text
PIPER
```

Flujo:

```text
LLM
 │
 ▼
Texto
 │
 ▼
Piper
 │
 ▼
Audio local
 │
 ▼
Experiencia
```

No se envía la voz a un proveedor externo.

La elección del LLM y la generación de voz están desacopladas.

```text
             ┌──────────────┐
             │     LLM      │
             └──────┬───────┘
                    │
                 texto
                    │
                    ▼
             ┌──────────────┐
             │    PIPER     │
             └──────┬───────┘
                    │
                  audio
                    │
                    ▼
               PRESENCIA
```

---

# 🎬 La experiencia

La interfaz está planteada como un **salón**, no como una consola técnica.

```text
┌────────────────────────────────────────────────────┐
│                                                    │
│                     ARCANA                         │
│                                                    │
│                 ◉ presencia                       │
│                                                    │
│            ┌──────────────────┐                    │
│            │                  │                    │
│            │      CARTA       │                    │
│            │                  │                    │
│            └──────────────────┘                    │
│                                                    │
│     “Escribe aquello que realmente quieres saber.” │
│                                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │                                              │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Elementos principales

* Chat amplio tipo salón
* Orbe de presencia
* Avatar intercambiable
* Fundido entre presencias
* Carta visible
* Respuesta textual
* Voz
* Atmósfera cinematográfica

La interfaz intenta conseguir algo bastante sencillo:

**que el usuario deje de pensar en la interfaz.**

---

# ✦ Orbe de presencia

El orbe funciona como elemento central de identidad.

No es simplemente decoración.

Representa:

```text
IDLE
 │
 ├── espera
 │
 ▼
THINKING
 │
 ├── consulta procesándose
 │
 ▼
SPEAKING
 │
 └── Piper reproduciendo voz
```

La presencia permanece viva aunque el sistema esté esperando.

---

# ⇄ Cambio de presencia

Arcana ↔ Arcano

El cambio no debería sentirse como cambiar de página.

Debe sentirse como cambiar de habitación.

```text
ARCANA
  │
  │  fade
  ▼
NEUTRAL
  │
  │  fade
  ▼
ARCANO
```

Mismo motor.

Otra atmósfera.

Otra presencia.

---

# 🏗 Arquitectura conceptual

```text
                    ┌───────────────────┐
                    │     FRONTEND      │
                    │                   │
                    │ Salón · Orbe      │
                    │ Carta · Chat      │
                    │ Presencia         │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      BACKEND      │
                    │                   │
                    │ Estado · Routing  │
                    │ Consultas         │
                    └─────────┬─────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
           ┌────────┐   ┌──────────┐   ┌────────┐
           │ CARTAS │   │   LLM    │   │ PIPER  │
           │ LOCAL  │   │          │   │ LOCAL  │
           └────────┘   └────┬─────┘   └────────┘
                              │
                     ┌────────┴────────┐
                     │                 │
                  Ollama             APIs
                                  Grok / OpenAI
```

La separación importante es:

```text
EXPERIENCIA
     ≠
INTELIGENCIA
     ≠
VOZ
     ≠
REPRESENTACIÓN DE CARTA
```

Cada capa puede evolucionar sin destruir las demás.

---

# ⚙️ Qué está cerrado

La versión definitiva fija estas reglas:

| Sistema                | Estado |
| :--------------------- | :----: |
| Arcana                 |    ✓   |
| Arcano                 |    ✓   |
| Saludo sin tirada      |    ✓   |
| Una carta por consulta |    ✓   |
| Carta local            |    ✓   |
| Pollinations opcional  |    ✓   |
| Piper local            |    ✓   |
| Ollama                 |    ✓   |
| Grok / xAI             |    ✓   |
| ChatGPT / OpenAI       |    ✓   |
| Chat tipo salón        |    ✓   |
| Orbe de presencia      |    ✓   |
| Cambio con fundido     |    ✓   |

**No es un catálogo de posibilidades.**

Es una experiencia con decisiones ya tomadas.

---

# 🚀 Ejecución

Desde PowerShell:

```powershell
powershell -File X:\GitHub\systems-lab\aigoritmo\PROBAR-ARCANA.ps1
```

Después:

```text
http://127.0.0.1:8000
```

### Health check

```text
http://127.0.0.1:8000/health
```

Versión:

```text
2.1.0-definitiva
```

### Atajo

```text
X:\PROBAR-ARCANA.bat
```

Documentación adicional:

```text
COMO-EJECUTAR.md
```

---

# 🩶 Flujo completo

```text
             ┌───────────────┐
             │    START      │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │   PRESENCIA   │
             │ Arcana/Arcano │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │    SALUDO     │
             └───────┬───────┘
                     │
                     │
                  esperar
                     │
                     ▼
             ┌───────────────┐
             │    CONSULTA   │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │  UNA CARTA    │
             │    LOCAL      │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │      LLM      │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │ INTERPRETACIÓN│
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │     PIPER     │
             │     LOCAL     │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │    RESPUESTA  │
             └───────────────┘
```

---

# 🔒 Principios técnicos

### Local first

La experiencia debe funcionar localmente siempre que sea posible.

### Provider agnostic

Ollama, Grok y OpenAI son proveedores intercambiables.

### Voice local

Piper mantiene la voz fuera de la arquitectura cloud.

### Experience first

Los nombres internos de modelos no forman parte de la experiencia.

### Deterministic UX

Las reglas de interacción están cerradas:

```text
1 consulta
1 carta
1 interpretación
1 respuesta
```

### Modularidad

Carta, LLM, voz y presencia no dependen conceptualmente de una única implementación.

---

# 🗂 Configuración

Estructura conceptual:

```text
aigoritmo/
│
├── .env.example
├── .env
│
├── PROBAR-ARCANA.ps1
├── PROBAR-ARCANA.bat
├── COMO-EJECUTAR.md
│
├── backend/
│   ├── ...
│   └── ...
│
├── frontend/
│   ├── ...
│   └── ...
│
├── cards/
│   └── ...
│
└── voice/
    └── Piper
```

> La estructura exacta puede evolucionar.
> La arquitectura conceptual no.

---

# 🧪 Estado

```text
ARCANA / ARCANO
        │
        ▼
  DEFINITIVA 2.1.0
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
CARTA   LLM   VOZ
LOCAL   SWAP  LOCAL
```

### Estado actual

**Definitiva.**

No significa que el código jamás pueda cambiar.

Significa que las reglas fundamentales de la experiencia ya están decididas.

---

# ✦ Filosofía

Arcana no intenta demostrar que una IA puede hablar.

Eso ya lo hemos comprobado unas cuantas veces.

El experimento es otro:

> **¿Qué ocurre cuando la tecnología deja de presentarse como tecnología?**

No ves:

```text
MODEL: ...
TEMPERATURE: ...
PROVIDER: ...
TOKEN: ...
```

Ves:

```text
PRESENCIA
    ↓
CARTA
    ↓
INTERPRETACIÓN
    ↓
VOZ
```

La complejidad existe.

Simplemente está detrás del telón.

---

# AIGORITMO

**Arcana · Arcano**

```text
LOCAL STUDIO
     │
     ├── PRESENCE
     ├── CARD
     ├── INTELLIGENCE
     ├── VOICE
     └── EXPERIENCE
```

**Una carta. Una presencia. Una respuesta.**

<br>

[![RUN](https://img.shields.io/badge/▶_EJECUTAR-ARCANA-C9A86A?style=for-the-badge\&labelColor=090909)](http://127.0.0.1:8000/)

</div>

---

### © 2026 Aigoritmo

Estudio experimental local de Gracián Baena.

**Arcana / Arcano · versión 2.1.0-definitiva**
