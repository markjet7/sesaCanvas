#%%
import igraph as ig
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import PyQt6.QtGui as QtGui
import PyQt6.QtCore as QtCore

import sys

# from os import path
# path_to_dat = path.abspath(path.join(path.dirname(__file__), 'thermosteam', 'units_of_measure.txt'))

import biosteam as bst

from math import cos, sin

# try:
#     from _misc import layout_system
# except:
#     from sesaCanvas._misc import layout_system
from _misc import layout_system
#%% 
class MyTableWidget(QTableWidget):
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            selected = self.selectedRanges()
            s = ""
            for r in range(selected[0].topRow(), selected[0].bottomRow()+1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(self.item(r,c).text()) + "\t"
                    except AttributeError:
                        s += "\t"
                s = s[:-1] + "\n"  # eliminate last '\t'
            self.clipboard = QApplication.clipboard()
            self.clipboard.setText(s)
        else:
            super().keyPressEvent(event)

class Arrow(QGraphicsLineItem):
    def __init__(self, startx, starty, endx, endy, source=None, sink=None):
        super().__init__()
        self.arrowHead = QGraphicsPolygonItem(self)
        self.setLine(startx, starty, endx, endy)
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy
        if source:
            self.source = source
            self.link_start(source)
        if sink:
            self.sink = sink
            self.link_end(sink)

    def link_start(self, rect):
        self.connect_line_start_to_rect(rect)

    def link_end(self, rect):
        self.connect_line_end_to_rect(rect)

    def distance_to_point(self, point1, point2):
        return ((point1.x() - point2.x())**2 + (point1.y() - point2.y())**2)**0.5
    
    def distance_to_line(self, point):
        x1, y1 = self.line().p1().x(), self.line().p1().y()
        x2, y2 = self.line().p2().x(), self.line().p2().y()
        x0, y0 = point.x(), point.y()
        return (((x0-x1)**2 + (y0-y1)**2)**0.5 + ((x0-x2)**2 + (y0-y2)**2)**0.5)

    def connect_line_end_to_rect(self,  rectItem: QGraphicsRectItem):
        rect = rectItem.boundingRect()  # Get the bounding rectangle of the item

        # Points of interest on the rectangle
        leftMid = QPointF(rect.left(), rect.center().y())
        rightMid = QPointF(rect.right(), rect.center().y())
        topMid = QPointF(rect.center().x(), rect.top())
        bottomMid = QPointF(rect.center().x(), rect.bottom())

        # Determine the endpoint of the line (assuming the start point is fixed and the end point is to be adjusted)
        lineEnd = self.line().p2()

        # Calculate distances to each edge's midpoint
        distances = {
            self.distance_to_line(leftMid): leftMid,
            self.distance_to_line(rightMid): rightMid,
            self.distance_to_line(topMid): topMid,
            self.distance_to_line(bottomMid): bottomMid,
        }

        # Find the nearest midpoint on the rectangle's edge to the line's endpoint
        nearestMidpoint = distances[min(distances)]
        self.setLine(self.line().p1().x(), self.line().p1().y(), nearestMidpoint.x(), nearestMidpoint.y())
        

    def connect_line_start_to_rect(self, rectItem: QGraphicsRectItem):
        rect = rectItem.boundingRect()  # Get the bounding rectangle of the item

        # Points of interest on the rectangle
        leftMid = QPointF(rect.left(), rect.center().y())
        rightMid = QPointF(rect.right(), rect.center().y())
        topMid = QPointF(rect.center().x(), rect.top())
        bottomMid = QPointF(rect.center().x(), rect.bottom())

        # Determine the start point of the line (this is the point to be adjusted)
        lineStart = self.line().p1()

        # Calculate distances to each edge's midpoint
        distances = {
            self.distance_to_line(leftMid): leftMid,
            self.distance_to_line(rightMid): rightMid,
            self.distance_to_line(topMid): topMid,
            self.distance_to_line(bottomMid): bottomMid,
        }

        # Find the nearest midpoint on the rectangle's edge to the line's start point
        nearestMidpoint = distances[min(distances)]
        self.setLine(nearestMidpoint.x(), nearestMidpoint.y(), self.line().p2().x(), self.line().p2().y())


    def setLine(self, startx, starty, endx, endy):
        super().setLine(startx, starty, endx, endy)
        pen = QPen(Qt.GlobalColor.black, 2) 
        self.setPen(pen)

        # calculate the angle of the line
        angle = self.line().angle()

        # create a polygon for the arrow head
        arrowHead = QPolygonF()

        # add points to the polygon to create the shape of the arrow head
        arrowHead.append(QPointF(0, 0))
        arrowHead.append(QPointF(-15, -7))
        arrowHead.append(QPointF(-15, 7))

        # rotate the arrow head to match the line angle
        self.arrowHead.setPolygon(arrowHead)
        self.arrowHead.setPos(self.line().p2())
        self.arrowHead.setRotation(-angle)




class GraphicsScene(QGraphicsScene):
    system = None
    output = None
    def __init__(self):
        super(GraphicsScene, self).__init__()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # get the item that was clicked on
        item = self.itemAt(event.scenePos(), QTransform())
        if item:
            # check if item is a QGraphicsTextItem
            if isinstance(item, QGraphicsTextItem):
                # get the text
                text = item.toPlainText()
                self.output.clear()

                stream = self.system.flowsheet.stream[text] if text in [s.ID for s in self.system.streams] else None

                if stream != None:
                    self.output.append("ID: " + text + "\n")
                    self.output.append(f"Mass flow: {stream.F_mass:.2f} kg/hr\n")
                    self.output.append(f"Molar flow: {stream.F_mol:.2f} mol/hr\n")
                    self.output.append("Chemicals:\n")
                    for c in stream.available_chemicals:
                        self.output.append(f"{c.ID} flow: {stream.imass[c.ID]:.2f} kg/hr\n")
                
                unit = self.system.flowsheet.unit[text] if text in [u.ID for u in self.system.units] else None
                if unit != None:
                    self.output.append("ID: " + text + "\n")
                    self.output.append("Inlets:\n")
                    for s in unit.ins:
                        self.output.append(f"{s.ID} flow: {s.F_mass:.2f} kg/hr\n")
                        for c in s.available_chemicals:
                            self.output.append(f"{c.ID} flow: {s.imass[c.ID]:.2f} kg/hr\n")
                    self.output.append("Outlets:\n")
                    for s in unit.outs:
                        self.output.append(f"{s.ID} flow: {s.F_mass:.2f} kg/hr\n")
                        for c in s.available_chemicals:
                            self.output.append(f"{c.ID} flow: {s.imass[c.ID]:.2f} kg/hr\n")
                    self.output.append("Heat utilities:\n")
                    for hu in unit.heat_utilities:
                        self.output.append(f"{hu.ID} duty: {hu.duty:.2f} kW\n")
                        self.output.append(f"{hu.ID} cost: {hu.cost:.2f} USD/hr\n")
                    for (k,v) in unit.design_results.items():
                        self.output.append(f"{k}: {v}\n")


class MainWindow(QMainWindow):
    system_dict = {}
    system_names = []
    def __init__(self):
        super().__init__()

        # show the window on the left side of the screen
        self.setGeometry(100, 100, 1200, 800)

        # add horizontal layout
        self.layout = QHBoxLayout()

        # Create a QGraphicsView which will serve as your canvas
        self.view = QGraphicsView()
        # add scrollbars 
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Create a QGraphicsScene which is the container for your graphical items
        self.scene = GraphicsScene()
        self.scene.setSceneRect(0, 0, 1600, 1250)

        # Set the scene to the view
        self.view.setScene(self.scene)

        # Create the central Widget
        self.layoutWidget = QWidget()
        self.layoutWidget.setLayout(self.layout)

        self.setCentralWidget(self.layoutWidget)

        # Add the QGraphicsView to the layout
        self.layout.addWidget(self.view)
        # self.layout.addWidget(self.text)

        # Set the window title
        self.setWindowTitle("Process Diagram")

        # create toolbar 
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # create action to load system
        load_system_action = QAction("Load System", self)
        load_system_action.triggered.connect(self.load_system)
        toolbar.addAction(load_system_action)

        # create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        load_system_action = QAction("Load System", self)
        load_system_action.triggered.connect(self.load_system)
        file_menu.addAction(load_system_action)

        # create a text view
        self.text = QTextEdit()

        # create a new window
        self.stream_window = QWidget()
        self.stream_window.layout = QVBoxLayout()
        self.stream_window.layout.addWidget(self.text)
        self.stream_window.setWindowTitle("Stream Info")
        # self.stream_window.setCentralWidget(self.text)
        self.stream_window.resize(500, 500)
        self.stream_window.setLayout(self.stream_window.layout)
        self.stream_window.show()
        # bring to the front
        self.stream_window.raise_()

        self.stream_table_window = QWidget()
        self.stream_table_window.layout = QVBoxLayout()
        self.stream_table_window.setWindowTitle("Stream Table")
        self.stream_table = MyTableWidget()
        self.stream_table_window.layout.addWidget(self.stream_table)
        self.stream_table_window.setLayout(self.stream_table_window.layout)
        # self.stream_table_window.setCentralWidget(self.stream_table)
        self.stream_table_window.resize(500, 500)

        # add a toolbar dropdown to show a list of systems
        self.system_dropdown = QComboBox()
        self.system_dropdown.addItems(["Systems..."])
        self.system_dropdown.currentIndexChanged.connect(self.change_system)
        toolbar.addWidget(self.system_dropdown)

        self.simulate_button = QPushButton("Simulate")
        self.simulate_button.clicked.connect(self.simulate)
        toolbar.addWidget(self.simulate_button)


        show_stream_info_action = QAction("Show Stream", self)
        show_stream_info_action.triggered.connect(self.stream_window.show)
        toolbar.addAction(show_stream_info_action)
        file_menu.addAction(show_stream_info_action)

        # show the stream table on the top right
        self.stream_table_window.setGeometry(1400, 100, 500, 500)
        self.stream_table_window.show()
        # show the stream info on the bottom right
        self.stream_window.setGeometry(1400, 600, 500, 500)
        self.stream_window.show()

    def simulate(self):
        self.system.simulate()
        self.change_system(self.system_dropdown.currentIndex())

    def change_system(self, index):
        if index > 0:
            self.system = self.system_dict[self.system_names[index-1]]
            self.draw(self.system)
            self.scene.system = self.system
            self.scene.output = self.text

            self.stream_table.clear()
            self.stream_table.setRowCount(len(self.system.streams))
            self.stream_table.setColumnCount(4 + len(self.system.streams[0].available_chemicals))
            self.stream_table.setHorizontalHeaderLabels(["ID", "Source", "Sink", "Type"] + [c.ID for c in self.system.streams[0].available_chemicals])
            for i, stream in enumerate(self.system.streams):
                self.stream_table.setItem(i, 0, QTableWidgetItem(stream.ID))
                self.stream_table.setItem(i, 1, QTableWidgetItem(stream.source.ID if stream.source else ""))
                self.stream_table.setItem(i, 2, QTableWidgetItem(stream.sink.ID if stream.sink else ""))
                self.stream_table.setItem(i, 3, QTableWidgetItem("S"))
                for j, c in enumerate(self.system.streams[0].available_chemicals):
                    self.stream_table.setItem(i, j+4, QTableWidgetItem(str(stream.imass[c.ID])))


    def load_system(self, path=None):
        # open file dialog 
        if path == False or path==None:
            path = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py)")[0]
        try:
            directory = path.split("/")[:-1]
            directory = "/".join(directory)
            sys.path.append(directory)
            with open(path, 'r') as f:
                try:
                    code = f.read()
                    exec(code, globals())
                except:
                    self.statusBar.showMessage("Error loading system")
                    return

            # get the systems
            # loop through the global objects and find the ones that are bst.System
            self.system_dict = {}
            for name, obj in globals().items():
                if isinstance(obj, bst.System):
                    self.system_dict[name] = obj
            self.system_names = list(self.system_dict.keys())
            # self.draw(list(self.system_dict.values())[0])
            self.system = list(self.system_dict.values())[0]
            self.scene.system = self.system
            self.scene.output = self.text

            for i in range(self.system_dropdown.count(), 1, -1):
                self.system_dropdown.removeItem(0)
            self.system_dropdown.addItems(self.system_names)
            self.system_dropdown.setCurrentIndex(1)
            self.change_system(1)
            

        except Exception as e:
            print(e)
            self.statusBar.showMessage("Error loading system")
            return


    def draw(self, sys):
        self.scene.clear()
        self.scene.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
        # self.scene.addLine(0, 0, 100, 100, pen)
        # self.scene.addRect(10, 10, 200, 100, pen)
        
        graph, layout, system = layout_system(sys)
        self.system = system
        self.scene.system = system 
        positions = {}
        grid_x = 250
        grid_y = 100
        for (l, p) in zip(graph.vs["label"], layout.coords):
            positions[l] = [p[0] * grid_x, (p[1]) * grid_y]

        self.scene.setSceneRect(
            min([p[0] for p in positions.values()]), 
            min([p[1] for p in positions.values()]), 
            max([p[0] for p in positions.values()]) + 100, 
            max([p[1] for p in positions.values()]) + 100)
        

        def placeLine(stream):
            pen = QPen(Qt.GlobalColor.black, 2) 
            textFont = self.scene.font()
            # set textFont color to black 
            if stream.source and stream.sink:
                if stream.source.ID in positions and stream.sink.ID in positions:
                        start_x, start_y, end_x, end_y = positions[stream.source.ID][0], positions[stream.source.ID][1], positions[stream.sink.ID][0], positions[stream.sink.ID][1]
                        arrow = Arrow(start_x, start_y, end_x, end_y,
                                source=rects[stream.source.ID],
                                sink=rects[stream.sink.ID])
                elif stream.source.ID in positions and stream.sink.ID not in positions:
                    start_x, start_y, end_x, end_y = positions[stream.source.ID][0], positions[stream.source.ID][1], positions[stream.source.ID][0]+250, positions[stream.source.ID][1]
                    arrow = Arrow(start_x, start_y, end_x, end_y,
                                source=rects[stream.source.ID])
                elif stream.sink.ID in positions and stream.source.ID not in positions:
                    start_x, start_y, end_x, end_y = positions[stream.sink.ID][0]-250, positions[stream.sink.ID][1], positions[stream.sink.ID][0], positions[stream.sink.ID][1]
                    arrow = Arrow(start_x, start_y, end_x, end_y,
                                sink=rects[stream.sink.ID])
                self.scene.addItem(arrow)
                text = self.scene.addText(stream.ID, textFont)
                text.setDefaultTextColor(Qt.GlobalColor.black)
                text.setPos(
                    (start_x + end_x)/2,
                    (start_y + end_y)/2)
            elif stream.source and stream.sink == None:
                if stream.source.ID in positions and stream.ID in positions:
                    start_x, start_y, end_x, end_y = positions[stream.source.ID][0], positions[stream.source.ID][1], positions[stream.ID][0]+250, positions[stream.ID][1]
                    arrow = Arrow(start_x, start_y, end_x, end_y,
                                    source=rects[stream.source.ID])
                else:
                    start_x, start_y, end_x, end_y = positions[stream.source.ID][0], positions[stream.source.ID][1], positions[stream.source.ID][0]+250, positions[stream.source.ID][1]
                    arrow = Arrow(start_x, start_y, end_x, end_y,
                                    source=rects[stream.source.ID])
                self.scene.addItem(arrow)
                text = self.scene.addText(stream.ID, textFont)
                text.setDefaultTextColor(Qt.GlobalColor.black)
                text.setPos(
                    start_x + 250,
                    start_y - 25)
            elif stream.sink and stream.source == None:
                if stream.sink.ID in positions and stream.ID in positions:
                    start_x, start_y, end_x, end_y = positions[stream.sink.ID][0]-250, positions[stream.sink.ID][1], positions[stream.ID][0], positions[stream.ID][1]
                    arrow = Arrow(start_x, start_y, end_x, end_y,
                                    sink=rects[stream.sink.ID])
                else:
                    start_x, start_y, end_x, end_y = positions[stream.sink.ID][0]-250, positions[stream.sink.ID][1], positions[stream.sink.ID][0], positions[stream.sink.ID][1]
                    arrow = Arrow(start_x, start_y, end_x, end_y,
                                    sink=rects[stream.sink.ID])

                self.scene.addItem(arrow)
                text = self.scene.addText(stream.ID, textFont)
                text.setDefaultTextColor(Qt.GlobalColor.black)
                text.setPos(
                    (start_x - 50),
                    (start_y - 25))
        
        rects = {}
        def placeUnit(unit):
            pen = QPen(Qt.GlobalColor.black, 2) 
            brush = QBrush(Qt.GlobalColor.white)
            rects[unit.ID] = self.scene.addRect(positions[unit.ID][0]-50,
                               positions[unit.ID][1]-25,
                               100,
                               50,
                               pen,
                               brush)
            text = self.scene.addText(unit.ID, self.scene.font())
            text.setDefaultTextColor(Qt.GlobalColor.black)
            # underline block 
            text.setHtml("<u>" + text.toPlainText() + "</u>")
            text.setPos(
                positions[unit.ID][0] - 50,
                positions[unit.ID][1] - 25)
                
        list(map(placeUnit, self.scene.system.units))
        list(map(placeLine, self.scene.system.streams))
        for item in self.scene.items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect)
        print("Done drawing")

def run(path=None):
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.stream_table_window.show()
    window.stream_table_window.raise_()
    window.stream_window.show()
    window.stream_window.raise_()
    if path:
        window.load_system(path)

    app.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()