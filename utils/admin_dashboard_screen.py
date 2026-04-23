from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from database.queries.admin_dashboard import get_all_lots
from database.db import run_in_background
from utils.admin_navigation import AdminScreen
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import StringProperty
import math

OM_RED = (0.816, 0.125, 0.176, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
TEXT_DARK = (0.1, 0.1, 0.1, 1)
TEXT_MUTED = (0.35, 0.35, 0.35, 1)

class AdminDashboardScreen(AdminScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Token used to cancel stale page-change deferred calls
        self._page_token = 0

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
        main.add_widget(Label(
            text="Live lot occupancy and capacity overview",
            size_hint_y=None,
            height=28,
            color=TEXT_MUTED,
            halign="left",
            valign="middle",
        ))

        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=28,
            color=TEXT_MUTED,
            halign="left",
            valign="middle",
        )
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
        main.add_widget(controls)

        self._all_lots = []
        self._page = 0
        self._page_size = 15

        self.cards_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=10,
            padding=5,
        )
        self.cards_box.bind(minimum_height=self.cards_box.setter("height"))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.cards_box)
        main.add_widget(scroll)

        self.pagination_bar = self._build_pagination_bar()
        main.add_widget(self.pagination_bar)

        root.add_widget(sidebar)
        root.add_widget(main)
        self.add_widget(root)

    def _build_pagination_bar(self):
        bar = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.prev_btn = Button(
            text="Previous",
            size_hint_x=None,
            width=120,
            background_normal="",
            background_color=OM_RED,
        )
        self.prev_btn.bind(on_release=lambda *_: self._go_page(self._page - 1))
        self.page_label = Label(text="", color=TEXT_DARK)
        self.next_btn = Button(
            text="Next",
            size_hint_x=None,
            width=120,
            background_normal="",
            background_color=OM_RED,
        )
        self.next_btn.bind(on_release=lambda *_: self._go_page(self._page + 1))
        bar.add_widget(self.prev_btn)
        bar.add_widget(self.page_label)
        bar.add_widget(self.next_btn)
        return bar

    def _go_page(self, page):
        total_pages = self._total_pages()
        if total_pages == 0:
            return
        self._page = max(0, min(page, total_pages - 1))
        self._refresh_page()

    def _total_pages(self):
        return math.ceil(len(self._all_lots) / self._page_size) if self._all_lots else 0

    def _refresh_page(self):
        self._page_token += 1

        start = self._page * self._page_size
        end = start + self._page_size
        page_slice = self._all_lots[start:end]

        total_pages = self._total_pages()
        self.page_label.text = f"Page {self._page + 1} of {total_pages}"
        self.prev_btn.disabled = (self._page == 0)
        self.next_btn.disabled = (self._page >= total_pages - 1)

        self.cards_box.clear_widgets()
        for lot in page_slice:
            self.cards_box.add_widget(self._make_card(lot))

    def _make_card(self, lot):
        utilization = float(lot.get("utilization_pct", 0))
        card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=108,
            padding=12,
            spacing=10,
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=lambda inst, val, r=rect: setattr(r, "pos", val))
        card.bind(size=lambda inst, val, r=rect: setattr(r, "size", val))

        details = Label(
            text=(
                f"{lot['lot_name']}\n"
                f"Occupancy: {lot['current_occupancy']} / {lot['capacity']} ({utilization}%)\n"
                f"EV Chargers: {lot['ev_charger_count']}"
            ),
            color=TEXT_DARK,
            halign="left",
            valign="middle",
            size_hint_x=0.8,
        )
        details.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        btn = Button(
            text="Manage Lot",
            size_hint_x=None,
            width=140,
            background_normal="",
            background_color=OM_RED,
        )
        btn.bind(on_release=lambda *_, l=lot: self.open_lot_detail(l))

        card.add_widget(details)
        card.add_widget(btn)
        return card

    def on_enter(self):
        if self._all_lots:
            self._refresh_page()
        Clock.schedule_once(lambda dt: self.load_data(), 0.2)

    def _set_loading_state(self, is_loading, is_refresh):
        if is_loading:
            self.status_label.text = "Refreshing lots..." if is_refresh else "Loading lots..."
        elif self.status_label.text.startswith(("Loading", "Refreshing")):
            self.status_label.text = ""

    def load_data(self, force=False):
        self.start_live_refresh(
            get_all_lots,
            self._apply_lots,
            self._set_loading_state,
            force=True,
        )

    def _apply_lots(self, lots):
        import threading
        # FIX: this is called on the main thread by _finish_refresh, so direct UI access is safe
        self._set_loading_state(False, False)
        print(f"DEBUG _apply_lots thread: {threading.current_thread().name}")

        if lots is None:
            self.rv.data = []
            self._all_lots = []
            self.page_label.text = ""
            return

        self._all_lots = lots
        self._page = 0
        self._refresh_page()
        print(f"DEBUG: loaded {len(lots)} lots")

    def open_lot_detail(self, lot):
        if self.manager:
            self.manager.selected_admin_lot = lot
            self.manager.current = "admin_lot_detail"