from PySide6.QtWidgets import QGraphicsPolygonItem, QGraphicsView, QGraphicsScene
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPolygonF, QPen

WALL_COLOR = QColor("black")
WALL_WIDTH = 4
GRID_COLOR = QColor(90, 90, 90)

CELL_SIZE = 50

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

    def _create_robot_item(self):
        size = CELL_SIZE * 0.4
        points = [
            QPointF(0, -size),
            QPointF(-size * 0.6, size * 0.6),
            QPointF(size * 0.6, size * 0.6),
        ]
        polygon = QPolygonF(points)
        item = QGraphicsPolygonItem(polygon)
        item.setBrush(QBrush(Qt.green))
        return item

    def draw_robot(self, world, x, y, direction, beeper_count=0):
        if self.robot_item is not None:
            self.scene.removeItem(self.robot_item)
        if self.robot_label_item is not None:
            self.scene.removeItem(self.robot_label_item)
            self.robot_label_item = None

        self.robot_item = self._create_robot_item()

        center_x = x * CELL_SIZE + CELL_SIZE / 2
        center_y = (world.height - 1 - y) * CELL_SIZE + CELL_SIZE / 2

        self.robot_item.setPos(center_x, center_y)
        self.robot_item.setRotation(direction.value * 90)
        self.scene.addItem(self.robot_item)

        if beeper_count > 0:
            self.robot_label_item = self.scene.addText(str(beeper_count))
            rect = self.robot_label_item.boundingRect()
            self.robot_label_item.setPos(center_x - rect.width() / 2, center_y - CELL_SIZE * 0.55)

    def draw_beepers(self, world):
        pile_radius = CELL_SIZE * 0.2
        hole_width = CELL_SIZE * 0.6
        hole_height = CELL_SIZE * 0.3

        for (x, y), count in world.beepers.items():
            center_x = x * CELL_SIZE + CELL_SIZE / 2
            center_y = (world.height - 1 - y) * CELL_SIZE + CELL_SIZE / 2

            if count > 0:
                color = QColor("purple")
                top_left_x = center_x - pile_radius
                top_left_y = center_y - pile_radius
                circle = self.scene.addEllipse(top_left_x, top_left_y, pile_radius * 2, pile_radius * 2)
                circle.setBrush(QBrush(color))

                text_item = self.scene.addText(str(count))
                rect = text_item.boundingRect()
                text_item.setPos(center_x - rect.width() / 2, center_y - rect.height() / 2)

            else:
                color = QColor("black")
                top_left_x = center_x - hole_width / 2
                top_left_y = center_y - hole_height / 2
                hole = self.scene.addEllipse(top_left_x, top_left_y, hole_width, hole_height)
                hole.setBrush(QBrush(color))

                text_item = self.scene.addText(str(abs(count)))
                rect = text_item.boundingRect()
                text_item.setPos(center_x - rect.width() / 2, center_y - rect.height() / 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_scene()

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

            if x1 == x2:  # horizontal wall
                boundary_y = (world.height - 1 - min(y1, y2)) * CELL_SIZE
                left = x1 * CELL_SIZE
                right = (x1 + 1) * CELL_SIZE
                self.scene.addLine(left, boundary_y, right, boundary_y, self.wall_pen)
            else:  # vertical wall
                boundary_x = max(x1, x2) * CELL_SIZE
                top = (world.height - 1 - y1) * CELL_SIZE
                bottom = (world.height - y1) * CELL_SIZE
                self.scene.addLine(boundary_x, top, boundary_x, bottom, self.wall_pen)

        self.draw_beepers(world)
        self.scene.setSceneRect(0, 0, world.width * CELL_SIZE, world.height * CELL_SIZE)
        self._fit_scene()
            