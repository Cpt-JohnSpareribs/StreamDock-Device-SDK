"""
Key Grid Widget for MSD-PRO Configurator.
Displays the 15 main keys + 4 secondary screen keys in a visual grid.

This widget allows:
- Visual representation of all keys
- Click to select a key for configuration
- Display current key images
- Show key numbers
"""

from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QLabel, 
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont
from typing import Optional, Dict, Callable
import sys
from pathlib import Path

# Add paths for imports
msdpro_path = Path(__file__).parent.parent
if str(msdpro_path) not in sys.path:
    sys.path.insert(0, str(msdpro_path))

from ui.styles import KEY_BUTTON_STYLE, TEXT_PRIMARY, DARK_GRAY_2, PASTEL_GREEN_2


class KeyButton(QPushButton):
    """
    Custom button representing a single key on the MSD-PRO.
    
    Features:
    - Displays key number
    - Can show a preview image
    - Emits signal when clicked
    - Visual feedback for selection
    """
    
    # Signal emitted when key is clicked (key_index)
    clicked_key = pyqtSignal(int)
    
    def __init__(self, key_index: int, parent: Optional[QWidget] = None):
        """
        Initialize the key button.
        
        Args:
            key_index: The logical key index (1-15 for main, 11-14 for secondary)
            parent: Parent widget
        """
        super().__init__(parent)
        self.key_index = key_index
        self.image_path: Optional[str] = None
        self.is_secondary = 11 <= key_index <= 14
        
        # Setup button appearance
        self.setFixedSize(80, 80)
        self.setStyleSheet(KEY_BUTTON_STYLE)
        
        # Set button text (key number)
        self.setText(str(key_index))
        self.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        
        # Connect click signal
        self.clicked.connect(self._on_clicked)
    
    def _on_clicked(self):
        """Handle button click."""
        self.clicked_key.emit(self.key_index)
    
    def set_image(self, image_path: Optional[str] = None, pixmap: Optional[QPixmap] = None):
        """
        Set the image for this key.
        
        Args:
            image_path: Optional path to image file
            pixmap: Optional QPixmap to display
        """
        self.image_path = image_path
        
        if pixmap and not pixmap.isNull():
            # Scale pixmap to fit button
            scaled_pixmap = pixmap.scaled(
                self.width() - 8, self.height() - 8,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setIcon(QIcon(scaled_pixmap))
            self.setIconSize(scaled_pixmap.size())
        else:
            self.setIcon(QIcon())
    
    def clear_image(self):
        """Clear the current image."""
        self.image_path = None
        self.setIcon(QIcon())
    
    def set_selected(self, selected: bool):
        """
        Set the selected state of the key.
        
        Args:
            selected: True if key should appear selected
        """
        if selected:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PASTEL_GREEN_2};
                    border: 2px solid {TEXT_PRIMARY};
                    border-radius: 8px;
                    color: {DARK_GRAY_2};
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(KEY_BUTTON_STYLE)


class KeyGrid(QWidget):
    """
    Grid widget displaying all 15 main keys + 4 secondary screen keys.
    
    Layout:
    - Main keys: 5 columns x 3 rows (keys 1-15)
    - Secondary screen keys: 4 keys below main grid (keys 11-14)
    
    Signals:
    - key_selected(int): Emitted when a key is selected
    """
    
    # Signal emitted when a key is selected (key_index)
    key_selected = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the key grid.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Create main keys grid (5 columns x 3 rows)
        self.main_grid = QGridLayout()
        self.main_grid.setSpacing(8)
        
        # Create secondary keys layout (4 keys in a row)
        self.secondary_layout = QHBoxLayout()
        self.secondary_layout.setSpacing(8)
        
        # Create key buttons
        self.key_buttons: Dict[int, KeyButton] = {}
        
        # Add main keys (1-15)
        main_keys = list(range(1, 16))
        for i, key_index in enumerate(main_keys):
            row = i // 5
            col = i % 5
            button = KeyButton(key_index)
            button.clicked_key.connect(self._on_key_clicked)
            self.key_buttons[key_index] = button
            self.main_grid.addWidget(button, row, col)
        
        # Add secondary screen keys (11-14)
        secondary_keys = list(range(11, 15))
        for key_index in secondary_keys:
            button = KeyButton(key_index)
            button.clicked_key.connect(self._on_key_clicked)
            self.key_buttons[key_index] = button
            self.secondary_layout.addWidget(button)
        
        # Add layouts to main layout
        main_layout.addLayout(self.main_grid)
        
        # Add label for secondary keys
        secondary_label = QLabel("Secondary Screen Keys (11-14)")
        secondary_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
        main_layout.addWidget(secondary_label)
        
        # Add secondary keys layout
        main_layout.addLayout(self.secondary_layout)
        
        # Store current selection
        self._selected_key: Optional[int] = None
        
        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
    def _on_key_clicked(self, key_index: int):
        """Handle key button click."""
        # Deselect previous key
        if self._selected_key is not None and self._selected_key in self.key_buttons:
            self.key_buttons[self._selected_key].set_selected(False)
        
        # Select new key
        self._selected_key = key_index
        self.key_buttons[key_index].set_selected(True)
        
        # Emit signal
        self.key_selected.emit(key_index)
    
    def set_key_image(self, key_index: int, image_path: Optional[str] = None, 
                      pixmap: Optional[QPixmap] = None):
        """
        Set the image for a specific key.
        
        Args:
            key_index: The key index (1-15)
            image_path: Optional path to image file
            pixmap: Optional QPixmap to display
        """
        if key_index in self.key_buttons:
            self.key_buttons[key_index].set_image(image_path, pixmap)
    
    def clear_key_image(self, key_index: int):
        """
        Clear the image for a specific key.
        
        Args:
            key_index: The key index (1-15)
        """
        if key_index in self.key_buttons:
            self.key_buttons[key_index].clear_image()
    
    def clear_all_images(self):
        """Clear all key images."""
        for button in self.key_buttons.values():
            button.clear_image()
    
    def get_selected_key(self) -> Optional[int]:
        """Get the currently selected key index."""
        return self._selected_key
    
    def select_key(self, key_index: int):
        """
        Programmatically select a key.
        
        Args:
            key_index: The key index to select
        """
        if key_index in self.key_buttons:
            self._on_key_clicked(key_index)
    
    def set_all_images(self, images: Dict[int, str]):
        """
        Set images for multiple keys at once.
        
        Args:
            images: Dictionary mapping key_index to image_path
        """
        for key_index, image_path in images.items():
            if key_index in self.key_buttons:
                # Load pixmap from path
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    self.key_buttons[key_index].set_image(image_path, pixmap)


class KeyGridWithPreview(QWidget):
    """
    Enhanced key grid with a preview panel for the selected key.
    
    Features:
    - Key grid for all 19 keys
    - Preview panel showing selected key details
    - Action configuration for selected key
    """
    
    # Signal emitted when a key is selected (key_index)
    key_selected = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the key grid with preview.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Create key grid
        self.key_grid = KeyGrid()
        self.key_grid.key_selected.connect(self._on_internal_key_selected)
        
        # Create preview panel
        self.preview_panel = QFrame()
        self.preview_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_panel.setMinimumWidth(250)
        preview_layout = QVBoxLayout(self.preview_panel)
        
        # Preview title
        self.preview_title = QLabel("No key selected")
        self.preview_title.setStyleSheet(f"""
            QLabel {{
                color: {PASTEL_GREEN_2};
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        preview_layout.addWidget(self.preview_title)
        
        # Preview image
        self.preview_image = QLabel()
        self.preview_image.setFixedSize(200, 200)
        self.preview_image.setStyleSheet(f"""
            QLabel {{
                background-color: {DARK_GRAY_2};
                border: 1px dashed {PASTEL_GREEN_2};
                border-radius: 4px;
            }}
        """)
        self.preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_image, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Preview info
        self.preview_info = QLabel("Select a key to configure")
        self.preview_info.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self.preview_info.setWordWrap(True)
        preview_layout.addWidget(self.preview_info)
        
        # Add widgets to main layout
        main_layout.addWidget(self.key_grid, stretch=2)
        main_layout.addWidget(self.preview_panel, stretch=1)
        
        # Store selected key
        self._selected_key: Optional[int] = None
        
        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
    def _on_internal_key_selected(self, key_index: int):
        """Handle internal key selection and forward signal."""
        self._selected_key = key_index
        self._update_preview(key_index)
        self.key_selected.emit(key_index)
    
    def _update_preview(self, key_index: int):
        """Update preview panel with selected key info."""
        self.preview_title.setText(f"Key {key_index}")
        
        # Get the button to get its image
        button = self.key_grid.key_buttons.get(key_index)
        if button and button.image_path:
            pixmap = QPixmap(button.image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    180, 180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_image.setPixmap(scaled_pixmap)
                self.preview_info.setText(f"Image: {button.image_path}")
            else:
                self.preview_image.clear()
                self.preview_info.setText("Image could not be loaded")
        else:
            self.preview_image.clear()
            self.preview_info.setText("No image set for this key")
    
    def get_selected_key(self) -> Optional[int]:
        """Get the currently selected key index."""
        return self._selected_key
    
    def get_key_grid(self) -> KeyGrid:
        """Get the underlying key grid widget."""
        return self.key_grid
