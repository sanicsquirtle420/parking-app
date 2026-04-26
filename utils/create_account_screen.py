from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from database.queries.users import create_user, gen_userid


ROLE_BY_SELECTION = {
    "Student": "student",
    "Faculty/Staff": "faculty",
    "Visitor": "visitor",
    "Admin": "admin",
}

PERMIT_LABEL_BY_SELECTION = {
    "Student": "Free Day Pass",
    "Faculty/Staff": "Free Day Pass",
    "Visitor": "Free Day Pass",
    "Admin": "Admin Access",
}

Builder.load_string('''
<BorderedSpinnerOption@SpinnerOption>:
    background_normal: ''
    background_color: 0.22, 0.22, 0.22, 1
    color: 1,1,1,1
    height: 44
    canvas.after:
        Color:
            rgba: 0.6, 0.6, 0.6, 1
        Line:
            rectangle: self.x, self.y, self.width, self.height
            width: 1.1
''')

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


class CreateAccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.07, 0.12, 0.2, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        root = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=24,
            size_hint=(None, None),
            width=520,
        )
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(Label(
            text="Create Account",
            font_size=24,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=42,
        ))

        def field(text, password=False):
            return TextInput(
                hint_text=text,
                multiline=False,
                password=password,
                size_hint_y=None,
                height=48,
                background_normal="",
                background_color=(1, 1, 1, 1),
                foreground_color=(0, 0, 0, 1),
            )

        self.first = field("First Name")
        self.last = field("Last Name")
        self.email = field("Email")
        self.password = field("Password", True)

        self.permit_type = Spinner(
            text="Select Account Type",
            values=("Student", "Faculty/Staff", "Visitor", "Admin"),
            size_hint_y=None,
            height=48,
            background_normal="",
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            option_cls="BorderedSpinnerOption",
        )

        for w in [self.first, self.last, self.email, self.password, self.permit_type]:
            root.add_widget(w)

        create_btn = red_button("Create Account")
        create_btn.bind(on_release=self.create)

        back_btn = red_button("Back to Login")
        back_btn.bind(on_release=self.back)

        root.add_widget(create_btn)
        root.add_widget(back_btn)

        self.msg = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=None, height=30)
        root.add_widget(self.msg)

        outer = AnchorLayout()
        outer.add_widget(root)
        self.add_widget(outer)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def create(self, instance):
        if not all([
            self.first.text.strip(),
            self.last.text.strip(),
            self.email.text.strip(),
            self.password.text.strip(),
        ]):
            self.msg.text = "Fill in all fields."
            return

        if self.permit_type.text == "Select Account Type":
            self.msg.text = "Select an account type"
            return

        selected_type = self.permit_type.text
        db_role = ROLE_BY_SELECTION.get(selected_type, "student")
        user_id = gen_userid(db_role)

        juno = create_user(
            user_id=user_id,
            first_name=self.first.text.strip(),
            last_name=self.last.text.strip(),
            email=self.email.text.strip(),
            password=self.password.text.strip(),
            role=db_role,
            assign_signup_pass=(db_role != "admin"),
        )

        if not juno:
            self.msg.text = "A user is already using that email."
            return

        App.get_running_app().user_data = {
            "user_id": user_id,
            "username": f"{self.first.text.strip()} {self.last.text.strip()}",
            "email": self.email.text.strip().lower(),
            "role": db_role,
            "permit": PERMIT_LABEL_BY_SELECTION.get(selected_type, "No Permit Assigned"),
        }

        if db_role == "admin":
            self.manager.current = "admin_dashboard"
        else:
            self.manager.current = "main"
            self.manager.get_screen("main").refresh_sidebar()

    def back(self, instance):
        self.manager.current = "login"

    def reset_fields(self):
        self.first.text = ""
        self.last.text = ""
        self.email.text = ""
        self.password.text = ""
        self.permit_type.text = "Select Account Type"
        self.msg.text = ""
