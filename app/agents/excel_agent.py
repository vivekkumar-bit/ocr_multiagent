import json
import pandas as pd
from io import BytesIO
from app.utils.json_utils import safe_json_loads

def excel_agent(state):
    print("DEBUG: Final JSON from state (first 500 chars):")
    print(state["final_json"][:500] + "...")
    data = safe_json_loads(state["final_json"])
    output = BytesIO()

    # Helper to clean headers (stock_name -> Stock Name)
    def clean_header(h):
        return str(h).replace("_", " ").title()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 1. Main Tables (Each table gets its own primary sheet)
        tables = data.get("tables", [])
        if isinstance(tables, list) and tables:
            for i, table in enumerate(tables):
                if isinstance(table, dict) and "rows" in table and isinstance(table["rows"], list):
                    df = pd.DataFrame(table["rows"])
                    if not df.empty:
                        # Clean headers for Excel display
                        df.columns = [clean_header(c) for c in df.columns]
                        
                        sheet_name = f"Table_{i+1}" if len(tables) > 1 else "Data"
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # Auto-adjust column width
                        worksheet = writer.sheets[sheet_name]
                        for idx, col in enumerate(df.columns):
                            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4
                            worksheet.column_dimensions[chr(65 + idx)].width = max_len

        # 2. Summary/Metadata Sheet
        metadata = data.get("metadata", {})
        if isinstance(metadata, dict) and metadata:
            meta_df = pd.DataFrame(
                [(clean_header(k), v) for k, v in metadata.items()],
                columns=["Property", "Value"]
            )
            meta_df.to_excel(writer, sheet_name="Summary", index=False)
            
            # Auto-adjust column width for Summary
            worksheet = writer.sheets["Summary"]
            worksheet.column_dimensions['A'].width = 25
            worksheet.column_dimensions['B'].width = 50

        # 3. Status Sheet (for debugging/audit)
        status_data = {
            "Status": ["Success"],
            "File Type": [state.get("file_type", "unknown")]
        }
        if "error" in data:
            status_data["Status"] = ["Partial Success (Repair Active)"]
            status_data["Error Details"] = [data["error"]]
        
        pd.DataFrame(status_data).to_excel(writer, sheet_name="Processing_Log", index=False)

    return {
        "excel_file": output.getvalue(),
        "final_json": state["final_json"]
    }
