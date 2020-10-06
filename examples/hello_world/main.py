"""
We all love "hello world" examples =)
"""

import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow

from qmxgraph.widget import QmxGraph


class HelloWorldWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("Qmx Hello World")

        self.graph_widget = QmxGraph(parent=self)
        # Only operate with the qmx's api after the widget has been loaded.
        self.graph_widget.loadFinished.connect(self.graph_load_handler)
        self.setCentralWidget(self.graph_widget)

    def graph_load_handler(self, is_loaded):
        assert is_loaded
        qmx = self.graph_widget.api

        qmx.insert_vertex(
            ignore_result,
            x=100, y=100,
            width=50, height=100,
            label="Qmx", id='v0',
        )
        qmx.insert_vertex(
            ignore_result,
            x=400, y=300,
            width=100, height=50,
            label="World", id='v1',
        )
        qmx.insert_edge(
            ignore_result, source_id='v0', target_id='v1', label="Hello"
        )


def ignore_result(v):
    pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWorldWindow()
    mainWin.show()
    sys.exit(app.exec_())
