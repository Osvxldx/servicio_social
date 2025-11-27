#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de configuración del sistema de agua potable
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .database import get_db_manager
from typing import Dict, List
import os

class ConfigurationWindow:
    def __init__(self, parent=None):
        # Crear ventana principal o usar la proporcionada
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("Configuración del Sistema")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        self.root.state('zoomed') if hasattr(self.root, 'state') else None  # Maximizar en Windows
        
        # Variables
        self.rates_vars = {}
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Cargar datos iniciales
        self.load_configuration()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal con notebook (pestañas)
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Configuración del Sistema",
            font=('Arial', 16, 'bold'),
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        # Crear notebook con pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de configuración general
        self.create_general_config_tab()
        
        # Pestaña de seguridad
        self.create_security_tab()
        
        # Botones principales
        self.create_main_buttons(main_frame)
    
    def create_general_config_tab(self):
        """Crea la pestaña de configuración general"""
        # Frame para la pestaña
        general_frame = tk.Frame(self.notebook)
        self.notebook.add(general_frame, text="Configuración General")
        
        # Frame principal con scroll
        canvas = tk.Canvas(general_frame)
        scrollbar = ttk.Scrollbar(general_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Sección de cuota mensual
        self.create_monthly_fee_section(scrollable_frame)
        
        # Sección de tarifas y multas
        self.create_rates_fines_section(scrollable_frame)
        
        # Sección de información del comité
        self.create_committee_info_section(scrollable_frame)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_monthly_fee_section(self, parent):
        """Crea la sección de configuración de cuota mensual"""
        # Frame de la sección
        fee_frame = tk.LabelFrame(parent, text="Cuota Mensual", font=('Arial', 12, 'bold'))
        fee_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame interno
        inner_frame = tk.Frame(fee_frame)
        inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Cuota actual
        current_frame = tk.Frame(inner_frame)
        current_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(current_frame, text="Cuota actual:", font=('Arial', 11)).pack(side=tk.LEFT)
        
        self.current_fee_label = tk.Label(
            current_frame,
            text="$0.00",
            font=('Arial', 11, 'bold'),
            fg='#27ae60'
        )
        self.current_fee_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Nueva cuota
        new_frame = tk.Frame(inner_frame)
        new_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(new_frame, text="Nueva cuota:", font=('Arial', 11)).pack(side=tk.LEFT)
        
        self.new_fee_var = tk.StringVar()
        self.new_fee_entry = tk.Entry(
            new_frame,
            textvariable=self.new_fee_var,
            font=('Arial', 11),
            width=15
        )
        self.new_fee_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Label(new_frame, text="$", font=('Arial', 11)).pack(side=tk.LEFT)
        
        # Botón actualizar cuota
        update_fee_btn = tk.Button(
            inner_frame,
            text="Actualizar Cuota Mensual",
            command=self.update_monthly_fee,
            bg='#3498db',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        update_fee_btn.pack(pady=10)
        
        # Información adicional
        info_label = tk.Label(
            inner_frame,
            text="La nueva cuota se aplicará a partir del próximo pago registrado.",
            font=('Arial', 9),
            fg='#7f8c8d',
            wraplength=400
        )
        info_label.pack(pady=(0, 5))

    def create_rates_fines_section(self, parent):
        """Crea la sección de tarifas y multas"""
        frame = tk.LabelFrame(parent, text="Tarifas y Multas", font=('Arial', 12, 'bold'))
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        inner_frame = tk.Frame(frame)
        inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        fields = [
            ("Costo por Vaca:", "costo_vacas"),
            ("Costo por Inquilino:", "costo_inquilinos"),
            ("Costo Cooperación:", "costo_cooperacion"),
            ("Costo Toma Nueva:", "costo_toma_nueva"),
            ("Multa por Retraso:", "multa_retraso"),
            ("Multa por Inasistencia:", "multa_inasistencia")
        ]
        
        self.rates_vars = {}
        
        for i, (label_text, key) in enumerate(fields):
            row_frame = tk.Frame(inner_frame)
            row_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(row_frame, text=label_text, width=20, anchor='w').pack(side=tk.LEFT)
            
            var = tk.StringVar()
            self.rates_vars[key] = var
            
            entry = tk.Entry(row_frame, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            
            tk.Label(row_frame, text="$").pack(side=tk.LEFT)
            
        btn = tk.Button(inner_frame, text="Actualizar Tarifas", command=self.update_rates, bg='#3498db', fg='white')
        btn.pack(pady=10)

    def update_rates(self):
        try:
            db = get_db_manager()
            for key, var in self.rates_vars.items():
                value = var.get().strip()
                if value:
                    try:
                        float(value) # Validate number
                        db.actualizar_configuracion(key, value)
                    except ValueError:
                        messagebox.showwarning("Error", f"Valor inválido para {key}")
                        return
            messagebox.showinfo("Éxito", "Tarifas actualizadas")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def create_committee_info_section(self, parent):
        """Crea la sección de información del comité"""
        # Frame de la sección
        info_frame = tk.LabelFrame(parent, text="Información del Comité", font=('Arial', 12, 'bold'))
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame interno
        inner_frame = tk.Frame(info_frame)
        inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Campos de información
        fields = [
            ("Nombre del Comité:", "committee_name"),
            ("Dirección:", "committee_address"),
            ("Teléfono:", "committee_phone"),
            ("Presidente:", "committee_president"),
            ("Tesorero:", "committee_treasurer")
        ]
        
        self.committee_vars = {}
        
        for label_text, var_name in fields:
            field_frame = tk.Frame(inner_frame)
            field_frame.pack(fill=tk.X, pady=3)
            
            label = tk.Label(field_frame, text=label_text, font=('Arial', 10), width=18, anchor='w')
            label.pack(side=tk.LEFT)
            
            var = tk.StringVar()
            entry = tk.Entry(field_frame, textvariable=var, font=('Arial', 10))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            
            self.committee_vars[var_name] = var
        
        # Botón actualizar información
        update_info_btn = tk.Button(
            inner_frame,
            text="Actualizar Información",
            command=self.update_committee_info,
            bg='#9b59b6',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        update_info_btn.pack(pady=(15, 5))
    
    def create_security_tab(self):
        """Crea la pestaña de configuración de seguridad"""
        # Frame para la pestaña
        security_frame = tk.Frame(self.notebook)
        self.notebook.add(security_frame, text="Seguridad")
        
        # Frame para cambio de PIN
        pin_frame = tk.LabelFrame(security_frame, text="Cambio de PIN de Acceso", font=('Arial', 12, 'bold'))
        pin_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame interno
        inner_frame = tk.Frame(pin_frame)
        inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # PIN actual
        current_pin_frame = tk.Frame(inner_frame)
        current_pin_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(current_pin_frame, text="PIN actual:", font=('Arial', 11), width=15, anchor='w').pack(side=tk.LEFT)
        
        self.current_pin_var = tk.StringVar()
        current_pin_entry = tk.Entry(
            current_pin_frame,
            textvariable=self.current_pin_var,
            show="*",
            font=('Arial', 11),
            width=15
        )
        current_pin_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Nuevo PIN
        new_pin_frame = tk.Frame(inner_frame)
        new_pin_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(new_pin_frame, text="Nuevo PIN:", font=('Arial', 11), width=15, anchor='w').pack(side=tk.LEFT)
        
        self.new_pin_var = tk.StringVar()
        new_pin_entry = tk.Entry(
            new_pin_frame,
            textvariable=self.new_pin_var,
            show="*",
            font=('Arial', 11),
            width=15
        )
        new_pin_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Confirmar nuevo PIN
        confirm_pin_frame = tk.Frame(inner_frame)
        confirm_pin_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(confirm_pin_frame, text="Confirmar PIN:", font=('Arial', 11), width=15, anchor='w').pack(side=tk.LEFT)
        
        self.confirm_pin_var = tk.StringVar()
        confirm_pin_entry = tk.Entry(
            confirm_pin_frame,
            textvariable=self.confirm_pin_var,
            show="*",
            font=('Arial', 11),
            width=15
        )
        confirm_pin_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botón cambiar PIN
        change_pin_btn = tk.Button(
            inner_frame,
            text="Cambiar PIN",
            command=self.change_pin,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        change_pin_btn.pack(pady=15)
        
        # Información de seguridad
        security_info = tk.Label(
            inner_frame,
            text="IMPORTANTE: Mantenga su PIN seguro y no lo comparta con personas no autorizadas.\n" +
                 "El PIN debe tener entre 4 y 8 dígitos.",
            font=('Arial', 9),
            fg='#7f8c8d',
            wraplength=500,
            justify=tk.LEFT
        )
        security_info.pack(pady=(0, 10))
        
        # Frame para respaldo y restauración
        backup_frame = tk.LabelFrame(security_frame, text="Respaldo de Datos", font=('Arial', 12, 'bold'))
        backup_frame.pack(fill=tk.X, padx=10, pady=10)
        
        backup_inner = tk.Frame(backup_frame)
        backup_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Botones de respaldo
        backup_btn = tk.Button(
            backup_inner,
            text="Crear Respaldo",
            command=self.create_backup,
            bg='#2ecc71',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        backup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        restore_btn = tk.Button(
            backup_inner,
            text="Restaurar Respaldo",
            command=self.restore_backup,
            bg='#f39c12',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        restore_btn.pack(side=tk.LEFT)
        
        # Información sobre respaldos
        backup_info = tk.Label(
            backup_inner,
            text="Se recomienda crear respaldos regulares de la base de datos.",
            font=('Arial', 9),
            fg='#7f8c8d'
        )
        backup_info.pack(pady=(10, 0))
    
    def create_main_buttons(self, parent):
        """Crea los botones principales"""
        buttons_frame = tk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botón cerrar
        close_btn = tk.Button(
            buttons_frame,
            text="Cerrar",
            command=self.root.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 12),
            height=2
        )
        close_btn.pack(side=tk.RIGHT)
    
    # === FUNCIONES DE CONFIGURACIÓN GENERAL ===
    
    def load_configuration(self):
        """Carga la configuración actual"""
        try:
            db = get_db_manager()
            
            # Cargar cuota mensual
            monthly_fee = db.obtener_configuracion('cuota_mensual')
            if monthly_fee:
                self.current_fee_label.config(text=f"${float(monthly_fee):.2f}")
            
            # Cargar tarifas y multas
            defaults = {
                'costo_vacas': '0.0',
                'costo_inquilinos': '0.0',
                'costo_cooperacion': '100.0',
                'costo_toma_nueva': '500.0',
                'multa_retraso': '100.0',
                'multa_inasistencia': '200.0'
            }
            
            for key, var in self.rates_vars.items():
                val = db.obtener_configuracion(key)
                if val:
                    var.set(val)
                else:
                    var.set(defaults.get(key, '0.0'))

            # Cargar información del comité
            committee_fields = [
                'committee_name', 'committee_address', 'committee_phone',
                'committee_president', 'committee_treasurer'
            ]
            
            for field in committee_fields:
                value = db.obtener_configuracion(field)
                if field in self.committee_vars and value:
                    self.committee_vars[field].set(value)
                    
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
    
    def update_monthly_fee(self):
        """Actualiza la cuota mensual"""
        new_fee_str = self.new_fee_var.get().strip()
        
        if not new_fee_str:
            messagebox.showwarning("Dato requerido", "Ingrese la nueva cuota mensual")
            return
        
        try:
            new_fee = float(new_fee_str)
            if new_fee <= 0:
                messagebox.showwarning("Valor inválido", "La cuota debe ser mayor a cero")
                return
            
            # Confirmar cambio
            if messagebox.askyesno("Confirmar Cambio",
                                 f"¿Confirma cambiar la cuota mensual a ${new_fee:.2f}?"):
                db = get_db_manager()
                if db.actualizar_configuracion('cuota_mensual', str(new_fee)):
                    self.current_fee_label.config(text=f"${new_fee:.2f}")
                    self.new_fee_var.set("")
                    messagebox.showinfo("Éxito", "Cuota mensual actualizada correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la cuota")
                    
        except ValueError:
            messagebox.showwarning("Valor inválido", "Ingrese un valor numérico válido")
    
    def update_committee_info(self):
        """Actualiza la información del comité"""
        try:
            db = get_db_manager()
            
            # Actualizar cada campo
            for field_name, var in self.committee_vars.items():
                value = var.get().strip()
                db.actualizar_configuracion(field_name, value)
            
            messagebox.showinfo("Éxito", "Información del comité actualizada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar información: {str(e)}")
    
    # === FUNCIONES DE SEGURIDAD ===
    
    def change_pin(self):
        """Cambia el PIN de acceso"""
        current_pin = self.current_pin_var.get().strip()
        new_pin = self.new_pin_var.get().strip()
        confirm_pin = self.confirm_pin_var.get().strip()
        
        if not current_pin or not new_pin or not confirm_pin:
            messagebox.showwarning("Datos incompletos", "Complete todos los campos")
            return
        
        # Validar PIN actual
        try:
            db = get_db_manager()
            if not db.verificar_pin(current_pin):
                messagebox.showerror("PIN incorrecto", "El PIN actual no es correcto")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar PIN: {str(e)}")
            return
        
        # Validar nuevo PIN
        if len(new_pin) < 4 or len(new_pin) > 8:
            messagebox.showwarning("PIN inválido", "El PIN debe tener entre 4 y 8 dígitos")
            return
        
        if not new_pin.isdigit():
            messagebox.showwarning("PIN inválido", "El PIN debe contener solo números")
            return
        
        if new_pin != confirm_pin:
            messagebox.showerror("PIN no coincide", "El nuevo PIN y la confirmación no coinciden")
            return
        
        # Confirmar cambio
        if messagebox.askyesno("Confirmar Cambio",
                             "¿Confirma cambiar el PIN de acceso?\n\n" +
                             "IMPORTANTE: No olvide el nuevo PIN."):
            try:
                if db.actualizar_configuracion('pin_acceso', new_pin):
                    messagebox.showinfo("Éxito", "PIN cambiado correctamente")
                    
                    # Limpiar campos
                    self.current_pin_var.set("")
                    self.new_pin_var.set("")
                    self.confirm_pin_var.set("")
                else:
                    messagebox.showerror("Error", "No se pudo cambiar el PIN")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al cambiar PIN: {str(e)}")

    def create_backup(self):
        """Crea un respaldo de la base de datos"""
        try:
            from tkinter import filedialog
            import sqlite3
            from datetime import datetime
            
            # Seleccionar ubicación para el respaldo
            default_name = f"agua_potable_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = filedialog.asksaveasfilename(
                title="Guardar respaldo como...",
                defaultextension=".db",
                filetypes=[("Base de datos SQLite", "*.db"), ("Todos los archivos", "*.*")],
                initialvalue=default_name
            )
            
            if backup_path:
                # Determinar ruta de la BD
                db_path = os.path.abspath("agua_potable.db")
                if not os.path.exists(db_path):
                    # Intentar en el directorio del script
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    db_path = os.path.join(script_dir, "agua_potable.db")
                
                if not os.path.exists(db_path):
                    raise FileNotFoundError(f"No se encuentra la base de datos en: {db_path}")

                # Usar la API de respaldo de SQLite
                source_conn = sqlite3.connect(db_path)
                dest_conn = sqlite3.connect(backup_path)
                
                with dest_conn:
                    source_conn.backup(dest_conn)
                
                dest_conn.close()
                source_conn.close()
                
                messagebox.showinfo("Éxito", f"Respaldo creado correctamente en:\n{backup_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear respaldo: {str(e)}")

    def restore_backup(self):
        """Restaura un respaldo de la base de datos"""
        try:
            from tkinter import filedialog
            import sqlite3
            
            # Seleccionar archivo de respaldo
            backup_path = filedialog.askopenfilename(
                title="Seleccionar archivo de respaldo",
                filetypes=[("Base de datos SQLite", "*.db"), ("Todos los archivos", "*.*")]
            )
            
            if not backup_path:
                return
                
            if messagebox.askyesno("Confirmar Restauración", 
                                 "ADVERTENCIA: Esta acción reemplazará todos los datos actuales con los del respaldo.\n" +
                                 "¿Está seguro de que desea continuar?"):
                
                # Determinar ruta de la BD
                db_path = os.path.abspath("agua_potable.db")
                if not os.path.exists(db_path):
                    # Intentar en el directorio del script
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    db_path = os.path.join(script_dir, "agua_potable.db")
                
                # Usar la API de respaldo de SQLite (al revés)
                source_conn = sqlite3.connect(backup_path)
                dest_conn = sqlite3.connect(db_path)
                
                with dest_conn:
                    source_conn.backup(dest_conn)
                
                dest_conn.close()
                source_conn.close()
                
                messagebox.showinfo("Éxito", "Base de datos restaurada correctamente.\nEl sistema se cerrará para aplicar los cambios.")
                self.root.quit()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar respaldo: {str(e)}")