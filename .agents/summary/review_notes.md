# Review Notes

## Consistency Check

✅ All documentation files reference the same module structure and API signatures.
✅ Config field names are consistent across docs.
✅ Degradation behavior described consistently (camera optional, audio required).

## Completeness Check

### Well Documented
- Configuration system (all fields, validation, TOML format)
- Component responsibilities and interfaces
- Detection loop workflow
- Error handling and degradation strategy
- Test coverage and structure

### Gaps Identified

| Area | Gap | Recommendation |
|------|-----|----------------|
| Video format | No documentation on H.264 playback/conversion | Add note about converting with ffmpeg |
| Max recording duration | No timeout on `wait_for_no_motion()` | Consider adding configurable max recording time |
| Log file output | Logs go to stderr only | Consider adding file handler option |
| MP3 file requirements | No docs on supported bitrates/formats | Document pygame.mixer MP3 limitations |
| Systemd service | No docs on running as a service | Add example .service file |

## Recommendations

1. **Add a systemd service file** — users will want this to run on boot
2. **Add max recording duration** — prevent infinite recordings if sensor stays triggered
3. **Document MP3 format requirements** — pygame.mixer has limitations with certain encodings
4. **Consider adding `--dry-run`** — useful for testing without hardware
5. **Add `.gitignore` entry for video output** — prevent accidental commits of recordings
