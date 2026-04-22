from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from database.queries.admin_dashboard import get_all_lots
from utils.admin_navigation import AdminScreen
from kivy.clock import Clock
import threading
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior

OM_RED = (0.816, 0.125, 0.176, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
TEXT_DARK = (0.1, 0.1, 0.1, 1)
TEXT_MUTED = (0.35, 0.35, 0.35, 1)

class LotCard(RecycleDataViewBehavior, BoxLayout):
    lot_text = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 80
        self.padding = 12
        self.spacing = 10
        self.details.shorten = True
        self.details.max_lines = 5

        # with self.canvas.before:
        #     Color(*CARD_BG)
        #     self.rect = Rectangle(pos=self.pos, size=self.size)
        # self.bind(pos=self._update_rect, size=self._update_rect)

        self.details = Label(
            markup=False,
            color=TEXT_DARK,
            halign="left",
            valign="middle",
        )

        self.details.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        self.bind(lot_text=self.details.setter('text'))

        self.manage_btn = Button(
            text="Manage Lot",
            size_hint_x=None,
            width=140,
            background_normal="",
            background_color=OM_RED,
        )

        self.manage_btn.bind(on_release=self.on_manage_press)

        self.add_widget(self.details)
        self.add_widget(self.manage_btn)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def refresh_view_attrs(self, rv, index, data):
        self.index = index 
        utilization = data.get("utilization_pct", 0)
        
        self.lot_text = (
            f"{data['lot_name']}\n"
            f"Occupancy: {data['current_occupancy']} / {data['capacity']} ({utilization}%)\n"
            f"EV Chargers: {data['ev_charger_count']}"
        )
        return super().refresh_view_attrs(rv, index, data)

    def on_manage_press(self, instance):
        app = App.get_running_app()
        rv = self.parent.recycleview
        lot_data = rv.data[self.index]
        app.root.get_screen("admin_dashboard").open_lot_detail(lot_data)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.on_manage_press(None)
            return True
        return super().on_touch_up(touch)
        
class LotsRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = LotCard
        layout = RecycleBoxLayout(
            orientation="vertical",
            spacing=10,
            default_size=(None, 108),
            default_size_hint=(1, None),
            size_hint_y=None,
        )
        
        layout.bind(minimum_height=layout.setter('height'))
        self.layout_manager = layout
        self.add_widget(layout) 
        self.data = []   

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

        self.rv = LotsRecycleView()
        main.add_widget(self.rv)

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
        if lots is None:
            self.status_label.text = "Unable to load parking lots."
            self.rv.data = []
            return

        self.rv.data = []
        self._lot_chunks = [lots[i:i+30] for i in range(0, len(lots), 30)]
        self._load_next_chunk()

    def _load_next_chunk(self, dt=0):
        if not self._lot_chunks:
            return

        chunk = self._lot_chunks.pop(0)

        new_data = self.rv.data + chunk
        self.rv.data = new_data

        Clock.schedule_once(self._load_next_chunk, 0.02)

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
        self.manager.selected_admin_lot = lot
        if self.manager:
            self.manager.current = "admin_lot_detail"
