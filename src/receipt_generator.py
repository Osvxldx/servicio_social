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
from reportlab.lib.units import inch, mm, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Frame, PageTemplate, BaseDocTemplate, FrameBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from .database import get_db_manager
import traceback

class ReceiptGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.colors = {
            'primary': colors.black,
            'text': colors.black,
            'gray': colors.Color(0.50, 0.50, 0.50),
            'light_gray': colors.Color(0.90, 0.90, 0.90),
        }
        self.create_custom_styles()
        self.receipts_dir = "recibos"
        self.ensure_directories()
    
    def create_custom_styles(self):
        """Crea estilos personalizados"""
        self.title_style = ParagraphStyle(
            'ReceiptTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            leading=16,
            alignment=TA_CENTER,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'ReceiptSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'ReceiptNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            alignment=TA_LEFT,
            textColor=self.colors['text'],
            fontName='Helvetica'
        )
        
        self.bold_style = ParagraphStyle(
            'ReceiptBold',
            parent=self.normal_style,
            fontName='Helvetica-Bold'
        )
        
        self.center_style = ParagraphStyle(
            'ReceiptCenter',
            parent=self.normal_style,
            alignment=TA_CENTER
        )
        
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.normal_style,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            fontSize=8
        )
        
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.normal_style,
            alignment=TA_CENTER,
            fontSize=8
        )

    def ensure_directories(self):
        if not os.path.exists(self.receipts_dir):
            os.makedirs(self.receipts_dir)
    
    def log_error(self, context: str, e: Exception):
        try:
            with open("error_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] Error en {context}: {e}\n")
                traceback.print_exc(file=f)
        except:
            print(f"Error logging error: {e}")

    def generate_waste_receipt(self, pago_id: int) -> Optional[str]:
        """Genera un recibo específico para multa por desperdicio"""
        try:
            db = get_db_manager()
            pago_data = db.obtener_detalle_pago(pago_id)
            
            if not pago_data:
                return None
            
            filename = f"multa_desperdicio_{pago_id}.pdf"
            filepath = os.path.join(self.receipts_dir, filename)
            
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=1*cm,
                leftMargin=1*cm,
                topMargin=1*cm,
                bottomMargin=1*cm
            )
            
            elements = []
            
            # Logo
            logo_path = os.path.join("assets", "logo.jpg")
            if os.path.exists(logo_path):
                elements.append(Image(logo_path, width=3*cm, height=3*cm))
                elements.append(Spacer(1, 10))
            
            # Títulos
            elements.append(Paragraph("COMITÉ DE AGUA POTABLE Y ALCANTARILLADO", self.title_style))
            elements.append(Paragraph("DEL BARRIO DE SAN ANTONIO TECAMACHALCO, PUE.", self.subtitle_style))
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph("MULTA POR DESPERDICIO DE AGUA", self.title_style))
            elements.append(Spacer(1, 20))
            
            # Datos
            fecha = datetime.strptime(pago_data['fecha_pago'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            
            data = [
                ["FOLIO:", f"{pago_data['id']:06d}"],
                ["FECHA:", fecha],
                ["USUARIO:", f"{pago_data['nombre']} (ID: {pago_data['usuario_id']})"],
                ["DIRECCIÓN:", pago_data['direccion']],
                ["OBSERVACIONES:", pago_data.get('observaciones', 'Desperdicio de agua')],
                ["TOTAL A PAGAR:", f"${pago_data['total']:.2f}"]
            ]
            
            t = Table(data, colWidths=[5*cm, 10*cm])
            t.setStyle(TableStyle([
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('SIZE', (0,0), (-1,-1), 12),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('TEXTCOLOR', (0,-1), (-1,-1), colors.red), # Total en rojo
            ]))
            
            elements.append(t)
            elements.append(Spacer(1, 40))
            
            # Firmas
            firmas_data = [
                ["_____________________________", "_____________________________"],
                ["FIRMA DE CONFORMIDAD", "AUTORIZÓ"]
            ]
            t_firmas = Table(firmas_data, colWidths=[8*cm, 8*cm])
            t_firmas.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            elements.append(t_firmas)
            
            doc.build(elements)
            return filepath
            
        except Exception as e:
            self.log_error("generate_waste_receipt", e)
            print(f"Error generando multa: {e}")
            return None

    def generate_account_statement(self, user_id: int, inasistencias: int = 0) -> Optional[str]:
        """Genera un estado de cuenta / resumen de adeudo"""
        try:
            db = get_db_manager()
            user = db.buscar_usuario_por_id(user_id)
            if not user: return None
            
            year = datetime.now().year
            
            # 1. Obtener meses de adeudo usando la lógica robusta
            meses_adeudo_nums = db.obtener_meses_adeudo(user_id, year)
            
            meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            
            adeudos = []
            total_deuda = 0.0
            
            cuota_base = float(db.obtener_configuracion('cuota_mensual') or 70.0)
            tomas = user.get('tomas', 1)
            costo_mensual = cuota_base * tomas
            
            # Procesar meses de adeudo
            for mes_num in meses_adeudo_nums:
                nombre_mes = meses_nombres[mes_num - 1]
                
                monto = costo_mensual
                # Agregar recargo si aplica (si el mes ya pasó)
                if datetime.now().month > mes_num:
                    recargo = (100.0 * tomas) - costo_mensual
                    if recargo > 0:
                        monto += recargo
                
                adeudos.append([nombre_mes, f"${monto:.2f}"])
                total_deuda += monto
            
            # Procesar Inasistencias
            if inasistencias > 0:
                costo_inasistencia = float(db.obtener_configuracion('multa_inasistencia') or 200.0)
                total_inasistencias = inasistencias * costo_inasistencia
                adeudos.append([f"Inasistencias ({inasistencias})", f"${total_inasistencias:.2f}"])
                total_deuda += total_inasistencias

            filename = f"estado_cuenta_{user_id}.pdf"
            filepath = os.path.join(self.receipts_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            
            # Logo
            logo_path = os.path.join("assets", "logo.jpg")
            if os.path.exists(logo_path):
                elements.append(Image(logo_path, width=2*cm, height=2*cm))
                elements.append(Spacer(1, 10))

            elements.append(Paragraph(f"ESTADO DE CUENTA - {year}", self.title_style))
            elements.append(Spacer(1, 20))
            
            # Info Usuario
            elements.append(Paragraph(f"<b>Usuario:</b> {user['nombre']} (ID: {user['id']})", self.normal_style))
            elements.append(Paragraph(f"<b>Dirección:</b> {user['direccion']}", self.normal_style))
            elements.append(Paragraph(f"<b>Tomas:</b> {tomas} | <b>Sesión:</b> {user['sesion']}", self.normal_style))
            elements.append(Spacer(1, 20))
            
            # Tabla de Adeudos
            if adeudos:
                data = [["CONCEPTO", "MONTO ESTIMADO"]] + adeudos
                data.append(["TOTAL A PAGAR", f"${total_deuda:.2f}"])
                
                t = Table(data, colWidths=[10*cm, 4*cm])
                t.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (0,1), (0,-2), 'LEFT'), # Alinear conceptos a la izquierda
                    ('TEXTCOLOR', (0,-1), (-1,-1), colors.red),
                ]))
                elements.append(t)
            else:
                elements.append(Paragraph("¡FELICIDADES! NO PRESENTA ADEUDOS ESTE AÑO.", self.title_style))
                
            # Nota
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("Nota: Este documento es informativo y no representa un comprobante de pago oficial.", self.center_style))
            
            doc.build(elements)
            return filepath
            
        except Exception as e:
            self.log_error("generate_account_statement", e)
            print(f"Error estado cuenta: {e}")
            return None

    def generate_receipt(self, pago_id: int) -> Optional[str]:
        try:
            db = get_db_manager()
            pago_data = db.obtener_detalle_pago(pago_id)
            
            if not pago_data:
                print(f"No se encontró el pago con ID {pago_id}")
                return None
            
            # Nombre de archivo fijo
            filename = "recibo_temporal.pdf"
            filepath = os.path.join(self.receipts_dir, filename)
            
            # Configurar documento
            doc = BaseDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=0.5*cm,
                leftMargin=0.5*cm,
                topMargin=0.5*cm,
                bottomMargin=0.5*cm
            )
            
            # Definir frames para media carta (superior e inferior)
            page_width, page_height = letter
            half_height = page_height / 2
            
            frame_top = Frame(
                doc.leftMargin, 
                half_height + 0.5*cm, 
                page_width - doc.leftMargin - doc.rightMargin, 
                half_height - 1.5*cm,
                id='user_copy',
                showBoundary=0
            )
            
            frame_bottom = Frame(
                doc.leftMargin, 
                doc.bottomMargin, 
                page_width - doc.leftMargin - doc.rightMargin, 
                half_height - 1.5*cm,
                id='admin_copy',
                showBoundary=0
            )
            
            template = PageTemplate(id='dual_receipt', frames=[frame_top, frame_bottom])
            doc.addPageTemplates([template])
            
            # Construir contenido
            story = []
            
            # Copia Usuario
            story.extend(self.build_receipt_copy(pago_data, "USUARIO"))
            story.append(FrameBreak())
            
            # Copia Comité
            story.extend(self.build_receipt_copy(pago_data, "COMITÉ"))
            
            doc.build(story)
            return filepath
            
        except Exception as e:
            self.log_error("generate_receipt", e)
            print(f"Error generando recibo: {e}")
            import traceback
            traceback.print_exc()
            return None

    def build_receipt_copy(self, pago_data: Dict, copy_type: str) -> list:
        elements = []
        
        # --- ENCABEZADO ---
        # Logo
        logo_path = os.path.join("assets", "logo.jpg")
        logo_img = None
        if os.path.exists(logo_path):
            logo_img = Image(logo_path, width=2.5*cm, height=2.5*cm)
        
        # Textos del encabezado
        header_text = [
            Paragraph("COMITÉ DE AGUA POTABLE Y ALCANTARILLADO", self.title_style),
            Paragraph("DEL BARRIO DE SAN ANTONIO TECAMACHALCO, PUE.", self.subtitle_style),
            Paragraph("R.F.C. CAP980115194", self.normal_style),
            Spacer(1, 5),
            Paragraph(f"RECIBO DE PAGO - COPIA {copy_type}", self.bold_style)
        ]
        
        # Tabla de encabezado (Logo | Texto | Folio/Fecha)
        fecha_pago = datetime.strptime(pago_data['fecha_pago'], '%Y-%m-%d %H:%M:%S')
        folio_fecha = [
            Paragraph(f"<b>FOLIO:</b> {pago_data['id']:06d}", self.normal_style),
            Paragraph(f"<b>FECHA:</b> {fecha_pago.strftime('%d/%m/%Y')}", self.normal_style),
            Paragraph(f"<b>HORA:</b> {fecha_pago.strftime('%H:%M')}", self.normal_style)
        ]
        
        header_data = [[logo_img if logo_img else "", header_text, folio_fecha]]
        t_header = Table(header_data, colWidths=[3*cm, 12*cm, 4*cm])
        t_header.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 10))
        
        # --- DATOS DEL USUARIO ---
        user_data = [
            [Paragraph(f"<b>USUARIO No.:</b> {pago_data['usuario_id']}", self.normal_style),
             Paragraph(f"<b>NOMBRE:</b> {pago_data['nombre']}", self.normal_style)],
            [Paragraph(f"<b>DIRECCIÓN:</b> {pago_data['direccion']}", self.normal_style),
             ""] # Span para dirección
        ]
        
        t_user = Table(user_data, colWidths=[6*cm, 13*cm])
        t_user.setStyle(TableStyle([
            ('SPAN', (1,1), (-1,1)), # Unir celdas de dirección
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_user)
        elements.append(Spacer(1, 10))
        
        # --- TABLA DE CONCEPTOS ---
        # Columnas: CONCEPTO | CUOTA | VACAS | INQUILINOS | INASISTENCIA | COOP | TOMA N | TOTAL
        headers = [
            Paragraph("CONCEPTO", self.table_header_style),
            Paragraph("CUOTA X TOMA", self.table_header_style),
            Paragraph("VACAS", self.table_header_style),
            Paragraph("INQUILINOS", self.table_header_style),
            Paragraph("INASISTENCIA", self.table_header_style),
            Paragraph("COOPERACIONES", self.table_header_style),
            Paragraph("TOMA NUEVA", self.table_header_style),
            Paragraph("TOTAL", self.table_header_style)
        ]
        
        # Procesar detalles para llenar la tabla
        rows = []
        detalles = pago_data['detalles']
        
        # Organizar datos para la tabla
        meses_procesados = {}
        extras = {'cooperacion': 0, 'toma_nueva': 0, 'inasistencia': 0}
        
        for d in detalles:
            concepto = d['concepto'].lower()
            precio = d['precio']
            
            if 'mensualidad' in concepto or 'recargo' in concepto:
                # Extraer mes si es posible
                mes_str = "PAGO"
                if 'enero' in concepto: mes_str = "ENERO"
                elif 'febrero' in concepto: mes_str = "FEBRERO"
                elif 'marzo' in concepto: mes_str = "MARZO"
                elif 'abril' in concepto: mes_str = "ABRIL"
                elif 'mayo' in concepto: mes_str = "MAYO"
                elif 'junio' in concepto: mes_str = "JUNIO"
                elif 'julio' in concepto: mes_str = "JULIO"
                elif 'agosto' in concepto: mes_str = "AGOSTO"
                elif 'septiembre' in concepto: mes_str = "SEPTIEMBRE"
                elif 'octubre' in concepto: mes_str = "OCTUBRE"
                elif 'noviembre' in concepto: mes_str = "NOVIEMBRE"
                elif 'diciembre' in concepto: mes_str = "DICIEMBRE"
                
                if mes_str not in meses_procesados:
                    meses_procesados[mes_str] = {'cuota': 0, 'vacas': 0, 'inquilinos': 0, 'total': 0}
                
                meses_procesados[mes_str]['cuota'] += precio
                meses_procesados[mes_str]['total'] += precio
                
            elif 'vacas' in concepto:
                key = list(meses_procesados.keys())[-1] if meses_procesados else "VARIOS"
                if key not in meses_procesados: meses_procesados[key] = {'cuota': 0, 'vacas': 0, 'inquilinos': 0, 'total': 0}
                meses_procesados[key]['vacas'] += precio
                meses_procesados[key]['total'] += precio
                
            elif 'inquilinos' in concepto:
                key = list(meses_procesados.keys())[-1] if meses_procesados else "VARIOS"
                if key not in meses_procesados: meses_procesados[key] = {'cuota': 0, 'vacas': 0, 'inquilinos': 0, 'total': 0}
                meses_procesados[key]['inquilinos'] += precio
                meses_procesados[key]['total'] += precio
                
            elif 'cooperación' in concepto or 'cooperacion' in concepto:
                extras['cooperacion'] += precio
            elif 'toma nueva' in concepto:
                extras['toma_nueva'] += precio
            elif 'inasistencia' in concepto:
                extras['inasistencia'] += precio
        
        # Construir filas de la tabla
        table_data = [headers]
        
        # Filas de meses
        for mes, data in meses_procesados.items():
            row = [
                Paragraph(mes, self.table_cell_style),
                Paragraph(f"${data['cuota']:.2f}", self.table_cell_style),
                Paragraph(f"${data['vacas']:.2f}", self.table_cell_style),
                Paragraph(f"${data['inquilinos']:.2f}", self.table_cell_style),
                Paragraph("-", self.table_cell_style),
                Paragraph("-", self.table_cell_style),
                Paragraph("-", self.table_cell_style),
                Paragraph(f"${data['total']:.2f}", self.table_cell_style)
            ]
            table_data.append(row)
            
        # Fila de Extras si existen
        if any(extras.values()):
            total_extras = sum(extras.values())
            row = [
                Paragraph("OTROS CARGOS", self.table_cell_style),
                Paragraph("-", self.table_cell_style),
                Paragraph("-", self.table_cell_style),
                Paragraph("-", self.table_cell_style),
                Paragraph(f"${extras['inasistencia']:.2f}", self.table_cell_style),
                Paragraph(f"${extras['cooperacion']:.2f}", self.table_cell_style),
                Paragraph(f"${extras['toma_nueva']:.2f}", self.table_cell_style),
                Paragraph(f"${total_extras:.2f}", self.table_cell_style)
            ]
            table_data.append(row)
            
        # Fila Total
        total_row = [
            Paragraph("<b>TOTAL A PAGAR</b>", self.table_header_style),
            "", "", "", "", "", "",
            Paragraph(f"<b>${pago_data['total']:.2f}</b>", self.table_header_style)
        ]
        table_data.append(total_row)
        
        # Estilo de tabla
        t_detalles = Table(table_data, colWidths=[3*cm, 2.2*cm, 2*cm, 2.2*cm, 2.5*cm, 2.5*cm, 2.2*cm, 2.4*cm])
        t_detalles.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('SPAN', (0,-1), (-2,-1)), # Unir celdas del total label
        ]))
        elements.append(t_detalles)
        elements.append(Spacer(1, 20))
        
        # --- PIE DE PÁGINA ---
        # Firmas
        firmas_data = [
            [Paragraph("_____________________________", self.center_style), 
             Paragraph("_____________________________", self.center_style)],
            [Paragraph("FIRMA DE CONFORMIDAD", self.center_style), 
             Paragraph("AUTORIZÓ", self.center_style)]
        ]
        
        t_firmas = Table(firmas_data, colWidths=[9*cm, 9*cm])
        t_firmas.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t_firmas)
        
        # Nota al pie
        elements.append(Spacer(1, 10))
        nota = "NOTA: ESTE RECIBO NO ES VÁLIDO SI PRESENTA TACHADURAS O ENMENDADURAS."
        elements.append(Paragraph(nota, self.center_style))
        
        return elements