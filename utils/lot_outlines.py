from database.queries.parking_sessions import start_parking_session, end_parking_session, get_active_session
from kivy.graphics import Color, Mesh, Line, RoundedRectangle
from database.queries.map_data import can_user_park_in_polygon
from kivy.graphics.tesselator import Tesselator
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapLayer
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label
from datetime import datetime
from kivy.clock import Clock
from kivy.app import App

class LotOutline(MapLayer):
    _active_instance = None
    def __init__(self, coordinates, color: tuple, info: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.coordinates = [tuple(c) for c in coordinates]
        self.color = color
        self.info = info
        self._screen_pts = []
        self._hovered = False
        self._tooltip = None
        self._hide_event = None
        Window.bind(mouse_pos=self.on_mouse)

    def reposition(self):
        self.canvas.clear()
        mapview = self.parent
        if not mapview or len(self.coordinates) < 3:
            return

        screen_pts = []
        for lat, lon in self.coordinates:
            x, y = mapview.get_window_xy_from(lat, lon, mapview.zoom)
            screen_pts.append((x, y))

        self._screen_pts = [(x, Window.height - y) for x, y in screen_pts]

        with self.canvas:
            Color(*self.color)
            t = Tesselator()
            t.add_contour([cord for point in screen_pts for cord in point])
            if t.tesselate():
                for vertices, indices in t.meshes:
                    Mesh(vertices=vertices, indices=indices, mode="triangle_fan")
            Color(self.color[0], self.color[1], self.color[2], 1.0)
            flat = [cord for point in screen_pts for cord in point]
            flat += flat[:2]
            Line(points=flat, width=2)

    def on_mouse(self, window, pos):
        if not self._screen_pts:
            return
        mx, my = pos

        # If another instance owns the active tooltip, don't interfere
        if LotOutline._active_instance and LotOutline._active_instance is not self:
            return

        # Check if hovering over the tooltip
        if self._tooltip:
            tx, ty = self._tooltip.pos
            tw, th = self._tooltip.size
            if tx <= mx <= tx + tw and ty <= my <= ty + th:
                if self._hide_event:
                    self._hide_event.cancel()
                    self._hide_event = None
                return

        my_flipped = Window.height - my
        is_inside = point_in_lot(mx, my_flipped, self._screen_pts)

        if is_inside and not self._hovered:
            self._hovered = True
            if self._hide_event:
                self._hide_event.cancel()
                self._hide_event = None
            LotOutline._active_instance = self
            self.show_tooltip(pos)
        elif not is_inside and self._hovered:
            self._hovered = False
            if self._hide_event:
                self._hide_event.cancel()
            self._hide_event = Clock.schedule_once(lambda dt: self._deactivate(), 0.3)

    def _deactivate(self):
        self.hide_tooltip()
        if LotOutline._active_instance is self:
            LotOutline._active_instance = None

    def _on_park_here(self, instance):
        app = App.get_running_app()
        user_id = app.user_data.get("user_id")
        info = self.info

        if not user_id:
            print("Cannot park: no user logged in")
            return

        result = start_parking_session(
            user_id=user_id,
            lot_id=info.get("lot_id"),
            lot_name=info.get("name", "Unknown Lot"),
        )

        if result:
            print(f"Parking session started in {info.get('name')}")
            app.active_parking_session = result
            try:
                main_screen = app.root.get_screen("main")
                main_screen.refresh_sidebar()
            except Exception:
                pass
        else:
            print("Could not start parking session (lot full or already parked)")

        self.hide_tooltip()

    def _on_end_session(self, instance):
        app = App.get_running_app()
        user_id = app.user_data.get("user_id")

        if not user_id:
            return

        success = end_parking_session(user_id)
        if success:
            print("Parking session ended")
            app.active_parking_session = None
            try:
                main_screen = app.root.get_screen("main")
                main_screen.refresh_sidebar()
            except Exception:
                pass
        else:
            print("Could not end parking session")

        self.hide_tooltip()

    def show_tooltip(self, pos):
        if self._tooltip:
            self.hide_tooltip()

        app = App.get_running_app()
        user_permit = app.user_data.get("permit")
        user_id = app.user_data.get("user_id")

        info = self.info
        now = datetime.now()
        occupancy = info.get('current_occupancy', 0)
        capacity = info.get('capacity', 'N/A')

        text = f"[b]{info.get('name', 'Parking Lot')}[/b]\n"
        text += f"Capacity: {capacity}\n"
        if isinstance(capacity, int) and isinstance(occupancy, int):
            spots_left = capacity - occupancy
            text += f"Spots Left: {spots_left}\n"
        text += f"Permit: {info.get('permit_required', 'N/A')}\n"
        text += f"[color=aaaaaa]Checked: {now.strftime('%a %I:%M:%S %p')}[/color]\n"

        can_park = can_user_park_in_polygon(user_id, info.get("lot_id"))
        if can_park is None:
            can_park = user_permit == info.get("permit_required", "N/A")

        if can_park:
            text += "[color=00ff00]You can park here.[/color]"
        else:
            text += "[color=ff0000]You cannot park here.[/color]"

        tooltip_box = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            padding=8,
            spacing=4,
        )

        info_label = Label(
            text=text,
            markup=True,
            size_hint=(None, None),
            color=(1, 1, 1, 1),
        )
        info_label.texture_update()
        tw, th = info_label.texture_size
        info_label.size = (tw + 10, th + 6)

        tooltip_box.add_widget(info_label)

        if user_id:
            active_session = get_active_session(user_id)
            if active_session and active_session.get("lot_id") == info.get("lot_id"):
                end_btn = Button(
                    text="End Session",
                    size_hint=(None, None),
                    size=(tw + 10, 32),
                    background_normal="",
                    background_color=(0.8, 0.1, 0.1, 1),
                    color=(1, 1, 1, 1),
                )
                end_btn.bind(on_release=self._on_end_session)
                tooltip_box.add_widget(end_btn)
            elif active_session:
                parked_label = Label(
                    text=f"[color=ffaa00]Parked in: {active_session.get('lot_name', '?')}[/color]",
                    markup=True,
                    size_hint=(None, None),
                    size=(tw + 10, 24),
                    color=(1, 1, 1, 1),
                )
                tooltip_box.add_widget(parked_label)
            elif can_park:
                park_btn = Button(
                    text="Park Here",
                    size_hint=(None, None),
                    size=(tw + 10, 32),
                    background_normal="",
                    background_color=(0.1, 0.6, 0.1, 1),
                    color=(1, 1, 1, 1),
                )
                park_btn.bind(on_release=self._on_park_here)
                tooltip_box.add_widget(park_btn)

        total_height = sum(c.height for c in tooltip_box.children) + 16 + (4 * (len(tooltip_box.children) - 1))
        max_width = max(c.width for c in tooltip_box.children) + 16
        tooltip_box.size = (max_width, total_height)
        tooltip_box.pos = (pos[0] + 10, pos[1] - total_height - 5)

        with tooltip_box.canvas.before:
            Color(0, 0, 0, 0.85)
            tooltip_box._bg_rect = RoundedRectangle(
                pos=tooltip_box.pos,
                size=tooltip_box.size,
                radius=[8]
            )

        tooltip_box.bind(
            pos=lambda inst, val: setattr(inst._bg_rect, 'pos', val),
            size=lambda inst, val: setattr(inst._bg_rect, 'size', val),
        )

        self._tooltip = tooltip_box

        root_window = self.get_root_window()
        if root_window is None:
            return
        root_window.add_widget(self._tooltip)

    def hide_tooltip(self):
        if self._hide_event:
            self._hide_event.cancel()
            self._hide_event = None
        if self._tooltip:
            root_window = self.get_root_window()
            if root_window:
                root_window.remove_widget(self._tooltip)
            self._tooltip = None
        if LotOutline._active_instance is self:
            LotOutline._active_instance = None
            self._tooltip = None

def point_in_lot(x, y, polygon):
    n = len(polygon)
    inside = False
    px, py = x, y
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside