from pathlib import Path

from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsView, QGraphicsScene, QLabel
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPolygonF, QPen, QPixmap, QFont

WALL_COLOR = QColor("black")
WALL_WIDTH = 4
GRID_COLOR = QColor(90, 90, 90)

CELL_SIZE = 50
MAZE_PADDING = 20
ROBOT_IMAGE_SIZE = CELL_SIZE * 0.95
FROG_IMAGE_SIZE = CELL_SIZE * 0.45
BEEPER_TEXT_FONT_SIZE = 6

_ASSETS_DIR = Path(__file__).parent / "assets"

def _make_text_font():
        font = QFont("Consolas", BEEPER_TEXT_FONT_SIZE)
        font.setStyleHint(QFont.Monospace)
        return font

class MazeView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.robot_item = None
        self.robot_label_item = None

        self.wall_pen = QPen(WALL_COLOR)
        self.wall_pen.setWidth(WALL_WIDTH)

        self.grid_pen = QPen(GRID_COLOR)
        self.grid_pen.setWidth(1)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)

        self.bag_overlay_label = QLabel("", self)
        self.bag_overlay_label.setStyleSheet(
            "background-color: rgba(30, 30, 30, 200); color: white; "
            "padding: 4px 8px; border-radius: 4px; font-size: 14px;"
        )
        self._position_bag_overlay()

        self.robot_pixmaps = {}
        for direction_name in ("north", "south", "east", "west"):
            for is_full, suffix in [(False, ""), (True, "_full")]:
                path = _ASSETS_DIR / f"robot_{direction_name}{suffix}.png"
                self.robot_pixmaps[(direction_name, is_full)] = QPixmap(str(path))

        self.frog_pixmap = QPixmap(str(_ASSETS_DIR / "lefrog.png"))

    def set_bag_count(self, count):
        self.bag_overlay_label.setText(f"Loptice kod robota: {count}")
        self._position_bag_overlay()

    def _position_bag_overlay(self):
        self.bag_overlay_label.adjustSize()
        margin = 8
        x = self.viewport().width() - self.bag_overlay_label.width() - margin
        y = margin
        self.bag_overlay_label.move(x, y)

    def draw_robot(self, world, x, y, direction, beeper_count=0):
        if self.robot_item is not None:
            self.scene.removeItem(self.robot_item)
        if self.robot_label_item is not None:
            self.scene.removeItem(self.robot_label_item)
            self.robot_label_item = None

        is_full = beeper_count > 0
        direction_name = direction.name.lower()
        pixmap = self.robot_pixmaps[(direction_name, is_full)]

        self.robot_item = QGraphicsPixmapItem(pixmap)
        self.robot_item.setTransformationMode(Qt.SmoothTransformation)

        scale = ROBOT_IMAGE_SIZE / pixmap.width()
        self.robot_item.setScale(scale)

        cell_left = x * CELL_SIZE
        cell_top = (world.height - 1 - y) * CELL_SIZE
        margin = (CELL_SIZE - ROBOT_IMAGE_SIZE) / 2
        self.robot_item.setPos(cell_left + margin, cell_top + margin)

        self.scene.addItem(self.robot_item)

        if beeper_count > 0:
            self.robot_label_item = self.scene.addText(str(beeper_count))
            self.robot_label_item.setZValue(1)
            self.robot_label_item.setPos(cell_left + 1, cell_top)
            self.robot_label_item.setFont(_make_text_font())

    def draw_beepers(self, world):
        hole_width = CELL_SIZE * 0.6
        hole_height = CELL_SIZE * 0.3

        for (x, y), count in world.beepers.items():
            center_x = x * CELL_SIZE + CELL_SIZE / 2
            center_y = (world.height - 1 - y) * CELL_SIZE + CELL_SIZE / 2

            if count > 0:
                frog_item = self.scene.addPixmap(self.frog_pixmap)
                frog_item.setTransformationMode(Qt.SmoothTransformation)
                scale = FROG_IMAGE_SIZE / self.frog_pixmap.width()
                frog_item.setScale(scale)
                frog_item.setPos(center_x - FROG_IMAGE_SIZE / 2, center_y - FROG_IMAGE_SIZE / 2)

                text_item = self.scene.addText(str(count))
                text_item.setFont(_make_text_font())
                text_item.setZValue(1)
                rect = text_item.boundingRect()
                text_item.setPos(center_x - rect.width() / 2, center_y - rect.height() / 2 + 1)

            else:
                color = QColor("#2E75B6")
                top_left_x = center_x - hole_width / 2
                top_left_y = center_y - hole_height / 2
                hole = self.scene.addEllipse(top_left_x, top_left_y, hole_width, hole_height)
                hole.setBrush(QBrush(color))

                text_item = self.scene.addText(str(abs(count)))
                text_item.setFont(_make_text_font())
                rect = text_item.boundingRect()
                text_item.setPos(center_x - rect.width() / 2, center_y - rect.height() / 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_scene()
        self._position_bag_overlay()

    def _fit_scene(self):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def render_world(self, world):
        self.scene.clear()
        self.robot_item = None
        self.robot_label_item = None

        for i in range(world.width + 1):
            self.scene.addLine(i * CELL_SIZE, 0, i * CELL_SIZE, world.height * CELL_SIZE, self.grid_pen)
        for j in range(world.height + 1):
            self.scene.addLine(0, j * CELL_SIZE, world.width * CELL_SIZE, j * CELL_SIZE, self.grid_pen)

        self.scene.addRect(0, 0, world.width * CELL_SIZE, world.height * CELL_SIZE, self.wall_pen)

        for wall in world.walls:
            p1, p2 = wall
            x1, y1 = p1
            x2, y2 = p2

            if x1 == x2:
                boundary_y = (world.height - 1 - min(y1, y2)) * CELL_SIZE
                left = x1 * CELL_SIZE
                right = (x1 + 1) * CELL_SIZE
                self.scene.addLine(left, boundary_y, right, boundary_y, self.wall_pen)
            else:
                boundary_x = max(x1, x2) * CELL_SIZE
                top = (world.height - 1 - y1) * CELL_SIZE
                bottom = (world.height - y1) * CELL_SIZE
                self.scene.addLine(boundary_x, top, boundary_x, bottom, self.wall_pen)

        self.draw_beepers(world)

        self.scene.setSceneRect(
            -MAZE_PADDING, -MAZE_PADDING,
            world.width * CELL_SIZE + 2 * MAZE_PADDING,
            world.height * CELL_SIZE + 2 * MAZE_PADDING,
        )
        self._fit_scene()