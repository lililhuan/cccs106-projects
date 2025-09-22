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

    popup_menu = ft.PopupMenuButton(
        icon = ft.Icons.MORE_VERT,
        items = [
            ft.PopupMenuItem(
                text = "Edit",
                icon = ft.Icons.EDIT,
                on_click = lambda _: open_edit_dialog (
                    page, contact, db_conn, contacts_list_view
                ),
            ),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(
                text = "DELETE",
                icon = ft.icons.DELETE,
                on_click = lambda _: confirm_delete_contact (
                    page, contact_id, name, db_conn, contacts_list_view
                ),
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
        elavaation = 2,
        margin =ft.margin.symmetric(vertical=2)
    )

def confirm_delete_contact (page, contact_id, name, db_conn, contacts_list_view):
    show_comfirmation_dialog(
        page,
        "Dete Contact",
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
        contacts = get_all_contacts_db(db_conn)
    if contacts:
        for contact in contacts:
            contact_card = create_contact_card(contact, page, db_conn, contacts_list_view)
            contacts_list_view.controls.apped(contact_card)
    else:
        no_contacts_text = "No contacts found." if search_term else "No contacts yet. Add your fist contacts above!"
        contacts_list_view.controls.append(
            ft.Container(
                content=ft.Text(
                    no_contacts_text,
                    size=16,
                    color=ft.colors.GREY,
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
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Contact added successfully!")))
        
    except Exception as e:
        page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error adding contact: {str(e)}")))
    
    page.update()

def delete_contact(page, contact_id, db_conn, contacts_list_view):
    """Deletes a contact and refreshes the list."""
    try:
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn)
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Contact deleted successfully!")))
    except Exception as e:
        page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error deleting contact: {str(e)}")))

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact

    edit_name = ft.TextField(label="Name", value=name, width=300)
    edit_phone = ft.TextField(label="Phone", value=phone or "", width=300)
    edit_email = ft.TextField(label="Email", value=email or "", width=300)

    def save_and_close(e):
        # Clear previous errors
        edit_name.error_text = None
        edit_phone.error_text = None  
        edit_email.error_text = None
        
        # Validation
        has_error = False
        
        if not edit_name.value.strip():
            edit_name.error_text = "Name cannot be empty"
            has_error = True
            
        if edit_phone.value and not validate_phone(edit_phone.value):
            edit_phone.error_text = "Invalid phone format"
            has_error = True
            
        if edit_email.value and not validate_email(edit_email.value):
            edit_email.error_text = "Invalid email format"
            has_error = True
            
        if has_error:
            page.update()
            return
        
        # Use your existing update function
        try:
            update_contact_db(
                db_conn,
                contact_id,
                edit_name.value.strip(),
                edit_phone.value.strip() or None,
                edit_email.value.strip() or None,
            )
            dialog.open = False
            page.update()
            display_contacts(page, contacts_list_view, db_conn)
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Contact updated successfully!")))
        except Exception as e:
            page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error updating contact: {str(e)}")))

    # Enhanced dialog with better styling
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([
            edit_name, 
            edit_phone, 
            edit_email
        ], tight=True, spacing=10),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=lambda e: setattr(dialog, "open", False) or page.update(),
            ),
            ft.ElevatedButton("Save", on_click=save_and_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()
