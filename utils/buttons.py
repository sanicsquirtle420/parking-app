from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App

BTN_HEIGHT: int = 35

class Buttons(BoxLayout):
    def __init__(self, map: MapView, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_x = 0.25
        self.spacing = 10
        self.padding = 10
        self.map = map

        with self.canvas.before:
            Color(0.071, 0.129, 0.259, 1)  
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        anchor = AnchorLayout(anchor_y="top")
        self.title = Label(
            text="Ole Miss Parking App",
            size_hint_y=None,
            height=40,
            color=(1, 1, 1, 1),
        )
        anchor.add_widget(self.title)
        self.add_widget(anchor)

        self.user_label = Label(
            text=self.get_user_text(),
            size_hint_y=None,
            height=40,
            color=(0.7, 0.8, 1, 1),
        )
        self.add_widget(self.user_label)

        btn1 = Button(
            text="See Tickets(test)",
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None,
            height=BTN_HEIGHT,
        )

        btn2 = Button(
            text="Log out",
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None,
            height=BTN_HEIGHT,
        )

        z_in = Button(
            text="Zoom In (+)",
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None,
            height=BTN_HEIGHT,
        )
        z_out = Button(
            text="Zoom Out (-)",
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1),
            size_hint_y=None,
            height=BTN_HEIGHT,
        )

        self.add_widget(btn1)        
        # TODO: Add function to display Tickets page
        btn1.bind(on_press=self.go_to_tickets)
        self.add_widget(btn2)
        btn2.bind(on_press=self.go_to_login)
        z_in.bind(on_press=self.zoom_in)
        self.add_widget(z_in)
        z_out.bind(on_press=self.zoom_out)
        self.add_widget(z_out)

    def get_user_text(self):
        app = App.get_running_app()
        if hasattr(app, "user_data"):
            u = app.user_data
            return f"{u['username']} ({u['permit']})"
        return "Guest (Visitor)"

    def refresh_user(self):
        self.user_label.text = self.get_user_text()

    def update_user_info(self):
        self.refresh_user()

    def go_to_login(self, instance):
        app = App.get_running_app()
        app.user_data = {}

        login_screen = app.root.get_screen("login")
        create_screen = app.root.get_screen("create")

        if hasattr(login_screen, "reset_fields"):
            login_screen.reset_fields()

        if hasattr(create_screen, "reset_fields"):
            create_screen.reset_fields()

        app.root.current = "login"

    def on_parent(self, *args):
         self.refresh_user()

    def zoom_in(self, instance):
        self.map.zoom += 1

    def zoom_out(self, instance):
        self.map.zoom -= 1

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_to_tickets(self, instance):
        print("Button clicked!")
        app = App.get_running_app()
        app.root.current = "tickets"