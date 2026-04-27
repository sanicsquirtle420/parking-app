from datetime import datetime

from kivy.config import Config
Config.set('graphics', 'multisamples', '0')

from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from utils.admin_navigation import AdminScreen
from database.db import run_in_background
from database.queries.admin_permits import (
    DEFAULT_USER_LIMIT,
    create_permit_type,
    delete_permit,
    get_admin_permits_snapshot,
    assign_permit_to_user,
    revoke_user_permit,
    renew_user_permit,
)
from database.queries.tickets import create_ticket, get_user_tickets

NAVY = (0.07, 0.12, 0.26, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
TEXT_DARK = (0.1, 0.1, 0.1, 1)
GREEN = (0.2, 0.6, 0.3, 1)
RED = (0.75, 0.15, 0.15, 1)
GRAY = (0.5, 0.5, 0.5, 1)


class AdminPermitsScreen(AdminScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.permits = []
        self.permit_map = {}
        self.users = []
        self._pending_status_message = ""
        self.sort_mode = None

        root = BoxLayout(orientation="horizontal")

        self.sidebar_container = BoxLayout(size_hint_x=0.25)
        self.refresh_sidebar()
        root.add_widget(self.sidebar_container)

        main = BoxLayout(orientation="vertical", padding=20, spacing=12)

        with main.canvas.before:
            Color(*LIGHT_BG)
            main.rect = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=self.update_rect, size=self.update_rect)

        main.add_widget(Label(
            text="Permits & Users",
            font_size=26,
            size_hint_y=None,
            height=50,
            color=TEXT_DARK
        ))

        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=28,
            color=(0.4, 0.4, 0.4, 1),
            halign="left",
            valign="middle",
        )
        self.status_label.bind(size=self.update_label_text_size)
        main.add_widget(self.status_label)

        permits_row = BoxLayout(size_hint_y=None, height=45, spacing=10)

        self.permit_name_input = TextInput(
            hint_text="Permit Name",
            multiline=False,
            size_hint_y=None,
            height=40
        )

        self.duration_input = TextInput(
            hint_text="Duration (days)",
            multiline=False,
            size_hint_y=None,
            height=40
        )

        add_btn = Button(
            text="Add Permit",
            size_hint=(None, None),
            width=140,
            height=40,
            size_hint_y=None,
            background_normal="",
            background_color=NAVY
        )

        permits_row.add_widget(self.permit_name_input)
        permits_row.add_widget(self.duration_input)
        permits_row.add_widget(add_btn)
        add_btn.bind(on_release=self.add_permit)

        main.add_widget(permits_row)

        self.permit_list = BoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint_y=None
        )
        self.permit_list.bind(minimum_height=self.permit_list.setter("height"))

        scroll = ScrollView(size_hint_y=None, height=220)
        scroll.add_widget(self.permit_list)

        main.add_widget(scroll)

        sort_row = BoxLayout(size_hint_y=None, height=45, spacing=10)

        sort_permit = Button(
            text="Sort: Permit",
            background_normal="",
            background_color=NAVY,
            size_hint_x=0.2,
            size_hint_y=None,
            height=40
        )
        self.filter_spinner = Spinner(
            text="Filter by Permit",
            values=list(self.permit_map.keys()),
            size_hint_x=0.4,
            size_hint_y=None,
            height=40
        )
        sort_exp_asc = Button(
            text="Exp Asc",
            background_normal="",
            background_color=NAVY,
            size_hint_x=0.2,
            size_hint_y=None,
            height=40
        )
        sort_exp_desc = Button(
            text="Exp Desc",
            background_normal="",
            background_color=NAVY,
            size_hint_x=0.2,
            size_hint_y=None,
            height=40
        )

        sort_permit.bind(on_release=self.filter_by_permit)
        sort_exp_asc.bind(on_release=lambda x: self.set_sort("exp_asc"))
        sort_exp_desc.bind(on_release=lambda x: self.set_sort("exp_desc"))

        sort_row.add_widget(sort_permit)
        sort_row.add_widget(self.filter_spinner)
        sort_row.add_widget(sort_exp_asc)
        sort_row.add_widget(sort_exp_desc)

        main.add_widget(sort_row)

        search_row = BoxLayout(size_hint_y=None, height=45, spacing=10)

        self.search_input = TextInput(
            hint_text="Search users...",
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1)
        )

        self.search_input.size_hint_x = 0.6

        search_btn = Button(
            text="Search",
            background_normal="",
            background_color=NAVY,
            size_hint_x=0.2,
            size_hint_y=None,
            height=40
        )
        clear_btn = Button(
            text="Clear",
            background_normal="",
            background_color=GRAY,
            size_hint_x=0.2,
            size_hint_y=None,
            height=40
        )

        search_btn.bind(on_release=self.run_search)
        clear_btn.bind(on_release=self.clear_search)

        search_row.add_widget(self.search_input)
        search_row.add_widget(search_btn)
        search_row.add_widget(clear_btn)

        main.add_widget(search_row)

        # ---- USER LIST ----
        self.user_box = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        self.user_box.bind(minimum_height=self.user_box.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.user_box)
        main.add_widget(scroll)
        root.add_widget(main)
        self.add_widget(root)

    def on_pre_enter(self):
        self.refresh_sidebar()
        self.load_data()

    def _set_loading_state(self, is_loading, is_refresh):
        if is_loading:
            query = self.search_input.text.strip()
            prefix = "Refreshing" if self.user_box.children else "Loading"
            suffix = " search results..." if query else " permits and users..."
            self.status_label.text = prefix + suffix
            if not self.user_box.children:
                self.user_box.add_widget(Label(text="Loading...", size_hint_y=None, height=50))
            return

        self.status_label.text = ""

    def _apply_data(self, result):
        if result is None:
            self.status_label.text = "Unable to load permits and users."
            return
        permits = result["permits"]
        self.permits = permits
        self.permit_map = {p["permit_name"]: p["permit_id"] for p in self.permits}
        self.filter_spinner.values = list(self.permit_map.keys())
        if self.filter_spinner.text not in self.filter_spinner.values:
            self.filter_spinner.text = "Filter by Permit"
        self.build_permit_list()
        self.users = result["users"]
        self.build_users()
        if self._pending_status_message:
            self.status_label.text = self._pending_status_message
            self._pending_status_message = ""

    def load_data(self, search_text=None, force=False):
        if search_text is None:
            search_text = self.search_input.text.strip()

        self.start_live_refresh(
            lambda: get_admin_permits_snapshot(
                search_text=search_text or None,
                limit=DEFAULT_USER_LIMIT,
            ),
            self._apply_data,
            self._set_loading_state,
            force=force,
        )

    def _generate_permit_id(self, permit_name):
        existing_ids = {permit["permit_id"] for permit in self.permits}
        tokens = [
            "".join(ch for ch in token if ch.isalnum())
            for token in permit_name.upper().split()
        ]
        tokens = [token for token in tokens if token]

        candidates = []
        if tokens:
            candidates.append("".join(token[0] for token in tokens)[:5])
            candidates.append("".join(token[:2] for token in tokens)[:5])
            candidates.append("".join(tokens)[:5])

        seen = set()
        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            if candidate not in existing_ids:
                return candidate

        base = (candidates[-1] if candidates else "PERMT")[:5] or "PERMT"
        suffix = 1
        while True:
            suffix_text = str(suffix)
            candidate = f"{base[:5 - len(suffix_text)]}{suffix_text}"
            if candidate not in existing_ids:
                return candidate
            suffix += 1

    def add_permit(self, *_):
        permit_name = self.permit_name_input.text.strip()
        duration_text = self.duration_input.text.strip()
        existing_names = {
            (permit["permit_name"] or "").strip().lower()
            for permit in self.permits
        }

        if not permit_name or not duration_text:
            self.status_label.text = "Permit name and duration are required."
            return

        if permit_name.lower() in existing_names:
            self.status_label.text = "That permit name already exists."
            return

        if not duration_text.isdigit() or int(duration_text) <= 0:
            self.status_label.text = "Duration must be a positive number of days."
            return

        permit_id = self._generate_permit_id(permit_name)
        duration_days = int(duration_text)
        description = f"{duration_days} days"
        self.status_label.text = "Adding permit..."

        run_in_background(
            lambda: create_permit_type(permit_id, permit_name, description),
            self._after_add_permit,
        )

    def _after_add_permit(self, result):
        if not result or not result.get("ok"):
            self.status_label.text = (
                result.get("message") if result else "Unable to add permit."
            )
            return

        self.permit_name_input.text = ""
        self.duration_input.text = ""
        self._pending_status_message = result.get("message", "Permit created.")
        self.invalidate_admin_screen("admin_lot_detail")
        self.load_data(force=True)

    def build_permit_list(self):
        self.permit_list.clear_widgets()

        for p in self.permits:
            row = BoxLayout(size_hint_y=None, height=40)

            duration = "N/A"
            if p.get("description"):
                try:
                    duration = p["description"].split()[0] + " days"
                except:
                    duration = "365 days"

            label = Label(
                text=f"{p['permit_name']} ({duration})",
                color=(0, 0, 0, 1),
                halign="left",
                size_hint_x=0.8
            )
            label.bind(size=label.setter("text_size"))

            in_use = p.get("usage_count", 0) > 0

            delete_btn = Button(
                text="Delete",
                size_hint_x=0.2,
                size_hint_y=None,
                height=40,
                background_normal="",
                background_color=RED if not in_use else (0.5, 0.5, 0.5, 1),
                disabled=in_use
            )

            delete_btn.bind(
                on_release=lambda x, pid=p["permit_id"]: self.confirm_delete(pid)
            )

            row.add_widget(label)
            row.add_widget(delete_btn)

            self.permit_list.add_widget(row)

    def confirm_delete(self, permit_id):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        layout.add_widget(Label(text="Delete this permit?"))

        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)

        yes = Button(
            text="Yes",
            background_normal="",
            background_color=RED,
            size_hint_y=None,
            height=40
        )
        no = Button(
            text="Cancel",
            size_hint_y=None,
            height=40
        )

        btns.add_widget(yes)
        btns.add_widget(no)
        layout.add_widget(btns)

        popup = Popup(
            title="Confirm Delete",
            content=layout,
            size_hint=(None, None),
            size=(300, 180)
        )

        yes.bind(on_release=lambda x: (popup.dismiss(), self.delete_permit_ui(permit_id)))
        no.bind(on_release=popup.dismiss)

        popup.open()

    def delete_permit_ui(self, permit_id):
        run_in_background(
            lambda: delete_permit(permit_id),
            lambda _: self.load_data(force=True)
        )

    def filter_by_permit(self, *_):
        selected = self.filter_spinner.text
        if selected == "Filter by Permit":
            self.build_users()
            return

        filtered = [
            u for u in self.users
            if u.get("permit_name") == selected
        ]

        self.build_users(filtered)

    def set_sort(self, mode):
        if mode == "permit":
            self.filter_by_permit()
            return
        self.sort_mode = mode
        self.build_users()

    def build_users(self, users_override=None):
        self.user_box.clear_widgets()

        users = users_override if users_override is not None else self.users

        if users_override is None and self.filter_spinner.text != "Filter by Permit":
            users = [
                u for u in users
                if u.get("permit_name") == self.filter_spinner.text
            ]

        if not users:
            self.user_box.add_widget(Label(
                text="No users found.",
                size_hint_y=None,
                height=50,
                color=(0.4, 0.4, 0.4, 1),
            ))
            return

        users = list(users)

        def get_exp(u):
            exp = u.get("expiration_date")
            if not exp:
                return datetime.max
            try:
                if isinstance(exp, datetime):
                    return exp
                if hasattr(exp, "year") and hasattr(exp, "month") and hasattr(exp, "day"):
                    return datetime(exp.year, exp.month, exp.day, 23, 59, 59)
                try:
                    return datetime.strptime(str(exp), "%Y-%m-%d %H:%M:%S")
                except:
                    parsed = datetime.strptime(str(exp), "%Y-%m-%d")
                    return parsed.replace(hour=23, minute=59, second=59)
            except:
                return datetime.max

        if self.sort_mode == "exp_asc":
            users.sort(key=lambda u: get_exp(u))
        elif self.sort_mode == "exp_desc":
            users.sort(key=lambda u: get_exp(u), reverse=True)

        for user in users:
            self.user_box.add_widget(self.build_user_card(user))

    def build_user_card(self, user):
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=190,
            padding=[15, 12],
            spacing=10
        )

        with card.canvas.before:
            Color(*CARD_BG)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self.update_rect, size=self.update_rect)

        exp = user.get("expiration_date")

        is_expired = False
        exp_text = "N/A"

        if exp:
            try:
                if isinstance(exp, datetime):
                    exp_dt = exp
                elif hasattr(exp, "year") and hasattr(exp, "month") and hasattr(exp, "day"):
                    exp_dt = datetime(exp.year, exp.month, exp.day, 23, 59, 59)
                else:
                    try:
                        exp_dt = datetime.strptime(str(exp), "%Y-%m-%d %H:%M:%S")
                    except:
                        exp_dt = datetime.strptime(str(exp), "%Y-%m-%d").replace(
                            hour=23,
                            minute=59,
                            second=59
                        )
                exp_text = exp_dt.strftime("%Y-%m-%d")
                if exp_dt < datetime.now():
                    is_expired = True
            except:
                exp_text = str(exp)

        status_line = f"[b][color=333333]Expires:[/color][/b] {exp_text}"

        if is_expired:
            status_line = f"[color=ff0000][b]EXPIRED[/b][/color]\n" + status_line

        info = Label(
            text=(
                f"[b]{user['first_name']} {user['last_name']} ({user['user_id']})[/b]\n"
                f"{user['email'] or 'No email'}\n"
                f"[b]Permit:[/b] {user['permit_name'] or 'None'}\n"
                f"{status_line}"
            ),
            markup=True,
            color=(0, 0, 0, 1),
            font_size=17,
            bold=True,
            halign="left",
            valign="middle"
        )
        info.bind(size=self.update_label_text_size)

        row = BoxLayout(size_hint_y=None, height=50, spacing=10, padding=[5, 5])

        spinner = Spinner(
            text="Select Permit Type",
            values=list(self.permit_map.keys()),
            size_hint_x=None,
            width=190,
            size_hint_y=None,
            height=40,
            font_size=14,
            text_size=(180, None),
            background_normal="",
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0, 0, 0, 1)
        )

        assign = Button(
            text="Assign",
            size_hint_x=None,
            width=90,
            size_hint_y=None,
            height=40,
            font_size=14,
            background_normal="",
            background_color=NAVY
        )
        revoke = Button(
            text="Revoke",
            size_hint_x=None,
            width=90,
            size_hint_y=None,
            height=40,
            font_size=14,
            background_normal="",
            background_color=RED
        )
        renew = Button(
            text="Renew",
            size_hint_x=None,
            width=90,
            size_hint_y=None,
            height=40,
            font_size=14,
            background_normal="",
            background_color=GREEN
        )
        ticket_btn = Button(
            text="Ticket",
            size_hint_x=None,
            width=90,
            size_hint_y=None,
            height=40,
            font_size=14,
            background_normal="",
            background_color=NAVY
        )

        assign.bind(on_release=lambda x: self.assign(user, spinner))
        revoke.bind(on_release=lambda x: self.revoke(user))
        renew.bind(on_release=lambda x: self.renew(user))
        ticket_btn.bind(on_release=lambda x: self.open_ticket_popup(user))

        row.add_widget(spinner)
        row.add_widget(Widget(size_hint_x=1))
        row.add_widget(assign)
        row.add_widget(revoke)
        row.add_widget(renew)
        row.add_widget(ticket_btn)

        card.add_widget(info)
        card.add_widget(row)

        return card

    def open_ticket_popup(self, user):
        content = BoxLayout(orientation="vertical", spacing=12, padding=18)

        status_label = Label(
            text="",
            size_hint_y=None,
            height=24,
            color=(0.4, 0.4, 0.4, 1),
            halign="left",
            valign="middle",
        )
        status_label.bind(size=self.update_label_text_size)
        content.add_widget(status_label)

        ticket_title = Label(
            text="Existing Tickets",
            size_hint_y=None,
            height=28,
            color=TEXT_DARK,
            bold=True,
            font_size=17,
            halign="left",
            valign="middle",
        )
        ticket_title.bind(size=self.update_label_text_size)
        content.add_widget(ticket_title)

        ticket_list = BoxLayout(orientation="vertical", spacing=9, size_hint_y=None, padding=[0, 0, 0, 4])
        ticket_list.bind(minimum_height=ticket_list.setter("height"))

        ticket_scroll = ScrollView(size_hint=(1, 0.42))
        ticket_scroll.add_widget(ticket_list)
        content.add_widget(ticket_scroll)

        separator = BoxLayout(size_hint_y=None, height=1)
        with separator.canvas.before:
            Color(0.78, 0.78, 0.78, 1)
            separator.rect = Rectangle(pos=separator.pos, size=separator.size)
        separator.bind(pos=self.update_rect, size=self.update_rect)
        content.add_widget(separator)

        form_title = Label(
            text="Add Ticket",
            size_hint_y=None,
            height=28,
            color=TEXT_DARK,
            bold=True,
            font_size=17,
            halign="left",
            valign="middle",
        )
        form_title.bind(size=self.update_label_text_size)
        content.add_widget(form_title)

        form = BoxLayout(orientation="vertical", size_hint_y=None, height=184, spacing=10)

        amount_input = TextInput(
            hint_text="Amount",
            multiline=False,
            size_hint_y=None,
            height=40,
            padding=[10, 10],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
        )
        description_input = TextInput(
            hint_text="Description",
            multiline=True,
            size_hint_y=None,
            height=84,
            padding=[10, 10],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
        )
        status_spinner = Spinner(
            text="Unpaid",
            values=["Unpaid", "Paid", "Pending"],
            size_hint_y=None,
            height=40,
            background_normal="",
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0, 0, 0, 1),
        )

        form.add_widget(amount_input)
        form.add_widget(description_input)
        form.add_widget(status_spinner)
        content.add_widget(form)

        button_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        button_row.add_widget(Widget(size_hint_x=1))
        add_btn = Button(
            text="Add Ticket",
            size_hint_x=None,
            width=120,
            size_hint_y=None,
            height=40,
            background_normal="",
            background_color=NAVY,
        )
        close_btn = Button(
            text="Close",
            size_hint_x=None,
            width=110,
            size_hint_y=None,
            height=40,
            background_normal="",
            background_color=GRAY,
        )
        button_row.add_widget(add_btn)
        button_row.add_widget(close_btn)
        content.add_widget(button_row)

        popup = Popup(
            title="User Tickets",
            content=content,
            size_hint=(0.6, 0.65),
        )

        popup_state = {
            "user": user,
            "ticket_list": ticket_list,
            "status_label": status_label,
            "amount_input": amount_input,
            "description_input": description_input,
            "status_spinner": status_spinner,
        }

        add_btn.bind(on_release=lambda *_: self.add_ticket_from_popup(popup_state))
        close_btn.bind(on_release=popup.dismiss)
        popup.bind(on_open=lambda *_: self.load_ticket_popup_list(popup_state))
        popup.open()

    def load_ticket_popup_list(self, popup_state, clear_status=True):
        ticket_list = popup_state["ticket_list"]
        status_label = popup_state["status_label"]
        ticket_list.clear_widgets()
        ticket_list.add_widget(Label(
            text="Loading tickets...",
            size_hint_y=None,
            height=40,
            color=(0.4, 0.4, 0.4, 1),
        ))
        if clear_status:
            status_label.text = ""
        user_id = popup_state["user"]["user_id"]

        run_in_background(
            lambda: get_user_tickets(user_id),
            lambda tickets: self.apply_ticket_popup_list(popup_state, tickets),
        )

    def apply_ticket_popup_list(self, popup_state, tickets):
        ticket_list = popup_state["ticket_list"]
        status_label = popup_state["status_label"]
        ticket_list.clear_widgets()

        if tickets is None:
            status_label.text = "Unable to load tickets."
            return

        if not tickets:
            ticket_list.add_widget(Label(
                text="No tickets found",
                size_hint_y=None,
                height=40,
                color=(0.4, 0.4, 0.4, 1),
            ))
            return

        for ticket in tickets:
            ticket_list.add_widget(self.build_admin_ticket_card(ticket))

    def build_admin_ticket_card(self, ticket):
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=70,
            padding=[12, 8],
            spacing=4,
        )
        with card.canvas.before:
            Color(*CARD_BG)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self.update_rect, size=self.update_rect)

        description = ticket.get("description") or "No description provided"
        label = Label(
            text=(
                f"Date: {ticket.get('issue_date')} | "
                f"${ticket.get('amount')} | "
                f"Status: {ticket.get('status')}\n"
                f"{description}"
            ),
            color=TEXT_DARK,
            halign="left",
            valign="middle",
        )
        label.bind(size=self.update_label_text_size)
        card.add_widget(label)
        return card

    def add_ticket_from_popup(self, popup_state):
        user_id = popup_state["user"]["user_id"]
        amount_input = popup_state["amount_input"]
        description_input = popup_state["description_input"]
        status_spinner = popup_state["status_spinner"]
        status_label = popup_state["status_label"]

        amount_text = amount_input.text.strip()
        description = description_input.text.strip()
        status = status_spinner.text

        if not amount_text:
            status_label.text = "Amount is required."
            return

        try:
            amount = float(amount_text)
        except ValueError:
            status_label.text = "Amount must be numeric."
            return

        if amount <= 0:
            status_label.text = "Amount must be greater than zero."
            return

        if not description:
            status_label.text = "Description is required."
            return

        status_label.text = "Adding ticket..."
        run_in_background(
            lambda: create_ticket(user_id, amount, description, status),
            lambda result: self.after_ticket_created(popup_state, result),
        )

    def after_ticket_created(self, popup_state, result):
        status_label = popup_state["status_label"]

        if not result or not result.get("ok"):
            status_label.text = result.get("message") if result else "Unable to create ticket."
            return

        popup_state["amount_input"].text = ""
        popup_state["description_input"].text = ""
        popup_state["status_spinner"].text = "Unpaid"
        status_label.text = result.get("message", "Ticket created.")
        self.load_ticket_popup_list(popup_state, clear_status=False)

    def assign(self, user, spinner):
        if spinner.text not in self.permit_map:
            return
        uid = user["user_id"]
        pid = self.permit_map[spinner.text]
        run_in_background(
            lambda: assign_permit_to_user(uid, pid),
            lambda _: self.load_data(force=True)
        )

    def revoke(self, user):
        if not user["permit_id"]:
            return
        uid, pid = user["user_id"], user["permit_id"]
        run_in_background(
            lambda: revoke_user_permit(uid, pid),
            lambda _: self.load_data(force=True)
        )

    def renew(self, user):
        if not user["permit_id"]:
            return
        uid, pid = user["user_id"], user["permit_id"]
        run_in_background(
            lambda: renew_user_permit(uid, pid),
            lambda _: self.load_data(force=True)
        )

    def run_search(self, *_):
        query = self.search_input.text.strip()
        self.load_data(query, force=True)

    def clear_search(self, *_):
        self.search_input.text = ""
        self.sort_mode = None

        if hasattr(self, "filter_spinner"):
            self.filter_spinner.text = "Filter by Permit"

        self.load_data("", force=True)

    def refresh_sidebar(self):
        self.sidebar_container.clear_widgets()
        new_sidebar = self.build_admin_sidebar(
            active_screen="admin_permits",
            section_label="Permits and Users",
        )

        self.sidebar_container.add_widget(new_sidebar)
