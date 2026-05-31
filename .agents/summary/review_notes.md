# Review Notes

## Consistency Check ✅

All documentation files are internally consistent:
- Function signatures match across `components.md` and `interfaces.md`
- Dependency information is consistent between `dependencies.md` and `architecture.md`
- Hardware pin assignments are consistent across all files (BCM pin 4)
- File paths and naming conventions are consistent throughout

## Completeness Check

### Gaps Identified

| Area | Gap | Severity | Recommendation |
|------|-----|----------|----------------|
| Testing | Tests are empty placeholders — no actual test coverage | High | Write unit tests for `random_mp3()`, `video_file_info()`, `current_time()` with mocked hardware |
| Error handling | No error handling for missing mp3/ directory, empty mp3 list, camera failures, or audio device unavailability | High | Add try/except blocks and meaningful error messages |
| Configuration | All parameters hardcoded (pin, volume, sleep time, flip settings) | Medium | Extract to config file or CLI arguments |
| Packaging bug | `pygame` not listed in `install_requires` | Medium | Add `pygame` to setup.py requirements |
| Multiprocessing misuse | `camera.start_recording()` and `mixer.music.play()` return `None`, so `multiprocessing.Process(target=None)` is a no-op | High | The multiprocessing code doesn't actually parallelize anything — the calls execute inline before Process is created |
| Deprecated dependency | `picamera` is deprecated; `picamera2` is the replacement | Low | Migrate when targeting newer Raspberry Pi OS |
| Python version support | Classifiers list Python 2.6–3.5 but shebang is Python 3 | Low | Update classifiers to reflect actual supported versions |
| Documentation | Sphinx docs have no actual API content (just template stubs) | Low | Run `sphinx-apidoc` and fill in docstrings |
| MP3 path resolution | Uses `os.getcwd()` which depends on where the script is run from, not where it's installed | Medium | Use `__file__`-relative paths or `pkg_resources` |

### Multiprocessing Bug Detail

In `main()`:
```python
for f in [camera.start_recording(video_file_path), mixer.music.play()]:
    j = multiprocessing.Process(target=f)
```

Both `camera.start_recording()` and `mixer.music.play()` are **called immediately** in the list comprehension. Their return values (`None`) are passed as `target` to `Process`. The multiprocessing code is effectively dead code — recording and playback happen synchronously in the main process.

## Recommendations

1. **Fix the multiprocessing bug** — either wrap calls in lambdas/functions or remove multiprocessing entirely (pygame and picamera both handle async internally)
2. **Add pygame to install_requires** in setup.py
3. **Add error handling** for hardware initialization failures
4. **Write actual tests** — at minimum for the utility functions
5. **Use `__file__`-relative paths** instead of `os.getcwd()` for MP3 directory resolution
6. **Add CLI arguments or config file** for hardware settings (pin, volume, sleep time)
