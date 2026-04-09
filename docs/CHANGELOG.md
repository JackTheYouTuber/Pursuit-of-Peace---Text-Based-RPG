# Pursuit of Peace — Changelog

## v0.7.5 (2026-04-09)

### UI System Overhaul

- **Dynamic theme constants** – `constants.py` now evaluates colours, fonts, and padding at runtime, so the loaded `themes.json` is actually respected.
- **Fixed critical syntax error** in `StyleManager.init_styles` (missing `def` keyword).
- **Corrected missing `const.` prefixes** in `dialog_box.py`, `input_field.py`, and `text_display.py`.
- **Replaced invalid `cget("background")` calls** with `const.CARD_BG` in `StatBar` and all complex panels.
- **Added `FONT_BOLD`** to the dynamic constants module.

All UI components now properly apply the user’s selected theme. The game no longer crashes due to TclError or NameError when building the main window.
