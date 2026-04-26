from kivy.app import App
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from database.queries.admin_dashboard import get_all_lots
from utils.admin_navigation import AdminScreen
from kivy.clock import Clock
import threading

OM_RED = (0.816, 0.125, 0.176, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
TEXT_DARK = (0.1, 0.1, 0.1, 1)
TEXT_MUTED = (0.35, 0.35, 0.35, 1)


def _make_lot_card(lot_data, on_manage):
    """Build one lot card as a plain BoxLayout."""
    utilization = lot_data.get("utilization_pct", 0)
    card_text = (
        f"{lot_data['lot_name']}\n"
        f"Occupancy: {lot_data['current_occupancy']} / {lot_data['capacity']} ({utilization}%)\n"
        f"EV Chargers: {lot_data['ev_charger_count']}"
    )

    card = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=90,
        padding=12,
        spacing=10,
    )

    with card.canvas.before:
        Color(*CARD_BG)
        card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[6])
    card.bind(
        pos=lambda inst, val: setattr(inst._bg, "pos", val),
        size=lambda inst, val: setattr(inst._bg, "size", val),
    )

    details = Label(
        text=card_text,
        color=TEXT_DARK,
        halign="left",
        valign="middle",
    )
    details.bind(size=lambda inst, val: setattr(inst, "text_size", val))

    manage_btn = Button(
        text="Manage Lot",
        size_hint_x=None,
        width=140,
        background_normal="",
        background_color=OM_RED,
    )
    manage_btn.bind(on_release=lambda inst: on_manage(lot_data))

    card.add_widget(details)
    card.add_widget(manage_btn)
    return card


class AdminDashboardScreen(AdminScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="horizontal")

        sidebar = self.build_admin_sidebar(
            active_screen="admin_dashboard",
            section_label="Dashboard",
        )

        main = BoxLayout(orientation="vertical", padding=20, spacing=12)

        with main.canvas.before:
            Color(*LIGHT_BG)
            main.rect = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=self.update_rect, size=self.update_rect)

        main.add_widget(Label(
            text="Parking Dashboard",
            font_size=26,
            size_hint_y=None,
            height=50,
            color=TEXT_DARK,
        ))

        subtitle = Label(
            text="Live lot occupancy and capacity overview",
            size_hint_y=None,
            height=28,
            color=TEXT_MUTED,
            halign="left",
            valign="middle",
        )
        subtitle.bind(size=self.update_label_text_size)
        main.add_widget(subtitle)

        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=28,
            color=TEXT_MUTED,
            halign="left",
            valign="middle",
        )
        self.status_label.bind(size=self.update_label_text_size)
        main.add_widget(self.status_label)

        controls = BoxLayout(size_hint_y=None, height=45, spacing=10)
        refresh_btn = Button(
            text="Refresh",
            size_hint_x=None,
            width=120,
            background_normal="",
            background_color=OM_RED,
        )
        refresh_btn.bind(on_release=lambda *_: self.load_data(force=True))
        controls.add_widget(refresh_btn)
        controls.add_widget(Label())
        main.add_widget(controls)

        self.lot_list = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.lot_list.bind(minimum_height=self.lot_list.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.lot_list)
        main.add_widget(scroll)

        root.add_widget(sidebar)
        root.add_widget(main)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_data(), 0.2)

    def _set_loading_state(self, is_loading, is_refresh):
        if is_loading:
            self.status_label.text = "Refreshing lots..." if is_refresh else "Loading lots..."
            return
        if self.status_label.text.startswith(("Loading", "Refreshing")):
            self.status_label.text = ""

    def _apply_lots(self, lots):
        self.lot_list.clear_widgets()

        if lots is None:
            self.status_label.text = "Unable to load parking lots."
            return

        if not lots:
            self.status_label.text = "No lots found."
            return

        self.status_label.text = f"{len(lots)} lots loaded"
        for lot in lots:
            card = _make_lot_card(lot, self.open_lot_detail)
            self.lot_list.add_widget(card)

    def _bg_load_lots(self):
        import time
        start = time.time()
        try:
            lots = get_all_lots()
            Clock.schedule_once(lambda dt: self._apply_lots(lots))
        except Exception as e:
            print(f"Database Error: {e}")
            Clock.schedule_once(lambda dt: self._apply_lots(None))
        finally:
            print(f"Lot load time: {time.time() - start:.2f} seconds")
            Clock.schedule_once(lambda dt: self._set_loading_state(False, False))

    def load_data(self, force=False):
        self._set_loading_state(True, force)
        threading.Thread(target=self._bg_load_lots, daemon=True).start()

    def open_lot_detail(self, lot):
        App.get_running_app().selected_admin_lot = lot
        if self.manager:
            self.manager.current = "admin_lot_detail"
