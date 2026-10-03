"""
Configuration Manager for MSD-PRO Configurator.
Handles loading, saving, and managing device configurations as JSON files.

This module provides a clean interface for:
- Saving key/knob/touchscreen configurations
- Loading configurations from files
- Validating configuration data
- Managing multiple device profiles
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum


class ActionType(str, Enum):
    """Types of actions that can be triggered by keys/knobs/swipes."""
    NONE = "none"                # No action
    SHELL_COMMAND = "shell"      # Execute shell command
    KEY_PRESS = "key_press"     # Simulate key press
    MEDIA_CONTROL = "media"     # Media controls (play, pause, volume, etc.)
    OPEN_URL = "open_url"       # Open URL in browser
    OPEN_APP = "open_app"       # Open application
    PLUGIN = "plugin"           # Trigger plugin action (for future use)
    EVENT = "event"             # Trigger custom event


class Direction(str, Enum):
    """Direction for knob rotation and swipe gestures."""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


class KnobAction:
    """Represents an action for a knob (press or rotation)."""
    
    def __init__(self, 
                 action_type: ActionType = ActionType.NONE,
                 command: str = "",
                 direction: Optional[Direction] = None):
        self.action_type = action_type
        self.command = command
        self.direction = direction
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "action_type": self.action_type.value,
            "command": self.command,
            "direction": self.direction.value if self.direction else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnobAction":
        """Create from dictionary (JSON deserialization)."""
        direction = None
        if data.get("direction"):
            direction = Direction(data["direction"])
        return cls(
            action_type=ActionType(data.get("action_type", "none")),
            command=data.get("command", ""),
            direction=direction
        )


@dataclass
class KeyAction:
    """Represents an action for a key press."""
    action_type: ActionType = ActionType.NONE
    command: str = ""
    # For future plugin support
    plugin_name: Optional[str] = None
    plugin_args: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "action_type": self.action_type.value,
            "command": self.command,
            "plugin_name": self.plugin_name
        }
        if self.plugin_args:
            result["plugin_args"] = self.plugin_args
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeyAction":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            action_type=ActionType(data.get("action_type", "none")),
            command=data.get("command", ""),
            plugin_name=data.get("plugin_name"),
            plugin_args=data.get("plugin_args")
        )


@dataclass
class SwipeAction:
    """Represents an action for swipe gestures."""
    left: KeyAction = field(default_factory=lambda: KeyAction(action_type=ActionType.NONE))
    right: KeyAction = field(default_factory=lambda: KeyAction(action_type=ActionType.NONE))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SwipeAction":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            left=KeyAction.from_dict(data.get("left", {})) if data.get("left") else KeyAction(),
            right=KeyAction.from_dict(data.get("right", {})) if data.get("right") else KeyAction()
        )


@dataclass
class KnobConfig:
    """Configuration for a single knob (4 knobs on MSD-PRO)."""
    press: KnobAction = field(default_factory=lambda: KnobAction(ActionType.NONE, ""))
    rotate_left: KnobAction = field(default_factory=lambda: KnobAction(ActionType.NONE, "", Direction.LEFT))
    rotate_right: KnobAction = field(default_factory=lambda: KnobAction(ActionType.NONE, "", Direction.RIGHT))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "press": self.press.to_dict(),
            "rotate_left": self.rotate_left.to_dict(),
            "rotate_right": self.rotate_right.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnobConfig":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            press=KnobAction.from_dict(data.get("press", {})) if data.get("press") else KnobAction(),
            rotate_left=KnobAction.from_dict(data.get("rotate_left", {})) if data.get("rotate_left") else KnobAction(),
            rotate_right=KnobAction.from_dict(data.get("rotate_right", {})) if data.get("rotate_right") else KnobAction()
        )


@dataclass
class DeviceConfig:
    """
    Complete configuration for an MSD-PRO device.
    
    This includes:
    - 15 main keys
    - 4 secondary screen keys
    - 4 knobs (press + rotation)
    - Touchscreen background
    - Swipe gestures
    - Brightness setting
    """
    # Device identification
    device_name: str = "MSD-PRO"
    device_serial: Optional[str] = None
    
    # Key configurations (1-15 for main keys, 11-14 for secondary screen)
    keys: Dict[int, KeyAction] = field(default_factory=dict)
    
    # Knob configurations (1-4)
    knobs: Dict[int, KnobConfig] = field(default_factory=dict)
    
    # Touchscreen background
    touchscreen_background: Optional[str] = None  # Path to image file
    
    # Swipe gestures
    swipe: SwipeAction = field(default_factory=SwipeAction)
    
    # Display brightness (0-100)
    brightness: int = 80
    
    # Additional metadata
    created_at: str = ""
    updated_at: str = ""
    version: str = "1.0"
    
    def __post_init__(self):
        """Initialize default configurations for all keys and knobs."""
        # Initialize all 15 keys with empty actions
        for i in range(1, 16):
            if i not in self.keys:
                self.keys[i] = KeyAction()
        
        # Initialize all 4 knobs with empty configurations
        for i in range(1, 5):
            if i not in self.knobs:
                self.knobs[i] = KnobConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert complete configuration to dictionary."""
        return {
            "device_name": self.device_name,
            "device_serial": self.device_serial,
            "keys": {k: v.to_dict() for k, v in self.keys.items()},
            "knobs": {k: v.to_dict() for k, v in self.knobs.items()},
            "touchscreen_background": self.touchscreen_background,
            "swipe": self.swipe.to_dict(),
            "brightness": self.brightness,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceConfig":
        """Create configuration from dictionary."""
        config = cls(
            device_name=data.get("device_name", "MSD-PRO"),
            device_serial=data.get("device_serial"),
            touchscreen_background=data.get("touchscreen_background"),
            brightness=data.get("brightness", 80),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            version=data.get("version", "1.0")
        )
        
        # Load keys
        if "keys" in data:
            for key, action_data in data["keys"].items():
                config.keys[int(key)] = KeyAction.from_dict(action_data)
        
        # Load knobs
        if "knobs" in data:
            for knob, knob_data in data["knobs"].items():
                config.knobs[int(knob)] = KnobConfig.from_dict(knob_data)
        
        # Load swipe
        if "swipe" in data:
            config.swipe = SwipeAction.from_dict(data["swipe"])
        
        return config
    
    def save(self, file_path: Union[str, Path]) -> bool:
        """Save configuration to JSON file."""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    @classmethod
    def load(cls, file_path: Union[str, Path]) -> Optional["DeviceConfig"]:
        """Load configuration from JSON file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return None


class ConfigManager:
    """
    Manages multiple device configurations.
    
    Provides methods for:
    - Loading configurations from files
    - Saving configurations
    - Finding available configurations
    - Creating new configurations
    """
    
    DEFAULT_CONFIG_DIR = "configs"
    DEFAULT_EXTENSION = ".msdpro.json"
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory to store configurations.
                       Defaults to 'configs' in the current directory.
        """
        self.config_dir = Path(config_dir) if config_dir else Path(self.DEFAULT_CONFIG_DIR)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_config_path(self, name: str) -> Path:
        """Get the full path for a configuration file."""
        return self.config_dir / f"{name}{self.DEFAULT_EXTENSION}"
    
    def save_config(self, config: DeviceConfig, name: Optional[str] = None) -> bool:
        """
        Save a device configuration.
        
        Args:
            config: The DeviceConfig to save
            name: Optional name for the configuration.
                 If None, uses device_serial or "default"
        
        Returns:
            True if saved successfully, False otherwise
        """
        if name is None:
            name = config.device_serial or "default"
        
        file_path = self.get_config_path(name)
        return config.save(file_path)
    
    def load_config(self, name: str) -> Optional[DeviceConfig]:
        """
        Load a device configuration.
        
        Args:
            name: Name of the configuration (without extension)
        
        Returns:
            DeviceConfig if found, None otherwise
        """
        file_path = self.get_config_path(name)
        return DeviceConfig.load(file_path)
    
    def list_configs(self) -> List[str]:
        """List all available configuration files."""
        return [
            f.stem.replace(self.DEFAULT_EXTENSION.replace(".", ""), "")
            for f in self.config_dir.glob(f"*{self.DEFAULT_EXTENSION}")
            if f.is_file()
        ]
    
    def delete_config(self, name: str) -> bool:
        """Delete a configuration file."""
        file_path = self.get_config_path(name)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def create_default_config(self) -> DeviceConfig:
        """Create a new default configuration."""
        return DeviceConfig()
