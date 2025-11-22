#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de generación de recibos PDF - Diseño Profesional y Limpio
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from datetime import datetime
import os
from database import get_db_manager
from typing import Dict, Optional, List

class ReceiptGenerator:
    def __init__(self):
        # Configurar directorios
        self.receipts_dir = "recibos"
        self.ensure_directories()
        
        # Colores Corporativos
        self.primary_color = colors.Color(0.12, 0.23, 0.54) # Azul oscuro
        self.accent_color = colors.Color(0.2, 0.6, 1.0)     # Azul claro
        self.text_color = colors.Color(0.2, 0.2, 0.2)       # Gris oscuro
        self.red_color = colors.Color(0.8, 0.0, 0.0)        # Rojo para folios/notas
        
    def ensure_directories(self):
        """Asegura que existan los directorios necesarios"""
        if not os.path.exists(self.receipts_dir):
            os.makedirs(self.receipts_dir)
    
    def generate_receipt(self, pago_id: int) -> Optional[str]:
        """
        Genera un recibo de pago en PDF con dos copias (Usuario y Comité)
        """
        try:
            # Obtener datos del pago
            db = get_db_manager()
            pago_data = db.obtener_detalle_pago(pago_id)
            
            if not pago_data:
                print(f"No se encontró el pago con ID {pago_id}")
                return None
            
            # Generar nombre del archivo
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recibo_{pago_data.get('id', 'sin_id')}_{fecha}.pdf"
            filepath = os.path.join(self.receipts_dir, filename)
            
            # Crear el canvas
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            
            # Altura de medio recibo (mitad de la página)
            half_height = height / 2
            
            # --- RECIBO USUARIO (Superior) ---
            self.draw_receipt(c, pago_data, height, "ORIGINAL - USUARIO")
            
            # --- LÍNEA DE CORTE ---
            c.setDash(4, 4)
            c.setStrokeColor(colors.gray)
            c.setLineWidth(0.5)
            c.line(10*mm, half_height, width - 10*mm, half_height)
            c.drawString(width/2 - 10*mm, half_height + 2*mm, "✂ Cortar aquí")
            c.setDash(1, 0) # Reset dash
            
            # --- RECIBO COMITÉ (Inferior) ---
            self.draw_receipt(c, pago_data, half_height, "COPIA - COMITÉ")
            
            c.save()
            return filepath
            
        except Exception as e:
            print(f"Error al generar recibo: {e}")
            import traceback
            traceback.print_exc()
            return None

    def draw_receipt(self, c: canvas.Canvas, data: Dict, start_y: float, copy_type: str):
        """
        Dibuja un recibo individual con diseño limpio y profesional.
        start_y: Coordenada Y superior donde comienza este recibo.
        """
        # Márgenes
        left_margin = 15 * mm
        right_margin = letter[0] - 15 * mm
        width = letter[0]
        content_width = width - 30*mm
        
        # Coordenada Y actual (empezamos un poco más abajo del tope)
        current_y = start_y - 10 * mm
        
        # --- ENCABEZADO ---
        
        # Logo (Izquierda) - MÁS ANCHO
        logo_path = "logo.jpg"
        logo_width = 50 * mm # Aumentado ancho
        logo_height = 35 * mm # Altura mantenida/ajustada
        if os.path.exists(logo_path):
            try:
                # Ajustamos la posición Y para que el logo grande no se salga
                c.drawImage(logo_path, left_margin, current_y - logo_height + 5*mm, width=logo_width, height=logo_height, mask='auto')
            except:
                pass
        
        # Título Principal (Centro)
        center_x = width / 2
        
        c.setFillColor(self.primary_color)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(center_x, current_y - 5*mm, "COMITÉ DE AGUA POTABLE Y ALCANTARILLADO")
        
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(self.accent_color)
        c.drawCentredString(center_x, current_y - 12*mm, "SAN ANTONIO")
        
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(self.primary_color)
        c.drawCentredString(center_x, current_y - 17*mm, "\"Cuidar el agua es tarea de todos\"")
        
        # Datos del Comité (Debajo del título)
        c.setFillColor(self.text_color)
        c.setFont("Helvetica", 8)
        c.drawCentredString(center_x, current_y - 21*mm, "BARRIO DE SAN ANTONIO, TECAMACHALCO, PUEBLA")
        
        # Fecha y Folio (Esquina Derecha Superior)
        box_y = current_y - 10*mm
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.text_color)
        c.drawRightString(right_margin - 25*mm, box_y, "FOLIO:")
        c.drawRightString(right_margin - 25*mm, box_y - 5*mm, "FECHA:")
        
        c.setFillColor(self.red_color)
        c.drawRightString(right_margin, box_y, str(data.get('id', '')))
        
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        c.setFillColor(self.text_color)
        c.setFont("Helvetica", 10)
        c.drawRightString(right_margin, box_y - 5*mm, fecha_actual)
        
        current_y -= 30 * mm # Espacio reservado para el encabezado
        
        # --- INFORMACIÓN DEL USUARIO (Grid Compacto) ---
        
        # Fondo suave para el área de usuario
        user_info_height = 18 * mm
        c.setFillColor(colors.Color(0.96, 0.96, 0.96))
        c.rect(left_margin, current_y - user_info_height, content_width, user_info_height, stroke=0, fill=1)
        c.setStrokeColor(colors.lightgrey)
        c.rect(left_margin, current_y - user_info_height, content_width, user_info_height, stroke=1, fill=0)
        
        c.setFillColor(self.text_color)
        
        # Fila 1: Usuario No. y Nombre
        row1_y = current_y - 6*mm
        
        # Usuario ID
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin + 5*mm, row1_y, "USUARIO NO:")
        c.setFont("Helvetica", 10)
        c.setFillColor(self.red_color)
        c.drawString(left_margin + 35*mm, row1_y, str(data.get('usuario_id', '')))
        
        # Nombre
        c.setFillColor(self.text_color)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin + 60*mm, row1_y, "NOMBRE:")
        c.setFont("Helvetica", 10)
        c.drawString(left_margin + 85*mm, row1_y, str(data.get('nombre', '')))
        
        # Fila 2: Dirección
        row2_y = current_y - 13*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin + 5*mm, row2_y, "DIRECCIÓN:")
        c.setFont("Helvetica", 9)
        direccion = str(data.get('direccion', ''))
        c.drawString(left_margin + 35*mm, row2_y, direccion[:60])
        
        # Tomas (Sesión) a la derecha
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(right_margin - 15*mm, row2_y, "TOMAS:")
        c.setFont("Helvetica", 10)
        c.drawRightString(right_margin - 5*mm, row2_y, str(data.get('sesion', '')))
            
        current_y -= (user_info_height + 5*mm)
        
        # --- TABLA DE CONCEPTOS (DINÁMICA) ---
        
        table_top = current_y
        
        # Columnas ajustadas para evitar desbordamiento
        # Total disponible: 185.9mm (aprox)
        # [Concepto, Mes, Cant, Precio, Total]
        col_widths = [75, 25, 20, 30, 35] # Total 185mm
        
        # Calcular posiciones X
        x_positions = [left_margin]
        for w in col_widths:
            x_positions.append(x_positions[-1] + w*mm)
            
        # Calcular altura dinámica
        detalles = data.get('detalles', [])
        num_items = len(detalles)
        header_height = 8 * mm
        row_height = 5 * mm
        min_rows = 3 # Mínimo de filas para que no se vea vacío
        display_rows = max(num_items, min_rows)
        
        table_body_height = (display_rows * row_height) + 2*mm # +2mm padding
        table_height = header_height + table_body_height
        table_bottom = table_top - table_height
        
        # Encabezado de Tabla
        c.setFillColor(self.primary_color)
        c.rect(left_margin, table_top - header_height, sum(col_widths)*mm, header_height, stroke=0, fill=1)
        
        # Textos Encabezado
        headers = ["CONCEPTO", "MES", "CANT.", "PRECIO", "TOTAL"]
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        
        for i, header in enumerate(headers):
            cell_center = x_positions[i] + (col_widths[i]*mm / 2)
            c.drawCentredString(cell_center, table_top - 5.5*mm, header)
            
        # Líneas verticales y borde
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.rect(left_margin, table_bottom, sum(col_widths)*mm, table_height)
        
        for x in x_positions[1:-1]:
            c.line(x, table_bottom, x, table_top)
            
        # Contenido de la Tabla
        row_y = table_top - header_height - 4*mm # Start slightly below header
        c.setFillColor(self.text_color)
        c.setFont("Helvetica", 9)
        
        total_pagar = 0
        
        for detalle in detalles:
            concepto = detalle.get('concepto', '')
            precio = detalle.get('precio', 0)
            cantidad = detalle.get('cantidad', 1)
            subtotal = precio * cantidad
            total_pagar += subtotal
            
            mes = detalle.get('mes')
            anio = detalle.get('anio')
            
            # Lógica de visualización
            texto_concepto = concepto
            texto_mes = "-"
            
            if mes:
                texto_concepto = "Servicio de Agua Potable"
                texto_mes = f"{self.get_month_name(mes)} {anio if anio else ''}"
            
            # 1. Concepto
            c.drawString(x_positions[0] + 2*mm, row_y, texto_concepto[:35]) # Truncar si es muy largo
            
            # 2. Mes
            c.drawCentredString(x_positions[1] + col_widths[1]*mm/2, row_y, texto_mes)
            
            # 3. Cantidad
            c.drawCentredString(x_positions[2] + col_widths[2]*mm/2, row_y, str(cantidad))
            
            # 4. Precio
            c.drawRightString(x_positions[3] + col_widths[3]*mm - 2*mm, row_y, f"${precio:.2f}")
            
            # 5. Total
            c.setFont("Helvetica-Bold", 9)
            c.drawRightString(x_positions[4] + col_widths[4]*mm - 2*mm, row_y, f"${subtotal:.2f}")
            c.setFont("Helvetica", 9)
            
            row_y -= row_height
            
        # Total a Pagar (Pie de tabla)
        total_y = table_bottom - 8*mm
        
        # Caja de Total
        c.setFillColor(self.primary_color)
        c.rect(x_positions[-2], total_y - 2*mm, (col_widths[-1] + col_widths[-2])*mm, 10*mm, stroke=0, fill=1)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(x_positions[-1] + col_widths[-1]*mm - 2*mm, total_y + 1.5*mm, f"${total_pagar:.2f}")
        c.drawString(x_positions[-2] + 2*mm, total_y + 1.5*mm, "TOTAL A PAGAR:")
        
        # Firmas (Dinámico basado en total_y)
        sign_y = total_y - 20*mm
        
        c.setFillColor(self.text_color)
        c.setStrokeColor(self.text_color)
        
        # Línea de firma
        c.line(width/2 - 30*mm, sign_y, width/2 + 30*mm, sign_y)
        
        c.setFont("Helvetica", 9)
        c.drawCentredString(width/2, sign_y - 5*mm, "CARLOS LOPEZ SANTOS")
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(width/2, sign_y - 9*mm, "COBRADOR AUTORIZADO")
        
        # Notas Legales (Pie de página)
        note_y = sign_y - 10*mm
        c.setFillColor(colors.grey)
        c.setFont("Helvetica-Oblique", 6)
        c.drawCentredString(width/2, note_y, "NOTA: Conserve este recibo para cualquier aclaración. El pago de este recibo no libera de adeudos anteriores.")
        
        # Indicador de copia (arriba a la derecha)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.red_color)
        c.drawRightString(right_margin, start_y - 5*mm, copy_type)
    
    def get_month_name(self, month: int) -> str:
        """Retorna el nombre del mes en español"""
        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        return meses.get(month, "")