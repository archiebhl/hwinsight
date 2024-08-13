import os
import sys
import subprocess
import multiprocessing
from threading import Thread
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from data_parser import DataParser
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis_range import LiveAxisRange
from pyqtgraph import mkPen  # type: ignore
from custom_title_bar import CustomTitleBar
import atexit
from pyqtgraph import PlotWidget, TextItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.large_font = QFont()
        self.large_font.setPointSize(16)
        self.med_font = QFont()
        self.med_font.setPointSize(14)
        self.small_font = QFont()
        self.small_font.setPointSize(12)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # remove default title bar
        self.setMenuWidget(CustomTitleBar(self))

        self.setWindowTitle("HWInsight")
        WINDOW_HEIGHT = 800
        WINDOW_WIDTH = 1200
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Create main layout grid
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QGridLayout()
        central_widget.setLayout(self.main_layout)

        # GPU Plots
        self.groupBoxGPUPlotsLayout = QGridLayout()
        self.groupBoxGPUPlots = QGroupBox("GPU")
        self.groupBoxGPUPlots.setLayout(self.groupBoxGPUPlotsLayout)
        self.groupBoxGPUPlots.setFont(self.large_font)
        self.main_layout.addWidget(self.groupBoxGPUPlots)

        # CPU Plots
        self.groupBoxCPUPlotsLayout = QGridLayout()
        self.groupBoxCPUPlots = QGroupBox("CPU")
        self.groupBoxCPUPlots.setLayout(self.groupBoxCPUPlotsLayout)
        self.groupBoxCPUPlots.setFont(self.large_font)
        self.main_layout.addWidget(self.groupBoxCPUPlots, 1, 0)

        # Set up plots and extra info
        self.set_up_plots()
        self.set_up_extra_info()
        
        # Add GPU Info group box to the main layout
        self.main_layout.addWidget(self.gpu_view, 0, 1)

        # Add CPU Info group box to the main layout
        self.main_layout.addWidget(self.cpu_view, 1, 1)

    def set_up_plots(self):
        data_sources = ['cpu_temp', 'cpu_usage', 'gpu_temp', 'gpu_usage']

        self.plot_widgets = []
        self.data_connectors = []
        for i, data_source in enumerate(data_sources):
            title = "Loading..."
            plot_widget = LivePlotWidget(
                title=title,
                background=None,
                y_range_controller=LiveAxisRange(fixed_range=[0, 100])
            )
            plot_widget.getPlotItem().setTitle(title=f"<span style='font-family: Segoe UI Variable; color: white; font-size: 11pt; text-align:left;'>{title}</span>")
            plot_curve = LiveLinePlot()
            #plot_curve.set_leading_line(LeadingLine.VERTICAL, pen=mkPen("#E0E0E0"), text_axis=LeadingLine.AXIS_Y, text_rotation=0)
            plot_widget.addItem(plot_curve)
            plot_widget.setYRange(0, 100)

            data_connector = DataConnector(plot_curve, max_points=600, update_rate=100)
            self.plot_widgets.append(plot_widget)
            self.data_connectors.append(data_connector)

            if "cpu" in data_sources[i]:
                row, col = divmod(i,2)
                self.groupBoxCPUPlotsLayout.addWidget(plot_widget, 0, col)
            else:
                row, col = divmod(i - 2, 2)
                self.groupBoxGPUPlotsLayout.addWidget(plot_widget, 0, col)

        self.data_parser = DataParser()
        self.data_thread = Thread(target=self.data_parser.parse_data, daemon=True)
        self.data_thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def update_data(self):
        self.groupBoxGPUPlots.setTitle("GPU: " + self.data_parser.get_gpu_name())
        self.groupBoxCPUPlots.setTitle("CPU: " + self.data_parser.get_cpu_name())

        data_points = self.data_parser.get_latest_data()
        for i, data_type in enumerate(self.data_parser.data_points):
            if data_points[data_type]:
                new_data = data_points[data_type][-1]  # Get the latest data point
                new_data = int(new_data)
                self.data_connectors[i].cb_append_data_point(new_data, len(data_points[data_type]))
                
                plot_mapping = [
                (self.groupBoxCPUPlotsLayout, 0, 0, "°C"),
                (self.groupBoxCPUPlotsLayout, 0, 1, "%"),
                (self.groupBoxGPUPlotsLayout, 0, 0, "°C"),
                (self.groupBoxGPUPlotsLayout, 0, 1, "%")
                ]

                if 0 <= i < len(plot_mapping):
                    layout, row, col, unit = plot_mapping[i]
                    self.update_plot_title(layout, row, col, new_data, unit)
        
        self.update_cpu_info()
        self.update_gpu_info()
    
    def update_plot_title(self, layout, row, col, new_data, unit):
        plot = layout.itemAtPosition(row, col)
        plot_widget = plot.widget()
        
        spacing = ""
        for i in range(48):
            spacing += "&nbsp;"

        if isinstance(plot_widget, LivePlotWidget):
            plot_widget.getPlotItem().setTitle(
                title=f"<span style='font-family: Segoe UI Variable; color: white; font-size: 16pt;'>{spacing}{new_data}{unit}</span>"
            )
    
    def update_cpu_info(self):
        self.cpu_extra_info_dict = self.data_parser.get_cpu_extra_info()
        
        # Grouping data per core
        cpu_core_data = {}
        for key, value in self.cpu_extra_info_dict.items():
            if "Thread" in key or "Distance to TjMax" in key:
                core_id = key.split()[2]  # e.g., "1", "2", etc.
                if core_id not in cpu_core_data:
                    cpu_core_data[core_id] = []
                cpu_core_data[core_id].append((key, value))

        cpu_col1 = ""
        cpu_col2 = ""
        cpu_col3 = ""
        count = 1

        for core_id, data in cpu_core_data.items():
            core_info = ""

            core_id = core_id.replace("#", "")
            core_info += f"<span style='font-size:14px;'>CPU Core {core_id}</span><br>"
            
            for key, value in data:
                if "Thread" in key:
                    RELEVANT_CHARS = 9
                    key = key[-RELEVANT_CHARS:]  # Get the thread utilization percentage
                    key = key.replace("#", "")
                    core_info += f"<span style='font-size:14px;'>{key}: </span> <span style='font-size:18px;'>{value}</span><br>"
            core_info += f"<br>"
            
            if count == 1:
                cpu_col1 += core_info
            elif count == 2:
                cpu_col2 += core_info
            elif count == 3:
                cpu_col3 += core_info
            
            count = 1 if count == 3 else count + 1

        cpu_text = f"""
        <span style='font-size:14px;'>CPU Thread Max</span><br>
        <span style='font-size:18px;'>{self.cpu_extra_info_dict['CPU Core Max']}</span><br

        <table style='width:100%';>
            <tr>
                <td style='vertical-align:top; padding-right:25px; line-height:1.25;'>
                    {cpu_col1}
                </td>
                <td style='vertical-align:top; padding-right:25px; line-height:1.25;'>
                    {cpu_col2}
                </td>
                <td style='vertical-align:top; line-height:1.25;'>
                    {cpu_col3}
                </td>
            </tr>
        </table>
        """
        self.cpu_text_item.setHtml(cpu_text) 

    def update_gpu_info(self):
        self.gpu_extra_info_dict = self.data_parser.get_gpu_extra_info()
        self.gpu_extra_info_dict['GPU Memory Used'] = self.gpu_extra_info_dict['GPU Memory Used'].replace(" MB", "")
        gpu_col1 = "".join([
            f"<span style='font-size:14px;'>GPU Core Clock</span><br>",
            f"<span style='font-size:18px;'>{self.gpu_extra_info_dict['GPU Core']}</span><br>",
            "<span style='font-size:14px;'></span><br>",
            "<span style='font-size:14px;'>GPU Memory</span><br>",
            f"<span style='font-size:18px;'>{self.gpu_extra_info_dict['GPU Memory Used']}/{self.gpu_extra_info_dict['GPU Memory Total']}</span><br>",
            "<span style='font-size:14px;'></span><br>",
            "<span style='font-size:14px;'>D3D Memory Usage</span><br>",
            f"<span style='font-size:18px;'>{self.gpu_extra_info_dict['D3D Dedicated Memory Used']}</span><br>"
        ])

        gpu_col2 = ""
        for key, value in self.gpu_extra_info_dict.items():
            if key not in ("GPU Core", "GPU Memory Used", "GPU Memory Total", "GPU Memory"):
                if key == "GPU Fan":
                    value = value[:-1] # for some reason the GPU fan RPM is not categorised in the library
                    value = value + " RPM"
                if "D3D" not in key:
                    gpu_col2 += f"<span style='font-size:14px;'>{key}:&nbsp;&nbsp;</span><span style='font-size:14px;'>{value}</span><br>"
            
        gpu_text = f"""
        <table style='width:100%;'>
            <tr>
                <td style='vertical-align:top; padding-right:25px; line-height:1.25;'>
                    {gpu_col1}
                </td>
                <td style='vertical-align:top; line-height:1.25;'>
                    {gpu_col2}
                </td>
            </tr>
        </table>
        """
        self.gpu_text_item.setHtml(gpu_text)

    def set_up_extra_info(self):
        
        self.cpu_scene = QGraphicsScene()
        self.gpu_scene = QGraphicsScene()
        
        self.cpu_view = QGraphicsView(self.cpu_scene)
        self.gpu_view = QGraphicsView(self.gpu_scene)

        self.cpu_text_item = QGraphicsTextItem()
        self.gpu_text_item = QGraphicsTextItem()

        self.cpu_extra_info = self.data_parser.get_cpu_extra_info()
        self.gpu_extra_info = self.data_parser.get_gpu_extra_info()

        self.cpu_scene.addItem(self.cpu_text_item)
        self.gpu_scene.addItem(self.gpu_text_item)

        #self.cpu_text_item.setTextWidth(self.cpu_view.viewport().width())

        self.cpu_view.setMinimumWidth(400)
        self.gpu_view.setMinimumWidth(400)
        self.cpu_view.setMinimumHeight(200) 
        self.gpu_view.setMinimumHeight(200)

def main():
    backend_process = subprocess.Popen(
        ["dotnet", "run", "--project", resourcePath("DataCollector.csproj")], 
        creationflags=subprocess.CREATE_NO_WINDOW, 
        )
    
    app = QApplication(sys.argv)
    
    try:
        with open(resourcePath('style.qss'), 'r') as f:
            app.setStyleSheet(f.read())
    except:
        show_error_message(f"File not found: style.qss")

    window = MainWindow()
    window.show()

    def cleanup():
        try:
            backend_process.terminate() 
        except Exception as e:
            print(f"Error communicating to backend process: {e}")
    
    atexit.register(cleanup)
    sys.exit(app.exec())

def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

def show_error_message(message):
    app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText(message)
    msg.setWindowTitle("Error")
    msg.exec()

if __name__ == "__main__":
    # Pyinstaller fix
    multiprocessing.freeze_support()
    main()

