import openpyxl
from openpyxl.cell.cell import MergedCell
import os

class ExcelManager:
    @staticmethod
    def _get_target_cell(ws, coord):
        """Devuelve la celda real (Top-Left si es Merged)"""
        cell = ws[coord]
        if isinstance(cell, MergedCell):
            for merged_range in ws.merged_cells.ranges:
                if coord in merged_range:
                    return ws.cell(row=merged_range.min_row, column=merged_range.min_col)
        return cell

    @staticmethod
    def generar_recibo(datos):
        base_dir = os.getcwd()
        template_path = os.path.join(base_dir, 'RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
        output_path = os.path.join(base_dir, 'recibo_temp.xlsx')

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"No se encontró la plantilla en: {template_path}")

        wb = openpyxl.load_workbook(template_path)
        
        if 'RECIBO 2025' in wb.sheetnames:
            ws = wb['RECIBO 2025']
        else:
            ws = wb.active

        # Función helper para escribir
        def write_safe(coord, value, clear_if_first=False):
            target = ExcelManager._get_target_cell(ws, coord)
            # Solo asignar, sobrescribiendo (openpyxl no tiene problema sobrescribiendo Top-Left)
            target.value = value
            return target

        # Extraer datos
        folio = datos.get('folio', '')
        fecha = datos.get('fecha', '')
        id_usuario = datos.get('id_usuario', '')
        nombre = datos.get('nombre', '')
        direccion = datos.get('direccion', '')
        tomas = datos.get('tomas', '')
        total = datos.get('total', 0.0)
        conceptos = datos.get('conceptos', [])

        # Mapeo Directo (Simples)
        write_safe('L2', folio)
        write_safe('L26', folio)
        write_safe('I5', fecha)
        write_safe('I29', fecha)
        write_safe('C6', id_usuario)
        write_safe('C30', id_usuario)
        write_safe('B8', nombre)
        write_safe('B32', nombre)
        write_safe('H8', direccion)
        write_safe('H32', direccion)
        write_safe('B10', tomas)
        write_safe('B34', tomas)
        write_safe('K18', total)
        # K42 es merged -> La función _get_target_cell lo resolverá a K41 automáticamente
        write_safe('K42', total)

        # Conceptos
        start_row_original = 12
        start_row_copy = 36
        
        # Rastrear celdas escritas para concatenar
        written_desc_coords_orig = set()
        
        # Limpiar área de conceptos original (Solo A12/B12 inicial si queremos ser puros, pero asumimos overwrite)
        
        for i, concepto in enumerate(conceptos):
            desc = concepto.get('descripcion', '')
            precio = concepto.get('importe', 0.0)
            
            # --- ORIGINAL ---
            coord_desc = f'B{start_row_original + i}'
            coord_precio = f'D{start_row_original + i}'
            
            target_desc = ExcelManager._get_target_cell(ws, coord_desc)
            target_precio = ExcelManager._get_target_cell(ws, coord_precio)
            
            # Lógica de concatenación para Descripción
            if target_desc.coordinate in written_desc_coords_orig:
                # Ya escribimos en esta celda (e.g. A12), concatenar
                current_text = str(target_desc.value) if target_desc.value else ""
                target_desc.value = current_text + "\n" + desc
            else:
                # Primera vez en esta celda para este recibo
                if i == 0: 
                    target_desc.value = desc # Primera línea absoluta
                else:
                    # Si saltamos a una nueva celda pero no es la primera vuelta, 
                    # sobrescribimos lo que tuviera la plantilla (idealmente vacía)
                    target_desc.value = desc
                written_desc_coords_orig.add(target_desc.coordinate)
            
            # Precio (Asumimos celdas individuales, pero si son merged se comportará igual de mal si no concatenamos, 
            # pero precios concatenados son feos. Asumimos D12, D13... son celdas distintas o un-merged)
            # Si D12 es merged a D12:D14, sobrescribiríamos.
            # La inspección mostró D12 normal.
            target_precio.value = precio

            # --- COPIA ---
            # Asumimos que la copia (B36 en adelante) son celdas normales según inspección
            coord_desc_copy = f'B{start_row_copy + i}'
            coord_precio_copy = f'D{start_row_copy + i}'
            
            write_safe(coord_desc_copy, desc)
            write_safe(coord_precio_copy, precio)

        # Guardar archivo con manejo de errores (PermissionError si está abierto)
        try:
            wb.save(output_path)
        except PermissionError:
            # Si el archivo está abierto, intentar con otro nombre
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(base_dir, f'recibo_temp_{timestamp}.xlsx')
            wb.save(output_path) # Si falla aquí, dejamos que explote para saberlo

        wb.close()
        return os.path.abspath(output_path)
