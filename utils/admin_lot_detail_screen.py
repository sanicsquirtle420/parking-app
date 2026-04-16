from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner

from utils.admin_navigation import AdminScreen
from database.db import run_in_background
from database.queries.admin_lot_detail import (
    get_admin_lot_detail_snapshot,
    update_lot_capacity,
    update_lot_occupancy,
    update_ev_chargers,
    add_rule,
    toggle_rule,
    delete_rule,
)

OM_RED = (0.816, 0.125, 0.176, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)


class AdminLotDetailScreen(AdminScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_controls = []

        root = BoxLayout(orientation="horizontal")

        sidebar = self.build_admin_sidebar(
            active_screen="admin_dashboard",
            section_label="Manage Lot"
        )

        main = BoxLayout(orientation="vertical", padding=20, spacing=12)

        with main.canvas.before:
            Color(*LIGHT_BG)
            main.rect = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=self.update_rect, size=self.update_rect)

        # Title
        self.title = Label(font_size=24, size_hint_y=None, height=50, color=(0.1,0.1,0.1,1))
        self.stats = Label(size_hint_y=None, height=40, color=(0.2,0.2,0.2,1))
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=26,
            color=(0.4, 0.4, 0.4, 1),
            halign="left",
            valign="middle",
        )
        self.status_label.bind(size=self.update_label_text_size)

        main.add_widget(self.title)
        main.add_widget(self.stats)
        main.add_widget(self.status_label)

        # Inputs
        self.capacity_input = TextInput(multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1))
        self.occupancy_input = TextInput(multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1))
        self.ev_input = TextInput(multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1))

        main.add_widget(self.build_row("Capacity", self.capacity_input, self.update_capacity))
        main.add_widget(self.build_row("Occupancy", self.occupancy_input, self.update_occupancy))
        main.add_widget(self.build_row("EV Chargers", self.ev_input, self.update_ev))

        # Days checkboxes
        self.days = {}
        days_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]:
            box = BoxLayout(size_hint_x=None, width=80)
            cb = CheckBox(
                size_hint=(None, None),
                size=(30, 30),
                color=(0.5, 0.5, 0.5, 1)
            )
            lbl = Label(text=d, color=(0,0,0,1), bold=True)
            self.days[d] = cb
            self.loading_controls.append(cb)
            box.add_widget(cb)
            box.add_widget(lbl)
            days_layout.add_widget(box)

        main.add_widget(days_layout)

        # Time + Permit
        self.start_time = TextInput(text="08:00", multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1))
        self.end_time = TextInput(text="17:00", multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1))

        self.permit_spinner = Spinner(
            text="Select Permit",
            background_normal="",
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )

        time_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.start_time.size_hint_x = 0.3
        self.end_time.size_hint_x = 0.3
        self.permit_spinner.size_hint_x = 0.4

        time_layout.add_widget(self.start_time)
        time_layout.add_widget(self.end_time)
        time_layout.add_widget(self.permit_spinner)

        main.add_widget(time_layout)
        self.loading_controls.extend([self.start_time, self.end_time, self.permit_spinner])

        # Add Rule button
        self.add_rule_btn = Button(
            text="Add Rule",
            background_normal="",
            background_color=OM_RED,
            size_hint_y=None,
            height=50
        )
        self.add_rule_btn.bind(on_release=self.handle_add_rule)
        self.loading_controls.append(self.add_rule_btn)
        main.add_widget(self.add_rule_btn)

        # Rules list
        self.rules_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        self.rules_box.bind(minimum_height=self.rules_box.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.rules_box)
        main.add_widget(scroll)

        root.add_widget(sidebar)
        root.add_widget(main)
        self.add_widget(root)

    def on_pre_enter(self):
        app = App.get_running_app()
        lot = app.selected_admin_lot
        self.lot_id = lot["lot_id"]

        # Reset all rule-input fields immediately so stale state never shows
        for cb in self.days.values():
            cb.active = False
        self.start_time.text = "08:00"
        self.end_time.text = "17:00"
        self.permit_spinner.text = "Select Permit"
        self.permit_spinner.values = []
        self.title.text = "Loading..."
        self.stats.text = ""
        self.status_label.text = "Loading lot details..."
        self.rules_box.clear_widgets()
        self.set_controls_enabled(False)

        self.start_live_refresh(
            lambda lot_id=self.lot_id: get_admin_lot_detail_snapshot(lot_id),
            self._apply_lot_data,
            self._set_loading_state,
            force=True,
        )

    def _apply_lot_data(self, result):
        if result is None:
            self.status_label.text = "Unable to load lot details."
            return
        data = result["lot"]
        permits = result["permits"]
        rules = result["rules"]
        if not data:
            self.status_label.text = "Lot not found."
            return

        self.title.text = data["lot_name"]
        self.stats.text = f"{data['current_occupancy']} / {data['capacity']} occupied"
        self.capacity_input.text = str(data["capacity"])
        self.occupancy_input.text = str(data["current_occupancy"])
        self.ev_input.text = str(data["ev_charger_count"])

        self.permit_map = {p["permit_name"]: p["permit_id"] for p in permits}
        self.permit_spinner.values = list(self.permit_map.keys())

        self._render_rules(rules)

    def _set_loading_state(self, is_loading, is_refresh):
        if is_loading:
            self.status_label.text = "Refreshing lot details..." if is_refresh else "Loading lot details..."
            self.set_controls_enabled(False)
            return

        self.status_label.text = ""
        self.set_controls_enabled(True)

    def set_controls_enabled(self, enabled):
        for widget in self.loading_controls:
            widget.disabled = not enabled
        for row in self.rules_box.children:
            for child in row.children:
                if isinstance(child, Button):
                    child.disabled = not enabled

    def build_row(self, label_text, input_widget, callback):
        row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        row.add_widget(Label(text=label_text, size_hint_x=0.3, color=(0,0,0,1)))
        row.add_widget(input_widget)
        btn = Button(text="Update", background_normal="", background_color=OM_RED, size_hint_x=0.3)
        btn.bind(on_release=callback)
        self.loading_controls.extend([input_widget, btn])
        row.add_widget(btn)
        return row

    def update_capacity(self, *_):
        run_in_background(
            lambda: update_lot_capacity(self.lot_id, int(self.capacity_input.text)),
            lambda _: self.after_lot_mutation()
        )

    def update_occupancy(self, *_):
        run_in_background(
            lambda: update_lot_occupancy(self.lot_id, int(self.occupancy_input.text)),
            lambda _: self.after_lot_mutation()
        )

    def update_ev(self, *_):
        run_in_background(
            lambda: update_ev_chargers(self.lot_id, int(self.ev_input.text)),
            lambda _: self.after_lot_mutation()
        )

    def handle_add_rule(self, *_):
        selected_days = [d for d, cb in self.days.items() if cb.active]
        if not selected_days:
            return
        permit_name = self.permit_spinner.text
        if permit_name not in self.permit_map:
            return

        lot_id = self.lot_id
        permit_id = self.permit_map[permit_name]
        days_str = ",".join(selected_days)
        start = self.start_time.text
        end = self.end_time.text

        run_in_background(
            lambda: add_rule(lot_id, permit_id, days_str, start, end),
            lambda _: self.after_lot_mutation()
        )

    def reload_snapshot(self):
        self.start_live_refresh(
            lambda lot_id=self.lot_id: get_admin_lot_detail_snapshot(lot_id),
            self._apply_lot_data,
            self._set_loading_state,
            force=True,
        )

    def after_lot_mutation(self):
        self.invalidate_admin_screen("admin_dashboard")
        self.invalidate_admin_screen("admin_analytics")
        self.reload_snapshot()

    def _render_rules(self, rules):
        self.rules_box.clear_widgets()
        if not rules:
            return

        for r in rules:
            row = BoxLayout(size_hint_y=None, height=45, spacing=10)

            txt = Label(
                text=f"{r['day_of_week']} {r['start_time']}–{r['end_time']}",
                color=(0,0,0,1),
                size_hint_x=0.5,
                halign="left"
            )
            txt.bind(size=txt.setter("text_size"))

            toggle_btn = Button(
                text="ON" if r["is_allowed"] else "OFF",
                size_hint_x=0.25,
                background_normal="",
                background_color=(0,0.5,0,1) if r["is_allowed"] else (0.6,0,0,1)
            )
            toggle_btn.bind(on_release=lambda i, rule=r: self.confirm_toggle(rule))

            delete_btn = Button(
                text="Delete",
                size_hint_x=0.25,
                background_normal="",
                background_color=(0.3,0.3,0.3,1)
            )
            delete_btn.bind(on_release=lambda i, rid=r["rule_id"]: self.confirm_delete(rid))

            row.add_widget(txt)
            row.add_widget(toggle_btn)
            row.add_widget(delete_btn)
            self.rules_box.add_widget(row)

    def confirm_action(self, msg, action):
        layout = BoxLayout(orientation="vertical", spacing=10)
        layout.add_widget(Label(text=msg))

        btns = BoxLayout(size_hint_y=None, height=40)
        yes = Button(text="Yes")
        no = Button(text="Cancel")

        btns.add_widget(yes)
        btns.add_widget(no)
        layout.add_widget(btns)

        popup = Popup(title="Confirm", content=layout, size_hint=(0.4,0.3))
        yes.bind(on_release=lambda x: (action(), popup.dismiss()))
        no.bind(on_release=popup.dismiss)
        popup.open()

    def confirm_toggle(self, rule):
        self.confirm_action("Change rule status?", lambda: self.toggle(rule))

    def confirm_delete(self, rule_id):
        self.confirm_action("Delete this rule?", lambda: self.delete(rule_id))

    def toggle(self, rule):
        run_in_background(
            lambda: toggle_rule(rule["rule_id"], rule["is_allowed"]),
            lambda _: self.after_lot_mutation()
        )

    def delete(self, rule_id):
        run_in_background(
            lambda: delete_rule(rule_id),
            lambda _: self.after_lot_mutation()
        )
