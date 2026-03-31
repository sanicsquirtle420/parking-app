from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle

class TicketsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set background color to match Login/Create screens
        with self.canvas.before:
            Color(0.07, 0.12, 0.2, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Header
        layout.add_widget(Label(
            text="Your Traffic Tickets", 
            font_size=28, 
            size_hint_y=None, 
            height=60,
            color=(1, 1, 1, 1)
        ))

        # Scrollable area for tickets
        self.ticket_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.ticket_list.bind(minimum_height=self.ticket_list.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.ticket_list)
        layout.add_widget(scroll)

        # Back Button
        back_btn = Button(
            text="Back to Map",
            size_hint_y=None,
            height=50,
            background_normal="",
            background_color=(0.8, 0.1, 0.1, 1)
        )
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def on_pre_enter(self):
        """This runs right before the screen is shown. Use it to load data."""
        self.ticket_list.clear_widgets()
        # Mock data - Replace this with a database call later
        tickets = [
            {"id": "T101", "date": "2026-03-20", "amount": "$50", "status": "Unpaid"},
            {"id": "T105", "date": "2026-03-15", "amount": "$25", "status": "Pending"},
        ]
        
        for t in tickets:
            ticket_row = Label(
                text=f"Ticket {t['id']} | {t['date']} | {t['amount']} | {t['status']}",
                size_hint_y=None,
                height=40,
                color=(0.7, 0.8, 1, 1)
            )
            self.ticket_list.add_widget(ticket_row)

    def go_back(self, instance):
        self.manager.current = "main"