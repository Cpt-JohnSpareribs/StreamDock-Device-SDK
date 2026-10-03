"""
Main Window for MSD-PRO Configurator.
The primary application window containing all configuration panels.

This window provides:
- Device selection and connection management
- Tabbed interface for different configuration sections
- Key, knob, and touchscreen configuration
- Save/load configuration functionality
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QComboBox, QPushButton, QStatusBar, QFileDialog,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont

from .styles import get_complete_style, TEXT_PRIMARY, PASTEL_GREEN_2, PASTEL_GOLD_2
from .key_grid import KeyGridWithPreview
from .knob_panel import KnobPanel
from .touchscreen import TouchscreenConfig
from ..core.device_handler import DeviceHandler, DeviceInfo, DeviceState
from ..core.config_manager import (
    ConfigManager, DeviceConfig, ActionType, KeyAction, KnobAction, Direction
)


class MainWindow(QMainWindow):
    """
    Main application window for MSD-PRO configuration.
    
    Features:
    - Tabbed interface for different configuration sections
    - Device connection management
    - Configuration save/load
    - Real-time preview
    """
    
    def __init__(self, device_handler: Optional[DeviceHandler] = None):
        """
        Initialize the main window.
        
        Args:
            device_handler: Optional DeviceHandler instance
        """
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("MSD-PRO Configurator")
        self.setMinimumSize(1000, 700)
        
        # Apply stylesheet
        self.setStyleSheet(get_complete_style())
        
        # Initialize device handler
        self.device_handler = device_handler or DeviceHandler(use_mock=True)
        self.config_manager = ConfigManager()
        
        # Current configuration
        self.current_config: Optional[DeviceConfig] = None
        self.current_config_path: Optional[str] = None
        
        # Setup UI
        self._setup_ui()
        
        # Setup connections
        self._setup_connections()
        
        # Load last configuration
        self._load_default_config()
        
        # Setup timers for periodic checks
        self._setup_timers()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Device bar (top)
        self._create_device_bar(main_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #3A3A3A;
                background-color: #2D2D2D;
            }}
            QTabBar::tab {{
                background-color: #2D2D2D;
                color: {TEXT_PRIMARY};
                padding: 8px 16px;
                border: 1px solid #3A3A3A;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {PASTEL_GREEN_2};
                color: #1E1E1E;
                border-bottom: 1px solid {PASTEL_GREEN_2};
            }}
            QTabBar::tab:hover {{
                background-color: #3A3A3A;
            }}
        """)
        
        # Create tabs
        self._create_keys_tab()
        self._create_knobs_tab()
        self._create_touchscreen_tab()
        self._create_settings_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: #2D2D2D;
                color: {PASTEL_GOLD_2};
                border-top: 1px solid #3A3A3A;
            }}
        """)
        self.setStatusBar(self.status_bar)
        
        # Set initial status
        self._update_status()
    
    def _create_device_bar(self, layout):
        """Create the device selection bar."""
        device_bar = QWidget()
        device_bar.setStyleSheet(f"""
            QWidget {{
                background-color: #2D2D2D;
                border-bottom: 1px solid #3A3A3A;
                padding: 8px;
            }}
        """)
        
        device_layout = QHBoxLayout(device_bar)
        device_layout.setContentsMargins(10, 0, 10, 0)
        device_layout.setSpacing(10)
        
        # Device label
        device_label = QLabel("Device:")
        device_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        device_layout.addWidget(device_label)
        
        # Device combo
        self.device_combo = QComboBox()
        self.device_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #1E1E1E;
                color: {TEXT_PRIMARY};
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 4px;
                min-width: 200px;
            }}
        """)
        device_layout.addWidget(self.device_combo)
        
        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PASTEL_GREEN_2};
                color: #1E1E1E;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PASTEL_GREEN_3};
            }}
            QPushButton:disabled {{
                background-color: #3A3A3A;
                color: #606060;
            }}
        """)
        device_layout.addWidget(self.connect_button)
        
        # Disconnect button
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #8B0000;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #A00000;
            }}
            QPushButton:disabled {{
                background-color: #3A3A3A;
                color: #606060;
            }}
        """)
        device_layout.addWidget(self.disconnect_button)
        
        # Save button
        self.save_button = QPushButton("💾 Save")
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PASTEL_GOLD_2};
                color: #1E1E1E;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #BF9F77;
            }}
        """)
        device_layout.addWidget(self.save_button)
        
        # Load button
        self.load_button = QPushButton("📂 Load")
        self.load_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #454545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """)
        device_layout.addWidget(self.load_button)
        
        # Add stretch
        device_layout.addStretch()
        
        # Help button
        self.help_button = QPushButton("?")
        self.help_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #3A3A3A;
                color: white;
                border: none;
                border-radius: 20px;
                width: 30px;
                height: 30px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #454545;
            }}
        """)
        device_layout.addWidget(self.help_button)
        
        layout.addWidget(device_bar)
    
    def _create_keys_tab(self):
        """Create the keys configuration tab."""
        self.keys_tab = QWidget()
        self.keys_tab.setStyleSheet(f"background-color: #1E1E1E;")
        
        layout = QVBoxLayout(self.keys_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Key Configuration (15 Main + 4 Secondary Keys)")
        title.setStyleSheet(f"""
            QLabel {{
                color: {PASTEL_GOLD_2};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(title)
        
        # Key grid with preview
        self.key_grid = KeyGridWithPreview()
        self.key_grid.key_selected.connect(self._on_key_selected)
        layout.addWidget(self.key_grid)
        
        # Key action configuration panel
        self._create_key_action_panel(layout)
        
        self.tab_widget.addTab(self.keys_tab, "🎹 Keys")
    
    def _create_key_action_panel(self, layout):
        """Create the key action configuration panel."""
        action_group = QWidget()
        action_group.setStyleSheet(f"""
            QWidget {{
                background-color: #2D2D2D;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        
        action_layout = QVBoxLayout(action_group)
        
        # Title
        action_title = QLabel("Selected Key Action")
        action_title.setStyleSheet(f"""
            QLabel {{
                color: {PASTEL_GREEN_2};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        action_layout.addWidget(action_title)
        
        # Action type
        self.key_action_type = QComboBox()
        self.key_action_type.addItems([t.value for t in ActionType])
        action_layout.addWidget(self.key_action_type)
        
        # Command input
        self.key_action_command = QLineEdit()
        self.key_action_command.setPlaceholderText(
            "Enter shell command (e.g., 'notepad.exe' or 'calc')"
        )
        action_layout.addWidget(self.key_action_command)
        
        # Apply button
        self.key_action_apply = QPushButton("Apply to Selected Key")
        self.key_action_apply.setStyleSheet(f"""
            QPushButton {{
                background-color: {PASTEL_GREEN_2};
                color: #1E1E1E;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PASTEL_GREEN_3};
            }}
        """)
        self.key_action_apply.clicked.connect(self._apply_key_action)
        action_layout.addWidget(self.key_action_apply)
        
        layout.addWidget(action_group)
    
    def _create_knobs_tab(self):
        """Create the knobs configuration tab."""
        self.knobs_tab = QWidget()
        self.knobs_tab.setStyleSheet(f"background-color: #1E1E1E;")
        
        layout = QVBoxLayout(self.knobs_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Knob panel
        self.knob_panel = KnobPanel()
        layout.addWidget(self.knob_panel)
        
        self.tab_widget.addTab(self.knobs_tab, "🎚️ Knobs")
    
    def _create_touchscreen_tab(self):
        """Create the touchscreen configuration tab."""
        self.touchscreen_tab = QWidget()
        self.touchscreen_tab.setStyleSheet(f"background-color: #1E1E1E;")
        
        layout = QVBoxLayout(self.touchscreen_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Touchscreen config
        self.touchscreen_config = TouchscreenConfig()
        layout.addWidget(self.touchscreen_config)
        
        # Brightness control
        self._create_brightness_control(layout)
        
        self.tab_widget.addTab(self.touchscreen_tab, "📱 Touchscreen")
    
    def _create_brightness_control(self, layout):
        """Create the brightness control widget."""
        brightness_group = QWidget()
        brightness_group.setStyleSheet(f"""
            QWidget {{
                background-color: #2D2D2D;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        
        brightness_layout = QHBoxLayout(brightness_group)
        brightness_layout.setContentsMargins(5, 5, 5, 5)
        
        # Label
        brightness_label = QLabel("Display Brightness:")
        brightness_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        brightness_layout.addWidget(brightness_label)
        
        # Slider
        from PyQt6.QtWidgets import QSlider
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(80)
        self.brightness_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 8px;
                background: #3A3A3A;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                background: {PASTEL_GOLD_2};
                margin: -4px 0;
            }}
            QSlider::sub-page:horizontal {{
                background: {PASTEL_GOLD_1};
                border-radius: 4px;
            }}
        """)
        brightness_layout.addWidget(self.brightness_slider)
        
        # Value label
        self.brightness_value = QLabel("80%")
        self.brightness_value.setStyleSheet(f"color: {PASTEL_GOLD_2}; font-weight: bold;")
        self.brightness_value.setMinimumWidth(40)
        brightness_layout.addWidget(self.brightness_value)
        
        # Connect slider
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        
        layout.addWidget(brightness_group)
    
    def _create_settings_tab(self):
        """Create the settings tab."""
        self.settings_tab = QWidget()
        self.settings_tab.setStyleSheet(f"background-color: #1E1E1E;")
        
        layout = QVBoxLayout(self.settings_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet(f"""
            QLabel {{
                color: {PASTEL_GOLD_2};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(title)
        
        # Info
        info = QLabel("MSD-PRO Configurator v0.1.0\n\n"
                     "Features:\n"
                     "- Configure 15 main keys + 4 secondary keys\n"
                     "- Configure 4 knobs (press + rotation)\n"
                     "- Set touchscreen background (800x480px)\n"
                     "- Configure swipe gestures\n"
                     "- Assign shell commands to keys/knobs/swipes\n"
                     "- Save/load configurations")
        info.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(info)
        
        # Add stretch
        layout.addStretch()
        
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
    
    def _setup_connections(self):
        """Setup signal connections."""
        # Device combo
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        
        # Connect button
        self.connect_button.clicked.connect(self._on_connect_clicked)
        
        # Disconnect button
        self.disconnect_button.clicked.connect(self._on_disconnect_clicked)
        
        # Save button
        self.save_button.clicked.connect(self._on_save_clicked)
        
        # Load button
        self.load_button.clicked.connect(self._on_load_clicked)
        
        # Device handler callbacks
        self.device_handler.set_device_list_changed_callback(self._on_device_list_changed)
        self.device_handler.set_connection_changed_callback(self._on_connection_changed)
        
        # Update device list
        self._update_device_list()
    
    def _setup_timers(self):
        """Setup periodic timers."""
        # Timer to refresh device list periodically
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._update_device_list)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def _update_device_list(self):
        """Update the list of available devices."""
        # Disconnect signals temporarily
        self.device_combo.currentIndexChanged.disconnect()
        
        # Get devices
        devices = self.device_handler.get_devices()
        
        # Update combo
        self.device_combo.clear()
        for device in devices:
            self.device_combo.addItem(f"{device.name} ({device.serial})", device)
        
        if not devices:
            self.device_combo.addItem("No devices found")
            self.device_combo.setEnabled(False)
        else:
            self.device_combo.setEnabled(True)
        
        # Reconnect signal
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        
        # Update status
        self._update_status()
    
    def _on_device_selected(self, index: int):
        """Handle device selection."""
        devices = self.device_handler.get_devices()
        if 0 <= index < len(devices):
            device_info = devices[index]
            self.device_handler.select_device(index)
            self._update_status()
    
    def _on_connect_clicked(self):
        """Handle connect button click."""
        index = self.device_combo.currentIndex()
        if index >= 0:
            self.device_handler.connect_device(index)
            self._update_status()
    
    def _on_disconnect_clicked(self):
        """Handle disconnect button click."""
        self.device_handler.disconnect_device()
        self._update_status()
    
    def _on_connection_changed(self, connected: bool):
        """Handle connection state change."""
        self._update_status()
    
    def _on_device_list_changed(self):
        """Handle device list change."""
        self._update_device_list()
    
    def _update_status(self):
        """Update status bar and button states."""
        state = self.device_handler.get_device_state()
        current_device = self.device_handler.get_current_device()
        
        # Update status text
        if state == DeviceState.CONNECTED and current_device:
            status_text = f"Connected to {current_device.name} ({current_device.serial})"
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        elif state == DeviceState.DISCONNECTED:
            status_text = "Disconnected"
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
        else:
            status_text = "Error: Connection failed"
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
        
        # Add config info
        if self.current_config_path:
            status_text += f" | Config: {self.current_config_path}"
        
        self.status_bar.showMessage(status_text)
    
    def _on_key_selected(self, key_index: int):
        """Handle key selection."""
        # Load the action for this key from current config
        if self.current_config and key_index in self.current_config.keys:
            action = self.current_config.keys[key_index]
            self.key_action_type.setCurrentText(action.action_type.value)
            self.key_action_command.setText(action.command)
    
    def _apply_key_action(self):
        """Apply action to the selected key."""
        selected_key = self.key_grid.get_selected_key()
        if selected_key is None:
            QMessageBox.warning(self, "No Key Selected", "Please select a key first.")
            return
        
        # Get action from UI
        action_type = ActionType(self.key_action_type.currentText())
        command = self.key_action_command.text()
        
        # Create or update config if needed
        if self.current_config is None:
            self.current_config = self.config_manager.create_default_config()
            self.current_config.device_name = "MSD-PRO"
        
        # Update the key action
        self.current_config.keys[selected_key] = KeyAction(
            action_type=action_type,
            command=command
        )
        
        # Show success message
        self.status_bar.showMessage(f"Action set for key {selected_key}", 3000)
    
    def _on_brightness_changed(self, value: int):
        """Handle brightness slider change."""
        self.brightness_value.setText(f"{value}%")
        
        # Update device if connected
        if self.device_handler.get_device_state() == DeviceState.CONNECTED:
            self.device_handler.set_brightness(value)
        
        # Update current config
        if self.current_config:
            self.current_config.brightness = value
    
    def _on_save_clicked(self):
        """Handle save button click."""
        # If no config, create one
        if self.current_config is None:
            self.current_config = self.config_manager.create_default_config()
        
        # Get values from UI
        self._update_config_from_ui()
        
        # Ask for file name
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "",
            "MSD-PRO Configuration (*.msdpro.json);;All Files (*)"
        )
        
        if file_path:
            # Ensure extension
            if not file_path.lower().endswith('.msdpro.json'):
                file_path += '.msdpro.json'
            
            # Save
            if self.config_manager.save_config(self.current_config, file_path):
                self.current_config_path = file_path
                self.status_bar.showMessage(f"Configuration saved to {file_path}", 5000)
            else:
                QMessageBox.critical(self, "Save Error", "Failed to save configuration.")
    
    def _on_load_clicked(self):
        """Handle load button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "MSD-PRO Configuration (*.msdpro.json);;All Files (*)"
        )
        
        if file_path:
            config = self.config_manager.load_config(file_path)
            if config:
                self.current_config = config
                self.current_config_path = file_path
                self._update_ui_from_config()
                self.status_bar.showMessage(f"Configuration loaded from {file_path}", 5000)
            else:
                QMessageBox.critical(self, "Load Error", "Failed to load configuration.")
    
    def _update_config_from_ui(self):
        """Update current config from UI elements."""
        if self.current_config is None:
            return
        
        # Brightness
        self.current_config.brightness = self.brightness_slider.value()
        
        # Touchscreen image
        image_path = self.touchscreen_config.get_image_path()
        self.current_config.touchscreen_background = image_path
        
        # Swipe actions
        swipe_actions = self.touchscreen_config.get_swipe_actions()
        from ..core.config_manager import SwipeAction, KeyAction
        from ..core.config_manager import Direction
        
        # Update swipe in config
        left_action = swipe_actions.get("left", {})
        right_action = swipe_actions.get("right", {})
        
        self.current_config.swipe.left = KeyAction(
            action_type=ActionType(left_action.get("type", "none")),
            command=left_action.get("command", "")
        )
        self.current_config.swipe.right = KeyAction(
            action_type=ActionType(right_action.get("type", "none")),
            command=right_action.get("command", "")
        )
    
    def _update_ui_from_config(self):
        """Update UI from current config."""
        if self.current_config is None:
            return
        
        # Brightness
        self.brightness_slider.setValue(self.current_config.brightness)
        
        # Touchscreen image
        if self.current_config.touchscreen_background:
            self.touchscreen_config.set_image_path(self.current_config.touchscreen_background)
        
        # Swipe actions
        swipe_dict = {
            "left": {
                "type": self.current_config.swipe.left.action_type.value,
                "command": self.current_config.swipe.left.command
            },
            "right": {
                "type": self.current_config.swipe.right.action_type.value,
                "command": self.current_config.swipe.right.command
            }
        }
        self.touchscreen_config.set_swipe_actions(swipe_dict)
    
    def _load_default_config(self):
        """Load default configuration."""
        self.current_config = self.config_manager.create_default_config()
        self.current_config_path = None
        
        # Update UI
        self._update_ui_from_config()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Disconnect device
        self.device_handler.disconnect_device()
        
        # Stop timers
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        event.accept()


def run_application(use_mock: bool = True):
    """
    Run the MSD-PRO Configurator application.
    
    Args:
        use_mock: If True, use mock devices for testing
    """
    app = QApplication(sys.argv)
    app.setApplicationName("MSD-PRO Configurator")
    app.setOrganizationName("Mars Gaming")
    
    # Set dark theme
    app.setStyle("Fusion")
    
    # Create and show main window
    device_handler = DeviceHandler(use_mock=use_mock)
    window = MainWindow(device_handler)
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    run_application(use_mock=True)
