#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidad para importar datos desde CSV al sistema de agua potable
"""

import csv
import os
from .database import get_db_manager
from tkinter import messagebox
import tkinter as tk
from tkinter import filedialog


class CSVImporter:
    def __init__(self):
        self.db = get_db_manager()
        
    def import_users_from_csv(self, csv_path: str) -> tuple:
        """
        Importa usuarios desde un archivo CSV
        
        Args:
            csv_path: Ruta al archivo CSV
            
        Returns:
            tuple: (usuarios_importados, errores)
        """
        if not os.path.exists(csv_path):
            return 0, ["Archivo no encontrado"]
        
        usuarios_importados = 0
        errores = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as file:
                # Intentar detectar el delimitador
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Mapear nombres de columnas comunes
                field_mapping = {
                    'numero': ['numero', 'num', 'number', 'id'],
                    'nombre': ['nombre', 'name', 'usuario', 'user'],
                    'direccion': ['direccion', 'address', 'domicilio', 'dir'],
                    'telefono': ['telefono', 'phone', 'tel', 'celular'],
                    'email': ['email', 'correo', 'mail', 'e-mail']
                }
                
                # Obtener los nombres reales de las columnas
                columns = [col.lower().strip() for col in reader.fieldnames]
                mapped_fields = {}
                
                for field, possible_names in field_mapping.items():
                    for possible in possible_names:
                        if possible in columns:
                            mapped_fields[field] = reader.fieldnames[columns.index(possible)]
                            break
                
                # Verificar que al menos tengamos número y nombre
                if 'numero' not in mapped_fields or 'nombre' not in mapped_fields:
                    return 0, ["El archivo CSV debe contener al menos las columnas 'numero' y 'nombre'"]
                
                for row_num, row in enumerate(reader, start=2):  # Empezar en 2 por el header
                    try:
                        # Extraer datos
                        numero_str = str(row.get(mapped_fields['numero'], '')).strip()
                        nombre = str(row.get(mapped_fields['nombre'], '')).strip()
                        direccion = str(row.get(mapped_fields.get('direccion', ''), '')).strip()
                        telefono = str(row.get(mapped_fields.get('telefono', ''), '')).strip()
                        email = str(row.get(mapped_fields.get('email', ''), '')).strip()
                        
                        # Validar datos obligatorios
                        if not numero_str or not nombre:
                            errores.append(f"Fila {row_num}: Número y nombre son obligatorios")
                            continue
                        
                        try:
                            numero = int(numero_str)
                        except ValueError:
                            errores.append(f"Fila {row_num}: Número '{numero_str}' no es válido")
                            continue
                        
                        # Intentar crear el usuario
                        if self.db.crear_usuario(numero, nombre, direccion, telefono, email):
                            usuarios_importados += 1
                        else:
                            errores.append(f"Fila {row_num}: Ya existe un usuario con el número {numero}")
                            
                    except Exception as e:
                        errores.append(f"Fila {row_num}: Error al procesar - {str(e)}")
                        
        except Exception as e:
            errores.append(f"Error al leer el archivo CSV: {str(e)}")
        
        return usuarios_importados, errores
    
    def import_payments_from_csv(self, csv_path: str, year: int) -> tuple:
        """
        Importa pagos desde un archivo CSV
        
        Args:
            csv_path: Ruta al archivo CSV
            year: Año de los pagos
            
        Returns:
            tuple: (pagos_importados, errores)
        """
        if not os.path.exists(csv_path):
            return 0, ["Archivo no encontrado"]
        
        pagos_importados = 0
        errores = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                columns = [col.lower().strip() for col in reader.fieldnames]
                
                # Buscar columna de número de usuario
                numero_col = None
                for col in reader.fieldnames:
                    if col.lower().strip() in ['numero', 'num', 'usuario', 'id']:
                        numero_col = col
                        break
                
                if not numero_col:
                    return 0, ["No se encontró columna de número de usuario"]
                
                # Buscar columnas de meses (1-12)
                month_cols = {}
                for i in range(1, 13):
                    for col in reader.fieldnames:
                        col_lower = col.lower().strip()
                        if (str(i) in col_lower and any(word in col_lower for word in ['mes', 'month', str(i)])) or \
                           col_lower == str(i):
                            month_cols[i] = col
                            break
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Obtener número de usuario
                        numero_str = str(row.get(numero_col, '')).strip()
                        if not numero_str:
                            errores.append(f"Fila {row_num}: Número de usuario vacío")
                            continue
                        
                        try:
                            numero = int(numero_str)
                        except ValueError:
                            errores.append(f"Fila {row_num}: Número '{numero_str}' no es válido")
                            continue
                        
                        # Buscar el usuario
                        usuario = self.db.buscar_usuario_por_numero(numero)
                        if not usuario:
                            errores.append(f"Fila {row_num}: No existe usuario con número {numero}")
                            continue
                        
                        # Identificar meses pagados
                        meses_pagados = []
                        for mes, col in month_cols.items():
                            valor = str(row.get(col, '')).strip().lower()
                            # Considerar como pagado si hay un valor que indique pago
                            if valor and valor not in ['0', 'no', 'false', '', 'n']:
                                meses_pagados.append(mes)
                        
                        if meses_pagados:
                            # Registrar el pago
                            pago_id = self.db.registrar_pago(
                                usuario_id=usuario['id'],
                                meses_pagados=meses_pagados,
                                anio=year,
                                observaciones=f"Importado desde CSV: {os.path.basename(csv_path)}"
                            )
                            
                            if pago_id > 0:
                                pagos_importados += 1
                            else:
                                errores.append(f"Fila {row_num}: Error al registrar pago para usuario {numero}")
                        
                    except Exception as e:
                        errores.append(f"Fila {row_num}: Error al procesar - {str(e)}")
                        
        except Exception as e:
            errores.append(f"Error al leer el archivo CSV: {str(e)}")
        
        return pagos_importados, errores


class ImporterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Importador de Datos CSV")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.importer = CSVImporter()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Importador de Datos CSV",
            font=('Arial', 16, 'bold'),
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Sección importar usuarios
        self.create_users_import_section(main_frame)
        
        # Separador
        separator = tk.Frame(main_frame, height=2, bg='#bdc3c7')
        separator.pack(fill=tk.X, pady=20)
        
        # Sección importar pagos
        self.create_payments_import_section(main_frame)
        
        # Área de resultados
        self.create_results_area(main_frame)
        
        # Botón cerrar
        close_btn = tk.Button(
            main_frame,
            text="Volver al Menú",
            command=self.root.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 12)
        )
        close_btn.pack(pady=(20, 0))
    
    def create_users_import_section(self, parent):
        """Crea la sección de importación de usuarios"""
        users_frame = tk.LabelFrame(parent, text="Importar Usuarios", font=('Arial', 12, 'bold'))
        users_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_label = tk.Label(
            users_frame,
            text="Seleccione un archivo CSV con la información de usuarios.\n" +
                 "Debe contener columnas: numero, nombre (y opcionalmente: direccion, telefono, email)",
            font=('Arial', 10),
            fg='#7f8c8d',
            justify=tk.LEFT
        )
        info_label.pack(anchor='w', padx=10, pady=5)
        
        button_frame = tk.Frame(users_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        select_users_btn = tk.Button(
            button_frame,
            text="Seleccionar Archivo CSV de Usuarios",
            command=self.import_users,
            bg='#3498db',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        select_users_btn.pack(side=tk.LEFT)
    
    def create_payments_import_section(self, parent):
        """Crea la sección de importación de pagos"""
        payments_frame = tk.LabelFrame(parent, text="Importar Pagos", font=('Arial', 12, 'bold'))
        payments_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_label = tk.Label(
            payments_frame,
            text="Seleccione un archivo CSV con pagos realizados.\n" +
                 "Debe contener columnas: numero (usuario) y columnas para cada mes (1-12)",
            font=('Arial', 10),
            fg='#7f8c8d',
            justify=tk.LEFT
        )
        info_label.pack(anchor='w', padx=10, pady=5)
        
        controls_frame = tk.Frame(payments_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Selección de año
        tk.Label(controls_frame, text="Año de los pagos:", font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.year_var = tk.StringVar(value="2024")
        year_entry = tk.Entry(controls_frame, textvariable=self.year_var, width=8, font=('Arial', 10))
        year_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        select_payments_btn = tk.Button(
            controls_frame,
            text="Seleccionar Archivo CSV de Pagos",
            command=self.import_payments,
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        select_payments_btn.pack(side=tk.LEFT)
    
    def create_results_area(self, parent):
        """Crea el área de resultados"""
        results_frame = tk.LabelFrame(parent, text="Resultados", font=('Arial', 12, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Área de texto con scroll
        text_frame = tk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.results_text = tk.Text(
            text_frame,
            font=('Arial', 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def import_users(self):
        """Importa usuarios desde CSV"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de usuarios",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if not file_path:
            return
        
        self.add_result(f"Importando usuarios desde: {os.path.basename(file_path)}")
        
        try:
            usuarios_importados, errores = self.importer.import_users_from_csv(file_path)
            
            self.add_result(f"✓ Usuarios importados exitosamente: {usuarios_importados}")
            
            if errores:
                self.add_result(f"⚠ Errores encontrados ({len(errores)}):")
                for error in errores[:10]:  # Mostrar máximo 10 errores
                    self.add_result(f"  • {error}")
                if len(errores) > 10:
                    self.add_result(f"  ... y {len(errores) - 10} errores más")
            
            self.add_result("-" * 50)
            
        except Exception as e:
            self.add_result(f"✗ Error al importar usuarios: {str(e)}")
    
    def import_payments(self):
        """Importa pagos desde CSV"""
        year_str = self.year_var.get().strip()
        if not year_str:
            messagebox.showwarning("Año requerido", "Ingrese el año de los pagos")
            return
        
        try:
            year = int(year_str)
        except ValueError:
            messagebox.showwarning("Año inválido", "Ingrese un año válido")
            return
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de pagos",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if not file_path:
            return
        
        self.add_result(f"Importando pagos desde: {os.path.basename(file_path)} (Año: {year})")
        
        try:
            pagos_importados, errores = self.importer.import_payments_from_csv(file_path, year)
            
            self.add_result(f"✓ Pagos importados exitosamente: {pagos_importados}")
            
            if errores:
                self.add_result(f"⚠ Errores encontrados ({len(errores)}):")
                for error in errores[:10]:  # Mostrar máximo 10 errores
                    self.add_result(f"  • {error}")
                if len(errores) > 10:
                    self.add_result(f"  ... y {len(errores) - 10} errores más")
            
            self.add_result("-" * 50)
            
        except Exception as e:
            self.add_result(f"✗ Error al importar pagos: {str(e)}")
    
    def add_result(self, text):
        """Agrega texto al área de resultados"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.config(state=tk.DISABLED)
        self.results_text.see(tk.END)
        self.root.update()
    
    def run(self):
        """Ejecuta la interfaz"""
        self.root.mainloop()


def main():
    """Función principal"""
    app = ImporterGUI()
    app.run()


if __name__ == "__main__":
    main()