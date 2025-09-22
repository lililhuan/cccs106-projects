# main.py
import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact


def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.SYSTEM

    # Initialize DB connection
    db_conn = init_db()

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_button.icon = ft.Icons.LIGHT_MODE
            theme_button.tooltip = "Switch to light mode"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_button.icon = ft.Icons.DARK_MODE
            theme_button.tooltip = "Switch to dark mode"

    page.update()
    def search_contacts(e):
        search_term = search_input.value.strip()
        display_contacts(page, contacts_list_view, db_conn, search_term)

    header = ft.Row([
        ft.Text("Contact Book", size=24, weight=ft.FontWeight.BOLD),
        ft.Container(expand=True),  # Spacer
        ft.IconButton(
            icon=ft.icons.DARK_MODE,
            tooltip="Switch to Dark Mode",
            on_click=toggle_theme,
        )
    ])
    
    theme_button = header.controls[2]
    # Input fields
    name_input = ft.TextField(label="Name", width=400, prefix_icon=ft.Icons.PERSON, border_radius=10, filled=True)
    phone_input = ft.TextField(label="Phone", width=400, prefix_icon=ft.Icons.PHONE, border_radius=10, filled=True)
    email_input = ft.TextField(label="Email", width=400, prefix_icon=ft.Icons.EMAIL, border_radius=10, filled=True)
    
    inputs = (name_input, phone_input, email_input)

    search_input = ft.TextField(
        label="Search contacts...",
        width=400,
        prefix_icon=ft.icons.SEARCH,
        border_radius=10,
        filled=True,
        on_change=search_contacts
    )
    # ListView for contacts
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True, padding=ft.padding.symmetric(horizontal=10))

    # Add button
    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        height=45
    )
    # Clear button
    def clear_inputs(e):
        name_input.value = ""
        phone_input.value = ""
        email_input.value = ""
        name_input.error_text = None
        phone_input.error_text = None
        email_input.error_text = None
        page.update()
    
    clear_button = ft.OutlinedButton(
        text="Clear",
        icon=ft.icons.CLEAR,
        on_click=clear_inputs,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        height=45
    )
    
    button_row = ft.Row([
        add_button,
        clear_button
    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    
    # Layout
    page.add(
        ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                ft.Text("Add New Contact:", size=18, weight=ft.FontWeight.W_500),
                name_input,
                phone_input,
                email_input,
                button_row,
                ft.Divider(thickness=2),
                ft.Row([
                    ft.Text("Your Contacts:", size=18, weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    ft.Text("* Required field", size=12, color=ft.colors.GREY),
                ]),
                search_input,
                ft.Container(
                    content=contacts_list_view,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    padding=5
                ),
            ], spacing=10),
            padding=20
        )
    )
    
    # Display existing contacts on load
    display_contacts(page, contacts_list_view, db_conn)
    
    # Handle app closing to clean up database connection
    def on_window_event(e):
        if e.data == "close":
            close_db(db_conn)
    
    page.window_prevent_close = True
    page.on_window_event = on_window_event


if __name__ == "__main__":
    ft.app(target=main)