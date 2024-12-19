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
from kivy.core.window import Window
from kivy.input.providers.mtdev import MTDMotionEvent
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from functools import partial
from datetime import datetime
from json_to_db import DataBase


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
        self.graph_container.bind(on_touch_down=self.on_touch_down)
        self.main_layout.add_widget(self.graph_container)
        
        self.double_tap_detected = False

        return self.main_layout
    
    def on_touch_down(self, instance, touch):
        
        if type(touch) != MTDMotionEvent:
            return False
        
        if touch.is_double_tap:
            self.double_tap_detected = True
            # Cancel any pending single tap callbacks
            Clock.unschedule(self.handle_single_tap)
            self.handle_double_tap(instance, touch)
        else:
            self.double_tap_detected = False
            # Schedule single tap handling
            Clock.schedule_once(lambda dt: self.handle_single_tap(instance, touch), 0.3)

    def handle_single_tap(self, instance, touch):
        if not self.double_tap_detected:
            self.open_add_graph_popup(None)

    def handle_double_tap(self, instance, touch):
        # Find the graph widget under the touch position
        for widget in self.graph_container.children:
            if widget.collide_point(*touch.pos):
                self.graph_container.remove_widget(widget)

    def handle_click_popup(self, instance, touch):
        """Handle clicks on the popup."""
        if type(touch) == MTDMotionEvent:
            return False
        return True

    def open_add_graph_popup(self, _):
        """Open a popup to configure a new graph."""
        content = GridLayout(cols=2, spacing=10, padding=10)
        content.bind(on_touch_down=self.handle_click_popup)
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
        duration_slider = Slider(min=1, max=240, value=12, step=1)
        duration_label = Label(text=f"Duration (hours): {int(duration_slider.value)}")
        content.add_widget(duration_label)
        content.add_widget(duration_slider)

        # Update the label when the slider value changes
        def update_duration_label(instance, value):
            duration_label.text = f"Duration (hours): {int(value)}"

        duration_slider.bind(value=update_duration_label)

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
                model = self.db.get_sensor_model(value)[0]
                modes = [mode[0] for mode in self.db.get_sensor_modes(model)]
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
        self.add_graph_called = False
        def on_add_btn_press(_):
            if not self.add_graph_called:
                self.add_graph_called = True
                self.add_graph(
                    device_spinner.text,
                    sensor_spinner.text,
                    mode_spinner.text,
                    duration_slider.value,
                    popup,
                )

        add_btn.bind(on_press=on_add_btn_press)

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

        # Get units for the sensor
        model = self.db.get_sensor_model(sensor)[0]
        unit = self.db.get_sensor_unit(model, mode)[0]

        # Create new graph figure
        plt.style.use('dark_background')
        fig, axs = plt.subplots()
        axs.set_title(sensor)
        axs.set_xlabel("Time")
        axs.set_ylabel(f"{mode} ({unit})")
        axs.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        axs.xaxis.grid(False)
        axs.yaxis.grid(True, color='grey')
        fig.autofmt_xdate()
        fig.tight_layout()
        
        # Create a line for the graph
        line = axs.plot([], [], label=sensor)

        # Add to the graph container
        self.graph_container.add_widget(FigureCanvasKivyAgg(fig))

        self.update_graph(axs, line, sensor, device, mode, duration, 1)
        
        # Schedule updates for the new graph
        Clock.schedule_interval(
            partial(self.update_graph, axs, line, sensor, device, mode, duration), 1
        )
        

    def update_graph(self, axs, line, sensor, device, mode, duration, _):
        """Update a graph with new data."""
        x, y = get_data(device, sensor, mode, self.db, duration)
        line[0].set_data(x, y)
        axs.relim()
        axs.autoscale_view()  # Ensure the data fits well within the plot
        axs.figure.canvas.draw()

    def show_error_popup(self, message):
        """Show an error popup."""
        popup = Popup(title="Error", content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

if __name__ == "__main__":
    Window.fullscreen = True
    Window.show_cursor = False
    Window.size = (1920, 1080)
    SensorApp().run()