from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        
        # Set up custom title bar layout
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Title label
        self.title_label = QLabel("PCInsight")
        self.title_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.title_label)
        
        # Button styles
        button_style = """
            QPushButton {
                background-color: #121212;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                color: #E0E0E0;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #333333; /* Color when hovering */
            }
        """

        close_button_style = """
            QPushButton {
                background-color: #121212;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                color: #E0E0E0;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #FF4C4C; /* Color when hovering */
            }
        """
        
        # Minimize button
        minimize_button = QPushButton("—")
        minimize_button.setStyleSheet(button_style)
        minimize_button.clicked.connect(self.minimize_window)
        minimize_button.setMaximumWidth(60)
        layout.addWidget(minimize_button)
        
        # Maximize button
        maximize_button = QPushButton("☐")
        maximize_button.setStyleSheet(button_style)
        maximize_button.clicked.connect(self.maximize_window)
        maximize_button.setMaximumWidth(60)
        layout.addWidget(maximize_button)
        
        # Close button
        close_button = QPushButton("X")
        close_button.setStyleSheet(close_button_style)  # Optional: change color for close button
        close_button.clicked.connect(self.close_window)
        close_button.setMaximumWidth(60)
        layout.addWidget(close_button)
        
        # Set background color
        self.setStyleSheet("background-color: #121212; color: #E0E0E0;")

        # Initialize drag position
        self.drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.position()

    def mouseMoveEvent(self, event):
        if self.drag_position:
            # Calculate the new position
            delta = event.position() - self.drag_position
            new_pos = self.window().pos() + QPoint(int(delta.x()), int(delta.y()))
            self.window().move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None

    def minimize_window(self):
        self.window().showMinimized()

    def maximize_window(self):
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def close_window(self):
        self.window().close()
