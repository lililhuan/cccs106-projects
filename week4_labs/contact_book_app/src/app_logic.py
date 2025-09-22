# app_logic.py
import flet as ft
import re
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

def validate_email(email):
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    if not phone:
        return True
    pattern = r'^[\d\s\-\(\)\+]+$'
    return re.match(pattern, phone) is not None and len(phone.replace(' ', ' ').replace('-', ' ').replace('(','').replace('+', '')) >= 7
    
def show_comfirmation_dialog(page, title, content, on_confirm, on_cancel=None):
    def close_dialog(e):
        dialog.open = False
        page.update()
        if on_cancel:
            on_cancel()

    def confirm_dialog(e):
        dialog.open = False
        page.update()
        on_confirm()
        
    dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text(title),
        content = ft.Text(content),
        actions = [
            ft.TextButton("AHHHH NO DADDY", on_click=close_dialog),
            ft.ElevatedButton("AHHH YES DADDY", on_click=confirm_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()
    
def create_contact_card(contact, page, db_conn, contacts_list_view):
    contact_id, name, phone, email = contact

    contact_info = [
        ft.Row([
            ft.Icon(ft.Icons.PERSON, size = 20, color = ft.Colors.BLUE),
            ft.Text(name, size = 16, weight = ft.FontWeight.BOLD)
        ], spacing = 10)
    ]

    if phone:
        contact_info.append(
            ft.Row([
                ft.Icon(ft.Icons.PHONE, size = 16, color = ft.Colors.GREEN),
                ft.Text(phone, size = 14)
            ], spacing = 10)
        )

    if email:
        contact_info.append(
            ft.Row([
                ft.Icon(ft.Icons.EMAIL, size = 16, color = ft.Colors.ORANGE),
                ft.Text(email, size = 14)
            ], spacing = 10)
        )
def display_contacts(page, contacts_list_view, db_conn):
    """Fetches and displays all contacts in the ListView."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn)

    for contact in contacts:
        contact_id, name, phone, email = contact

        contacts_list_view.controls.append(
            ft.ListTile(
                title=ft.Text(name),
                subtitle=ft.Text(f"Phone: {phone} | Email: {email}"),
                trailing=ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(
                            text="Edit",
                            icon=ft.Icons.EDIT,
                            on_click=lambda _, c=contact: open_edit_dialog(
                                page, c, db_conn, contacts_list_view
                            ),
                        ),
                        ft.PopupMenuItem(),  # divider
                        ft.PopupMenuItem(
                            text="Delete",
                            icon=ft.Icons.DELETE,
                            on_click=lambda _, cid=contact_id: delete_contact(
                                page, cid, db_conn, contacts_list_view
                            ),
                        ),
                    ],
                ),
            )
        )

    page.update()


def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact and refreshes the list."""
    name_input, phone_input, email_input = inputs
    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)

    # clear input fields
    for field in inputs:
        field.value = ""

    display_contacts(page, contacts_list_view, db_conn)
    page.update()


def delete_contact(page, contact_id, db_conn, contacts_list_view):
    """Deletes a contact and refreshes the list."""
    delete_contact_db(db_conn, contact_id)
    display_contacts(page, contacts_list_view, db_conn)


def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact

    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        update_contact_db(
            db_conn,
            contact_id,
            edit_name.value,
            edit_phone.value,
            edit_email.value,
        )
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=lambda e: setattr(dialog, "open", False) or page.update(),
            ),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )

    page.open(dialog)
