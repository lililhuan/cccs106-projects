import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    # Configure the page
    page.window.center()
    page.window.frameless = True
    page.title = "User Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 350
    page.window.width = 400
    page.bgcolor = ft.Colors.AMBER_ACCENT
    
    # Create UI controls
    login_title = ft.Text(
        "User Login",
        text_align=ft.TextAlign.CENTER,
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        color=ft.Colors.BLACK
    )
    
    username_field = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        disabled=False,
        icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
        color=ft.Colors.BLACK
    )
    
    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        disabled=False,
        password=True,
        can_reveal_password=True,
        icon=ft.Icons.PASSWORD,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
        color=ft.Colors.BLACK
    )
    
    async def login_click(e):
        # Create Dialogs for Feedback
        success_dialog = ft.AlertDialog(
            title=ft.Text("Login Successful"),
            content=ft.Text(f"Welcome, {username_field.value}!", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: page.close(success_dialog))],
            icon=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
        )
        
        failure_dialog = ft.AlertDialog(
            title=ft.Text("Login Failed"),
            content=ft.Text("Invalid username or password", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: page.close(failure_dialog))],
            icon=ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED)
        )
        
        invalid_input_dialog = ft.AlertDialog(
            title=ft.Text("Input Error"),
            content=ft.Text("Please enter username and password", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: page.close(invalid_input_dialog))],
            icon=ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE)
        )
        
        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error"),
            content=ft.Text("An error occurred while connecting to the database", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: page.close(database_error_dialog))]
        )
        
        # Validation and Database Logic
        if not username_field.value or not password_field.value:
            page.open(invalid_input_dialog)
            return
        
        try:
            # Establish database connection
            conn = connect_db()
            cursor = conn.cursor()
            
            # Execute parameterized SQL query
            query = "SELECT * FROM user WHERE username = %s AND password = %s"
            cursor.execute(query, (username_field.value, password_field.value))
            result = cursor.fetchone()
            
            # Close database connection
            conn.close()
            
            if result:
                page.open(success_dialog)
            else:
                page.open(failure_dialog)
            
            page.update()
            
        except mysql.connector.Error:
            page.open(database_error_dialog)
            page.update()
    
    # Create the Login Button
    login_button = ft.ElevatedButton(
        text="Login",
        on_click=login_click,
        width=100,
        icon=ft.Icons.LOGIN,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK
    )
    
    # Add all controls to the page
    page.add(
        login_title,
        ft.Container(
            content=ft.Column(
                controls=[username_field, password_field],
                spacing=20
            )
        ),
        ft.Container(
            content=login_button,
            alignment=ft.alignment.top_right,
            margin=ft.margin.only(top=0, right=20, bottom=40, left=0)
        )
    )

ft.app(main)