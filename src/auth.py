#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pantalla de autenticación con PIN para el sistema de agua potable
"""

import tkinter as tk
from tkinter import messagebox
from .database import get_db_manager

class LoginWindow:
    def __init__(self, parent=None):
        self.parent = parent
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("Sistema de Agua Potable - Acceso")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centrar la ventana
        self.center_window()
        
        # Variables
        self.pin_var = tk.StringVar()
        self.authenticated = False
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Configurar eventos
        self.root.bind('<Return>', lambda e: self.verify_pin())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        if parent:
            self.root.grab_set()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Sistema de Gestión\nAgua Potable",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # Subtítulo
        subtitle_label = tk.Label(
            main_frame,
            text="Ingrese su PIN de acceso",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#34495e'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Frame para el PIN
        pin_frame = tk.Frame(main_frame, bg='#f0f0f0')
        pin_frame.pack(pady=10)
        
        # Campo de PIN
        self.pin_entry = tk.Entry(
            pin_frame,
            textvariable=self.pin_var,
            show="*",
            font=('Arial', 14),
            width=15,
            justify='center',
            relief=tk.RAISED,
            bd=2
        )
        self.pin_entry.pack(pady=10)
        self.pin_entry.focus()
        
        # Frame para botones
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # Botón de ingresar
        login_btn = tk.Button(
            button_frame,
            text="Ingresar",
            command=self.verify_pin,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        )
        login_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón de salir
        exit_btn = tk.Button(
            button_frame,
            text="Salir",
            command=self.on_closing,
            font=('Arial', 12),
            bg='#e74c3c',
            fg='white',
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        )
        exit_btn.pack(side=tk.LEFT, padx=5)
        
        # Teclado numérico
        self.create_numeric_keypad(main_frame)
    
    def create_numeric_keypad(self, parent):
        """Crea un teclado numérico virtual"""
        keypad_frame = tk.Frame(parent, bg='#f0f0f0')
        keypad_frame.pack(pady=20)
        
        # Botones del teclado
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['C', '0', '⌫']
        ]
        
        for i, row in enumerate(buttons):
            row_frame = tk.Frame(keypad_frame, bg='#f0f0f0')
            row_frame.pack()
            
            for j, btn_text in enumerate(row):
                if btn_text == 'C':
                    cmd = self.clear_pin
                    bg_color = '#f39c12'
                elif btn_text == '⌫':
                    cmd = self.backspace_pin
                    bg_color = '#f39c12'
                else:
                    cmd = lambda x=btn_text: self.add_digit(x)
                    bg_color = '#ecf0f1'
                
                btn = tk.Button(
                    row_frame,
                    text=btn_text,
                    command=cmd,
                    font=('Arial', 12, 'bold'),
                    bg=bg_color,
                    width=4,
                    height=2,
                    relief=tk.RAISED,
                    bd=1
                )
                btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def add_digit(self, digit):
        """Añade un dígito al PIN"""
        current_pin = self.pin_var.get()
        if len(current_pin) < 6:  # Limitar a 6 dígitos máximo
            self.pin_var.set(current_pin + digit)
    
    def clear_pin(self):
        """Limpia el campo PIN"""
        self.pin_var.set("")
    
    def backspace_pin(self):
        """Elimina el último dígito del PIN"""
        current_pin = self.pin_var.get()
        if current_pin:
            self.pin_var.set(current_pin[:-1])
    
    def verify_pin(self):
        """Verifica el PIN ingresado"""
        pin = self.pin_var.get().strip()
        
        if not pin:
            messagebox.showwarning("Advertencia", "Por favor ingrese su PIN")
            return
        
        try:
            db = get_db_manager()
            
            if db.verificar_pin(pin):
                self.authenticated = True
                self.root.destroy()
            else:
                messagebox.showerror("Error", "PIN incorrecto")
                self.pin_var.set("")
                self.pin_entry.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar PIN: {str(e)}")
    
    def on_closing(self):
        """Maneja el cierre de la ventana"""
        self.root.destroy()
    
    def show(self):
        """Muestra la ventana y devuelve si se autenticó correctamente"""
        if self.parent:
            self.root.wait_window()
        else:
            self.root.mainloop()
        
        return self.authenticated


def authenticate(parent=None):
    """Función principal para autenticar al usuario"""
    login_window = LoginWindow(parent)
    return login_window.show()


if __name__ == "__main__":
    # Test de la ventana de login
    if authenticate():
        print("Autenticación exitosa")
    else:
        print("Autenticación fallida")