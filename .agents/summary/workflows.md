# Workflows

## Application Startup

```mermaid
sequenceDiagram
    participant CLI as __main__
    participant CFG as Config
    participant AP as AudioPlayer
    participant VR as VideoRecorder
    participant DET as Detector

    CLI->>CFG: load_config(args.config)
    CFG-->>CLI: Config instance
    CLI->>CLI: _setup_logging(config.log_level)
    CLI->>AP: AudioPlayer(mp3_dir, volume)
    Note over AP: Discovers MP3s, inits mixer<br/>Fatal if no MP3s found
    CLI->>VR: VideoRecorder(video_dir, vflip, hflip)
    Note over VR: Tries picamera2 init<br/>Degrades if unavailable
    CLI->>DET: Detector(config, audio, video)
    DET->>DET: MotionSensor(pir_pin)
    CLI->>DET: run()
```

## Detection Loop

```mermaid
sequenceDiagram
    participant S as PIR Sensor
    participant D as Detector
    participant A as AudioPlayer
    participant V as VideoRecorder

    loop Forever
        S->>D: wait_for_motion() [blocks]
        D->>A: play_random()
        Note over A: Non-blocking playback
        D->>V: start()
        Note over V: Skipped if unavailable
        S->>D: wait_for_no_motion() [blocks]
        D->>V: stop()
        D->>D: sleep(cooldown_seconds)
    end
```

## Graceful Shutdown (Ctrl+C)

```mermaid
sequenceDiagram
    participant U as User
    participant D as Detector
    participant A as AudioPlayer
    participant V as VideoRecorder

    U->>D: KeyboardInterrupt
    D->>A: stop()
    D->>A: quit()
    D->>V: close()
    Note over V: Stops recording if active,<br/>releases camera
    D->>D: Log "Shutdown complete"
```

## Configuration Loading

1. Parse `--config` CLI argument
2. If path is None or file doesn't exist → return `Config()` with defaults
3. If file exists → parse with `tomllib`
4. If TOML is invalid → log error, `sys.exit(1)`
5. Map TOML sections to Config fields (missing keys use defaults)
6. Validate: volume 0.0–1.0, pin 0–27
7. If validation fails → log error, `sys.exit(1)`
