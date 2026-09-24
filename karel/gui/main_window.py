import copy
import random

from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QButtonGroup, QLabel
from PySide6.QtCore import QTimer

from karel.gui.code_editor import CodeEditor
from karel.gui.style import LEVEL_BUTTON_STYLE
from karel.robot import Robot
from karel.gui.maze_view import MazeView
from karel.executor import execute_program
from karel.exceptions import KarelRuntimeError, InvalidCommandError
from karel.task_registry import LEVEL_TASKS
from karel.grader import grade


LEVEL_NAMES = ["linijski", "brojacka_petlja", "uslovna_petlja", "grananje", "napredni"]
LEVEL_LABELS = {
    "linijski": "1. Linijski program",
    "brojacka_petlja": "2. Brojačka petlja",
    "uslovna_petlja": "3. Uslovna petlja",
    "grananje": "4. Grananje",
    "napredni": "5. Napredni",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karel")
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        code_panel = QVBoxLayout()
        code_panel.addWidget(QLabel("Kod:"))

        self.code_editor = CodeEditor()
        code_panel.addWidget(self.code_editor)

        self.run_button = QPushButton("Pokreni")
        code_panel.addWidget(self.run_button)
        self.run_button.clicked.connect(self.on_run_clicked)

        self.new_task_button = QPushButton("Novi zadatak")
        code_panel.addWidget(self.new_task_button)
        self.new_task_button.clicked.connect(self._on_new_task_clicked)

        self.new_variation_button = QPushButton("Nova varijanta")
        code_panel.addWidget(self.new_variation_button)
        self.new_variation_button.clicked.connect(self._on_new_variation_clicked)

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

        level_panel.addStretch()

        main_layout.addLayout(level_panel)
        main_layout.addLayout(code_panel)

        self.maze_view = MazeView()
        main_layout.addWidget(self.maze_view)

        self._load_new_task("linijski")

    def _make_level_handler(self, level):
        def handler(checked):
            if checked:
                self._load_new_task(level)
        return handler

    def _load_new_task(self, level):
        self.run_button.setVisible(True)
        self.next_task_button.setVisible(False)

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
        self._render_current_task()

    def _render_current_task(self):
        self.maze_view.render_world(self.task_world)
        x, y, direction = self.task_start
        self.maze_view.draw_robot(self.task_world, x, y, direction, self.task_initial_beepers)

    def _on_new_task_clicked(self):
        self._load_new_task(self.task_level)

    def _on_new_variation_clicked(self):
        self._display_current_task()

    def _on_next_task_clicked(self):
        self._load_new_task(self.task_level)

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
        self.animation_index += 1

    def _check_success(self):
        if self.task_num_variations == 1:
            def frozen_task_factory():
                world = copy.deepcopy(self.task_world)
                return world, self.task_start, self.task_initial_beepers, self.task_success
            is_correct = grade(self.current_code, self.task_level, frozen_task_factory, 1)
        else:
            is_correct = grade(self.current_code, self.task_level, self.task_factory, self.task_num_variations)

        if is_correct:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Rezultat")
            if self.task_num_variations > 1:
                msg_box.setText("Tačno! Rešenje radi za sve varijante zadatka.")
            else:
                msg_box.setText("Tačno!")
            msg_box.setIcon(QMessageBox.Information)
            ok_button = msg_box.addButton(QMessageBox.Ok)
            next_button = msg_box.addButton("Sledeći zadatak", QMessageBox.ActionRole)
            msg_box.exec()

            if msg_box.clickedButton() == next_button:
                self._load_new_task(self.task_level)
        else:
            QMessageBox.warning(self, "Rezultat", "Rešenje nije tačno :c pokušaj ponovo.")
            self._render_current_task()

    def on_run_clicked(self):
        code = self.code_editor.toPlainText()
        self.current_code = code

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
            QMessageBox.warning(self, "Greška", str(e))
            self.execution_failed = True

        self.current_robot = robot
        self.current_world = world_copy
        self._play_animation()