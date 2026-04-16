from kivy.graphics import Color, Mesh, Line, RoundedRectangle
from kivy.graphics.tesselator import Tesselator
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.mapview import MapLayer
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.app import App

class LotOutline(MapLayer):
    def __init__(self, coordinates, color: tuple, info: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.coordinates = [tuple(c) for c in coordinates]
        self.color = color
        self.info = info or {}
        self._screen_pts = []
        self._hovered = False
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
        # Kivy y-axis is flipped vs window
        my = Window.height - my
        is_inside = point_in_lot(mx, my, self._screen_pts)

        if is_inside and not self._hovered:
            self._hovered = True
            self.show_tooltip(pos)
        elif not is_inside and self._hovered:
            self._hovered = False
            self.hide_tooltip()

    def show_tooltip(self, pos):
        if hasattr(self, '_tooltip') and self._tooltip:
            self.hide_tooltip()

        app = App.get_running_app()
        user_permit = app.user_data.get("permit")

        info = self.info
        text = f"[b]{info.get('name', 'Parking Lot')}[/b]\n"
        text += f"Capacity: {info.get('capacity', 'N/A')}\n"
        text += f"Permit: {info.get('permit_required', 'N/A')}\n"
        if user_permit == info.get("permit_required", "N/A"):
            text += "[color=00ff00]You can park here.[/color]"
        else:
            text += "[color=ff0000]You can not park here.[/color]"

        self._tooltip = Label(
            text=text,
            markup=True,
            size_hint=(None, None),
            padding=(10, 8),
            color=(1, 1, 1, 1),
        )

        self._tooltip.texture_update()
        texture_w, texture_h = self._tooltip.texture_size

        padding_x, padding_y = 15, 10
        self._tooltip.size = (texture_w + padding_x, texture_h + padding_y)
        self._tooltip.pos = (pos[0] + 10, pos[1] - self._tooltip.size[1] - 5)

        with self._tooltip.canvas.before:
            Color(0, 0, 0, 0.75)
            self._tooltip._bg_rect = RoundedRectangle(
                pos=self._tooltip.pos,
                size=self._tooltip.size,
                radius=[8]
            )

        self._tooltip.bind(
            pos=lambda inst, val: setattr(inst._bg_rect, 'pos', val),
            size=lambda inst, val: setattr(inst._bg_rect, 'size', val),
        )

        root_window = self.get_root_window()
        if root_window is None:
            return
        root_window.add_widget(self._tooltip)
            
    def hide_tooltip(self):
        if hasattr(self, '_tooltip') and self._tooltip:
            root_window = self.get_root_window()
            if root_window is None:
                return
            root_window.remove_widget(self._tooltip)
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