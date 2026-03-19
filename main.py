from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView
from utils.buttons import Buttons
from kivy.app import App

class MainApp(App):
    def build(self):
        root = BoxLayout(orientation="horizontal")
        map = MapView(zoom=15, lon=-89.538, lat=34.365, size_hint_x=0.75)
        
        root.add_widget(map)
        root.add_widget(Buttons(map))

        return root

if __name__ == "__main__":
    MainApp().run()