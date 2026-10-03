"""
Device Handler for MSD-PRO Configurator.
Wraps the StreamDock SDK to provide a clean interface for the GUI.

This module:
- Manages device enumeration and connection
- Handles image setting for keys and touchscreen
- Manages callbacks for input events
- Provides a mock mode for testing without hardware
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Callable, Dict, Any, Tuple
from enum import Enum

# Add parent directory to path for SDK imports
sdk_path = Path(__file__).parent.parent.parent.parent / "src"
if str(sdk_path) not in sys.path:
    sys.path.insert(0, str(sdk_path))

try:
    from StreamDock.DeviceManager import DeviceManager
    from StreamDock.Devices.StreamDockN4Pro import StreamDockN4Pro
    from StreamDock.InputTypes import InputEvent, ButtonKey, EventType, KnobId, Direction
    SDK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: StreamDock SDK not available: {e}")
    SDK_AVAILABLE = False
    DeviceManager = None
    StreamDockN4Pro = None


class DeviceState(Enum):
    """Current state of the device connection."""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"


class MockStreamDockN4Pro:
    """
    Mock implementation of StreamDockN4Pro for testing without hardware.
    Allows GUI development and testing without a physical device.
    """
    
    KEY_COUNT = 15
    DIAL_COUNT = 4
    
    def __init__(self):
        self.connected = True
        self.brightness = 80
        self.serial_number = "MOCK-001"
        self.firmware_version = "1.0.0"
        self._key_images: Dict[int, str] = {}  # key_index -> image_path
        self._touchscreen_image: Optional[str] = None
        self._callbacks: Dict[str, Callable] = {}
        
        # Mock device info
        self.vendor_id = 0x0b00
        self.product_id = 0x1003
        self.path = "/mock/path"
        self.feature_option = type('obj', (object,), {
            'hasRGBLed': True,
            'ledCounts': 4,
            'deviceType': 'mock',
            'supportBackgroundGif': True,
            'supportConfig': True
        })()
    
    def open(self):
        """Mock open method."""
        self.connected = True
    
    def close(self, notify: bool = True):
        """Mock close method."""
        self.connected = False
    
    def init(self):
        """Mock init method."""
        pass
    
    def set_brightness(self, percent: int) -> int:
        """Set display brightness."""
        self.brightness = max(0, min(100, percent))
        print(f"[MOCK] Brightness set to {self.brightness}%")
        return 0
    
    def set_key_image(self, key: int, path: str) -> int:
        """Set image for a key."""
        if not os.path.exists(path):
            print(f"[MOCK] Error: Image not found: {path}")
            return -1
        self._key_images[key] = path
        print(f"[MOCK] Key {key} image set to: {path}")
        return 0
    
    def set_touchscreen_image(self, path: str) -> int:
        """Set touchscreen background image."""
        if not os.path.exists(path):
            print(f"[MOCK] Error: Image not found: {path}")
            return -1
        self._touchscreen_image = path
        print(f"[MOCK] Touchscreen background set to: {path}")
        return 0
    
    def set_frame_background(self, path: str) -> int:
        """Set frame background image."""
        return self.set_touchscreen_image(path)
    
    def set_seondscreen_image(self, key: int, path: str) -> int:
        """Set image for secondary screen key."""
        return self.set_key_image(key, path)
    
    def get_serial_number(self) -> str:
        """Get device serial number."""
        return self.serial_number
    
    def register_key_callback(self, callback: Callable, async_run: bool = False):
        """Register callback for key events."""
        self._callbacks['key'] = callback
    
    def register_knob_callback(self, callback: Callable, async_run: bool = False):
        """Register callback for knob events."""
        self._callbacks['knob'] = callback
    
    def register_touch_bar_callback(self, callback: Callable, async_run: bool = False):
        """Register callback for touch bar events."""
        self._callbacks['touch'] = callback
    
    def register_swipe_callback(self, callback: Callable, async_run: bool = False):
        """Register callback for swipe events."""
        self._callbacks['swipe'] = callback
    
    def get_image_key(self, logical_key: int) -> int:
        """Convert logical key to hardware key."""
        # Mock mapping - same as real device for simplicity
        key_map = {
            1: 11, 2: 12, 3: 13, 4: 14, 5: 15,
            6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
            11: 1, 12: 2, 13: 3, 14: 4, 15: 5
        }
        return key_map.get(logical_key, logical_key)
    
    def key_image_format(self) -> Dict[str, Any]:
        """Get key image format."""
        return {"size": (112, 112), "format": "PNG", "rotation": 180, "flip": (False, False)}
    
    def touchscreen_image_format(self) -> Dict[str, Any]:
        """Get touchscreen image format."""
        return {"size": (800, 480), "format": "JPEG", "rotation": 180, "flip": (False, False)}
    
    def secondscreen_image_format(self) -> Dict[str, Any]:
        """Get secondary screen image format."""
        return {"size": (176, 112), "format": "PNG", "rotation": 180, "flip": (False, False)}
    
    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self.connected


class DeviceInfo:
    """Information about a detected device."""
    
    def __init__(self, device: Any, index: int = 0):
        self.device = device
        self.index = index
        self.serial = getattr(device, 'serial_number', f'Device-{index}')
        self.path = getattr(device, 'path', f'/dev/input/{index}')
        self.vendor_id = getattr(device, 'vendor_id', 0)
        self.product_id = getattr(device, 'product_id', 0)
        self.name = "MSD-PRO"
        if hasattr(device, 'feature_option'):
            if hasattr(device.feature_option, 'deviceType'):
                self.name = device.feature_option.deviceType
    
    def __repr__(self) -> str:
        return f"DeviceInfo(serial={self.serial}, path={self.path}, name={self.name})"


class DeviceHandler:
    """
    Main device handler class.
    Provides a clean interface between the GUI and the StreamDock SDK.
    
    Features:
    - Device enumeration and selection
    - Image management for keys and touchscreen
    - Event callback management
    - Mock mode for testing without hardware
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize the device handler.
        
        Args:
            use_mock: If True, use mock devices instead of real hardware.
                     Useful for development and testing.
        """
        self.use_mock = use_mock
        self.devices: List[DeviceInfo] = []
        self.current_device: Optional[DeviceInfo] = None
        self.device_manager: Optional[DeviceManager] = None
        self.state = DeviceState.DISCONNECTED
        self._use_sdk = SDK_AVAILABLE and not use_mock
        
        # Callbacks for GUI events
        self._on_device_list_changed: Optional[Callable] = None
        self._on_connection_changed: Optional[Callable] = None
        
        if self._use_sdk:
            self._initialize_sdk()
        else:
            self._initialize_mock()
    
    def _initialize_sdk(self):
        """Initialize the real SDK."""
        try:
            self.device_manager = DeviceManager()
            self._refresh_device_list()
            self.state = DeviceState.CONNECTED if self.devices else DeviceState.DISCONNECTED
        except Exception as e:
            print(f"Error initializing SDK: {e}")
            self.state = DeviceState.ERROR
            self._use_sdk = False
            self._initialize_mock()
    
    def _initialize_mock(self):
        """Initialize mock devices for testing."""
        # Create a single mock device
        mock_device = MockStreamDockN4Pro()
        self.devices = [DeviceInfo(mock_device, 0)]
        self.current_device = self.devices[0]
        self.state = DeviceState.CONNECTED
    
    def _refresh_device_list(self):
        """Refresh the list of available devices."""
        if not self._use_sdk or not self.device_manager:
            return
        
        try:
            self.devices = []
            detected_devices = self.device_manager.enumerate()
            
            for idx, device in enumerate(detected_devices):
                # Only include MSD-PRO devices (N4Pro)
                if isinstance(device, StreamDockN4Pro):
                    self.devices.append(DeviceInfo(device, idx))
            
            # Set current device to first available if none selected
            if not self.current_device and self.devices:
                self.current_device = self.devices[0]
                self.state = DeviceState.CONNECTED
            elif not self.devices:
                self.current_device = None
                self.state = DeviceState.DISCONNECTED
            
            # Notify GUI about device list change
            if self._on_device_list_changed:
                self._on_device_list_changed()
            
        except Exception as e:
            print(f"Error refreshing device list: {e}")
            self.state = DeviceState.ERROR
    
    def get_devices(self) -> List[DeviceInfo]:
        """Get list of available devices."""
        return self.devices
    
    def get_current_device(self) -> Optional[DeviceInfo]:
        """Get the currently selected device."""
        return self.current_device
    
    def select_device(self, index: int) -> bool:
        """Select a device by index."""
        if 0 <= index < len(self.devices):
            self.current_device = self.devices[index]
            self.state = DeviceState.CONNECTED
            if self._on_connection_changed:
                self._on_connection_changed(True)
            return True
        return False
    
    def connect_device(self, index: int) -> bool:
        """Connect to a device by index."""
        if self.select_device(index):
            try:
                if self._use_sdk and self.current_device:
                    device = self.current_device.device
                    if hasattr(device, 'open'):
                        device.open()
                    if hasattr(device, 'init'):
                        device.init()
                return True
            except Exception as e:
                print(f"Error connecting to device: {e}")
                self.state = DeviceState.ERROR
                if self._on_connection_changed:
                    self._on_connection_changed(False)
                return False
        return False
    
    def disconnect_device(self) -> bool:
        """Disconnect from current device."""
        if self.current_device:
            try:
                if self._use_sdk:
                    device = self.current_device.device
                    if hasattr(device, 'close'):
                        device.close()
                self.current_device = None
                self.state = DeviceState.DISCONNECTED
                if self._on_connection_changed:
                    self._on_connection_changed(False)
                return True
            except Exception as e:
                print(f"Error disconnecting device: {e}")
                self.state = DeviceState.ERROR
                return False
        return False
    
    def get_device_state(self) -> DeviceState:
        """Get current device connection state."""
        return self.state
    
    def set_key_image(self, key: int, image_path: str) -> bool:
        """
        Set image for a key.
        
        Args:
            key: Key index (1-15 for main keys, 11-14 for secondary screen)
            image_path: Path to the image file (PNG or JPEG)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.current_device:
            print("No device selected")
            return False
        
        try:
            device = self.current_device.device
            
            # For secondary screen keys (11-14), use set_seondscreen_image
            if 11 <= key <= 14:
                if self._use_sdk:
                    return device.set_seondscreen_image(key, image_path) == 0
                else:
                    return device.set_seondscreen_image(key, image_path) == 0
            else:
                if self._use_sdk:
                    return device.set_key_image(key, image_path) == 0
                else:
                    return device.set_key_image(key, image_path) == 0
        except Exception as e:
            print(f"Error setting key image: {e}")
            return False
    
    def set_touchscreen_image(self, image_path: str) -> bool:
        """
        Set touchscreen background image.
        
        Args:
            image_path: Path to the image file (800x480, JPEG recommended)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.current_device:
            print("No device selected")
            return False
        
        try:
            device = self.current_device.device
            if self._use_sdk:
                return device.set_touchscreen_image(image_path) == 0
            else:
                return device.set_touchscreen_image(image_path) == 0
        except Exception as e:
            print(f"Error setting touchscreen image: {e}")
            return False
    
    def set_brightness(self, percent: int) -> bool:
        """
        Set display brightness.
        
        Args:
            percent: Brightness percentage (0-100)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.current_device:
            print("No device selected")
            return False
        
        try:
            device = self.current_device.device
            if self._use_sdk:
                return device.set_brightness(percent) == 0
            else:
                return device.set_brightness(percent) == 0
        except Exception as e:
            print(f"Error setting brightness: {e}")
            return False
    
    def register_key_callback(self, callback: Callable[[int, int], None]):
        """
        Register callback for key press/release events.
        
        Args:
            callback: Function to call with (key_index, state) where state=1 for press, 0 for release
        """
        if not self.current_device:
            return
        
        def key_event_handler(device, event):
            if event.event_type == EventType.BUTTON:
                callback(event.key.value, 1 if event.state else 0)
        
        try:
            device = self.current_device.device
            if self._use_sdk:
                device.register_key_callback(key_event_handler)
            else:
                # For mock, store callback
                if hasattr(device, '_callbacks'):
                    device._callbacks['key'] = key_event_handler
        except Exception as e:
            print(f"Error registering key callback: {e}")
    
    def register_knob_callback(self, callback: Callable[[int, str, int], None]):
        """
        Register callback for knob events.
        
        Args:
            callback: Function to call with (knob_index, action_type, direction)
                     action_type: 'press', 'rotate'
                     direction: 0 for left/counter-clockwise, 1 for right/clockwise
        """
        if not self.current_device:
            return
        
        def knob_event_handler(device, event):
            if event.event_type == EventType.KNOB_PRESS:
                callback(event.knob_id.value, 'press', 0)
            elif event.event_type == EventType.KNOB_ROTATE:
                direction = 1 if event.direction == Direction.RIGHT else 0
                callback(event.knob_id.value, 'rotate', direction)
        
        try:
            device = self.current_device.device
            if self._use_sdk:
                device.register_knob_callback(knob_event_handler)
            else:
                if hasattr(device, '_callbacks'):
                    device._callbacks['knob'] = knob_event_handler
        except Exception as e:
            print(f"Error registering knob callback: {e}")
    
    def register_swipe_callback(self, callback: Callable[[str], None]):
        """
        Register callback for swipe events.
        
        Args:
            callback: Function to call with direction ('left' or 'right')
        """
        if not self.current_device:
            return
        
        def swipe_event_handler(device, event):
            if event.event_type == EventType.SWIPE:
                direction = 'right' if event.direction == Direction.RIGHT else 'left'
                callback(direction)
        
        try:
            device = self.current_device.device
            if self._use_sdk:
                device.register_swipe_callback(swipe_event_handler)
            else:
                if hasattr(device, '_callbacks'):
                    device._callbacks['swipe'] = swipe_event_handler
        except Exception as e:
            print(f"Error registering swipe callback: {e}")
    
    def set_device_list_changed_callback(self, callback: Callable[[], None]):
        """Set callback for when device list changes."""
        self._on_device_list_changed = callback
    
    def set_connection_changed_callback(self, callback: Callable[[bool], None]):
        """Set callback for when connection state changes."""
        self._on_connection_changed = callback
    
    def start_listening(self):
        """Start listening for device hotplug events."""
        if self._use_sdk and self.device_manager:
            try:
                self.device_manager.listen(
                    on_device_added=self._on_device_added,
                    on_device_removed=self._on_device_removed,
                    auto_open=True,
                    auto_init=True
                )
            except Exception as e:
                print(f"Error starting device listener: {e}")
    
    def _on_device_added(self, device):
        """Callback when a device is added."""
        print(f"Device added: {device}")
        self._refresh_device_list()
    
    def _on_device_removed(self, device):
        """Callback when a device is removed."""
        print(f"Device removed: {device}")
        self._refresh_device_list()
    
    def get_key_image_format(self) -> Dict[str, Any]:
        """Get key image format specifications."""
        if self.current_device:
            device = self.current_device.device
            if hasattr(device, 'key_image_format'):
                return device.key_image_format()
        return {"size": (112, 112), "format": "PNG", "rotation": 180, "flip": (False, False)}
    
    def get_touchscreen_image_format(self) -> Dict[str, Any]:
        """Get touchscreen image format specifications."""
        if self.current_device:
            device = self.current_device.device
            if hasattr(device, 'touchscreen_image_format'):
                return device.touchscreen_image_format()
        return {"size": (800, 480), "format": "JPEG", "rotation": 180, "flip": (False, False)}
    
    def get_secondary_screen_image_format(self) -> Dict[str, Any]:
        """Get secondary screen image format specifications."""
        if self.current_device:
            device = self.current_device.device
            if hasattr(device, 'secondscreen_image_format'):
                return device.secondscreen_image_format()
        return {"size": (176, 112), "format": "PNG", "rotation": 180, "flip": (False, False)}
    
    def get_serial_number(self) -> Optional[str]:
        """Get the serial number of the current device."""
        if self.current_device:
            return self.current_device.serial
        return None


# Singleton instance for easy access
_device_handler: Optional[DeviceHandler] = None


def get_device_handler(use_mock: bool = False) -> DeviceHandler:
    """Get or create the singleton device handler instance."""
    global _device_handler
    if _device_handler is None:
        _device_handler = DeviceHandler(use_mock=use_mock)
    return _device_handler


def reset_device_handler():
    """Reset the singleton device handler instance."""
    global _device_handler
    if _device_handler is not None:
        _device_handler.disconnect_device()
        _device_handler = None
