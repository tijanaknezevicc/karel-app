import copy
import random

from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QButtonGroup, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon


from karel.gui.code_editor import CodeEditor
from karel.gui.help_dialog import HelpDialog
from karel.gui.style import HELP_BUTTON_STYLE, LEVEL_BUTTON_STYLE, PANEL_LABEL_STYLE, STATUS_STYLES, TASK_DESCRIPTION_STYLE
from karel.robot import Robot
from karel.gui.maze_view import MazeView
from karel.executor import execute_program
from karel.exceptions import KarelRuntimeError, InvalidCommandError
from karel.task_registry import LEVEL_TASKS
from karel.grader import grade, missing_required_constructs


LEVEL_NAMES = ["linijski", "brojacka_petlja", "uslovna_petlja", "grananje", "napredni"]
LEVEL_LABELS = {
    "linijski": "1. Linijski program",
    "brojacka_petlja": "2. Brojačka petlja",
    "uslovna_petlja": "3. Uslovna petlja",
    "grananje": "4. Grananje",
    "napredni": "5. Napredni",
}

_ASSETS_DIR = Path(__file__).parent / "assets"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karel")
        self.setMinimumSize(1100, 650)
        self.setWindowIcon(QIcon(str(_ASSETS_DIR / "robot_south.png")))


        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        level_panel = QVBoxLayout()
        level_panel.addWidget(QLabel("Izaberi nivo:"))

        self.level_button_group = QButtonGroup(self)
        for level in LEVEL_NAMES:
            button = QPushButton(LEVEL_LABELS[level])
            button.setCheckable(True)
            button.setStyleSheet(LEVEL_BUTTON_STYLE)
            level_panel.addWidget(button)
            self.level_button_group.addButton(button)
            if level == "linijski":
                button.setChecked(True)
            button.toggled.connect(self._make_level_handler(level))

        self.help_button = QPushButton("Podsetnik")
        self.help_button.setStyleSheet(HELP_BUTTON_STYLE)
        self.help_button.clicked.connect(self._on_help_clicked)
        level_panel.addWidget(self.help_button)

        level_panel.addStretch()

        code_panel = QVBoxLayout()

        code_label = QLabel("Kod")
        code_label.setStyleSheet(PANEL_LABEL_STYLE)
        code_label.setAlignment(Qt.AlignCenter)
        code_panel.addWidget(code_label)

        self.code_editor = CodeEditor()
        code_panel.addWidget(self.code_editor)

        self.run_button = QPushButton("Pokreni")
        self.run_button.clicked.connect(self.on_run_clicked)

        self.new_variation_button = QPushButton("Nova varijanta")
        self.new_variation_button.clicked.connect(self._on_new_variation_clicked)

        self.reset_button = QPushButton("Resetuj")
        self.reset_button.clicked.connect(self._render_current_task)

        run_row = QHBoxLayout()
        run_row.addWidget(self.run_button)
        run_row.addWidget(self.reset_button)
        run_row.addWidget(self.new_variation_button)
        code_panel.addLayout(run_row)        

        self.new_task_button = QPushButton("Sledeći zadatak")
        code_panel.addWidget(self.new_task_button)
        self.new_task_button.clicked.connect(self._on_new_task_clicked)

        self.maze_view = MazeView()

        maze_panel = QVBoxLayout()

        self.task_description_label = QLabel("")
        self.task_description_label.setWordWrap(True)
        self.task_description_label.setStyleSheet(TASK_DESCRIPTION_STYLE)

        maze_top_row = QHBoxLayout()
        maze_top_row.addWidget(self.task_description_label)
        maze_panel.addLayout(maze_top_row)
        maze_panel.addWidget(self.maze_view)

        right_side = QVBoxLayout()

        content_layout = QHBoxLayout()
        content_layout.addLayout(code_panel, 3)
        content_layout.addLayout(maze_panel, 4)
        right_side.addLayout(content_layout)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(STATUS_STYLES["info"])
        right_side.addWidget(self.status_label)

        main_layout.addLayout(level_panel)
        main_layout.addLayout(right_side)

        self._load_new_task("linijski")

    def _on_help_clicked(self):
        dialog = HelpDialog(self.task_level, self)
        dialog.exec()

    def _set_status(self, text, kind="info"):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(STATUS_STYLES.get(kind, STATUS_STYLES["info"]))

    def _make_level_handler(self, level):
        def handler(checked):
            if checked:
                self._load_new_task(level)
        return handler

    def _load_new_task(self, level):
        self.code_editor.clear()
        self._set_status("", "info")
        self.run_button.setVisible(True)

        maker, num_variations = random.choice(LEVEL_TASKS[level])
        self.task_factory = maker()
        self.task_level = level
        self.task_num_variations = num_variations
        self.new_variation_button.setVisible(num_variations > 1)

        self._display_current_task()

    def _display_current_task(self):
        world, start, initial_beepers, success = self.task_factory()
        self.task_world = world
        self.task_start = start
        self.task_initial_beepers = initial_beepers
        self.task_success = success
        self.task_description_label.setText(getattr(success, "description", ""))
        self._render_current_task()

    def _render_current_task(self):
        self.maze_view.render_world(self.task_world)
        x, y, direction = self.task_start
        self.maze_view.set_bag_count(self.task_initial_beepers)
        self.maze_view.draw_robot(self.task_world, x, y, direction, self.task_initial_beepers)

    def _on_new_task_clicked(self):
        self._load_new_task(self.task_level)

    def _on_new_variation_clicked(self):
        self._display_current_task()

    def _play_animation(self):
        self.animation_index = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._show_next_frame)
        self.animation_timer.start(300)

    def _show_next_frame(self):
        if self.animation_index >= len(self.animation_frames):
            self.animation_timer.stop()
            if not self.execution_failed:
                self._check_success()
            return

        x, y, direction, beepers, bag_count = self.animation_frames[self.animation_index]
        self.current_world.beepers = beepers
        self.maze_view.render_world(self.current_world)
        self.maze_view.draw_robot(self.current_world, x, y, direction, bag_count)
        self.maze_view.set_bag_count(bag_count)
        self.animation_index += 1

    def _check_success(self):
        missing = missing_required_constructs(self.current_code, self.task_level)
        if missing:
            self._set_status(f"Netačno. Nije upotrebljena {', '.join(missing)}.", "error")
            self._render_current_task()
            return

        if self.task_num_variations == 1:
            def frozen_task_factory():
                world = copy.deepcopy(self.task_world)
                return world, self.task_start, self.task_initial_beepers, self.task_success
            is_correct = grade(self.current_code, self.task_level, frozen_task_factory, 1)
        else:
            is_correct = grade(self.current_code, self.task_level, self.task_factory, self.task_num_variations)

        if is_correct:
            if self.task_num_variations > 1:
                self._set_status("Tačno! Rešenje radi za sve varijante zadatka.", "success")
            else:
                self._set_status("Tačno!", "success")
        else:
            self._set_status("Rešenje nije tačno :c pokušaj ponovo.", "error")
            self._render_current_task()

    def on_run_clicked(self):
        code = self.code_editor.toPlainText()
        if not code.strip():
            return

        self.current_code = code
        self._set_status("", "info")

        world_copy = copy.deepcopy(self.task_world)
        x, y, direction = self.task_start
        robot = Robot(x=x, y=y, direction=direction)
        robot.beepers = self.task_initial_beepers
        robot.place_in_world(world_copy)

        self.animation_frames = []

        def record_frame():
            self.animation_frames.append((
                robot.x, robot.y, robot.direction,
                copy.deepcopy(world_copy.beepers),
                robot.beeper_count_in_bag(),
                ))
        robot.on_step = record_frame

        self.execution_failed = False
        try:
            execute_program(code, robot, self.task_level)
        except (KarelRuntimeError, InvalidCommandError) as e:
            self._set_status(str(e), "error")
            self.execution_failed = True

        self.current_robot = robot
        self.current_world = world_copy
        self._play_animation()