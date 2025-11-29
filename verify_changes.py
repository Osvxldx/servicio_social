import sys
import os
import datetime
from src.database import DatabaseManager
from src.receipt_generator import ReceiptGenerator

def log(msg):
    with open("verification_log.txt", "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")
    print(msg)

def verify():
    if os.path.exists("verification_log.txt"):
        os.remove("verification_log.txt")
        
    log("Iniciando verificación...")
    
    # 1. Inicializar DB y Migración
    db = DatabaseManager("test_db.sqlite")
    # INYECTAR DB DE PRUEBA EN EL SINGLETON
    import src.database
    src.database._db_manager = db
    log("DB inicializada e inyectada.")
    
    # 2. Crear Usuario
    log("Creando usuario de prueba...")
    # Usar un nombre único para evitar duplicados si la DB persiste
    nombre_user = f"Usuario Test {datetime.datetime.now().timestamp()}"
    db.crear_usuario(nombre_user, 1, "Direccion Test", "1234567890", "test@test.com")
    
    # Obtener ID
    users = db.buscar_usuarios_por_nombre(nombre_user)
    if not users:
        log("ERROR: No se creó el usuario")
        return
    user_id = users[0]['id']
    log(f"Usuario creado con ID: {user_id}")
    
    # 3. Verificar Historial
    historial = db.obtener_historial_estatus(user_id)
    log(f"Historial inicial: {historial}")
    if not historial:
        log("ERROR: No se creó historial inicial")
    
    # 4. Probar cálculo de adeudo
    log("Probando cálculo de adeudo...")
    meses_adeudo = db.obtener_meses_adeudo(user_id, datetime.datetime.now().year)
    log(f"Meses adeudo (recién creado): {meses_adeudo}")
    
    # 5. Generar Estado de Cuenta
    log("Generando estado de cuenta...")
    gen = ReceiptGenerator()
    gen.receipts_dir = "test_recibos"
    gen.ensure_directories()
    
    pdf_path = gen.generate_account_statement(user_id, inasistencias=2)
    if pdf_path and os.path.exists(pdf_path):
        log(f"Estado de cuenta generado: {pdf_path}")
    else:
        log("ERROR: No se generó el estado de cuenta")

    # 6. Generar Multa Desperdicio
    log("Generando multa desperdicio...")
    pago_id = db.registrar_pago(user_id, [{'concepto': 'Multa Desperdicio', 'precio': 500.0, 'cantidad': 1}], "Prueba Multa")
    log(f"Pago registrado con ID: {pago_id}")
    
    # DEBUG
    log(f"DEBUG: Verificando pago {pago_id} para usuario {user_id}")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pagos WHERE id=?", (pago_id,))
    log(f"DEBUG: Pago raw: {cursor.fetchone()}")
    
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    log(f"DEBUG: Usuario raw: {cursor.fetchone()}")
    
    pago_data = db.obtener_detalle_pago(pago_id)
    log(f"DEBUG: obtener_detalle_pago resultado: {pago_data}")
    conn.close()

    if pago_id == 0:
        log("ERROR: Falló registrar_pago")
    else:
        pdf_waste = gen.generate_waste_receipt(pago_id)
        if pdf_waste and os.path.exists(pdf_waste):
            log(f"Recibo multa generado: {pdf_waste}")
        else:
            log("ERROR: No se generó el recibo de multa (generate_waste_receipt devolvió None o archivo no existe)")

    log("Verificación completada.")

if __name__ == "__main__":
    verify()
