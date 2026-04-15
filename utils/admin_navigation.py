from time import monotonic

from kivy.graphics import Color, Rectangle
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from database.db import run_in_background


ADMIN_NAV_ITEMS = [
    ("admin_dashboard", "Dashboard"),
    ("admin_permits", "Permits & Users"),
    ("admin_analytics", "Analytics"),
]

LIGHT_BG = (0.96, 0.97, 0.98, 1)
OM_RED = (0.816, 0.125, 0.176, 1)


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._refresh_in_flight = False
        self._refresh_active_token = None
        self._refresh_requested_token = 0
        self._refresh_latest = None
        self._refresh_dirty = True
        self._last_refresh_completed_at = None
        self.live_refresh_interval = 10.0

        with self.canvas.before:
            Color(*LIGHT_BG)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def build_admin_sidebar(
        self,
        active_screen=None,
        section_label="",
        back_target="main",
        back_label="Back to Map",
    ):
        sidebar = BoxLayout(
            orientation="vertical",
            size_hint_x=0.24,
            spacing=10,
            padding=10,
        )

        with sidebar.canvas.before:
            Color(0.071, 0.129, 0.259, 1)
            sidebar.rect = Rectangle(pos=sidebar.pos, size=sidebar.size)

        sidebar.bind(pos=self.update_rect, size=self.update_rect)

        sidebar.add_widget(Label(
            text="Admin Panel",
            size_hint_y=None,
            height=40,
            color=(1, 1, 1, 1),
        ))

        if section_label:
            sidebar.add_widget(Label(
                text=section_label,
                size_hint_y=None,
                height=35,
                color=(0.7, 0.8, 1, 1),
            ))

        for screen_name, label in ADMIN_NAV_ITEMS:
            sidebar.add_widget(self.build_admin_nav_button(
                text=label,
                target=screen_name,
                active=(screen_name == active_screen),
            ))

        sidebar.add_widget(self.build_admin_nav_button(
            text=back_label,
            target=back_target,
            active=False,
            height=50,
        ))
        return sidebar

    def build_admin_nav_button(self, text, target, active=False, height=46):
        button = Button(
            text=text,
            background_normal="",
            background_color=(0.3, 0.3, 0.3, 1) if active else OM_RED,
            size_hint_y=None,
            height=height,
        )
        button.bind(on_release=lambda *_: self.navigate_to(target))
        return button

    def navigate_to(self, target):
        if self.manager:
            app = App.get_running_app()
            if target == "main" and app.user_data.get("role") == "admin":
                app.user_data = {
                    "username": "Guest",
                    "role": "Visitor",
                    "permit": "Visitor",
                }
                self.manager.current = target
                self.manager.get_screen("main").refresh_sidebar()
                return
            self.manager.current = target

    def start_live_refresh(self, fetch_fn, apply_fn, show_loading_fn=None, force=False):
        if self._refresh_in_flight:
            return

        if not force and self.has_fresh_data():
            return

        self._refresh_requested_token += 1
        token = self._refresh_requested_token
        self._refresh_latest = (fetch_fn, apply_fn, show_loading_fn)

        if show_loading_fn:
            show_loading_fn(True, False)

        self._launch_refresh(token)

    def _launch_refresh(self, token):
        fetch_fn, apply_fn, show_loading_fn = self._refresh_latest
        self._refresh_in_flight = True
        self._refresh_active_token = token

        def _deliver(result):
            self._finish_refresh(token, result, apply_fn, show_loading_fn)

        run_in_background(fetch_fn, _deliver)

    def _finish_refresh(self, token, result, apply_fn, show_loading_fn):
        if token != self._refresh_active_token:
            return

        latest_token = self._refresh_requested_token
        self._refresh_in_flight = False
        self._refresh_active_token = None

        if token == latest_token:
            if result is not None:
                self._refresh_dirty = False
                self._last_refresh_completed_at = monotonic()

            if show_loading_fn:
                show_loading_fn(False, False)

            apply_fn(result)
            return

        if show_loading_fn:
            show_loading_fn(True, True)
        self._launch_refresh(latest_token)

    def has_fresh_data(self):
        if self._refresh_dirty or self._last_refresh_completed_at is None:
            return False
        return (monotonic() - self._last_refresh_completed_at) < self.live_refresh_interval

    def invalidate_live_data(self):
        self._refresh_dirty = True

    def invalidate_admin_screen(self, screen_name):
        if not self.manager or not self.manager.has_screen(screen_name):
            return

        screen = self.manager.get_screen(screen_name)
        if hasattr(screen, "invalidate_live_data"):
            screen.invalidate_live_data()

    def on_leave(self, *args):
        self._refresh_in_flight = False
        self._refresh_active_token = None

    def update_rect(self, instance, _value):
        if hasattr(instance, "rect"):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def update_label_text_size(self, instance, _value):
        instance.text_size = (instance.width, None)
