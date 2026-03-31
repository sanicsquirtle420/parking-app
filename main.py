from utils.create_account_screen import CreateAccountScreen
from kivy.uix.screenmanager import ScreenManager, Screen
from utils.tickets_screen import TicketsScreen
from utils.login_screen import LoginScreen
from utils.lot_outlines import LotOutline
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView
from utils.buttons import Buttons
from utils.lot_cords import zones
from kivy.app import App

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="horizontal")
        map = MapView(zoom=15, lon=-89.538, lat=34.365, size_hint_x=0.75)

        for zone in zones:
            for coords in zone["lots"]:
                outline = LotOutline(coords, zone["color"])
                map.add_layer(outline)

        root.add_widget(map)
        root.add_widget(Buttons(map))

        self.add_widget(root)

    def refresh_sidebar(self):
        sidebar = self.children[0].children[0]
        sidebar.update_user_info()


class MainApp(App):
    def build(self):
        self.title = "University of Mississippi Parking App"

        self.user_data = {
            "username": "Guest",
            "role": "Visitor",
            "permit": "Visitor",
        }

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(CreateAccountScreen(name="create"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(TicketsScreen(name="tickets"))

        return sm

    def infer_permit(self, username):
        if "staff" in username.lower():
            return "Faculty/Staff"
        elif "visitor" in username.lower():
            return "Visitor"
        return "Student"


if __name__ == "__main__":
    MainApp().run()