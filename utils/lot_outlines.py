from kivy.graphics.tesselator import Tesselator
from kivy.graphics import Color, Mesh, Line
from kivy_garden.mapview import MapLayer

class LotOutline(MapLayer):
    def __init__(self, coordinates, color: tuple, **kwargs):
        super().__init__(*kwargs)
        self.coordinates = coordinates
        self.color = color

    def reposition(self):
        self.canvas.clear()
        mapview = self.parent
        if not mapview or len(self.coordinates) < 3:
            return
        
        screen_pts = []
        for lat, lon in self.coordinates:
            x, y = mapview.get_window_xy_from(lat, lon, mapview.zoom)
            screen_pts.append((x, y))
        
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