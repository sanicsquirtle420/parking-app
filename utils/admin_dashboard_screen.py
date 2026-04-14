from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from database.queries.admin_dashboard import get_all_lots
from utils.admin_navigation import AdminScreen


OM_RED = (0.816, 0.125, 0.176, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
TEXT_DARK = (0.1, 0.1, 0.1, 1)
TEXT_MUTED = (0.35, 0.35, 0.35, 1)


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

        self.lots_box = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None,
        )
        self.lots_box.bind(minimum_height=self.lots_box.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.lots_box)
        main.add_widget(scroll)

        root.add_widget(sidebar)
        root.add_widget(main)
        self.add_widget(root)

    def on_pre_enter(self):
        self.load_data(force=True)

    def _set_loading_state(self, is_loading, is_refresh):
        if is_loading:
            self.status_label.text = "Refreshing lots..." if is_refresh else "Loading lots..."
            if not self.lots_box.children:
                self.lots_box.clear_widgets()
                self.lots_box.add_widget(Label(
                    text="Loading lots...",
                    size_hint_y=None,
                    height=50,
                    color=TEXT_MUTED,
                ))
            return

        if self.status_label.text.startswith("Loading") or self.status_label.text.startswith("Refreshing"):
            self.status_label.text = ""

    def _apply_lots(self, lots):
        self.lots_box.clear_widgets()

        if lots is None:
            self.status_label.text = "Unable to load parking lots."
            return

        if not lots:
            self.lots_box.add_widget(Label(
                text="No lots found.",
                size_hint_y=None,
                height=50,
                color=TEXT_MUTED,
            ))
            return

        for lot in lots:
            self.lots_box.add_widget(self.build_lot_card(lot))

    def load_data(self, force=False):
        self.start_live_refresh(
            get_all_lots,
            self._apply_lots,
            self._set_loading_state,
            force=force,
        )

    def build_lot_card(self, lot):
        card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=108,
            padding=12,
            spacing=10,
        )

        with card.canvas.before:
            Color(*CARD_BG)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self.update_rect, size=self.update_rect)

        utilization_pct = lot.get("utilization_pct") or 0
        details = Label(
            text=(
                f"[b]{lot['lot_name']}[/b]\n"
                f"Occupancy: {lot['current_occupancy']} / {lot['capacity']} ({utilization_pct}%)\n"
                f"EV Chargers: {lot['ev_charger_count']}"
            ),
            markup=True,
            color=TEXT_DARK,
            halign="left",
            valign="middle",
        )
        details.bind(size=self.update_label_text_size)

        manage_btn = Button(
            text="Manage Lot",
            size_hint_x=None,
            width=140,
            background_normal="",
            background_color=OM_RED,
        )
        manage_btn.bind(on_release=lambda *_: self.open_lot_detail(lot))

        card.add_widget(details)
        card.add_widget(manage_btn)
        return card

    def open_lot_detail(self, lot):
        App.get_running_app().selected_admin_lot = lot
        if self.manager:
            self.manager.current = "admin_lot_detail"
