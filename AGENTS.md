# AGENTS.md

## Cursor Cloud specific instructions

This is a single-file Python/Kivy application (`main.py`) that calculates aircraft takeoff performance characteristics. All UI text is in Russian.

### Running the application

```
export DISPLAY=:1
python3 main.py
```

On headless environments, use `xvfb-run -a python3 main.py` to run with a virtual framebuffer.

### Linting

```
flake8 main.py --max-line-length=120
```

Most existing lint warnings are E231 (missing whitespace) in large numeric lookup tables — these are intentional for readability of the tabular data.

### Key notes

- The only runtime dependency is `kivy` (installed via pip).
- The `libmtdev.so.1` error on startup is non-critical — it's a touch input provider that isn't needed on desktop/headless environments.
- The app window opens at default Kivy size; on first launch you may need to click "Взлётные характеристики" to access the calculator form.
- `buildozer.spec` is for Android APK packaging only — not needed for desktop development or testing.
