import tkinter as tk
from tkinter import ttk, messagebox
from .database import get_db_manager
from datetime import datetime
from .receipt_generator import ReceiptGenerator
from .excel_manager import ExcelManager
import os

class PaymentHistoryWindow:
    def __init__(self, parent, user_id):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Historial de Pagos - Usuario {user_id}")
        self.top.geometry("900x600")
        
        self.user_id = user_id
        self.db = get_db_manager()
        self.receipt_gen = ReceiptGenerator()
        
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.top, bg='#8e44ad', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Historial de Pagos", font=('Arial', 16, 'bold'), fg='white', bg='#8e44ad').pack(side=tk.LEFT, padx=20)
        
        # Lista de Pagos
        list_frame = tk.Frame(self.top)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('id', 'fecha', 'total', 'observaciones')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.tree.heading('id', text='Folio')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('total', text='Total')
        self.tree.heading('observaciones', text='Observaciones')
        
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('fecha', width=150, anchor='center')
        self.tree.column('total', width=100, anchor='e')
        self.tree.column('observaciones', width=300)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Detalles del pago seleccionado
        self.detail_frame = tk.LabelFrame(self.top, text="Detalles del Pago", font=('Arial', 10, 'bold'), height=200)
        self.detail_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.detail_tree = ttk.Treeview(self.detail_frame, columns=('concepto', 'mes', 'anio', 'precio'), show='headings', height=5)
        self.detail_tree.heading('concepto', text='Concepto')
        self.detail_tree.heading('mes', text='Mes')
        self.detail_tree.heading('anio', text='Año')
        self.detail_tree.heading('precio', text='Importe')
        
        self.detail_tree.column('concepto', width=250)
        self.detail_tree.column('mes', width=50, anchor='center')
        self.detail_tree.column('anio', width=60, anchor='center')
        self.detail_tree.column('precio', width=100, anchor='e')
        
        self.detail_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botones
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.btn_reprint = tk.Button(btn_frame, text="Reimprimir Recibo (Excel)", command=self.reprint_receipt, 
                                   bg='#2ecc71', fg='white', state='disabled', font=('Arial', 10, 'bold'))
        self.btn_reprint.pack(side=tk.RIGHT)
        
    def load_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        pagos = self.db.obtener_pagos_usuario(self.user_id)
        for p in pagos:
            self.tree.insert('', 'end', values=(p['id'], p['fecha_pago'], f"${p['total']:.2f}", p['observaciones']))
            
    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        pago_id = item['values'][0]
        
        # Cargar detalles
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
            
        detalles_data = self.db.obtener_detalle_pago(pago_id)
        detalles = detalles_data.get('detalles', [])
        for d in detalles:
            self.detail_tree.insert('', 'end', values=(d['concepto'], d['mes'] or '-', d['anio'] or '-', f"${d['precio']:.2f}"))
            
        self.btn_reprint.config(state='normal')
        self.selected_pago_id = pago_id
        
    def reprint_receipt(self):
        if not hasattr(self, 'selected_pago_id'):
            return
            
        pago_id = self.selected_pago_id
        
        try:
            # Reconstruir datos para ExcelManager
            # Necesitamos fecha, total, nombre usuario, etc.
            
            # Obtener datos del pago
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pagos WHERE id = ?", (pago_id,))
            pago = cursor.fetchone()
            conn.close()
            
            if not pago:
                messagebox.showerror("Error", "Pago no encontrado")
                return

            # Obtener usuario
            usuario = self.db.buscar_usuario_por_id(self.user_id)
            if not usuario:
                messagebox.showerror("Error", "Usuario no encontrado")
                return

            # Obtener detalles
            detalles = self.db.obtener_detalle_pago(pago_id)
            
            # Construir dict
            conceptos_fmt = []
            for d in detalles:
                desc = d['concepto']
                # Reconstruir logica de nombre de mes si se desea, 
                # pero el detalle ya deberia tener info suficiente o el concepto guardado.
                # Si el concepto guardado es "Mensualidad", podríamos agregar el mes si existe.
                if d['mes']:
                     months = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                     if 'Mensualidad' in desc and str(d['mes']) not in desc:
                         # Solo agregar si no está ya (evitar duplicados si se guardó completo)
                         if 1 <= int(d['mes']) <= 12:
                             desc += f" {months[int(d['mes'])]}"
                
                conceptos_fmt.append({
                    'descripcion': desc,
                    'importe': d['precio']
                })
            
            datos_recibo = {
                'folio': pago_id,
                'fecha': datetime.strptime(pago['fecha_pago'], '%Y-%m-%d %H:%M:%S').strftime("%d/%m/%Y"),
                'id_usuario': usuario['id'],
                'nombre': usuario['nombre'],
                'direccion': usuario['direccion'],
                'tomas': usuario.get('tomas', 1),
                'total': pago['total'],
                'conceptos': conceptos_fmt
            }

            ruta_excel = ExcelManager.generar_recibo(datos_recibo)
            if ruta_excel and os.path.exists(ruta_excel):
                os.startfile(ruta_excel)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar recibo: {e}")
