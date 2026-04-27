from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from database.queries.tickets import get_user_tickets

class TicketsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.07, 0.12, 0.2, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg_rect, pos=self.update_bg_rect)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(
            text="Your Traffic Tickets", 
            font_size=40, 
            size_hint_y=None, 
            height=60,
            color=(1, 1, 1, 1)
        ))

        self.ticket_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.ticket_list.bind(minimum_height=self.ticket_list.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.ticket_list)
        layout.add_widget(scroll)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)

        pay_nav_btn = Button(
            text="Pay Tickets",
            background_normal="",
            background_color=(0.1, 0.6, 0.1, 1)
        )
        pay_nav_btn.bind(on_release=self.go_to_pay)

        back_btn = Button(
            text="Back to Map",
            size_hint_y=None,
            height=50,
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1)
        )
        back_btn.bind(on_release=self.go_back)

        button_layout.add_widget(back_btn)
        button_layout.add_widget(pay_nav_btn)
        
        layout.add_widget(button_layout)

        self.add_widget(layout)

    def go_to_pay(self, instance):
        self.manager.current = "pay_tickets"

    def on_pre_enter(self):
        self.ticket_list.clear_widgets()
        app = App.get_running_app()
        current_user = app.user_data.get("user_id")

        if not current_user:
            self.ticket_list.add_widget(Label(text="Please login to view tickets", size_hint_y=None, height=50))
            return

        try:
            tickets = get_user_tickets(current_user)
            
            if not tickets:
                self.ticket_list.add_widget(Label(text="No tickets found.", size_hint_y=None, height=50))
                return

            unpaid_tickets = [t for t in tickets if t['status'].lower() == 'unpaid']
            paid_tickets = [t for t in tickets if t['status'].lower() == 'paid']

            if unpaid_tickets:
                self.ticket_list.add_widget(Label(
                    text="UNPAID TICKETS", 
                    bold=True, font_size=30, color=(1, 0.3, 0.3, 1),
                    size_hint_y=None, height=50
                ))
                for t in unpaid_tickets:
                    self.add_ticket_card(t, is_unpaid=True)

            if paid_tickets:
                self.ticket_list.add_widget(Label(
                    text="TICKET HISTORY", 
                    bold=True, font_size=30, color=(0.3, 1, 0.3, 1),
                    size_hint_y=None, height=50
                ))
                for t in paid_tickets:
                    self.add_ticket_card(t, is_unpaid=False)

        except Exception as e:
            print(f"UI Error: {e}")

    def add_ticket_card(self, t, is_unpaid):
        box_color = (0.816, 0.125, 0.176, 1) if is_unpaid else (0.69, 0.84, 0.93, 1)
        text_color = (1, 1, 1, 1) if is_unpaid else (0, 0, 0, 1)

        card = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=[20, 10], spacing=5)
        with card.canvas.before:
            Color(*box_color)
            card.bg_rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self.update_card_rect, size=self.update_card_rect)

        header = f"Date: {t['issue_date']}  |  ${t['amount']}"
        desc = t.get('description') or "No description provided"

        ticket_info = Label(
            text=f"{header}\n[size=20]{desc}[/size]",
            color=text_color, bold=True, halign='left', markup=True
        )
        ticket_info.bind(size=ticket_info.setter('text_size'))
        
        card.add_widget(ticket_info)
        self.ticket_list.add_widget(card)

    def update_bg_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_card_rect(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

    def go_back(self, instance):
        self.manager.current = "main"