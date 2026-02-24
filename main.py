from kivy_garden.mapview import MapView, MapMarker
from kivy.app import App

class MainApp(App):
    def build(self):
        map = MapView(zoom=15,lon=-89.538, lat=34.365) # University, MS
        m1 = MapMarker(lon=-89.5375, lat=34.3709) # Stockard Hall
        m2 = MapMarker(lon=-89.5375, lat=34.3662) # Weir Hall
        map.add_marker(m1)
        map.add_marker(m2)
        return map

def main():
    MainApp().run()

if __name__ == "__main__":
    main()