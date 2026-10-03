"""
Dark Pastel Color Theme for MSD-PRO Configurator
Colors: Green, Gray, Gold (dark pastel tones)

This module provides QSS (Qt Style Sheets) for a consistent dark pastel theme.
"""

# Dark Pastel Color Palette
# Green: Soft, muted green for primary actions
# Gray: Dark gray for backgrounds and neutrals  
# Gold: Warm gold for accents and highlights

DARK_GRAY_1 = "#1E1E1E"      # Almost black - main background
DARK_GRAY_2 = "#2D2D2D"      # Slightly lighter - card backgrounds
DARK_GRAY_3 = "#3A3A3A"      # Medium dark - borders, dividers
DARK_GRAY_4 = "#454545"      # Light dark - text on dark backgrounds

PASTEL_GREEN_1 = "#2E5A3D"   # Dark pastel green - primary buttons
PASTEL_GREEN_2 = "#3A6B4A"   # Medium pastel green - hover states
PASTEL_GREEN_3 = "#457A58"   # Light pastel green - active states
PASTEL_GREEN_4 = "#5F8B69"   # Bright pastel green - highlights

PASTEL_GOLD_1 = "#8B7355"    # Dark pastel gold - accents
PASTEL_GOLD_2 = "#A58A66"    # Medium pastel gold - secondary accents
PASTEL_GOLD_3 = "#BF9F77"    # Light pastel gold - highlights
PASTEL_GOLD_4 = "#D9B887"    # Bright pastel gold - active accents

TEXT_PRIMARY = "#E0E0E0"    # Light text on dark backgrounds
TEXT_SECONDARY = "#B0B0B0"  # Medium text
TEXT_DISABLED = "#606060"   # Disabled text

# QSS (Qt Style Sheet) for the main application
MAIN_WINDOW_STYLE = f"""
QMainWindow {{
    background-color: {DARK_GRAY_1};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}}

QMenuBar {{
    background-color: {DARK_GRAY_2};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {DARK_GRAY_3};
    padding: 4px;
}}

QMenuBar::item {{
    padding: 4px 8px;
}}

QMenuBar::item:selected {{
    background-color: {PASTEL_GREEN_2};
    color: {TEXT_PRIMARY};
}}

QMenu {{
    background-color: {DARK_GRAY_2};
    color: {TEXT_PRIMARY};
    border: 1px solid {DARK_GRAY_3};
    padding: 4px;
}}

QMenu::item:selected {{
    background-color: {PASTEL_GREEN_2};
    color: {TEXT_PRIMARY};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {DARK_GRAY_2};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background: {PASTEL_GREEN_2};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    background: none;
    border: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: {DARK_GRAY_3};
}}
"""

# Style for key buttons (15 main keys + 4 secondary)
KEY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {DARK_GRAY_2};
    border: 2px solid {DARK_GRAY_3};
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    font-size: 10px;
    padding: 4px;
    min-width: 80px;
    min-height: 80px;
    text-align: bottom;
}}

QPushButton:hover {{
    border-color: {PASTEL_GREEN_2};
    background-color: {DARK_GRAY_3};
}}

QPushButton:pressed {{
    border-color: {PASTEL_GREEN_3};
    background-color: {PASTEL_GREEN_1};
}}

QPushButton:checked {{
    border-color: {PASTEL_GOLD_2};
    background-color: {PASTEL_GOLD_1};
}}
"""

# Style for knob controls
KNOB_STYLE = f"""
QDial {{
    background-color: {DARK_GRAY_2};
    border: 2px solid {PASTEL_GOLD_2};
    border-radius: 50%;
}}

QDial::groove {{
    border: 2px solid {DARK_GRAY_3};
    border-radius: 50%;
    background: {DARK_GRAY_3};
}}

QDial::handle {{
    background: {PASTEL_GOLD_3};
    border: 1px solid {PASTEL_GOLD_2};
    border-radius: 50%;
    width: 16px;
    height: 16px;
}}
"""

# Style for touchscreen preview
TOUCHSCREEN_STYLE = f"""
QLabel {{
    background-color: {DARK_GRAY_1};
    border: 2px solid {PASTEL_GOLD_1};
    border-radius: 4px;
    margin: 4px;
}}
"""

# Style for action configuration panel
ACTION_PANEL_STYLE = f"""
QGroupBox {{
    background-color: {DARK_GRAY_2};
    border: 1px solid {DARK_GRAY_3};
    border-radius: 6px;
    color: {PASTEL_GOLD_2};
    font-weight: bold;
    margin-top: 10px;
    padding: 8px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}}

QLineEdit {{
    background-color: {DARK_GRAY_1};
    color: {TEXT_PRIMARY};
    border: 1px solid {DARK_GRAY_3};
    border-radius: 4px;
    padding: 4px;
    selection-background-color: {PASTEL_GREEN_2};
}}

QComboBox {{
    background-color: {DARK_GRAY_1};
    color: {TEXT_PRIMARY};
    border: 1px solid {DARK_GRAY_3};
    border-radius: 4px;
    padding: 4px;
}}

QComboBox::drop-down {{
    border: none;
    background: {DARK_GRAY_3};
}}

QComboBox QAbstractItemView {{
    background-color: {DARK_GRAY_2};
    color: {TEXT_PRIMARY};
    selection-background-color: {PASTEL_GREEN_2};
}}

QSlider::groove:horizontal {{
    height: 8px;
    background: {DARK_GRAY_3};
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
"""

# Style for primary action buttons
PRIMARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {PASTEL_GREEN_2};
    color: {TEXT_PRIMARY};
    border: 1px solid {PASTEL_GREEN_3};
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {PASTEL_GREEN_3};
}}

QPushButton:pressed {{
    background-color: {PASTEL_GREEN_1};
}}
"""

# Style for secondary action buttons
SECONDARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {DARK_GRAY_3};
    color: {TEXT_PRIMARY};
    border: 1px solid {DARK_GRAY_4};
    border-radius: 4px;
    padding: 6px 12px;
}}

QPushButton:hover {{
    background-color: {PASTEL_GOLD_1};
    border-color: {PASTEL_GOLD_2};
}}
"""

# Style for status bar
STATUS_BAR_STYLE = f"""
QStatusBar {{
    background-color: {DARK_GRAY_2};
    color: {PASTEL_GOLD_2};
    border-top: 1px solid {DARK_GRAY_3};
    padding: 4px;
}}
"""

# Complete application style
get_complete_style = lambda: (
    MAIN_WINDOW_STYLE + "\n" +
    KEY_BUTTON_STYLE + "\n" +
    KNOB_STYLE + "\n" +
    TOUCHSCREEN_STYLE + "\n" +
    ACTION_PANEL_STYLE + "\n" +
    PRIMARY_BUTTON_STYLE + "\n" +
    SECONDARY_BUTTON_STYLE + "\n" +
    STATUS_BAR_STYLE
)

# Color constants for programmatic use
COLORS = {
    "dark_gray_1": DARK_GRAY_1,
    "dark_gray_2": DARK_GRAY_2,
    "dark_gray_3": DARK_GRAY_3,
    "pastel_green": PASTEL_GREEN_2,
    "pastel_gold": PASTEL_GOLD_2,
    "text_primary": TEXT_PRIMARY,
    "text_secondary": TEXT_SECONDARY,
}
