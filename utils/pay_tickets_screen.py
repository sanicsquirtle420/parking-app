from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from database.queries.tickets import get_user_tickets, pay_all_user_tickets

class PayTicketsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.07, 0.12, 0.2, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_pre_enter(self):
        self.refresh_ui()

    def refresh_ui(self, status_msg="Payment Portal"):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        app = App.get_running_app()
        user_id = app.user_data.get("user_id")
        
        tickets = get_user_tickets(user_id)
        unpaid_total = sum(float(t['amount']) for t in tickets if t['status'].lower() == 'unpaid')

        layout.add_widget(Label(
            text=status_msg, 
            font_size=32, 
            bold=True, 
            color=(1, 1, 1, 1)
        ))
        
        if unpaid_total > 0:
            layout.add_widget(Label(
                text=f"Amount Due: ${unpaid_total:.2f}",
                font_size=24,
                color=(1, 0.3, 0.3, 1)
            ))
            
            self.pay_btn = Button(
                text="Confirm Mock Payment",
                size_hint_y=None, height=60,
                background_normal="",
                background_color=(0.1, 0.6, 0.1, 1)
            )
            self.pay_btn.bind(on_release=self.start_mock_payment)
            layout.add_widget(self.pay_btn)
        else:
            layout.add_widget(Label(text="No balance due. All tickets paid!", color=(0.3, 1, 0.3, 1)))

        back_btn = Button(
            text="Back to Tickets", 
            size_hint_y=None, height=50,
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1)
        )
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def start_mock_payment(self, instance):
        instance.disabled = True
        instance.text = "Processing Transaction..."
        Clock.schedule_once(self.complete_payment, 2)

    def complete_payment(self, dt):
        app = App.get_running_app()
        pay_all_user_tickets(app.user_data.get("user_id"))
        self.refresh_ui(status_msg="Payment Successful!")

    def go_back(self, instance):
        self.manager.current = "tickets"