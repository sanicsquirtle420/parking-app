from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from database.queries.admin_analytics import get_analytics_data
from utils.admin_navigation import AdminScreen
import threading
from kivy.clock import Clock


OM_RED = (0.816, 0.125, 0.176, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
TEXT_DARK = (0.1, 0.1, 0.1, 1)
TEXT_MUTED = (0.35, 0.35, 0.35, 1)
GREEN = (0, 0.6, 0, 1)
ORANGE = (1, 0.6, 0.1, 1)
RED = (1, 0, 0, 1)
BLUE = (0.2, 0.45, 0.85, 1)


class AdminAnalyticsScreen(AdminScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="horizontal")

        self.sidebar_container = BoxLayout(size_hint_x=0.25)
        self.refresh_sidebar()
        root.add_widget(self.sidebar_container)

        main = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15,
        )

        with main.canvas.before:
            Color(*LIGHT_BG)
            main.rect = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=self.update_rect, size=self.update_rect)

        title = Label(
            text="Parking Analytics",
            font_size=26,
            size_hint_y=None,
            height=50,
            color=TEXT_DARK,
        )
        main.add_widget(title)

        subtitle = Label(
            text="Read-only analytics from live parking and occupancy-log data",
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

        self.content = BoxLayout(
            orientation="vertical",
            spacing=14,
            size_hint_y=None,
        )
        self.content.bind(minimum_height=self.content.setter("height"))

        self.content.add_widget(self.build_overview_section())
        self.content.add_widget(self.build_list_section("Peak Occupancy", "peak_box"))
        self.content.add_widget(self.build_list_section("EV Utilization", "ev_box"))
        self.content.add_widget(self.build_list_section("Overloaded Lots", "overloaded_box"))
        self.content.add_widget(self.build_list_section("Underutilized Lots", "underutilized_box"))

        scroll = ScrollView()
        scroll.add_widget(self.content)
        main.add_widget(scroll)

        # root.add_widget(sidebar)
        root.add_widget(main)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.start_live_refresh(
            get_analytics_data,
            self._apply_data,
            self._set_loading_state
        ), 0.2)

    def _set_loading_state(self, is_loading, is_refresh):
        if is_loading:
            self.status_label.text = "Refreshing analytics..." if is_refresh else "Loading analytics..."
            return

        self.status_label.text = ""

    def _apply_data(self, data):
        if not data:
            return

        overview = data["overview"]
        self.total_lots_label.text = str(overview["total_lots"] or 0)
        self.critical_lots_label.text = str(overview["critical_lots"] or 0)
        self.avg_util_label.text = f"{overview['avg_utilization'] or 0}%"
        self.no_ev_label.text = str(overview["no_ev"] or 0)

        # Clear existing
        self.peak_box.clear_widgets()
        self.ev_box.clear_widgets()
        self.overloaded_box.clear_widgets()
        self.underutilized_box.clear_widgets()

        def add_item(box, text, color):
            box.add_widget(Label(
                text=text, color=color, halign="left", valign="middle",
                size_hint_y=None, height=30
            ))

        for p in data.get("peak", []):
            add_item(self.peak_box, f"{p['lot_name']}: Peak {p['peak_occupancy']}", TEXT_DARK)

        for e in data.get("ev", []):
            add_item(self.ev_box, f"{e['lot_name']} - Chargers: {e['ev_charger_count']}", TEXT_DARK)

        for l in data.get("overloaded", []):
            add_item(self.overloaded_box, f"{l['lot_name']} ({l['utilization']}%)", RED)

        for l in data.get("underutilized", []):
            add_item(self.underutilized_box, f"{l['lot_name']} ({l['utilization']}%)", GREEN)

    def build_overview_section(self):
        section = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None,
        )
        section.bind(minimum_height=section.setter("height"))

        section.add_widget(self.build_section_title("Overview"))

        row = GridLayout(
            cols=4,
            spacing=12,
            size_hint_y=None,
            height=110,
        )

        row.add_widget(self.build_summary_card("Total Lots", "total_lots_label", BLUE))
        row.add_widget(self.build_summary_card("Critical Lots", "critical_lots_label", RED))
        row.add_widget(self.build_summary_card("Avg Utilization", "avg_util_label", ORANGE))
        row.add_widget(self.build_summary_card("No EV Chargers", "no_ev_label", GREEN))

        section.add_widget(row)
        return section

    def build_list_section(self, title, box_name):
        section = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None,
        )
        section.bind(minimum_height=section.setter("height"))

        section.add_widget(self.build_section_title(title))

        card = self.build_card()
        box = BoxLayout(
            orientation="vertical",
            spacing=6,
            size_hint_y=None,
        )
        box.bind(minimum_height=box.setter("height"))
        setattr(self, box_name, box)
        card.add_widget(box)
        section.add_widget(card)

        return section

    def build_section_title(self, text):
        label = Label(
            text=text,
            font_size=20,
            bold=True,
            color=TEXT_DARK,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=34,
        )
        label.bind(size=self.update_label_text_size)
        return label

    def build_summary_card(self, title, value_attr, accent_color):
        card = BoxLayout(
            orientation="vertical",
            padding=12,
            spacing=6,
        )

        with card.canvas.before:
            Color(*CARD_BG)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self.update_rect, size=self.update_rect)

        accent = Label(
            text="|",
            color=accent_color,
            size_hint_y=None,
            height=20,
        )

        title_label = Label(
            text=title,
            color=TEXT_MUTED,
            halign="center",
            valign="middle",
        )
        title_label.bind(size=self.update_label_text_size)

        value_label = Label(
            text="0",
            font_size=22,
            bold=True,
            color=TEXT_DARK,
            halign="center",
            valign="middle",
        )
        value_label.bind(size=self.update_label_text_size)
        setattr(self, value_attr, value_label)

        card.add_widget(accent)
        card.add_widget(title_label)
        card.add_widget(value_label)
        return card

    def build_card(self):
        card = BoxLayout(
            orientation="vertical",
            padding=12,
            spacing=8,
            size_hint_y=None,
        )
        card.bind(minimum_height=card.setter("height"))

        with card.canvas.before:
            Color(*CARD_BG)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self.update_rect, size=self.update_rect)

        return card
    
    def on_pre_enter(self):
        self._set_loading_state(True, False)
        threading.Thread(target=self._bg_load_data, daemon=True).start()
        if hasattr(self, "refresh_sidebar"):
            self.refresh_sidebar()

    def _bg_load_data(self):
        try:
            data = get_analytics_data()
            Clock.schedule_once(lambda dt: self._apply_data(data))
        except Exception as e:
            print(f"Background load error: {e}")
        finally:
            Clock.schedule_once(lambda dt: self._set_loading_state(False, True))

    def refresh_sidebar(self):
        self.sidebar_container.clear_widgets()
        new_sidebar = self.build_admin_sidebar(
            active_screen="admin_analytics", 
            section_label="Analytics"
        )
        self.sidebar_container.add_widget(new_sidebar)