import sys
import psutil
import numpy as np
import time
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame)
from PyQt6.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Theme Definitions
THEMES = {
    'dark': {
        'bg': '#121212',
        'card': '#1E1E1E',
        'accent': '#00B4D8',
        'text': '#E0E0E0',
        'subtext': '#888888',
        'chart_fill': '#00B4D844',
        'chart_line': '#00B4D8'
    },
    'light': {
        'bg': '#F8F9FA',
        'card': '#FFFFFF',
        'accent': '#0077B6',
        'text': '#212529',
        'subtext': '#6C757D',
        'chart_fill': '#0077B633',
        'chart_line': '#0077B6'
    }
}

class CPUChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, theme='dark'):
        self.current_theme = theme
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        # Initialize base class first
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.axes = self.fig.add_subplot(111)
        self.x_data = []
        self.y_data = []
        self.line, = self.axes.plot([], [], color=THEMES[theme]['chart_line'], linewidth=2.5)
        self.fill = None
        
        self.apply_theme(theme)
        
        self.axes.set_ylim(0, 100)
        self.axes.set_ylabel("CPU Usage (%)", fontsize=10)
        self.axes.set_xlabel("Time Progress (s)", fontsize=10)

    def apply_theme(self, theme):
        self.current_theme = theme
        colors = THEMES[theme]
        self.fig.patch.set_facecolor(colors['bg'])
        self.axes.set_facecolor(colors['bg'])
        self.axes.tick_params(colors=colors['text'], labelsize=9)
        self.axes.xaxis.label.set_color(colors['subtext'])
        self.axes.yaxis.label.set_color(colors['subtext'])
        
        for spine in self.axes.spines.values():
            spine.set_edgecolor('#333333' if theme == 'dark' else '#DDDDDD')
            
        if hasattr(self, 'line'):
            self.line.set_color(colors['chart_line'])
        self.draw()

    def update_chart(self, x, y):
        self.x_data.append(x)
        self.y_data.append(y)
        
        if len(self.x_data) > 60:
            # Keep rolling window
            self.x_data.pop(0)
            self.y_data.pop(0)
            
        self.line.set_data(self.x_data, self.y_data)
        
        if len(self.x_data) > 1:
            self.axes.set_xlim(min(self.x_data), max(self.x_data))
        else:
            self.axes.set_xlim(0, 1)
            
        # Robustly manage shaded area
        if self.fill is not None:
            try:
                self.fill.remove()
            except:
                pass
            self.fill = None
            
        if self.x_data:
            self.fill = self.axes.fill_between(self.x_data, self.y_data, color=THEMES[self.current_theme]['chart_fill'])
        
        self.draw()

class CPUAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = 'dark'
        self.setWindowTitle("CPU Area Calculator")
        
        # Lock window size to preserve layout
        self.setFixedSize(1100, 780)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        
        # Internal State
        self.start_time = time.time()
        self.total_area = 0.0
        self.last_cpu = 0.0
        self.last_time = 0.0
        self.is_running = True
        
        self.setup_ui()
        self.apply_theme_to_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def setup_ui(self):
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(30)
        
        # Header Group
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        
        self.header_title = QLabel("CPU REAL-TIME INTEGRAL ANALYSIS")
        self.header_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_title.setStyleSheet("font-size: 34px; font-weight: 900; letter-spacing: -1px;")
        
        self.header_subtitle = QLabel("NUMERICAL INTEGRATION USING TRAPEZOIDAL RULE")
        self.header_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_subtitle.setStyleSheet("font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 3px;")
        
        header_layout.addWidget(self.header_title)
        header_layout.addWidget(self.header_subtitle)
        self.main_layout.addWidget(header_container)

        # Dashboard Grid (Stats)
        stats_layout = QHBoxLayout()
        self.area_card = self.create_stat_card("TOTAL COMPUTED AREA", "0.00", "%·s")
        self.cpu_card = self.create_stat_card("CURRENT WORKLOAD", "0.0", "%")
        stats_layout.addWidget(self.area_card)
        stats_layout.addWidget(self.cpu_card)
        self.main_layout.addLayout(stats_layout)
        
        # Chart Display
        chart_frame = QFrame()
        chart_frame.setObjectName("chart_frame")
        chart_layout = QVBoxLayout(chart_frame)
        self.canvas = CPUChart(self, theme=self.current_theme)
        chart_layout.addWidget(self.canvas)
        self.main_layout.addWidget(chart_frame)
        
        # Action Bar
        footer = QHBoxLayout()
        
        self.theme_btn = QPushButton("🌙 DARK MODE")
        self.theme_btn.setFixedSize(160, 45)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        self.toggle_btn = QPushButton("PAUSE MONITORING")
        self.toggle_btn.setFixedSize(220, 45)
        self.toggle_btn.clicked.connect(self.toggle_monitoring)
        
        self.reset_btn = QPushButton("RESET CALCULATION")
        self.reset_btn.setFixedSize(200, 45)
        self.reset_btn.clicked.connect(self.reset_calculation)
        
        footer.addWidget(self.theme_btn)
        footer.addStretch()
        footer.addWidget(self.toggle_btn)
        footer.addWidget(self.reset_btn)
        self.main_layout.addLayout(footer)
        
        self.setCentralWidget(main_widget)

    def create_stat_card(self, title, value, unit):
        frame = QFrame()
        frame.setObjectName("stat_card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 25, 25, 25)
        
        t_lbl = QLabel(title)
        t_lbl.setObjectName("card_title")
        
        h_layout = QHBoxLayout()
        v_lbl = QLabel(value)
        v_lbl.setObjectName("card_value")
        u_lbl = QLabel(unit)
        u_lbl.setObjectName("card_unit")
        u_lbl.setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        h_layout.addWidget(v_lbl)
        h_layout.addWidget(u_lbl)
        h_layout.addStretch()
        
        layout.addWidget(t_lbl)
        layout.addLayout(h_layout)
        return frame

    def apply_theme_to_ui(self):
        colors = THEMES[self.current_theme]
        is_dark = self.current_theme == 'dark'
        
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                font-family: 'Segoe UI', Roboto, Helvetica, Sans-Serif;
            }}
            QLabel {{ background-color: transparent; }}
            #stat_card {{ 
                background-color: {colors['card']}; 
                border-radius: 20px; 
                border: 1px solid {'#333' if is_dark else '#E9ECEF'}; 
            }}
            #card_title {{ color: {colors['subtext']}; font-size: 11px; font-weight: 700; }}
            #card_value {{ color: {colors['accent']}; font-size: 46px; font-weight: 800; }}
            #card_unit {{ color: {colors['subtext']}; font-size: 16px; font-weight: 600; padding-bottom: 8px; }}
            #chart_frame {{
                background-color: {colors['card']};
                border-radius: 20px;
                padding: 10px;
                border: 1px solid {'#2A2A2A' if is_dark else '#EEE'};
            }}
            QPushButton {{ 
                background-color: {colors['card'] if is_dark else '#FFF'}; 
                color: {colors['text']}; 
                border-radius: 10px; 
                border: 1px solid {'#333' if is_dark else '#DEE2E6'};
                font-weight: 700;
                font-size: 11px;
            }}
            QPushButton:hover {{ 
                background-color: {'#252525' if is_dark else '#F8F9FA'}; 
                border: 1px solid {colors['accent']};
            }}
        """)
        
        self.theme_btn.setText("☀️ LIGHT MODE" if is_dark else "🌙 DARK MODE")
        
        # Dynamic button color for status
        if self.is_running:
            self.toggle_btn.setStyleSheet(f"background-color: {colors['accent']}; color: white; border: none; border-radius: 10px; font-weight: 800;")
        else:
            self.toggle_btn.setStyleSheet("background-color: #E63946; color: white; border: none; border-radius: 10px; font-weight: 800;")

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme_to_ui()
        self.canvas.apply_theme(self.current_theme)

    def update_stats(self):
        if not self.is_running:
            return
            
        current_cpu = psutil.cpu_percent()
        current_time = time.time() - self.start_time
        
        if self.last_time > 0:
            dt = current_time - self.last_time
            delta_area = (self.last_cpu + current_cpu) / 2.0 * dt
            self.total_area += delta_area
            
        self.last_cpu = current_cpu
        self.last_time = current_time
        
        cpu_val = self.cpu_card.findChild(QLabel, "card_value")
        area_val = self.area_card.findChild(QLabel, "card_value")
        
        if cpu_val: cpu_val.setText(f"{current_cpu:.1f}")
        if area_val: area_val.setText(f"{self.total_area:.2f}")
        
        self.canvas.update_chart(current_time, current_cpu)

    def toggle_monitoring(self):
        self.is_running = not self.is_running
        self.apply_theme_to_ui()
        self.toggle_btn.setText("PAUSE MONITORING" if self.is_running else "RESUME MONITORING")

    def reset_calculation(self):
        # Numerical Reset
        self.total_area = 0.0
        self.start_time = time.time()
        self.last_time = 0.0
        self.last_cpu = 0.0
        
        # Label Reset
        cpu_val = self.cpu_card.findChild(QLabel, "card_value")
        area_val = self.area_card.findChild(QLabel, "card_value")
        if cpu_val: cpu_val.setText("0.0")
        if area_val: area_val.setText("0.00")
        
        # Graph Reset
        self.canvas.x_data = []
        self.canvas.y_data = []
        
        if self.canvas.fill is not None:
            try:
                self.canvas.fill.remove()
            except:
                pass
            self.canvas.fill = None
            
        self.canvas.line.set_data([], [])
        self.canvas.axes.set_xlim(0, 1)
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CPUAnalyzer()
    window.show()
    sys.exit(app.exec())
