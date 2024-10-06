import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QLabel
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import requests
import pandas as pd
from io import StringIO
from PyQt5.QtWidgets import QFileDialog


def export_star_chart(self):
    file_path, _ = QFileDialog.getSaveFileName(self, "Save Star Chart", "", "PNG Files (*.png);;JPEG Files (*.jpg)")

    if file_path:
        self.chart_canvas.figure.savefig(file_path, dpi=300)  # Export the chart as an image


def fetch_exoplanet_data():
    api_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

    query = """
    SELECT pl_name, hostname, ra, dec, st_dist
    FROM ps
    WHERE pl_name IS NOT NULL
    """

    params = {
        "query": query,
        "format": "csv"
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = pd.read_csv(StringIO(response.text))
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None

class StarChartCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111, projection='mollweide')
        super().__init__(fig)
        self.setParent(parent)

    def plot_star_chart(self, exoplanets):
        self.axes.clear()  

        ra = np.radians(exoplanets['ra'])
        dec = np.radians(exoplanets['dec'])

        self.axes.scatter(ra, dec, color='yellow', s=10, label='Exoplanets')  # Customize marker size/color

        self.axes.grid(True)
        self.axes.set_title('Star Chart with Exoplanets', fontsize=12)

        self.draw() 

class ExoplanetApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Exoplanet Explorer")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.info_label = QLabel("Select an exoplanet and show its star chart.", self)
        self.layout.addWidget(self.info_label)

        self.planet_dropdown = QComboBox(self)
        self.layout.addWidget(self.planet_dropdown)

        self.show_chart_button = QPushButton('Show Star Chart', self)
        self.show_chart_button.clicked.connect(self.show_star_chart)
        self.layout.addWidget(self.show_chart_button)

        self.chart_canvas = StarChartCanvas(self)
        self.layout.addWidget(self.chart_canvas)

        self.exoplanet_data = fetch_exoplanet_data()
        if self.exoplanet_data is not None:
            self.populate_planet_dropdown()

    def populate_planet_dropdown(self):
        self.planet_dropdown.addItems(self.exoplanet_data['pl_name'].tolist())

    def show_star_chart(self):
        selected_planet_name = self.planet_dropdown.currentText()

        selected_planet = self.exoplanet_data[self.exoplanet_data['pl_name'] == selected_planet_name]

        self.chart_canvas.plot_star_chart(self.exoplanet_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExoplanetApp()
    window.show()
    sys.exit(app.exec_())
