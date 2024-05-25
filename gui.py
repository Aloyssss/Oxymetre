import dearpygui.dearpygui as dpg
import time
from collections import deque

DEQUE_MAX_LEN = 100

class Gui: 

    def __init__(self, data_y = deque(maxlen=DEQUE_MAX_LEN), data_x = deque(maxlen=DEQUE_MAX_LEN)):
        
        self.start_button = False
        self.data_y = data_y
        self.data_x = data_x
        dpg.create_context()



    def __del__(self):

        dpg.destroy_context()
        dpg.show_debug()



    def toggle_button(self, sender, data):

        self.start_button = not self.start_button

        if self.start_button :
            dpg.configure_item("start_button", label="Stop")
        else :
            dpg.configure_item("start_button", label="Start")

    

    def update_plot(self):
        dpg.configure_item('line', x=list(self.data_x), y=list(self.data_y))
        if dpg.get_value("auto_fit_checkbox"):
            dpg.fit_axis_data("xaxis")


    def init_window(self):

        with dpg.window(label="ECG"):

            ########    Creation du boutton start/stop  ##########

            with dpg.theme(tag="boutton_theme"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 255,255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 255,255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 255,255))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 25)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 18, 18)

            dpg.add_button(label="Start", callback=self.toggle_button, tag="start_button")
            dpg.bind_item_theme("start_button", "boutton_theme")

            ###########################################################


            with dpg.plot(height=400, width=500):
                dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="xaxis", time=True, no_tick_labels=True)
                dpg.add_plot_axis(dpg.mvYAxis, label="Amplitude", tag="yaxis")
                dpg.add_line_series([], [], tag='line', parent="yaxis")
                #dpg.set_axis_limits("yaxis", -1.5, 1.5)

            dpg.add_checkbox(label="Auto-fit x-axis limits", tag="auto_fit_checkbox", default_value=True)

        dpg.create_viewport(width=900, height=600, title='Updating plot data')
        dpg.setup_dearpygui()
        dpg.show_viewport()


    def start_render(self):

        while dpg.is_dearpygui_running() :
            if(self.start_button):
                self.data_x.append(time.time())
                self.update_plot()
            dpg.render_dearpygui_frame()
            
