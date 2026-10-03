"""
Knob Panel Widget for MSD-PRO Configurator.
Configures the 4 knobs (press, rotation left/right) with actions.

This widget allows:
- Visual representation of all 4 knobs
- Configuration of press, left rotation, and right rotation actions
- Selection of action type (shell command, plugin, etc.)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QComboBox, QLineEdit, QDial, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, List, Callable

from .styles import (
    KNOB_STYLE, TEXT_PRIMARY, TEXT_SECONDARY, 
    PASTEL_GOLD_2, PASTEL_GOLD_3, DARK_GRAY_2, DARK_GRAY_3
)
from ..core.config_manager import ActionType, Direction


class KnobControl(QWidget):
    """
    Widget for configuring a single knob.
    
    Shows:
    - Knob number (1-4)
    - Dial visualization
    - Action configuration for press, left rotation, right rotation
    """
    
    def __init__(self, knob_index: int, parent: Optional[QWidget] = None):
        """
        Initialize the knob control.
        
        Args:
            knob_index: The knob index (1-4)
            parent: Parent widget
        """
        super().__init__(parent)
        self.knob_index = knob_index
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)
        
        # Title
        title = QLabel(f"Knob {knob_index}")
        title.setStyleSheet(f"""
            QLabel {{
                color: {PASTEL_GOLD_2};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        main_layout.addWidget(title)
        
        # Dial visualization
        self.dial = QDial()
        self.dial.setRange(0, 100)
        self.dial.setNotchesVisible(True)
        self.dial.setStyleSheet(KNOB_STYLE)
        self.dial.setFixedSize(100, 100)
        main_layout.addWidget(self.dial, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Action group
        action_group = QGroupBox("Actions")
        action_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {DARK_GRAY_3};
                border-radius: 6px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                color: {PASTEL_GOLD_2};
            }}
        """)
        action_layout = QVBoxLayout(action_group)
        
        # Press action
        press_layout = QHBoxLayout()
        press_label = QLabel("Press:")
        press_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self.press_type = QComboBox()
        self.press_type.addItems([t.value for t in ActionType])
        self.press_command = QLineEdit()
        self.press_command.setPlaceholderText("Enter command or path...")
        press_layout.addWidget(press_label)
        press_layout.addWidget(self.press_type)
        press_layout.addWidget(self.press_command)
        action_layout.addLayout(press_layout)
        
        # Rotation left action
        rotate_left_layout = QHBoxLayout()
        rotate_left_label = QLabel("Rotate Left:")
        rotate_left_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self.rotate_left_type = QComboBox()
        self.rotate_left_type.addItems([t.value for t in ActionType])
        self.rotate_left_command = QLineEdit()
        self.rotate_left_command.setPlaceholderText("Enter command or path...")
        rotate_left_layout.addWidget(rotate_left_label)
        rotate_left_layout.addWidget(self.rotate_left_type)
        rotate_left_layout.addWidget(self.rotate_left_command)
        action_layout.addLayout(rotate_left_layout)
        
        # Rotation right action
        rotate_right_layout = QHBoxLayout()
        rotate_right_label = QLabel("Rotate Right:")
        rotate_right_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self.rotate_right_type = QComboBox()
        self.rotate_right_type.addItems([t.value for t in ActionType])
        self.rotate_right_command = QLineEdit()
        self.rotate_right_command.setPlaceholderText("Enter command or path...")
        rotate_right_layout.addWidget(rotate_right_label)
        rotate_right_layout.addWidget(self.rotate_right_type)
        rotate_right_layout.addWidget(self.rotate_right_command)
        action_layout.addLayout(rotate_right_layout)
        
        main_layout.addWidget(action_group)
        
        # Set size policy
        self.setSizePolicy(
            QWidget.SizePolicy.Policy.Preferred,
            QWidget.SizePolicy.Policy.Preferred
        )
    
    def get_actions(self) -> Dict[str, Dict[str, str]]:
        """
        Get all actions for this knob.
        
        Returns:
            Dictionary with 'press', 'rotate_left', 'rotate_right' actions
        """
        return {
            "press": {
                "type": self.press_type.currentText(),
                "command": self.press_command.text()
            },
            "rotate_left": {
                "type": self.rotate_left_type.currentText(),
                "command": self.rotate_left_command.text()
            },
            "rotate_right": {
                "type": self.rotate_right_type.currentText(),
                "command": self.rotate_right_command.text()
            }
        }
    
    def set_actions(self, actions: Dict[str, Dict[str, str]]):
        """
        Set all actions for this knob.
        
        Args:
            actions: Dictionary with 'press', 'rotate_left', 'rotate_right' actions
        """
        # Press
        press = actions.get("press", {})
        if "type" in press:
            idx = self.press_type.findText(press["type"])
            if idx >= 0:
                self.press_type.setCurrentIndex(idx)
        if "command" in press:
            self.press_command.setText(press["command"])
        
        # Rotate left
        rotate_left = actions.get("rotate_left", {})
        if "type" in rotate_left:
            idx = self.rotate_left_type.findText(rotate_left["type"])
            if idx >= 0:
                self.rotate_left_type.setCurrentIndex(idx)
        if "command" in rotate_left:
            self.rotate_left_command.setText(rotate_left["command"])
        
        # Rotate right
        rotate_right = actions.get("rotate_right", {})
        if "type" in rotate_right:
            idx = self.rotate_right_type.findText(rotate_right["type"])
            if idx >= 0:
                self.rotate_right_type.setCurrentIndex(idx)
        if "command" in rotate_right:
            self.rotate_right_command.setText(rotate_right["command"])


class KnobPanel(QWidget):
    """
    Panel for configuring all 4 knobs of the MSD-PRO.
    
    Layout:
    - 4 KnobControl widgets in a grid (2x2)
    - Signals when any knob configuration changes
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the knob panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Title
        title = QLabel("Knob Configuration (4 Knobs)")
        title.setStyleSheet(f"""
            QLabel {{
                color: {PASTEL_GOLD_2};
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        main_layout.addWidget(title)
        
        # Create knob controls
        self.knob_controls: Dict[int, KnobControl] = {}
        knob_grid = QHBoxLayout()
        knob_grid.setSpacing(10)
        
        # Left column (Knobs 1-2)
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        
        for i in range(1, 3):
            knob = KnobControl(i)
            self.knob_controls[i] = knob
            left_column.addWidget(knob)
        
        # Right column (Knobs 3-4)
        right_column = QVBoxLayout()
        right_column.setSpacing(10)
        
        for i in range(3, 5):
            knob = KnobControl(i)
            self.knob_controls[i] = knob
            right_column.addWidget(knob)
        
        knob_grid.addLayout(left_column)
        knob_grid.addLayout(right_column)
        main_layout.addLayout(knob_grid)
        
        # Set size policy
        self.setSizePolicy(
            QWidget.SizePolicy.Policy.Expanding,
            QWidget.SizePolicy.Policy.Expanding
        )
    
    def get_all_actions(self) -> Dict[int, Dict[str, Dict[str, str]]]:
        """
        Get actions for all knobs.
        
        Returns:
            Dictionary mapping knob_index to its actions
        """
        return {i: knob.get_actions() for i, knob in self.knob_controls.items()}
    
    def set_all_actions(self, actions: Dict[int, Dict[str, Dict[str, str]]]):
        """
        Set actions for all knobs.
        
        Args:
            actions: Dictionary mapping knob_index to its actions
        """
        for knob_index, knob_actions in actions.items():
            if knob_index in self.knob_controls:
                self.knob_controls[knob_index].set_actions(knob_actions)
    
    def reset_all(self):
        """Reset all knob configurations to default."""
        for knob in self.knob_controls.values():
            knob.set_actions({
                "press": {"type": ActionType.NONE.value, "command": ""},
                "rotate_left": {"type": ActionType.NONE.value, "command": ""},
                "rotate_right": {"type": ActionType.NONE.value, "command": ""}
            })
