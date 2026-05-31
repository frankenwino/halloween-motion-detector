# Architecture

## Design Pattern

Single-process application with an event-driven blocking loop. Hardware I/O is abstracted behind classes with dependency injection for testability.

## System Architecture

```mermaid
graph TB
    subgraph Entry["Entry Point (__main__.py)"]
        CLI[CLI Args] --> CFG[load_config]
        CFG --> LOG[Setup Logging]
    end

    subgraph Components["Application Components"]
        AP[AudioPlayer]
        VR[VideoRecorder]
        DET[Detector]
    end

    subgraph Hardware["Hardware Layer"]
        PIR[PIR Sensor<br/>gpiozero]
        CAM[Pi Camera<br/>picamera2]
        SPK[Speakers<br/>pygame.mixer]
    end

    LOG --> AP
    LOG --> VR
    LOG --> DET
    DET --> AP
    DET --> VR
    DET --> PIR
    AP --> SPK
    VR --> CAM
```

## Concurrency Model

No explicit threading or multiprocessing. Both `pygame.mixer.music.play()` and `picamera2.start_recording()` are non-blocking — they manage background execution internally. The main thread blocks only on `MotionSensor.wait_for_motion()` and `wait_for_no_motion()`.

## Degradation Strategy

| Missing Resource | Behavior |
|-----------------|----------|
| Camera (picamera2) | WARNING logged, runs in audio-only mode |
| MP3 files | CRITICAL logged, `sys.exit(1)` |
| PIR sensor (gpiozero) | RuntimeError on init, application exits |
| Audio device (pygame) | Error on mixer.init(), application exits |

## Configuration Flow

```mermaid
flowchart LR
    A["--config flag"] --> B{File exists?}
    B -->|No| C[Use defaults]
    B -->|Yes| D[Parse TOML]
    D --> E{Valid?}
    E -->|No| F[Exit with error]
    E -->|Yes| G[Validate values]
    G --> H{In range?}
    H -->|No| F
    H -->|Yes| I[Return Config]
    C --> I
```

## Key Design Decisions

- **Dataclass for config**: Type-safe, immutable-ish, with field defaults
- **Package-relative paths**: MP3 dir resolved from `__file__`, not CWD
- **Lazy camera import**: `picamera2` imported inside `VideoRecorder.__init__` to allow graceful degradation
- **No global state**: All components receive dependencies via constructors
