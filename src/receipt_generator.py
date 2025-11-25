#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de recibos de pago para el sistema de agua potable
"""

import os
from datetime import datetime
from typing import Dict, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from .database import get_db_manager

class ReceiptGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Paleta de colores corporativa
        self.colors = {
            'primary': colors.Color(0.05, 0.25, 0.50),    # Azul marino profundo
            'secondary': colors.Color(0.20, 0.60, 0.85),  # Azul cielo
            'accent': colors.Color(0.10, 0.60, 0.30),     # Verde éxito
            'text': colors.Color(0.15, 0.15, 0.15),       # Gris casi negro
            'gray': colors.Color(0.50, 0.50, 0.50),       # Gris medio
            'light_gray': colors.Color(0.95, 0.95, 0.95), # Gris muy claro
            'white': colors.white
        }
        self.create_custom_styles()
        self.receipts_dir = "recibos"
        self.ensure_directories()
    
    def create_custom_styles(self):
        """Crea estilos personalizados para un recibo profesional"""
        # Título Principal
        self.title_style = ParagraphStyle(
            'ReceiptTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            leading=26,
            alignment=TA_CENTER,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        
        # Subtítulo
        self.subtitle_style = ParagraphStyle(
            'ReceiptSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=self.colors['secondary'],
            fontName='Helvetica-Bold',
            spaceAfter=15
        )
        
        # Texto Normal
        self.normal_style = ParagraphStyle(
            'ReceiptNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            textColor=self.colors['text'],
            fontName='Helvetica'
        )
        
        # Etiquetas (Labels)
        self.label_style = ParagraphStyle(
            'ReceiptLabel',
            parent=self.normal_style,
            fontName='Helvetica-Bold',
            textColor=self.colors['primary']
        )
        
        # Totales
        self.total_label_style = ParagraphStyle(
            'TotalLabel',
            parent=self.normal_style,
            fontSize=12,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT,
            textColor=self.colors['primary']
        )
        
        self.total_value_style = ParagraphStyle(
            'TotalValue',
            parent=self.normal_style,
            fontSize=14,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT,
            textColor=self.colors['accent']
        )
        
        # Pie de página
        self.footer_style = ParagraphStyle(
            'ReceiptFooter',
            parent=self.normal_style,
            fontSize=8,
            alignment=TA_CENTER,
            textColor=self.colors['gray']
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
            
            # Nombre de archivo único
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_num = pago_data.get('usuario_id', 'SN')
            filename = f"recibo_{user_num}_{fecha}.pdf"
            filepath = os.path.join(self.receipts_dir, filename)
            
            # Configuración del documento
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                title=f"Recibo de Pago - {user_num}"
            )
            
            story = []
            
            # Construcción del contenido
            story.extend(self.build_header(pago_data))
            story.append(Spacer(1, 20))
            story.extend(self.build_customer_info(pago_data))
            story.append(Spacer(1, 20))
            story.extend(self.build_payment_details(pago_data))
            story.append(Spacer(1, 10))
            story.extend(self.build_totals(pago_data))
            story.append(Spacer(1, 40))
            story.extend(self.build_footer(pago_data))
            
            doc.build(story)
            return filepath
            
        except Exception as e:
            print(f"Error generando recibo: {e}")
            import traceback
            traceback.print_exc()
            return None

    def build_header(self, pago_data: Dict) -> list:
        """Encabezado con Logo y Datos de la Empresa"""
        # Intentar cargar logo
        logo_path = os.path.join("assets", "logo.jpg")
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=1.2*inch, height=1.2*inch)
                img.hAlign = 'CENTER'
            except:
                img = Paragraph("💧", self.title_style)
        else:
            img = Paragraph("💧", self.title_style)

        # Datos de la empresa
        empresa_info = [
            Paragraph("COMITÉ DE AGUA POTABLE", self.title_style),
            Paragraph("Sistema de Gestión y Cobranza", self.subtitle_style),
            Paragraph("Calle Principal S/N, Centro", self.footer_style),
            Paragraph("Tel: (555) 123-4567 | Email: contacto@agua.com", self.footer_style),
        ]
        
        # Tabla Header: Logo | Info
        data = [[img, empresa_info]]
        t = Table(data, colWidths=[2*inch, 4.5*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        return [t, Spacer(1, 10), Paragraph("________________________________________________________________________________", self.footer_style)]

    def build_customer_info(self, pago_data: Dict) -> list:
        """Información del Cliente y del Recibo"""
        fecha_pago = datetime.strptime(pago_data['fecha_pago'], '%Y-%m-%d %H:%M:%S')
        
        # Columna Izquierda: Datos del Cliente
        cliente_data = [
            [Paragraph("CLIENTE:", self.label_style), Paragraph(pago_data['nombre'], self.normal_style)],
            [Paragraph("DIRECCIÓN:", self.label_style), Paragraph(pago_data['direccion'] or "N/A", self.normal_style)],
            [Paragraph("N° TOMA:", self.label_style), Paragraph(str(pago_data.get('usuario_id', 'N/A')), self.normal_style)],
            [Paragraph("EXTRAS:", self.label_style), Paragraph(f"Vacas: {pago_data.get('vacas', 0)} | Inquilinos: {pago_data.get('inquilinos', 0)}", self.normal_style)],
        ]
        
        # Columna Derecha: Datos del Recibo
        recibo_data = [
            [Paragraph("FOLIO:", self.label_style), Paragraph(str(pago_data['id']).zfill(6), self.normal_style)],
            [Paragraph("FECHA:", self.label_style), Paragraph(fecha_pago.strftime('%d/%m/%Y'), self.normal_style)],
            [Paragraph("HORA:", self.label_style), Paragraph(fecha_pago.strftime('%H:%M hrs'), self.normal_style)],
        ]
        
        # Tablas internas
        t_cliente = Table(cliente_data, colWidths=[1*inch, 2.5*inch])
        t_recibo = Table(recibo_data, colWidths=[0.8*inch, 1.5*inch])
        
        # Tabla contenedora
        main_data = [[t_cliente, t_recibo]]
        main_table = Table(main_data, colWidths=[4*inch, 3*inch])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 1, self.colors['light_gray']),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        
        return [main_table]

    def build_payment_details(self, pago_data: Dict) -> list:
        """Tabla de Conceptos"""
        # Encabezados
        headers = [
            Paragraph("CONCEPTO", self.label_style),
            Paragraph("PERIODO", self.label_style),
            Paragraph("CANT.", self.label_style),
            Paragraph("PRECIO", self.label_style),
            Paragraph("IMPORTE", self.label_style)
        ]
        
        data = [headers]
        
        # Procesar detalles
        detalles = pago_data.get('detalles', [])
        
        # Ordenar: Mensualidades primero, luego otros
        mensualidades = [d for d in detalles if d['mes']]
        otros = [d for d in detalles if not d['mes']]
        mensualidades.sort(key=lambda x: x['mes'])
        
        # Agregar filas
        for d in mensualidades:
            mes_nombre = self.get_month_name(d['mes'])
            concepto = f"Servicio de Agua - {mes_nombre}"
            periodo = str(d['anio'])
            data.append([
                Paragraph(concepto, self.normal_style),
                Paragraph(periodo, self.normal_style),
                str(d['cantidad']),
                f"${d['precio']:.2f}",
                f"${d['precio'] * d['cantidad']:.2f}"
            ])
            
        for d in otros:
            concepto = d['concepto']
            periodo = "-"
            data.append([
                Paragraph(concepto, self.normal_style),
                Paragraph(periodo, self.normal_style),
                str(d['cantidad']),
                f"${d['precio']:.2f}",
                f"${d['precio'] * d['cantidad']:.2f}"
            ])
            
        # Si no hay detalles (caso raro)
        if len(data) == 1:
            data.append(["Sin detalles", "-", "0", "$0.00", "$0.00"])

        # Crear Tabla
        t = Table(data, colWidths=[3*inch, 1.2*inch, 0.8*inch, 1*inch, 1*inch])
        
        # Estilos de tabla
        estilos = [
            ('BACKGROUND', (0,0), (-1,0), self.colors['light_gray']),
            ('LINEBELOW', (0,0), (-1,0), 1, self.colors['primary']),
            ('ALIGN', (2,1), (-1,-1), 'CENTER'), # Cantidad centrada
            ('ALIGN', (3,1), (-1,-1), 'RIGHT'),  # Precio derecha
            ('ALIGN', (4,1), (-1,-1), 'RIGHT'),  # Importe derecha
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, self.colors['light_gray']),
            ('BOX', (0,0), (-1,-1), 0.5, self.colors['gray']),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [self.colors['white'], colors.Color(0.98, 0.99, 1.0)])
        ]
        t.setStyle(TableStyle(estilos))
        
        return [t]

    def build_totals(self, pago_data: Dict) -> list:
        """Sección de Totales"""
        total = pago_data.get('total', 0.0)
        
        # Convertir total a texto (opcional, aquí simple)
        total_text = f"${total:,.2f}"
        
        data = [
            [Paragraph("TOTAL A PAGAR:", self.total_label_style), Paragraph(total_text, self.total_value_style)]
        ]
        
        t = Table(data, colWidths=[5.5*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEABOVE', (0,0), (-1,-1), 1, self.colors['primary']),
            ('TOPPADDING', (0,0), (-1,-1), 12),
        ]))
        
        return [t]

    def build_footer(self, pago_data: Dict) -> list:
        """Firmas y Mensaje Final"""
        observaciones = pago_data.get('observaciones', '')
        
        elements = []
        
        if observaciones:
            elements.append(Paragraph(f"<b>Observaciones:</b> {observaciones}", self.normal_style))
            elements.append(Spacer(1, 20))
            
        # Área de firmas
        firma_data = [
            ["__________________________", "__________________________"],
            ["Firma de Conformidad", "Firma del Cobrador"]
        ]
        
        t_firmas = Table(firma_data, colWidths=[3.5*inch, 3.5*inch])
        t_firmas.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Oblique'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('TEXTCOLOR', (0,0), (-1,-1), self.colors['gray']),
        ]))
        
        elements.append(t_firmas)
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("¡Gracias por su pago puntual!", self.subtitle_style))
        
        return elements

    def get_month_name(self, month_num: int) -> str:
        months = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return months[month_num] if 1 <= month_num <= 12 else str(month_num)
    
    def print_receipt(self, filepath: str) -> bool:
        try:
            if os.name == 'nt': # Windows
                os.startfile(filepath, "print")
            else:
                # Linux/Mac (comando genérico, ajustar según necesidad)
                import subprocess
                subprocess.run(['lp', filepath])
            return True
        except Exception as e:
            print(f"Error al imprimir: {e}")
            return False


def main():
    """Función de prueba"""
    generator = ReceiptGenerator()
    
    # Crear un pago de prueba
    db = get_db_manager()
    
    # Verificar si hay usuarios para hacer una prueba
    usuarios = db.obtener_todos_usuarios()
    if not usuarios:
        print("No hay usuarios en la base de datos para hacer prueba")
        return
    
    # Usar el primer usuario
    usuario = usuarios[0]
    
    # Registrar un pago de prueba
    pago_id = db.registrar_pago(
        usuario_id=usuario['id'],
        meses_pagados=[1, 2, 3],
        anio=2024,
        conceptos_adicionales=[("Cooperación Anual", 100.0)],
        observaciones="Pago de prueba del sistema"
    )
    
    if pago_id > 0:
        print(f"Pago de prueba registrado con ID: {pago_id}")
        
        # Generar recibo
        pdf_path = generator.generate_receipt(pago_id)
        if pdf_path:
            print(f"Recibo generado: {pdf_path}")
        else:
            print("Error al generar recibo")
    else:
        print("Error al registrar pago de prueba")


if __name__ == "__main__":
    main()