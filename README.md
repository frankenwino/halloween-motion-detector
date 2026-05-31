# Halloween Motion Detector

A Raspberry Pi application that uses a PIR motion sensor to trigger spooky MP3 playback and video recording. When motion is detected, a random sound plays through USB speakers while the Pi Camera records video. When motion stops, recording ends and the system enters a cooldown period before watching for motion again.

## Hardware Requirements

- Raspberry Pi 3, 4, or 5
- PIR motion sensor (HC-SR501 or compatible)
- Raspberry Pi Camera Module (v2 or v3)
- USB speakers or 3.5mm audio output
- Raspberry Pi OS Bookworm or later

## Wiring

| PIR Sensor Pin | Raspberry Pi Pin |
|----------------|------------------|
| VCC            | 5V (Pin 2)       |
| GND            | GND (Pin 6)      |
| OUT (Signal)   | BCM 4 (Pin 7)    |

The signal pin is configurable via `config.toml` (default: BCM pin 4).

## Installation

```bash
# Clone the repository
git clone https://github.com/frankenwino/halloween-motion-detector.git
cd halloween-motion-detector

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .

# For development (includes pytest)
pip install -e ".[dev]"
```

## Configuration

The application works with sensible defaults out of the box. To customize, create a `config.toml` file:

```toml
[sensor]
pir_pin = 4              # BCM pin number (0-27)

[audio]
volume = 0.7             # 0.0 (silent) to 1.0 (max)
# mp3_dir = "/path/to/custom/mp3/folder"

[video]
# output_dir = "/home/pi/halloween-videos"
camera_vflip = true      # Flip vertically (camera mounted upside-down)
camera_hflip = true      # Flip horizontally

[app]
cooldown_seconds = 15    # Pause between detection cycles
log_level = "INFO"       # DEBUG, INFO, WARNING, ERROR
```

All values are optional — defaults are used for any missing setting.

## Usage

```bash
# Run with defaults
halloween-motion-detector

# Run with a custom config file
halloween-motion-detector --config /path/to/config.toml

# Stop with Ctrl+C (graceful shutdown)
```

The application will:
1. Wait for motion on the PIR sensor
2. Play a random MP3 from the sounds directory
3. Record video (if camera is available)
4. Wait for motion to stop
5. Stop recording and enter cooldown
6. Repeat

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov --cov-report=term-missing

# Check coverage meets threshold
pytest --cov --cov-fail-under=80
```

## Troubleshooting

### No camera detected

The application runs in **audio-only mode** if no camera is found. You'll see a warning:

```
Camera unavailable: ... Running in audio-only mode.
```

To fix: ensure the camera is connected, enabled (`sudo raspi-config` → Interface Options → Camera), and your user is in the `video` group.

### No audio output

If you hear nothing:
- Check USB speakers are connected and powered
- Verify audio output: `aplay /usr/share/sounds/alsa/Front_Center.wav`
- Check volume isn't muted: `alsamixer`
- Ensure your user is in the `audio` group

### No MP3 files found (fatal error)

The application exits if no `.mp3` files are found in the configured directory. The default location is the bundled `mp3/` folder inside the package. If using a custom `mp3_dir`, ensure it contains at least one `.mp3` file.

### Permission errors

Ensure your user is in the required groups:

```bash
sudo usermod -aG gpio,video,audio $USER
# Log out and back in for changes to take effect
```

### PIR sensor not triggering

- Check wiring (VCC, GND, Signal)
- Adjust sensitivity and delay potentiometers on the HC-SR501
- Test with: `python3 -c "from gpiozero import MotionSensor; pir = MotionSensor(4); pir.wait_for_motion(); print('Motion!')"`

## License

GNU General Public License v3 — see [LICENSE](LICENSE) for details.
