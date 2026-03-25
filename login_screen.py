from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle


def red_button(text):
    default = (0.8, 0.1, 0.1, 1)
    pressed = (0, 0, 0, 1)

    btn = Button(
        text=text,
        size_hint_y=None,
        height=50,
        background_normal="",
        background_color=default,
        color=(1, 1, 1, 1),
    )

    def on_state(instance, value):
        instance.background_color = pressed if value == "down" else default

    btn.bind(state=on_state)
    return btn


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.07, 0.12, 0.2, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        root = BoxLayout(orientation="vertical", spacing=14, padding=24, size_hint=(None, None), width=520)
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(Label(text="Ole Miss Parking", font_size=28, color=(1, 1, 1, 1), size_hint_y=None, height=52))
        root.add_widget(Label(text="Login", font_size=18, color=(0.7, 0.8, 1, 1), size_hint_y=None, height=30))

        self.username = TextInput(hint_text="User ID", multiline=False, size_hint_y=None, height=48)
        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height=48)

        root.add_widget(self.username)
        root.add_widget(self.password)

        login_btn = red_button("Login")
        login_btn.bind(on_release=self.login)

        guest_btn = red_button("Continue as Visitor")
        guest_btn.bind(on_release=self.guest)

        create_btn = red_button("Create Account")
        create_btn.bind(on_release=lambda x: setattr(self.manager, "current", "create"))

        root.add_widget(login_btn)
        root.add_widget(guest_btn)
        root.add_widget(create_btn)

        self.error = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=None, height=30)
        root.add_widget(self.error)

        outer = AnchorLayout()
        outer.add_widget(root)
        self.add_widget(outer)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def login(self, instance):
        if not self.username.text or not self.password.text:
            self.error.text = "Enter User ID and Password"
            return

        app = App.get_running_app()
        permit = app.infer_permit(self.username.text)

        app.user_data = {
            "username": self.username.text,
            "role": permit,
            "permit": permit,
        }

        self.manager.current = "main"
        self.manager.get_screen("main").refresh_sidebar()

    def guest(self, instance):
        App.get_running_app().user_data = {
            "username": "Guest",
            "role": "Visitor",
            "permit": "Visitor",
        }
        self.manager.current = "main"
        self.manager.get_screen("main").refresh_sidebar()

    def reset_fields(self):
        self.username.text = ""
        self.password.text = ""
        self.error.text = ""