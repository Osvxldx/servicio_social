#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de registro de pagos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar
from .database import get_db_manager
from .receipt_generator import ReceiptGenerator
import os

class PaymentRegistrationWindow:
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
            
        self.root.title("Registro de Pagos")
        self.root.geometry("1200x700")
        self.root.state('zoomed') if hasattr(self.root, 'state') else None
        
        self.db = get_db_manager()
        self.receipt_gen = ReceiptGenerator()
        
        # Variables de estado
        self.current_user = None
        self.selected_months = set()
        self.cart_items = []
        self.total_amount = 0.0
        
        # Variables de configuración
        self.load_config_values()
        
        self.setup_ui()
        
    def load_config_values(self):
        """Carga valores de configuración necesarios"""
        self.monthly_fee = float(self.db.obtener_configuracion('cuota_mensual') or 70.0)
        self.cost_vacas = float(self.db.obtener_configuracion('costo_vacas') or 0.0)
        self.cost_inquilinos = float(self.db.obtener_configuracion('costo_inquilinos') or 0.0)
        self.cost_cooperacion = float(self.db.obtener_configuracion('costo_cooperacion') or 50.0)
        self.cost_toma_nueva = float(self.db.obtener_configuracion('costo_toma_nueva') or 3000.0)
        self.fine_absence = float(self.db.obtener_configuracion('multa_inasistencia') or 200.0)

    def setup_ui(self):
        # Header con botón Volver
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="Registro de Pagos", 
            font=('Arial', 20, 'bold'), 
            fg='white', 
            bg='#2c3e50'
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            header_frame,
            text="Volver al Menú",
            command=self.root.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.RIGHT, padx=20)

        # Contenedor principal
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel Izquierdo
        left_panel = tk.Frame(main_container, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.create_search_panel(left_panel)
        self.create_user_info_panel(left_panel)
        
        # Panel Central
        center_panel = tk.Frame(main_container)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.create_months_panel(center_panel)
        self.create_extras_panel(center_panel)
        
        # Panel Derecho
        right_panel = tk.Frame(main_container, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.create_summary_panel(right_panel)

    def create_search_panel(self, parent):
        frame = tk.LabelFrame(parent, text="Buscar Usuario", font=('Arial', 10, 'bold'))
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Búsqueda por nombre o ID
        tk.Label(frame, text="Nombre o ID:").pack(anchor='w', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        tk.Entry(frame, textvariable=self.search_var).pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Lista de resultados
        self.results_list = tk.Listbox(frame, height=6)
        self.results_list.pack(fill=tk.X, padx=5, pady=5)
        self.results_list.bind('<<ListboxSelect>>', self.on_user_select)

    def create_user_info_panel(self, parent):
        self.info_frame = tk.LabelFrame(parent, text="Información del Usuario", font=('Arial', 10, 'bold'))
        self.info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.lbl_nombre = tk.Label(self.info_frame, text="Seleccione un usuario", font=('Arial', 12, 'bold'), wraplength=280)
        self.lbl_nombre.pack(pady=10)
        
        details_frame = tk.Frame(self.info_frame)
        details_frame.pack(fill=tk.X, padx=5)
        
        self.lbl_id = tk.Label(details_frame, text="ID: -")
        self.lbl_id.pack(anchor='w')
        
        self.lbl_direccion = tk.Label(details_frame, text="Dirección: -", wraplength=280, justify=tk.LEFT)
        self.lbl_direccion.pack(anchor='w')
        
        self.lbl_vacas = tk.Label(details_frame, text="Vacas: 0")
        self.lbl_vacas.pack(anchor='w')
        
        self.lbl_inquilinos = tk.Label(details_frame, text="Inquilinos: 0")
        self.lbl_inquilinos.pack(anchor='w')
        
        # Historial reciente
        tk.Label(self.info_frame, text="\nÚltimos Pagos:", font=('Arial', 9, 'bold')).pack(anchor='w', padx=5)
        self.history_list = tk.Listbox(self.info_frame, height=8, bg='#f0f0f0')
        self.history_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_months_panel(self, parent):
        frame = tk.LabelFrame(parent, text="Selección de Meses", font=('Arial', 10, 'bold'))
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selector de año
        year_frame = tk.Frame(frame)
        year_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(year_frame, text="Año:").pack(side=tk.LEFT)
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_spin = ttk.Spinbox(year_frame, from_=2020, to=2030, textvariable=self.year_var, width=5)
        year_spin.pack(side=tk.LEFT, padx=5)
        year_spin.bind('<ButtonRelease-1>', self.refresh_months_grid)
        
        # Botón Año Completo
        tk.Button(year_frame, text="Seleccionar Año Completo", command=self.select_full_year, 
                 bg='#3498db', fg='white').pack(side=tk.RIGHT)
        
        # Grid de meses
        self.months_frame = tk.Frame(frame)
        self.months_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.month_buttons = {}
        self.refresh_months_grid()

    def create_extras_panel(self, parent):
        frame = tk.LabelFrame(parent, text="Cargos Adicionales", font=('Arial', 10, 'bold'))
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Checkboxes para extras
        self.var_cooperacion = tk.BooleanVar()
        self.var_toma_nueva = tk.BooleanVar()
        
        tk.Checkbutton(frame, text=f"Cooperación (${self.cost_cooperacion:.2f})", 
                      variable=self.var_cooperacion, command=self.update_cart).pack(anchor='w', padx=10, pady=2)
        
        tk.Checkbutton(frame, text=f"Toma Nueva (${self.cost_toma_nueva:.2f})", 
                      variable=self.var_toma_nueva, command=self.update_cart).pack(anchor='w', padx=10, pady=2)
        
        # Multa por Inasistencia (Spinbox 0-6)
        inasistencia_frame = tk.Frame(frame)
        inasistencia_frame.pack(anchor='w', padx=10, pady=2)
        
        tk.Label(inasistencia_frame, text=f"Inasistencias (${self.fine_absence:.2f} c/u):").pack(side=tk.LEFT)
        
        self.var_inasistencia = tk.IntVar(value=0)
        self.spin_inasistencia = ttk.Spinbox(inasistencia_frame, from_=0, to=6, 
                                           textvariable=self.var_inasistencia, width=5,
                                           command=self.update_cart)
        self.spin_inasistencia.pack(side=tk.LEFT, padx=5)
        self.spin_inasistencia.bind('<KeyRelease>', lambda e: self.update_cart())
        self.spin_inasistencia.bind('<<Increment>>', lambda e: self.update_cart())
        self.spin_inasistencia.bind('<<Decrement>>', lambda e: self.update_cart())

    def create_summary_panel(self, parent):
        frame = tk.LabelFrame(parent, text="Resumen de Pago", font=('Arial', 12, 'bold'))
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de items en el carrito
        self.cart_tree = ttk.Treeview(frame, columns=('Concepto', 'Importe'), show='headings', height=15)
        self.cart_tree.heading('Concepto', text='Concepto')
        self.cart_tree.heading('Importe', text='Importe')
        self.cart_tree.column('Concepto', width=200)
        self.cart_tree.column('Importe', width=80, anchor='e')
        self.cart_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Total
        total_frame = tk.Frame(frame, bg='#ecf0f1')
        total_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(total_frame, text="TOTAL A PAGAR:", font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_total = tk.Label(total_frame, text="$0.00", font=('Arial', 16, 'bold'), fg='#e74c3c', bg='#ecf0f1')
        self.lbl_total.pack(side=tk.RIGHT, padx=10)
        
        # Botón Pagar
        self.btn_pagar = tk.Button(frame, text="REGISTRAR PAGO", command=self.process_payment,
                                 bg='#2ecc71', fg='white', font=('Arial', 14, 'bold'), state='disabled')
        self.btn_pagar.pack(fill=tk.X, padx=10, pady=10)

    # === LÓGICA ===

    def on_search_change(self, *args):
        search_term = self.search_var.get().strip()
        self.results_list.delete(0, tk.END)
        
        if not search_term:
            return

        # Búsqueda por ID si es número
        if search_term.isdigit():
            user = self.db.buscar_usuario_por_id(int(search_term))
            if user:
                self.results_list.insert(tk.END, f"{user['id']} - {user['nombre']}")
        
        # Búsqueda por nombre (siempre)
        if len(search_term) >= 2:
            users = self.db.buscar_usuarios_por_nombre(search_term)
            for user in users:
                # Evitar duplicados si ya salió por ID
                item = f"{user['id']} - {user['nombre']}"
                if item not in self.results_list.get(0, tk.END):
                    self.results_list.insert(tk.END, item)

    def on_user_select(self, event):
        selection = self.results_list.curselection()
        if not selection:
            return
            
        user_str = self.results_list.get(selection[0])
        user_id = int(user_str.split(' - ')[0])
        self.current_user = self.db.buscar_usuario_por_id(user_id)
        
        if self.current_user:
            self.update_user_display()
            self.refresh_months_grid()
            self.reset_selections()

    def update_user_display(self):
        u = self.current_user
        self.lbl_nombre.config(text=u['nombre'])
        self.lbl_id.config(text=f"ID: {u['id']}")
        self.lbl_direccion.config(text=f"Dirección: {u['direccion']}")
        self.lbl_vacas.config(text=f"Vacas: {u['vacas']}")
        self.lbl_inquilinos.config(text=f"Inquilinos: {u['inquilinos']}")
        
        # Cargar historial
        self.history_list.delete(0, tk.END)
        pagos = self.db.obtener_pagos_usuario(u['id'])
        for p in pagos[:5]: # Últimos 5
            fecha = p['fecha_pago'].split()[0]
            self.history_list.insert(tk.END, f"{fecha} - ${p['total']:.2f}")

    def refresh_months_grid(self, event=None):
        # Limpiar grid
        for widget in self.months_frame.winfo_children():
            widget.destroy()
            
        if not self.current_user:
            return

        year = int(self.year_var.get())
        paid_months = self.db.obtener_pagos_usuario_anio(self.current_user['id'], year)
        
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        for i, month_name in enumerate(months):
            month_num = i + 1
            state = 'disabled' if month_num in paid_months else 'normal'
            bg = '#bdc3c7' if month_num in paid_months else '#f0f0f0'
            
            btn = tk.Button(self.months_frame, text=month_name, width=5, height=2, bg=bg,
                          command=lambda m=month_num: self.toggle_month(m))
            
            if month_num in paid_months:
                btn.config(state='disabled', relief='sunken')
                
            row = i // 4
            col = i % 4
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.month_buttons[month_num] = btn

    def toggle_month(self, month):
        if month in self.selected_months:
            self.selected_months.remove(month)
            self.month_buttons[month].config(bg='#f0f0f0')
        else:
            self.selected_months.add(month)
            self.month_buttons[month].config(bg='#3498db')
        self.update_cart()

    def select_full_year(self):
        if not self.current_user:
            return
            
        year = int(self.year_var.get())
        paid_months = self.db.obtener_pagos_usuario_anio(self.current_user['id'], year)
        
        # Seleccionar todos los no pagados
        for m in range(1, 13):
            if m not in paid_months:
                self.selected_months.add(m)
                if m in self.month_buttons:
                    self.month_buttons[m].config(bg='#3498db')
        
        self.update_cart()

    def reset_selections(self):
        self.selected_months.clear()
        self.var_cooperacion.set(False)
        self.var_toma_nueva.set(False)
        self.var_inasistencia.set(0)
        self.update_cart()

    def is_late_payment(self, month, year):
        """Determina si un pago es tardío (después del 3er domingo del mes)"""
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        if year < current_year:
            return True
        if year == current_year and month < current_month:
            return True
        if year == current_year and month == current_month:
            # Calcular 3er domingo
            c = calendar.Calendar(firstweekday=calendar.SUNDAY)
            month_cal = c.monthdatescalendar(year, month)
            sundays = [day for week in month_cal for day in week if day.weekday() == calendar.SUNDAY and day.month == month]
            
            if len(sundays) >= 3:
                third_sunday = sundays[2]
                if now.date() > third_sunday:
                    return True
        return False

    def update_cart(self):
        self.cart_items = []
        if not self.current_user:
            return

        # 1. Meses seleccionados
        year = int(self.year_var.get())
        sorted_months = sorted(list(self.selected_months))
        
        # Agregar meses
        for m in sorted_months:
            is_late = self.is_late_payment(m, year)
            
            # Base mensual ($70)
            self.cart_items.append({
                'concepto': f"Mensualidad",
                'mes': m,
                'anio': year,
                'precio': self.monthly_fee,
                'cantidad': 1
            })
            
            # Recargo si es tarde ($30 para llegar a $100)
            if is_late:
                recargo = 100.0 - self.monthly_fee # Asumiendo $100 total
                if recargo > 0:
                    self.cart_items.append({
                        'concepto': f"Recargo Mes {m}",
                        'mes': m,
                        'anio': year,
                        'precio': recargo,
                        'cantidad': 1
                    })
            
            # Vacas (por mes)
            if self.current_user['vacas'] > 0:
                self.cart_items.append({
                    'concepto': f"Costo Vacas ({self.current_user['vacas']})",
                    'mes': m,
                    'anio': year,
                    'precio': self.current_user['vacas'] * self.cost_vacas,
                    'cantidad': 1
                })
                
            # Inquilinos (por mes)
            if self.current_user['inquilinos'] > 0:
                self.cart_items.append({
                    'concepto': f"Costo Inquilinos ({self.current_user['inquilinos']})",
                    'mes': m,
                    'anio': year,
                    'precio': self.current_user['inquilinos'] * self.cost_inquilinos,
                    'cantidad': 1
                })

        # 2. Extras
        if self.var_cooperacion.get():
            self.cart_items.append({
                'concepto': "Cooperación",
                'precio': self.cost_cooperacion,
                'cantidad': 1,
                'anio': year
            })
            
        if self.var_toma_nueva.get():
            self.cart_items.append({
                'concepto': "Toma Nueva",
                'precio': self.cost_toma_nueva,
                'cantidad': 1,
                'anio': year
            })
            
        inasistencias = self.var_inasistencia.get()
        if inasistencias > 0:
            self.cart_items.append({
                'concepto': f"Multa Inasistencia ({inasistencias})",
                'precio': self.fine_absence * inasistencias,
                'cantidad': 1,
                'anio': year
            })
            
        # Actualizar Treeview
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        self.total_amount = 0.0
        for item in self.cart_items:
            importe = item['precio'] * item.get('cantidad', 1)
            self.total_amount += importe
            
            # Formato para mostrar
            desc = item['concepto']
            if 'mes' in item and 'Recargo' not in desc: # Mostrar mes solo en mensualidad base
                months = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                desc += f" {months[item['mes']]}"
            
            self.cart_tree.insert('', tk.END, values=(desc, f"${importe:.2f}"))
            
        self.lbl_total.config(text=f"${self.total_amount:.2f}")
        
        # Habilitar botón pagar
        if self.total_amount > 0:
            self.btn_pagar.config(state='normal')
        else:
            self.btn_pagar.config(state='disabled')

    def process_payment(self):
        if not self.current_user or not self.cart_items:
            return
            
        if messagebox.askyesno("Confirmar Pago", f"¿Registrar pago por ${self.total_amount:.2f}?"):
            try:
                pago_id = self.db.registrar_pago(
                    self.current_user['id'],
                    self.cart_items,
                    observaciones=""
                )
                
                if pago_id:
                    messagebox.showinfo("Éxito", "Pago registrado correctamente")
                    
                    # Generar Recibo
                    try:
                        pdf_path = self.receipt_gen.generate_receipt(pago_id)
                        if pdf_path and os.path.exists(pdf_path):
                            os.startfile(pdf_path) if os.name == 'nt' else None
                        else:
                            messagebox.showwarning("Aviso", "El recibo se generó pero no se pudo abrir automáticamente.")
                    except Exception as e:
                        messagebox.showerror("Error Recibo", f"Pago registrado pero error al abrir recibo: {e}")
                    
                    # Resetear
                    self.reset_selections()
                    self.refresh_months_grid()
                    self.update_user_display()
                else:
                    messagebox.showerror("Error", "No se pudo registrar el pago en la base de datos")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {e}")