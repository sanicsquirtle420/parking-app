from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView
from kivy.uix.button import Button
from kivy.uix.label import Label

BTN_HEIGHT: int = 35

class Buttons(BoxLayout):
    def __init__(self, map: MapView, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_x = 0.25
        self.spacing = 10
        self.padding = 10
        self.map = map

        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.071, 0.129, 0.259, 1) # Navy
            self.rect = Rectangle(pos=self.pos, size=self.size)

        anchor = AnchorLayout(anchor_y="top")
        txt = Label(text="Ole Miss Parking App", size_hint_y= None, height=40)
        
        btn1 = Button(text="See Tickets", background_normal="", background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None, height=BTN_HEIGHT) # Red
        btn2 = Button(text="Login", background_normal="", background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None, height=BTN_HEIGHT)
        z_in = Button(text="Zoom In (+)", background_normal="", background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None, height=BTN_HEIGHT)
        z_out = Button(text="Zoom Out (-)", background_normal="", background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None, height=BTN_HEIGHT)
        
        anchor.add_widget(txt)
        self.add_widget(anchor)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.add_widget(btn1)
        # TODO: Add function to display Tickets page
        self.add_widget(btn2)
        # TODO: Add function to display Login page
        z_in.bind(on_press=self.zoom_in)
        self.add_widget(z_in)
        z_out.bind(on_press=self.zoom_out)
        self.add_widget(z_out)

    def zoom_in(self, instance):
        self.map.zoom += 1

    def zoom_out(self, instance):
        self.map.zoom -= 1

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size