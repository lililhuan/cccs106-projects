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
    return re.match(pattern, phone) is not None and len(phone.replace(' ', ' ').replace('-', ' ').replace('(','').replace(')','').replace('+', '')) >= 7
    
def show_confirmation_dialog(page, title, content, on_confirm, on_cancel=None):
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
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.ElevatedButton("Delete", on_click=confirm_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
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
    def handle_edit(e):
        open_edit_dialog(page, contact, db_conn, contacts_list_view)

    def handle_delete(e):
        confirm_delete_contact(page, contact_id, name, db_conn, contacts_list_view)   

    popup_menu = ft.PopupMenuButton(
        icon = ft.Icons.MORE_VERT,
        items = [
            ft.PopupMenuItem(
                text = "EDIT",
                icon = ft.Icons.EDIT,
                on_click = handle_edit
            ),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(
                text = "DELETE",
                icon = ft.Icons.DELETE,
                on_click = handle_delete
            ),
        ],
    )

    return ft.Card(
        content = ft.Container(
            content = ft.Row([
                ft.Column(contact_info, spacing = 5, expand = True),
                popup_menu
            ], alignment = ft.MainAxisAlignment.SPACE_BETWEEN),
            padding = 15,
        ),
        elevation = 2,
        margin =ft.margin.symmetric(vertical=2)
    )

def confirm_delete_contact (page, contact_id, name, db_conn, contacts_list_view):
    show_confirmation_dialog(
        page,
        "Delete Contact",
        f"Are you sure you want to delete '{name}'?",
        lambda: delete_contact(page, contact_id, db_conn, contacts_list_view)
    )
    
def display_contacts(page, contacts_list_view, db_conn, search_term = ""):
    """Fetches and displays all contacts in the ListView."""
    contacts_list_view.controls.clear()
    
    if search_term:
        contacts = [c for c in get_all_contacts_db(db_conn)
                    if search_term.lower() in c[1].lower()]
    else:
        contacts = get_all_contacts_db(db_conn)\

    if contacts:
        for contact in contacts:
            contact_card = create_contact_card(contact, page, db_conn, contacts_list_view)
            contacts_list_view.controls.append(contact_card)
    else:
        no_contacts_text = "No contacts found." if search_term else "No contacts yet. Add your first contacts above!"
        contacts_list_view.controls.append(
            ft.Container(
                content=ft.Text(
                    no_contacts_text,
                    size=16,
                    color=ft.Colors.GREY,
                    text_align=ft.TextAlign.CENTER
                ),
                alignment=ft.alignment.center,
                padding=20
            )
        )

    page.update()


def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact and refreshes the list."""
    name_input, phone_input, email_input = inputs

    name_input.error_text = None
    phone_input.error_text = None
    email_input.error_text = None
    
    name = name_input.value.strip() if name_input.value else ""
    phone = phone_input.value.strip() if phone_input.value else ""
    email = email_input.value.strip() if email_input.value else ""
    
    has_error = False
    
    if not name:
        name_input.error_text = "Name cannot be empty"
        has_error = True
    
    if phone and not validate_phone(phone):
        phone_input.error_text = "Invalid phone format"
        has_error = True
    
    if email and not validate_email(email):
        email_input.error_text = "Invalid email format"
        has_error = True
    
    if has_error:
        page.update()
        return
    
    try:
        add_contact_db(db_conn, name, phone or None, email or None)
        
        # Clear input fields (keeping your original approach)
        for field in inputs:
            field.value = ""
            field.error_text = None
        
        display_contacts(page, contacts_list_view, db_conn)

        page.snack_bar = ft.SnackBar(content=ft.Text("Contact added successfully!"), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True
    except Exception as e:
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Error adding contact: {str(e)}"), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
    page.update()

def delete_contact(page, contact_id, db_conn, contacts_list_view):
    """Deletes a contact and refreshes the list."""
    try:
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn)

        page.snack_bar = ft.SnackBar(content=ft.Text("Contact deleted successfully!"), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True
    except Exception as e:
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Error deleting contact: {str(e)}"), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
    page.update()

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact

    edit_name = ft.TextField(
        label="Name",
        value=name,
        width=350,
        prefix_icon=ft.Icons.PERSON,
        border_radius=10,
        filled=True
    )
    edit_phone = ft.TextField(
        label="Phone",
        value=phone or "",
        width=350,
        prefix_icon=ft.Icons.PHONE,
        border_radius=10,
        filled=True
    )
    edit_email = ft.TextField(
        label="Email",
        value=email or "",
        width=350,
        prefix_icon=ft.Icons.EMAIL,
        border_radius=10,
        filled=True
    )
    def cancel_edit(e):
        dialog.open = False
        page.update()

    def save_and_close(e):
        edit_name.error_text = None
        edit_phone.error_text = None  
        edit_email.error_text = None
        
        # Get values
        new_name = edit_name.value.strip() if edit_name.value else ""
        new_phone = edit_phone.value.strip() if edit_phone.value else ""
        new_email = edit_email.value.strip() if edit_email.value else ""
        
        # Validation
        has_error = False
        
        if not new_name:
            edit_name.error_text = "Name is required"
            has_error = True
            
        if new_phone and not validate_phone(new_phone):
            edit_phone.error_text = "Invalid phone format"
            has_error = True
            
        if new_email and not validate_email(new_email):
            edit_email.error_text = "Invalid email format"
            has_error = True
            
        if has_error:
            page.update()
            return
        
        # Update contact
        try:
            update_contact_db(
                db_conn,
                contact_id,
                new_name,
                new_phone or None,
                new_email or None,
            )
            dialog.open = False
            page.update()
            display_contacts(page, contacts_list_view, db_conn)

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Contact updated successfully!"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
        except Exception as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error updating contact: {str(e)}"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()

    # Enhanced dialog with better styling
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact", size=20, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                edit_name, 
                edit_phone, 
                edit_email,
                ft.Text("* Required field", size=12, color=ft.Colors.GREY)
            ], tight=True, spacing=15),
            width=400,
            height=300
        ),
        actions=[
            ft.OutlinedButton(
                "Cancel",
                on_click=cancel_edit,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
            ),
            ft.ElevatedButton(
                "Save Changes",
                on_click=save_and_close,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
