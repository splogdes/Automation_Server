from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from kivy.clock import Clock
from kivy.uix.slider import Slider
from matplotlib.figure import Figure
from functools import partial
from datetime import datetime
from json_to_db import DataBase
from udp_server import client_handler
import sys

def get_data(device, sname, type, db, duration=4):
    data = db.get_data(device, sname, type, duration)
    x = [datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S') for x in data]
    y = [x[0] for x in data]
    return x, y

class SensorApp(App):
    def build(self):
        self.db = DataBase()

        # Main layout with top bar and graph area
        self.main_layout = BoxLayout(orientation='vertical')

        # Graph container
        self.graph_container = BoxLayout(orientation='vertical')
        self.graph_container.bind(on_touch_down=self.handle_click)
        self.main_layout.add_widget(self.graph_container)

        return self.main_layout
    
    def handle_click(self, instance, touch):
        """Handle left-click to add a graph."""
        if touch.button == 'left' and self.graph_container.collide_point(*touch.pos):
            # Open the graph configuration popup
            self.open_add_graph_popup(None)
            
        if touch.button == 'right' and self.graph_container.collide_point(*touch.pos):
            # Remove the last graph
            self.graph_container.remove_widget(self.graph_container.children[-1])

    def open_add_graph_popup(self, _):
        """Open a popup to configure a new graph."""
        content = GridLayout(cols=2, spacing=10, padding=10)

        # Dropdown for selecting device
        content.add_widget(Label(text="Device:"))
        device_spinner = Spinner(
            text="Select Device",
            values=[device[0] for device in self.db.get_devices()],  # Extract MAC addresses
        )
        content.add_widget(device_spinner)

        # Dropdown for selecting sensor
        content.add_widget(Label(text="Sensor:"))
        sensor_spinner = Spinner(text="Select Sensor")
        content.add_widget(sensor_spinner)

        # Dropdown for selecting mode
        content.add_widget(Label(text="Mode:"))
        mode_spinner = Spinner(text="Select Mode")
        content.add_widget(mode_spinner)

        # Slider for selecting duration
        content.add_widget(Label(text="Duration (hours):"))
        duration_slider = Slider(min=1, max=40000, value=30000, step=10000)
        content.add_widget(duration_slider)

        # Update the sensors dynamically based on the selected device
        def update_sensors(_, value):
            if value and value != "Select Device":
                sensors = [sensor[0] for sensor in self.db.get_sensors(value)]
                sensor_spinner.values = sensors if sensors else ["No Sensors Found"]
                sensor_spinner.text = "Select Sensor"

        device_spinner.bind(text=update_sensors)

        # Update modes dynamically based on the selected sensor
        def update_modes(_, value):
            if value and value != "Select Sensor":
                modes = [mode[0] for mode in self.db.get_sensor_modes(value)]
                mode_spinner.values = modes if modes else ["No Modes Found"]
                mode_spinner.text = "Select Mode"

        sensor_spinner.bind(text=update_modes)

        # Buttons
        button_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        add_btn = Button(text="Add")
        cancel_btn = Button(text="Cancel")
        button_layout.add_widget(add_btn)
        button_layout.add_widget(cancel_btn)

        # Popup
        popup_content = BoxLayout(orientation="vertical")
        popup_content.add_widget(content)
        popup_content.add_widget(button_layout)

        popup = Popup(title="Add New Graph", content=popup_content, size_hint=(0.8, 0.6))

        # Button bindings
        add_btn.bind(
            on_press=lambda _: self.add_graph(
                device_spinner.text,
                sensor_spinner.text,
                mode_spinner.text,
                duration_slider.value,
                popup,
            )
        )
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def add_graph(self, device, sensor, mode, duration, popup):
        """Add a new graph to the graph container."""
        if (
            device == "Select Device"
            or sensor == "Select Sensor"
            or mode == "Select Mode"
        ):
            self.show_error_popup("Please select valid device, sensor, and mode!")
            return

        # Close popup
        popup.dismiss()

        # Create new graph figure
        fig, axs, lines = self.setup_figure([sensor], f"{device} - {sensor} ({mode})")

        # Add to the graph container
        self.graph_container.add_widget(FigureCanvasKivyAgg(fig))

        # Schedule updates for the new graph
        Clock.schedule_interval(
            partial(self.update_graph, axs, lines, [sensor], device, mode, duration), 1
        )
        
        self.update_graph(axs, lines, [sensor], device, mode, duration, 1)

    def setup_figure(self, sensors, title):
        """Set up a matplotlib figure with subplots for a list of sensors."""
        fig = Figure()
        axes = []
        lines = []

        for sensor in sensors:
            ax = fig.add_subplot(len(sensors), 1, len(axes) + 1)
            ax.set_title(sensor)
            axes.append(ax)
            lines.append(ax.plot([], [])[0])  # Initialize an empty line

        fig.suptitle(title)
        return fig, axes, lines

    def update_graph(self, axs, lines, sensors, device, mode, duration, _):
        """Update a graph with new data."""
        for i, sensor in enumerate(sensors):
            x, y = get_data(device, sensor, mode, self.db, duration)
            lines[i].set_xdata(x)
            lines[i].set_ydata(y)
            axs[i].relim()
            axs[i].autoscale_view()
            axs[i].figure.canvas.draw()

    def show_error_popup(self, message):
        """Show an error popup."""
        popup = Popup(title="Error", content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

if __name__ == "__main__":        
    SensorApp().run()
