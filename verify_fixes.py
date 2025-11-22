import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("--- Verifying Modules ---")

try:
    import user_management
    print("[OK] Successfully imported user_management")
except Exception as e:
    print(f"[FAIL] Failed to import user_management: {e}")

try:
    import payment_registration
    print("[OK] Successfully imported payment_registration")
except Exception as e:
    print(f"[FAIL] Failed to import payment_registration: {e}")

try:
    from receipt_generator import ReceiptGenerator
    print("[OK] Successfully imported ReceiptGenerator")
    
    generator = ReceiptGenerator()
    print("[OK] Successfully initialized ReceiptGenerator")
    
except Exception as e:
    print(f"[FAIL] Failed to use ReceiptGenerator: {e}")

print("--- Verification Completed ---")
