# MSD-PRO Configurator

A graphical configuration tool for the **Mars Gaming MSD-PRO** StreamDock device.

## Features

- **Key Configuration**: Configure all 15 main keys + 4 secondary screen keys
- **Knob Configuration**: Set actions for 4 knobs (press, rotation left/right)
- **Touchscreen**: Set background image (800×480px) and configure swipe gestures
- **Action Types**: Assign different action types to keys/knobs/swipes:
  - Shell commands (execute any command)
  - Media controls (play, pause, volume, etc.)
  - Open URLs
  - Open applications
  - Plugin actions (for future extensions)
- **Visual Preview**: Real-time preview of key icons and touchscreen
- **Save/Load**: Save configurations to JSON files and load them later
- **Mock Mode**: Develop and test without physical hardware

## Screenshots

*(Add screenshots here after first run)*

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

### Setup

```bash
# Clone the repository (if not already done)
git clone https://github.com/Cpt-JohnSpareribs/StreamDock-Device-SDK.git
cd StreamDock-Device-SDK/Python-SDK/tools/msdpro_configurator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Development Setup

For development, install in editable mode:

```bash
pip install -e .
```

## Usage

### Run with Mock Devices (Testing)

```bash
python -m msdpro_configurator.main
# or
python main.py
```

### Run with Real Hardware

```bash
python -m msdpro_configurator.main --real
```

### Command Line Options

```
--real    Use real StreamDock SDK (requires MSD-PRO hardware)
--mock    Use mock devices for testing (default)
```

## Project Structure

```
msdpro_configurator/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md               # This file
├── core/
│   ├── __init__.py
│   ├── device_handler.py   # SDK integration
│   └── config_manager.py   # Configuration management
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── key_grid.py         # Key grid widget
│   ├── knob_panel.py       # Knob configuration panel
│   ├── touchscreen.py      # Touchscreen configuration
│   └── styles.py           # Dark pastel color theme
└── utils/
    ├── __init__.py
    └── image_helpers.py     # Image processing utilities
```

## Configuration Format

Configurations are saved as JSON files with the `.msdpro.json` extension.

### Example Configuration

```json
{
  "device_name": "MSD-PRO",
  "device_serial": "ABC123",
  "keys": {
    "1": {
      "action_type": "shell",
      "command": "notepad.exe"
    },
    "2": {
      "action_type": "media",
      "command": "volume_up"
    }
  },
  "knobs": {
    "1": {
      "press": {"action_type": "shell", "command": "calc.exe"},
      "rotate_left": {"action_type": "shell", "command": "prev_track"},
      "rotate_right": {"action_type": "shell", "command": "next_track"}
    }
  },
  "touchscreen_background": "/path/to/image.jpg",
  "swipe": {
    "left": {"action_type": "shell", "command": "alt_tab"},
    "right": {"action_type": "shell", "command": "show_desktop"}
  },
  "brightness": 80
}
```

## Action Types

| Type | Description | Command Examples |
|------|-------------|------------------|
| `none` | No action | - |
| `shell` | Execute shell command | `notepad.exe`, `calc`, `python script.py` |
| `key_press` | Simulate key press | `F1`, `Ctrl+C`, `Alt+Tab` |
| `media` | Media controls | `play`, `pause`, `volume_up`, `volume_down` |
| `open_url` | Open URL in browser | `https://google.com` |
| `open_app` | Open application | `chrome.exe`, `notepad++.exe` |
| `plugin` | Trigger plugin action | Plugin-specific |
| `event` | Trigger custom event | Event name |

## Device Support

- **MSD-PRO (N4Pro)**: Full support (15 keys, 4 knobs, touchscreen, swipe gestures)
- **Other StreamDock devices**: Limited support (may work with some features)

## Color Theme

The application uses a **dark pastel color theme**:

- **Green**: Primary actions, buttons
- **Gray**: Backgrounds, neutral elements
- **Gold**: Accents, highlights, secondary actions

## Development

### Adding New Features

1. Create a new module in the appropriate directory (`core/`, `ui/`, or `utils/`)
2. Add functionality to the module
3. Integrate with the main window or other components
4. Add tests (optional)

### Testing

Run the application in mock mode for testing:

```bash
python main.py --mock
```

### Debugging

Enable debug logging by setting the `DEBUG` environment variable:

```bash
DEBUG=1 python main.py
```

## Troubleshooting

### Common Issues

1. **PyQt6 not found**: Make sure PyQt6 is installed (`pip install PyQt6`)
2. **SDK not available**: The application will automatically fall back to mock mode
3. **Device not detected**: Check USB connection, try reconnecting the device
4. **Image loading failed**: Ensure the image path is correct and the file exists

### Logs

Check the console output for error messages. For more detailed logging, enable debug mode.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a Pull Request

### Code Style

- Use type hints
- Add docstrings to all public methods
- Follow PEP 8 guidelines
- Use descriptive variable names
- Add comments for complex logic

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits

- **StreamDock SDK**: [Original SDK Repository](https://github.com/Cpt-JohnSpareribs/StreamDock-Device-SDK)
- **PyQt6**: [Qt for Python](https://www.qt.io/qt-for-python)
- **Pillow**: [Python Imaging Library](https://python-pillow.org/)

## Contact

For questions or support, please contact the repository maintainer.
