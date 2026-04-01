from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
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
            font_size=28, 
            size_hint_y=None, 
            height=60,
            color=(1, 1, 1, 1)
        ))

        self.ticket_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.ticket_list.bind(minimum_height=self.ticket_list.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.ticket_list)
        layout.add_widget(scroll)

        back_btn = Button(
            text="Back to Map",
            size_hint_y=None,
            height=50,
            background_normal="",
            background_color=(0.816, 0.125, 0.176, 1)
        )
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def on_pre_enter(self):
        self.ticket_list.clear_widgets()
        app = App.get_running_app()
        current_user = app.user_data.get("user_id")

        if not current_user:
            self.ticket_list.add_widget(Label(text="Please login to view tickets", size_hint_y=None, height=50))
            return

        POWDER_BLUE = (0.69, 0.84, 0.93, 1)
        OM_RED = (0.816, 0.125, 0.176, 1)

        try:
            tickets = get_user_tickets(current_user)
            
            if not tickets:
                self.ticket_list.add_widget(Label(text="No active tickets found.", size_hint_y=None, height=50))
                return

            for i, t in enumerate(tickets):
                is_even = (i % 2 == 0)
                box_color = POWDER_BLUE if is_even else OM_RED
                text_color = (0, 0, 0, 1) if is_even else (1, 1, 1, 1)

                card = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=140,
                    padding=[20, 10],
                    spacing=5
                )

                with card.canvas.before:
                    Color(*box_color)
                    card.bg_rect = Rectangle(pos=card.pos, size=card.size)
                
                card.bind(pos=self.update_card_rect, size=self.update_card_rect)

                header = f"Ticket #{t['ticket_id']}  |  ${t['amount']}  |  {t['status']}"
                desc = t.get('description') or "No description provided"

                ticket_info = Label(
                    text=f"{header}\n[size=24][i]{desc}[/i][/size]",
                    color=text_color,
                    bold=True,
                    halign='left',
                    valign='middle',
                    markup=True
                )
                ticket_info.bind(size=ticket_info.setter('text_size'))

                card.add_widget(ticket_info)
                self.ticket_list.add_widget(card)

        except Exception as e:
            print(f"UI Error: {e}")

    def update_bg_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_card_rect(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

    def go_back(self, instance):
        self.manager.current = "main"