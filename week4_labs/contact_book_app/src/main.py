# main.py
import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact


def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.width = 450
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0

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

    theme_button = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Switch to Dark Mode",
        on_click=toggle_theme,

    )
    header = ft.Row([
        ft.Text("Contact Book", size=24, weight=ft.FontWeight.BOLD),
        ft.Container(expand=True),  # Spacer
        theme_button
    ])
    
    # Input fields
    name_input = ft.TextField(label="Name", width=400, prefix_icon=ft.Icons.PERSON, border_radius=10, filled=True, hint_text="Enter full name")
    phone_input = ft.TextField(label="Phone", width=400, prefix_icon=ft.Icons.PHONE, border_radius=10, filled=True, hint_text="Enter phone number")
    email_input = ft.TextField(label="Email", width=400, prefix_icon=ft.Icons.EMAIL, border_radius=10, filled=True, hint_text="Enter email address")
    
    inputs = (name_input, phone_input, email_input)

    search_input = ft.TextField(
        label="Search contacts...",
        width=400,
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        filled=True,
        on_change=search_contacts,
        hint_text="Type to search"
    )
    # ListView for contacts
    contacts_list_view = ft.ListView(expand=True, spacing=5, auto_scroll=False, padding=10, divider_thickness=0)

    # Add button
    add_button = ft.ElevatedButton(
        text="Add Contact",
        icon=ft.Icons.ADD,
        on_click=lambda _: add_contact(page, inputs, contacts_list_view, db_conn),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_600
        ),
        height=45,
        width=180
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
        icon=ft.Icons.CLEAR,
        on_click=clear_inputs,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            color=ft.Colors.BLUE_600
        ),
        height=45,
        width=180
    )
    
    button_row = ft.Row([
        add_button,
        clear_button
    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    
    # Layout
    main_content = ft.Column([
        # Fixed header section
        ft.Container(
            content=ft.Column([
                header,
                ft.Divider(thickness=1),
                ft.Text("Add New Contact:", size=18, weight=ft.FontWeight.W_500),
                name_input,
                phone_input,
                email_input,
                button_row,
                ft.Divider(thickness=2),
                ft.Row([
                    ft.Text("Your Contacts:", size=18, weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    ft.Text("* Required field", size=12, color=ft.Colors.GREY),
                ]),
                search_input,
            ], spacing=10),
            padding=ft.padding.all(20)
        ),
        
        # Scrollable contacts section
        ft.Container(
            content=contacts_list_view,
            expand=True,
            margin=ft.margin.symmetric(horizontal=20),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            padding=ft.padding.all(5)
        ),
        
        # Footer space
        ft.Container(height=20)
    ], 
    expand=True,
    spacing=0,
    scroll=ft.ScrollMode.AUTO  # Enable scrolling for the entire column
    )
    
    # Add main content to page
    page.add(main_content)
    
    # Initial load of contacts
    display_contacts(page, contacts_list_view, db_conn, "")

if __name__ == "__main__":
    ft.app(target=main)