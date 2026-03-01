# English Flashcard Player

Minimal English vocabulary player built with **Flet**.  
Reads words from Excel and provides distraction-free playback for focused memorization.

---

## Features

- Smart Excel column detection (Word / Meaning / Example)
- Auto & manual playback
- Sequential / Random mode
- Keyboard shortcuts
- Persistent settings (`config.json`)
- Clean auto-hide control panel

---

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Excel Format

Supports:

- With header (auto keyword matching)
- Without header (Col1=Word, Col2=Meaning, Col3=Example)

Default file: `list.xlsx`  
Configurable via `config.json`

---

## Shortcuts

| Key | Action |
|------|--------|
| Space | Play / Pause |
| -> | Next |
| <- | Previous (Sequential only) |
| M | Toggle Random |
| R | Reload Excel |

---

## Configuration

Editable in `config.json`:

- `display_time`
- `is_random_mode`
- `window_width` / `window_height`
- `always_on_top`
- `excel_file`
- `sheet_name`

---

## Philosophy

Designed for focus.  
No noise. No clutter. Just repetition.

---

Michael Lu  
michaellu0220@gmail.com