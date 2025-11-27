#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de recibos de pago para el sistema de agua potable
"""

import os
from datetime import datetime
from typing import Dict, Optional, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Frame, PageTemplate, BaseDocTemplate, FrameBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from .database import get_db_manager

class ReceiptGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.colors = {
            'primary': colors.Color(0.05, 0.25, 0.50),    # Azul marino profundo
            'text': colors.black,
            'gray': colors.Color(0.50, 0.50, 0.50),
            'light_gray': colors.Color(0.90, 0.90, 0.90),
            'blue_header': colors.Color(0.8, 0.9, 1.0),   # Azul claro para headers
        }
        self.create_custom_styles()
        self.receipts_dir = "recibos"
        self.ensure_directories()
    
    def create_custom_styles(self):
        """Crea estilos personalizados"""
        self.title_style = ParagraphStyle(
            'ReceiptTitle',
            parent=self.styles['Heading1'],
            fontSize=12,
            leading=14,
            alignment=TA_CENTER,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'ReceiptNormal',
            parent=self.styles['Normal'],
            fontSize=7,
            leading=9,
            alignment=TA_LEFT,
            textColor=self.colors['text'],
            fontName='Helvetica'
        )
        
        self.center_style = ParagraphStyle(
            'ReceiptCenter',
            parent=self.normal_style,
            alignment=TA_CENTER
        )
        
        self.bold_style = ParagraphStyle(
            'ReceiptBold',
            parent=self.normal_style,
            fontName='Helvetica-Bold'
        )
        
        self.header_style = ParagraphStyle(
            'TableHeader',
            parent=self.normal_style,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            fontSize=6
        )

        self.small_style = ParagraphStyle(
            'ReceiptSmall',
            parent=self.normal_style,
            fontSize=6,
            leading=8
        )

    def ensure_directories(self):
        if not os.path.exists(self.receipts_dir):
            os.makedirs(self.receipts_dir)
    
    def generate_receipt(self, pago_id: int) -> Optional[str]:
        try:
            db = get_db_manager()
            pago_data = db.obtener_detalle_pago(pago_id)
            
            if not pago_data:
                print(f"No se encontró el pago con ID {pago_id}")
                return None
            
            # Obtener configuración actual para cálculos
            self.config = {
                'cuota_mensual': float(db.obtener_configuracion('cuota_mensual') or 70.0),
            }
            
            # Nombre de archivo
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_num = pago_data.get('usuario_id', 'SN')
            filename = f"recibo_{user_num}_{fecha}.pdf"
            filepath = os.path.join(self.receipts_dir, filename)
            
            # Configurar documento en Portrait (Vertical)
            doc = BaseDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # Crear frames para dos copias (Arriba y Abajo)
            page_width, page_height = letter
            frame_height = (page_height - 1.5*inch) / 2
            
            frame_top = Frame(
                doc.leftMargin, 
                doc.bottomMargin + frame_height + 0.5*inch, 
                page_width - 1*inch, 
                frame_height,
                id='user_copy',
                showBoundary=0
            )
            
            frame_bottom = Frame(
                doc.leftMargin, 
                doc.bottomMargin, 
                page_width - 1*inch, 
                frame_height,
                id='admin_copy',
                showBoundary=0
            )
            
            template = PageTemplate(id='dual_receipt', frames=[frame_top, frame_bottom])
            doc.addPageTemplates([template])
            
            # Construir contenido
            content_user = self.build_receipt_content(pago_data, "USUARIO")
            content_admin = self.build_receipt_content(pago_data, "COMITÉ")
            
            story = []
            story.extend(content_user)
            story.append(FrameBreak()) # Saltar al siguiente frame (abajo)
            story.extend(content_admin)
            
            doc.build(story)
            return filepath
            
        except Exception as e:
            print(f"Error generando recibo: {e}")
            import traceback
            traceback.print_exc()
            return None

    def build_receipt_content(self, pago_data: Dict, copy_type: str) -> list:
        elements = []
        elements.extend(self.build_header(pago_data, copy_type))
        elements.extend(self.build_body(pago_data))
        elements.extend(self.build_footer(copy_type))
        return elements

    def build_header(self, pago_data: Dict, copy_type: str) -> list:
        # Logo
        logo_path = os.path.join("assets", "logo.jpg")
        if os.path.exists(logo_path):
            img = Image(logo_path, width=0.8*inch, height=0.8*inch)
        else:
            img = Paragraph("💧", self.title_style)
            
        # Info Empresa
        empresa_info = [
            Paragraph("COMITÉ DE AGUA POTABLE Y ALCANTARILLADO", self.title_style),
            Paragraph("DEL BARRIO DE SAN ANTONIO TECAMACHALCO, PUE.", self.title_style),
        ]
        
        # Tabla Header Superior
        data = [[img, empresa_info]]
        t = Table(data, colWidths=[1.0*inch, 5.0*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        # Info Usuario y Fecha
        fecha_pago = datetime.strptime(pago_data['fecha_pago'], '%Y-%m-%d %H:%M:%S')
        
        # Fila 1: Usuario No | Fecha
        # Fila 2: Nombre | Folio
        # Fila 3: Tomas | Direccion
        
        user_info = [
            [
                Paragraph(f"<b>USUARIO No.</b> {pago_data['usuario_id']}", self.normal_style),
                "",
                Paragraph(f"<b>FECHA:</b> {fecha_pago.strftime('%d-%b-%y')}", self.normal_style)
            ],
            [
                Paragraph(f"<b>NOMBRE:</b> {pago_data['nombre']}", self.normal_style),
                "",
                Paragraph(f"<b>FOLIO:</b> {str(pago_data['id']).zfill(5)}", ParagraphStyle('RedFolio', parent=self.normal_style, textColor=colors.red, alignment=TA_RIGHT))
            ],
            [
                Paragraph(f"<b>TOMAS:</b> 0 <b>HIDRANTE</b>", self.normal_style),
                "",
                Paragraph(f"{pago_data.get('direccion', '')}", self.normal_style)
            ]
        ]
        
        t_info = Table(user_info, colWidths=[3.0*inch, 1.0*inch, 3.0*inch])
        t_info.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black), # Linea bajo usuario/fecha
            ('LINEBELOW', (0,1), (-1,1), 0.5, colors.black), # Linea bajo nombre/folio
            ('ALIGN', (2,1), (2,1), 'RIGHT'), # Folio a la derecha
        ]))
        
        return [t, Spacer(1, 5), t_info, Spacer(1, 5)]

    def build_body(self, pago_data: Dict) -> list:
        detalles = pago_data.get('detalles', [])
        
        # Cálculos
        importe_cuota = sum(d['precio'] for d in detalles if 'Mensualidad' in d['concepto'])
        importe_vacas = sum(d['precio'] for d in detalles if 'Vacas' in d['concepto'])
        importe_inquilinos = sum(d['precio'] for d in detalles if 'Inquilinos' in d['concepto'])
        multa_inasistencia = sum(d['precio'] for d in detalles if 'Inasistencia' in d['concepto'])
        cooperaciones = sum(d['precio'] for d in detalles if 'Cooperación' in d['concepto'])
        toma_nueva = sum(d['precio'] for d in detalles if 'Toma Nueva' in d['concepto'])
        
        meses_pagados = [d for d in detalles if d['mes'] and 'Mensualidad' in d['concepto']]
        meses_pagados.sort(key=lambda x: x['mes'])
        num_meses = len(meses_pagados)
        
        # Texto de meses
        if meses_pagados:
            first = self.get_month_name(meses_pagados[0]['mes'])
            last = self.get_month_name(meses_pagados[-1]['mes'])
            year = meses_pagados[0]['anio']
            if len(meses_pagados) == 1:
                periodo_txt = f"{first.upper()} DE {year}"
            else:
                periodo_txt = f"{first.upper()} A {last.upper()} DE {year}"
        else:
            periodo_txt = ""

        # Definición de Columnas y Anchos
        col_widths = [
            1.8*inch, # Concepto
            0.7*inch, # Cuota x Toma
            0.7*inch, # Forma Pago
            0.5*inch, # Vacas
            0.6*inch, # Inquilinos
            0.7*inch, # Inasistencia
            0.8*inch, # Cooperaciones
            0.7*inch, # Toma Nueva
            0.8*inch  # Total
        ]
        
        # Headers
        headers = [
            Paragraph("CONCEPTO", self.header_style),
            Paragraph("CUOTA X<br/>TOMA", self.header_style),
            Paragraph("FORMA DE<br/>PAGO<br/>Mensual", self.header_style),
            Paragraph("VACAS", self.header_style),
            Paragraph("INQUILINOS", self.header_style),
            Paragraph("INASISTENCIA", self.header_style),
            Paragraph("COOPERACION<br/>ES", self.header_style),
            Paragraph("TOMA NUEVA", self.header_style),
            Paragraph("TOTAL A<br/>PAGAR", self.header_style)
        ]
        
        # Fila 1: Precios Unitarios / Cantidades
        row1 = [
            "", # Concepto vacio
            Paragraph(f"${self.config['cuota_mensual']:.2f}", self.center_style),
            Paragraph(str(num_meses), self.center_style),
            Paragraph(str(pago_data.get('vacas', 0)), self.center_style),
            Paragraph(str(pago_data.get('inquilinos', 0)), self.center_style),
            "", "", "", "" # Resto vacio
        ]
        
        # Fila 2: Importes
        row2 = [
            Paragraph("PAGO POR BOMBEO Y DISTRIBUCION<br/>DE AGUA POTABLE", self.bold_style),
            Paragraph(f"${importe_cuota:.2f}", self.center_style),
            Paragraph(f"${importe_cuota:.2f}", self.center_style), # Repite importe en forma pago? Segun imagen parece que si o vacio. Pondremos el total de cuota.
            Paragraph(f"${importe_vacas:.2f}", self.center_style),
            Paragraph(f"${importe_inquilinos:.2f}", self.center_style),
            Paragraph(f"${multa_inasistencia:.2f}", self.center_style),
            Paragraph(f"${cooperaciones:.2f}", self.center_style),
            Paragraph(f"${toma_nueva:.2f}", self.center_style),
            Paragraph(f"${pago_data['total']:.2f}", self.bold_style)
        ]
        
        # Fila 3: Periodo
        row3 = [
            Paragraph(f"De: {periodo_txt}", self.normal_style),
            "", "", "", "", "", "", "", ""
        ]
        
        # Fila Total (Footer de tabla)
        row_total = [
            "", "", "", "", "", "", 
            Paragraph("TOTAL", self.bold_style),
            "",
            Paragraph(f"${pago_data['total']:.2f}", self.bold_style)
        ]
        
        data = [headers, row1, row2, row3, row_total]
        
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-2), 0.5, colors.black), # Grid completo excepto ultima fila
            ('BOX', (0,0), (-1,-1), 1, colors.black), # Borde exterior
            ('BACKGROUND', (0,0), (-1,0), self.colors['blue_header']), # Header azul
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,2), (0,3), 'LEFT'), # Concepto alineado izquierda
            ('SPAN', (0,1), (0,1)), # Span celda vacia concepto row1? No, mejor dejarla
            ('LINEBELOW', (0,3), (-1,3), 1, colors.black), # Linea antes del total
            ('ALIGN', (-1,-1), (-1,-1), 'RIGHT'), # Total alineado derecha
        ]))
        
        return [t]

    def build_footer(self, copy_type: str) -> list:
        firma_data = [
            [Spacer(1, 20), Spacer(1, 20)],
            ["_______________________", "_______________________"],
            ["CARLOS LOPEZ SANTOS", "SELLO"],
            [
                Paragraph("NOTA: 1.- ES NECESARIO CONSERVAR ESTE COMPROBANTE, DEBERA PRESENTARLO EN SU PROXIMO PAGO PARA CUALQUIER ACLARACIÓN.<br/>2.- EL PAGO DE ESTE RECIBO NO TE LIBERA DE DEUDAS ANTERIORES.", self.small_style),
                Paragraph(copy_type, ParagraphStyle('CopyType', parent=self.bold_style, alignment=TA_RIGHT, textColor=colors.red))
            ]
        ]
        
        t = Table(firma_data, colWidths=[4.0*inch, 3.0*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,3), (0,3), 'LEFT'), # Nota izquierda
            ('ALIGN', (1,3), (1,3), 'RIGHT'), # Tipo copia derecha
        ]))
        
        return [Spacer(1, 10), t]

    def get_month_name(self, month_num: int) -> str:
        months = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return months[month_num] if 1 <= month_num <= 12 else str(month_num)