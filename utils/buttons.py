from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.app import App
from datetime import datetime
from database.queries.parking_sessions import (
    end_parking_session, get_active_session
)
from database.queries.map_data import get_user_allowed_lots

BTN_HEIGHT: int = 35
LOT_ITEM_HEIGHT: int = 36

class Buttons(BoxLayout):
    def __init__(self, map: MapView, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_x = 0.25
        self.spacing = 10
        self.padding = 10
        self.map = map

        with self.canvas.before:
            Color(0.071, 0.129, 0.259, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        anchor = AnchorLayout(anchor_y="top", size_hint_y=None, height=40)
        self.title = Label(
            text="Ole Miss Parking App",
            size_hint_y=None,
            height=40,
            color=(1, 1, 1, 1),
        )
        anchor.add_widget(self.title)
        self.add_widget(anchor)

        self.user_label = Label(
            text=self.get_user_text(),
            size_hint_y=None,
            height=100,
            color=(0.7, 0.8, 1, 1),
            halign="center",
            valign="middle",
            markup=True,
            text_size=(self.width, None)
        )
        self.user_label.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
        self.add_widget(self.user_label)

        # Active session indicator
        self.session_label = Label(
            text="",
            size_hint_y=None,
            height=0,
            color=(0.5, 1, 0.5, 1),
            halign="center",
            valign="middle",
            markup=True,
        )
        self.add_widget(self.session_label)

        # End Session button (hidden when no active session)
        self.end_session_btn = Button(
            text="End Parking Session",
            size_hint_y=None,
            height=0,
            background_normal="",
            background_color=(0.8, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            opacity=0,
        )
        self.end_session_btn.bind(on_release=self._on_end_session)
        self.add_widget(self.end_session_btn)

        self.clock_label = Label(
            text=self._get_time_text(),
            size_hint_y=None,
            height=40,
            color=(0.9, 0.9, 0.5, 1),
            halign="center",
            valign="middle",
            markup=True,
        )
        self.add_widget(self.clock_label)
        Clock.schedule_interval(self._update_clock, 1)

        btn1 = Button(
            text="See Tickets",
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None,
            height=BTN_HEIGHT,
        )

        btn2 = Button(
            text="Log out",
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None,
            height=BTN_HEIGHT,
        )

        z_in = Button(
            text="Zoom In (+)",
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None,
            height=BTN_HEIGHT,
        )
        z_out = Button(
            text="Zoom Out (-)",
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None,
            height=BTN_HEIGHT,
        )

        self.add_widget(btn1)
        btn1.bind(on_press=self.go_to_tickets)
        self.add_widget(btn2)
        btn2.bind(on_press=self.go_to_login)
        z_in.bind(on_press=self.zoom_in)
        self.add_widget(z_in)
        z_out.bind(on_press=self.zoom_out)
        self.add_widget(z_out)

        # --- Available Lots section ---
        lots_header = Label(
            text="[b]Available Lots[/b]",
            markup=True,
            size_hint_y=None,
            height=28,
            color=(1, 1, 1, 1),
        )
        self.add_widget(lots_header)

        self.lot_scroll = ScrollView(size_hint=(1, 1))
        self.lot_list_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=2,
            padding=(0, 2),
        )
        self.lot_list_box.bind(minimum_height=self.lot_list_box.setter("height"))
        self.lot_scroll.add_widget(self.lot_list_box)
        self.add_widget(self.lot_scroll)

        # Load lots after a short delay to ensure DB is ready
        Clock.schedule_once(self._load_lot_list, 0.5)

    def _load_lot_list(self, dt=None):
        """Populate the sidebar lot list with only lots the user can park in.
        Uses the same permit/rules/day/time logic as the map tooltip.
        Each lot is a clickable button that pans the map to that lot.
        """
        self.lot_list_box.clear_widgets()

        app = App.get_running_app()
        user_id = app.user_data.get("user_id") if hasattr(app, "user_data") and app.user_data else None

        try:
            allowed_lots = get_user_allowed_lots(user_id)
        except Exception as e:
            print("Error loading allowed lots for sidebar:", e)
            allowed_lots = {}

        if not allowed_lots:
            no_lots = Label(
                text="No lots available\nfor your permit",
                size_hint_y=None,
                height=40,
                color=(0.6, 0.6, 0.6, 1),
                halign="center",
                markup=True,
            )
            self.lot_list_box.add_widget(no_lots)
            return

        # Sort lots by name
        sorted_lots = sorted(allowed_lots.values(), key=lambda l: l.get("lot_name", ""))

        for lot in sorted_lots:
            lot_name = lot.get("lot_name", "Unknown")
            lat = lot.get("latitude")
            lon = lot.get("longitude")

            lot_btn = Button(
                text=lot_name,
                size_hint_y=None,
                height=LOT_ITEM_HEIGHT,
                background_normal="",
                background_color=(0.15, 0.22, 0.38, 1),
                color=(0.85, 0.9, 1, 1),
                halign="left",
                valign="middle",
                font_size=13,
            )
            lot_btn.text_size = (None, None)
            lot_btn.bind(size=lambda s, w: s.setter('text_size')(s, (s.width - 10, None)))

            # Capture lat/lon for the closure
            if lat is not None and lon is not None:
                _lat = float(lat)
                _lon = float(lon)
                lot_btn.bind(
                    on_release=lambda inst, la=_lat, lo=_lon: self._pan_to_lot(la, lo)
                )

            self.lot_list_box.add_widget(lot_btn)

    def _pan_to_lot(self, lat, lon):
        """Pan and zoom the map to a specific lot."""
        self.map.center_on(lat, lon)
        if self.map.zoom < 17:
            self.map.zoom = 17

    def _on_end_session(self, instance):
        """End the active parking session from the sidebar button."""
        app = App.get_running_app()
        user_id = app.user_data.get("user_id")
        if not user_id:
            return

        success = end_parking_session(user_id)
        if success:
            print("Parking session ended (from sidebar)")
            app.active_parking_session = None
        else:
            print("Could not end session")

        self.update_user_info()

    def _get_time_text(self):
        now = datetime.now()
        return f"[b]{now.strftime('%A, %b %d')}[/b]\n{now.strftime('%I:%M:%S %p')}"

    def _update_clock(self, dt):
        self.clock_label.text = self._get_time_text()

    #DISPLAYING USERID INFORMATION
    def get_user_text(self):
        app = App.get_running_app()
        if hasattr(app, "user_data") and app.user_data:
            u = app.user_data
            name = u.get('username', 'User')
            email = u.get('email', '')
            permit = u.get('permit', 'No Permit')

            return f"[b][size=40]{name}[/size][/b]\n{email}\n{permit}"
        return "Guest\nNo Email\nVisitor"

    def _update_session_label(self):
        """Update the session indicator and end-session button."""
        app = App.get_running_app()
        user_id = app.user_data.get("user_id") if hasattr(app, "user_data") and app.user_data else None

        if not user_id:
            self.session_label.text = ""
            self.session_label.height = 0
            self.end_session_btn.height = 0
            self.end_session_btn.opacity = 0
            return

        active = getattr(app, "active_parking_session", None)
        if not active:
            try:
                active = get_active_session(user_id)
                if active:
                    app.active_parking_session = active
            except Exception:
                pass

        if active:
            lot_name = active.get("lot_name", "Unknown")
            start = active.get("start_time", "")
            self.session_label.text = f"[b]Parked:[/b] {lot_name}\nSince: {start}"
            self.session_label.height = 40
            self.end_session_btn.height = BTN_HEIGHT
            self.end_session_btn.opacity = 1
        else:
            self.session_label.text = ""
            self.session_label.height = 0
            self.end_session_btn.height = 0
            self.end_session_btn.opacity = 0

    def refresh_user(self):
        self.user_label.text = self.get_user_text()

    def update_user_info(self):
        self.refresh_user()
        self._update_session_label()
        self._load_lot_list()

    def go_to_login(self, instance):
        app = App.get_running_app()
        app.user_data = {}
        app.active_parking_session = None

        login_screen = app.root.get_screen("login")
        create_screen = app.root.get_screen("create")

        if hasattr(login_screen, "reset_fields"):
            login_screen.reset_fields()

        if hasattr(create_screen, "reset_fields"):
            create_screen.reset_fields()

        app.root.current = "login"

    def on_parent(self, *args):
         self.refresh_user()
         self._update_session_label()

    def zoom_in(self, instance):
        self.map.zoom += 1

    def zoom_out(self, instance):
        self.map.zoom -= 1

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_to_tickets(self, instance):
        print("Button clicked!")
        app = App.get_running_app()
        app.root.current = "tickets"