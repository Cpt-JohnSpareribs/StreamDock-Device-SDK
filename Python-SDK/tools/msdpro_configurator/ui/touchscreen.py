"""
Touchscreen Widget for MSD-PRO Configurator.
Displays and configures the touchscreen background (800x480px).

This widget allows:
- Preview of the touchscreen background image
- Drag and drop or file selection for new images
- Configuration of swipe gestures
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QGroupBox, QComboBox, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import QMimeData, QUrl
from typing import Optional, Dict
import sys
from pathlib import Path

# Add paths for imports
msdpro_path = Path(__file__).parent.parent
if str(msdpro_path) not in sys.path:
    sys.path.insert(0, str(msdpro_path))

from ui.styles import (
    TOUCHSCREEN_STYLE, TEXT_PRIMARY, TEXT_SECONDARY,
    PASTEL_GREEN_2, PASTEL_GREEN_3, DARK_GRAY_2, DARK_GRAY_3, PASTEL_GOLD_2
)
from core.config_manager import ActionType


class TouchscreenPreview(QLabel):
    """
    Widget for displaying the touchscreen background preview.
    Supports drag and drop for image loading.
    """
    
    # Signal emitted when image is changed (image_path)
    image_changed = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the touchscreen preview.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Setup appearance
        self.setFixedSize(400, 240)  # Half size of 800x480 for preview
        self.setStyleSheet(TOUCHSCREEN_STYLE)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drag & Drop image here\nor click to browse")
        self.setAcceptDrops(True)
        
        # Store image
        self._image_path: Optional[str] = None
        self._pixmap: Optional[QPixmap] = None
        
        # Enable word wrap
        self.setWordWrap(True)
    
    def set_image(self, image_path: str):
        """
        Set the touchscreen image.
        
        Args:
            image_path: Path to the image file
        """
        self._image_path = image_path
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Scale to fit the preview
            scaled_pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._pixmap = pixmap
            self.setPixmap(scaled_pixmap)
            self.clear()  # Remove text
            self.image_changed.emit(image_path)
        else:
            self._pixmap = None
            self.clear()
            self.setText(f"Could not load:\n{image_path}")
    
    def clear(self):
        """Clear the current image."""
        self._image_path = None
        self._pixmap = None
        QLabel.clear(self)
        self.setText("Drag & Drop image here\nor click to browse")
    
    def get_image_path(self) -> Optional[str]:
        """Get the current image path."""
        return self._image_path
    
    def get_pixmap(self) -> Optional[QPixmap]:
        """Get the current pixmap."""
        return self._pixmap
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                # Check if it's an image file
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    self.set_image(file_path)
                    event.accept()
                    return
        event.ignore()
    
    def mousePressEvent(self, event):
        """Handle mouse press (for click-to-browse)."""
        # This will be connected in the parent widget
        super().mousePressEvent(event)


class SwipeConfig(QGroupBox):
    """
    Widget for configuring swipe gestures.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the swipe configuration.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Swipe Gestures", parent)
        
        self.setStyleSheet(f"""
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
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(10)
        
        # Left swipe
        left_layout = QVBoxLayout()
        left_label = QLabel("Swipe Left:")
        left_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self.left_type = QComboBox()
        self.left_type.addItems([t.value for t in ActionType])
        self.left_command = QLineEdit()
        self.left_command.setPlaceholderText("Enter command...")
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.left_type)
        left_layout.addWidget(self.left_command)
        layout.addLayout(left_layout)
        
        # Right swipe
        right_layout = QVBoxLayout()
        right_label = QLabel("Swipe Right:")
        right_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self.right_type = QComboBox()
        self.right_type.addItems([t.value for t in ActionType])
        self.right_command = QLineEdit()
        self.right_command.setPlaceholderText("Enter command...")
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.right_type)
        right_layout.addWidget(self.right_command)
        layout.addLayout(right_layout)
    
    def get_actions(self) -> Dict[str, Dict[str, str]]:
        """Get swipe actions."""
        return {
            "left": {
                "type": self.left_type.currentText(),
                "command": self.left_command.text()
            },
            "right": {
                "type": self.right_type.currentText(),
                "command": self.right_command.text()
            }
        }
    
    def set_actions(self, actions: Dict[str, Dict[str, str]]):
        """Set swipe actions."""
        left = actions.get("left", {})
        if "type" in left:
            idx = self.left_type.findText(left["type"])
            if idx >= 0:
                self.left_type.setCurrentIndex(idx)
        if "command" in left:
            self.left_command.setText(left["command"])
        
        right = actions.get("right", {})
        if "type" in right:
            idx = self.right_type.findText(right["type"])
            if idx >= 0:
                self.right_type.setCurrentIndex(idx)
        if "command" in right:
            self.right_command.setText(right["command"])


class TouchscreenConfig(QWidget):
    """
    Complete touchscreen configuration widget.
    
    Combines:
    - Touchscreen preview
    - Image selection (drag & drop or browse)
    - Swipe gesture configuration
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the touchscreen configuration.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Title
        title = QLabel("Touchscreen Configuration (800×480px)")
        title.setStyleSheet(f"""
            QLabel {{
                color: {PASTEL_GOLD_2};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        main_layout.addWidget(title)
        
        # Preview
        self.preview = TouchscreenPreview()
        self.preview.image_changed.connect(self._on_image_changed)
        main_layout.addWidget(self.preview, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Button to browse for image
        self.browse_button = QPushButton("📁 Browse for Image...")
        self.browse_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_GRAY_2};
                color: {TEXT_PRIMARY};
                border: 1px solid {DARK_GRAY_3};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {PASTEL_GREEN_2};
                border-color: {PASTEL_GREEN_3};
            }}
        """)
        self.browse_button.clicked.connect(self._browse_for_image)
        main_layout.addWidget(self.browse_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Clear button
        self.clear_button = QPushButton("🗑️ Clear Image")
        self.clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_GRAY_2};
                color: {TEXT_PRIMARY};
                border: 1px solid {DARK_GRAY_3};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: #8B0000;
                border-color: #FF0000;
            }}
        """)
        self.clear_button.clicked.connect(self._clear_image)
        main_layout.addWidget(self.clear_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Swipe configuration
        self.swipe_config = SwipeConfig()
        main_layout.addWidget(self.swipe_config)
        
        # Current image label
        self.current_image_label = QLabel("No image selected")
        self.current_image_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.current_image_label.setWordWrap(True)
        main_layout.addWidget(self.current_image_label)
        
        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
    def _browse_for_image(self):
        """Open file dialog to browse for an image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Touchscreen Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.preview.set_image(file_path)
    
    def _clear_image(self):
        """Clear the current image."""
        self.preview.clear()
        self.current_image_label.setText("No image selected")
    
    def _on_image_changed(self, image_path: str):
        """Handle image change."""
        self.current_image_label.setText(f"Current: {image_path}")
    
    def get_image_path(self) -> Optional[str]:
        """Get the current image path."""
        return self.preview.get_image_path()
    
    def get_swipe_actions(self) -> Dict[str, Dict[str, str]]:
        """Get swipe gesture actions."""
        return self.swipe_config.get_actions()
    
    def set_image_path(self, image_path: Optional[str]):
        """Set the image path."""
        if image_path:
            self.preview.set_image(image_path)
        else:
            self.preview.clear()
    
    def set_swipe_actions(self, actions: Dict[str, Dict[str, str]]):
        """Set swipe gesture actions."""
        self.swipe_config.set_actions(actions)
    
    def reset(self):
        """Reset to default state."""
        self.preview.clear()
        self.current_image_label.setText("No image selected")
        self.swipe_config.set_actions({
            "left": {"type": ActionType.NONE.value, "command": ""},
            "right": {"type": ActionType.NONE.value, "command": ""}
        })
