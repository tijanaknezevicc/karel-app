LEVEL_BUTTON_STYLE = """
QPushButton {
    padding: 10px;
    text-align: left;
    border: 1px solid #555;
    border-radius: 4px;
    background-color: #2b2b2b;
    color: white;
}
QPushButton:checked {
    background-color: #2f6fbf;
    border-color: #2f6fbf;
}
QPushButton:hover {
    background-color: #3a3a3a;
}
"""

PANEL_LABEL_STYLE = "padding: 6px; font-size: 13px; font-weight: bold; background-color: #2b2b2b; border: 1px solid #555; border-radius: 4px;"
TASK_DESCRIPTION_STYLE = "padding: 6px; font-size: 13px; background-color: #2b2b2b; border: 1px solid #555; border-radius: 4px;"


STATUS_STYLES = {
    "success": "padding: 10px; font-size: 14px; background-color: #1e4620; color: #8fe08f; border-radius: 4px;",
    "error": "padding: 10px; font-size: 14px; background-color: #4a1e1e; color: #f28b8b; border-radius: 4px;",
    "info": "padding: 10px; font-size: 14px; background-color: transparent; color: #cccccc;",
}