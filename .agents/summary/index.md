# Documentation Index — Halloween Motion Detector

## How to Use This Documentation (AI Assistants)

This index is your primary entry point. Start here to determine which file contains the information you need.

**Quick navigation:**
- Architecture questions → `architecture.md`
- What does component X do? → `components.md`
- How do modules interact? → `interfaces.md`
- Data structures and file formats → `data_models.md`
- How does the detection loop work? → `workflows.md`
- What libraries are used? → `dependencies.md`
- Raw codebase facts → `codebase_info.md`
- Known gaps and improvements → `review_notes.md`

## Project Summary

A Raspberry Pi application that uses a PIR motion sensor to trigger simultaneous MP3 playback and video recording. Python 3.11+ with 5 modules, TOML configuration, and graceful degradation (runs audio-only if no camera). Built with gpiozero, picamera2, and pygame.

## Documentation Files

| File | Purpose | Consult When... |
|------|---------|-----------------|
| [codebase_info.md](codebase_info.md) | Tech stack, directory structure, entry points | You need factual metadata about the project |
| [architecture.md](architecture.md) | System design, concurrency model, degradation strategy | You need to understand the overall design |
| [components.md](components.md) | Individual components and their responsibilities | You need to modify or understand a specific module |
| [interfaces.md](interfaces.md) | CLI, TOML schema, hardware connections, Python APIs | You need to change configuration or component contracts |
| [data_models.md](data_models.md) | Config dataclass, file formats, runtime state | You need to understand data flow or outputs |
| [workflows.md](workflows.md) | Startup, detection loop, shutdown sequences | You need to understand or modify runtime behavior |
| [dependencies.md](dependencies.md) | External libraries, platform requirements | You need to update, replace, or add dependencies |
| [review_notes.md](review_notes.md) | Documentation gaps and improvement ideas | You want to improve the project |

## Relationships Between Files

```mermaid
graph LR
    INDEX[index.md] --> ARCH[architecture.md]
    INDEX --> COMP[components.md]
    INDEX --> IFACE[interfaces.md]
    INDEX --> DATA[data_models.md]
    INDEX --> WORK[workflows.md]
    INDEX --> DEPS[dependencies.md]

    ARCH --> COMP
    COMP --> IFACE
    WORK --> COMP
    WORK --> DATA
    DEPS --> COMP
```

- **architecture.md** provides the high-level view; **components.md** details each piece
- **workflows.md** references components and data models to explain runtime behavior
- **interfaces.md** bridges components and describes their contracts
- **dependencies.md** maps external libraries to the components that use them
