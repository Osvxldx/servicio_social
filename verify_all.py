import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def verify_module(module_name):
    try:
        print(f"Verifying {module_name}...")
        __import__(module_name)
        print(f"✅ {module_name} imported successfully.")
        return True
    except Exception as e:
        print(f"❌ Error importing {module_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

modules = [
    "database",
    "payment_registration",
    "receipt_generator",
    "configuration",
    "user_management",
    "main"
]

success = True
for mod in modules:
    if not verify_module(mod):
        success = False

if success:
    print("\nAll modules verified successfully!")
else:
    print("\nSome modules failed verification.")
