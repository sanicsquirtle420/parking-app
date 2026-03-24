from utils.lot_outlines import LotOutline
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView
from utils.buttons import Buttons
from utils.lot_cords import *
from kivy.app import App

class MainApp(App):
    def build(self):
        self.title = "University of Mississippi Parking App"
        root = BoxLayout(orientation="horizontal")
        map = MapView(zoom=15, lon=-89.538, lat=34.365, size_hint_x=0.75)

        green = (0, 0.639, 0.031, 0.45)
        grey = (0.671, 0.671, 0.671, 0.45)
        red = (1, 0, 0, 0.45)
        nw1_l = LotOutline(res_nw1, green)
        nw2_l = LotOutline(res_nw2, green)
        rd1_l = LotOutline(com_rd1, red)
        rd2_l = LotOutline(com_rd2, red)
        rd3_l = LotOutline(com_rd3, red)
        rg1_l = LotOutline(res_ga1, grey)
        root.add_widget(map)
        map.add_layer(nw1_l)
        map.add_layer(nw2_l)
        map.add_layer(rd1_l)
        map.add_layer(rd2_l)
        map.add_layer(rd3_l)
        map.add_layer(rg1_l)
        root.add_widget(Buttons(map))

        return root

if __name__ == "__main__":
    MainApp().run()