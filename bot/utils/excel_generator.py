import pandas as pd
import io

def generate_report():
    # Stub implementation: In a real scenario, this fetches data from Supabase
    df = pd.DataFrame({"Item": ["Item A", "Item B"], "Stock": [10, 20], "Monthly Sales": [150, 80]})
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventory Report')
    
    buffer.seek(0)
    return buffer
