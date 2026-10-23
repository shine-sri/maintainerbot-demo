# TinyNotes

> TinyNotes is a **fictional project** used to demo [MaintainerBot](https://github.com/shine-sri/maintainerbot). Open an issue to see the bot respond. See [DEMO.md](DEMO.md) for ideas.

TinyNotes is a small command-line notes app. It stores your notes in a local file, and supports tags, search and a simple config file. It has no dependencies and runs on Windows, macOS and Linux.

## Installation

TinyNotes needs Python 3.9 or newer. Install it with pip:

```bash
pip install tinynotes
```

On Windows, open PowerShell or Command Prompt and run the same command. If `pip` is not recognized, use `py -m pip install tinynotes` instead. On macOS and Linux, use `python3 -m pip install tinynotes` if `pip` points to an old Python. A virtual environment is recommended but not required. Check the install with `tinynotes --version`.

## Quick start

Create your first note with `tinynotes add "Buy milk"`. List all notes with `tinynotes list`, which shows each note with its id. Edit a note with `tinynotes edit <id>`, which opens your editor. Delete a note with `tinynotes delete <id>`. Run `tinynotes --help` to see every command.

## Configuration

TinyNotes reads its settings from `~/.tinynotes/config.toml` (on Windows, `C:\Users\<you>\.tinynotes\config.toml`). Set `notes_path` to change where notes are saved. It can point to any folder, including a folder synced by Dropbox, iCloud or OneDrive. Set `editor` to choose the editor used by `tinynotes edit`. To reset everything to defaults, delete the config file.

## Tags and search

Add tags when you create a note: `tinynotes add "Dentist" --tag health`. You can repeat `--tag` to add several. Search note text with `tinynotes search milk`. Filter by tag with `tinynotes list --tag health`. Searches are case-insensitive, and partial words match.

## Updating and uninstalling

Update to the latest version with `pip install --upgrade tinynotes`. Your notes and config are kept. To uninstall, run `pip uninstall tinynotes`. Uninstalling does not delete your notes file. To remove all data, delete the `~/.tinynotes` folder yourself.

## Troubleshooting

If you see "command not found" after installing, your Python scripts folder is not on your PATH. Run TinyNotes with `python -m tinynotes` instead, or add the scripts folder to PATH. If `tinynotes list` shows nothing, check that `notes_path` in your config points to the right file. If a note file becomes corrupted, restore the backup at `notes.json.bak` in the same folder.

## Contributing

Open an issue to discuss changes before sending a pull request. Run the tests with `pytest` and format code with `black`. Keep pull requests small and focused, and add a test for any bug you fix. Be kind in reviews and discussions.

## License

TinyNotes is released under the MIT License.
