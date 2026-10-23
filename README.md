# TinyNotes

TinyNotes is a small command-line notes app. It stores notes in a local file and supports tags and search.

## Installation

TinyNotes needs Python 3.9 or newer. Install it with pip:

```bash
pip install tinynotes
```

On Windows, open PowerShell or Command Prompt and run the same command. If `pip` is not recognized, use `py -m pip install tinynotes`. A virtual environment is recommended but not required.

## Quick start

Create your first note with `tinynotes add "Buy milk"`. List all notes with `tinynotes list`. Delete a note with `tinynotes delete <id>`.

## Configuration

TinyNotes reads its settings from `~/.tinynotes/config.toml`. You can change the notes file location with `notes_path` and the default editor with `editor`. To reset to defaults, delete the config file.

## Tags and search

Add tags when you create a note: `tinynotes add "Dentist" --tag health`. Search by text with `tinynotes search milk`, or filter by tag with `tinynotes list --tag health`.

## Contributing

Open an issue to discuss changes before sending a pull request. Run the tests with `pytest` and format code with `black`.
