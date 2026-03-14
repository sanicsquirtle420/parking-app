from kivy_garden.mapview import MapView, MapMarker
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.app import App

Builder.load_file("parking-app.kv")

class MapScreen(Screen):
    def __init__(self, **kwargs):
        super(MapScreen, self).__init__(**kwargs)

class MainApp(App):
    def build(self):
        # m1 = MapMarker(lon=-89.5375, lat=34.3709) # Stockard Hall
        # m2 = MapMarker(lon=-89.5375, lat=34.3662) # Weir Hall
        return MapScreen(name="map_screen")

if __name__ == "__main__":
    MainApp().run()