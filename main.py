from utils.admin_lot_detail_screen import AdminLotDetailScreen
from utils.admin_dashboard_screen import AdminDashboardScreen
from utils.admin_analytics_screen import AdminAnalyticsScreen
from utils.create_account_screen import CreateAccountScreen
from utils.admin_permits_screen import AdminPermitsScreen
from kivy.uix.screenmanager import ScreenManager, Screen
from utils.tickets_screen import TicketsScreen
from utils.login_screen import LoginScreen
from utils.lot_outlines import LotOutline
from database.queries.parking_sessions import ensure_parking_sessions_table
from database.queries.map_data import get_map_lot_lookup
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView
from utils.buttons import Buttons
from kivy.config import Config
from kivy.app import App
import signal 
import json
import os

signal.signal(signal.SIGINT, signal.SIG_DFL)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="horizontal")
        map = MapView(zoom=15, lon=-89.538, lat=34.365, size_hint_x=0.75)
        Config.set("graphics", "resizable", True)

        lot_json_path = os.path.join(os.path.dirname(__file__), "utils", "lot_cords.json")
        with open(lot_json_path) as f:
            data = json.load(f)
        lots = data["parking_lots"]
        lot_lookup = get_map_lot_lookup()

        for lot in lots:
            try:
                polygon_id = lot.get("id")
                db_lot = lot_lookup.get(polygon_id, {})
                outline = LotOutline(
                    lot["coordinates"],
                    tuple(lot["color"]),
                    info = {
                        "polygon_id": polygon_id,
                        "lot_id": db_lot.get("lot_id"),
                        "name": db_lot.get("lot_name", lot["name"]),
                        "capacity": db_lot.get("capacity", 250),
                        "current_occupancy": db_lot.get("current_occupancy", 0),
                        "permit_required": db_lot.get("zone", lot["permit"]),
                    }
                )
            except TypeError as e:
                print(f"Bad lot: {lot.get('id')} - {lot.get('name')}")
                print(f"  coordinates type: {type(lot.get('coordinates'))}")
                print(f"  first coord: {lot['coordinates'][0] if lot.get('coordinates') else 'N/A'}")
                raise

            map.add_layer(outline)

        root.add_widget(map)
        root.add_widget(Buttons(map))

        self.add_widget(root)

    def refresh_sidebar(self):
        sidebar = self.children[0].children[0]
        sidebar.update_user_info()


class MainApp(App):
    def on_stop(self):
        os.kill(os.getpid(), signal.SIGKILL)

    def build(self):
        self.title = "University of Mississippi Parking App"

        self.user_data = {
            "username": "Guest",
            "role": "Visitor",
            "permit": "Visitor",
        }
        self.active_parking_session = None

        # Ensure the parking_sessions table exists
        try:
            ensure_parking_sessions_table()
        except Exception as e:
            print(f"Warning: Could not create parking_sessions table: {e}")

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(CreateAccountScreen(name="create"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(TicketsScreen(name="tickets"))
        sm.add_widget(AdminDashboardScreen(name="admin_dashboard"))
        sm.add_widget(AdminLotDetailScreen(name="admin_lot_detail"))
        sm.add_widget(AdminPermitsScreen(name="admin_permits"))
        sm.add_widget(AdminAnalyticsScreen(name="admin_analytics"))

        return sm

    def infer_permit(self, username):
        if "staff" in username.lower():
            return "Faculty/Staff"
        elif "visitor" in username.lower():
            return "Visitor"
        return "Student"


if __name__ == "__main__":
    MainApp().run()
