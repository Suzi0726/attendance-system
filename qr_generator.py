# qr_generator.py

import qrcode

base_url = "https://attendance-system-wbqo.onrender.com"  # Change to your live Streamlit link after deploying
staff_ids = ["EMP001", "EMP002", "EMP003", "EMP004", "EMP005", "EMP006", "EMP007",
             "EMP008", "EMP009", "EMP010", "EMP011", "EMP012", "EMP013", "EMP014",
             "EMP015", "EMP016", "EMP017", "EMP018", "EMP019", "EMP020"]

for staff_id in staff_ids:
    full_url = f"{base_url}/?staff={staff_id}"
    img = qrcode.make(full_url)
    img.save(f"{staff_id}.png")
    print(f"✅ QR code saved for {staff_id}")
