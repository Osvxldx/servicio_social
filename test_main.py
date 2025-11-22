#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el error
"""

import sys
import traceback

try:
    print("Intentando importar main...")
    from main import MainApplication
    print("✅ main importado correctamente")
    
    print("\nIntentando crear la aplicación...")
    app = MainApplication()
    print("✅ Aplicación creada correctamente")
    
    print("\n✅ Todo funcionó correctamente!")
    print("El app debería iniciar sin problemas.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n=== TRACEBACK COMPLETO ===")
    traceback.print_exc()
