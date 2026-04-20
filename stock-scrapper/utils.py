import io
import csv
import json
from typing import List, Dict
from fastapi.responses import StreamingResponse

def to_csv_response(data: List[Dict], filename: str, fields: List[str]):
    if not data:
        print(f"Warning: No data found for {filename}")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(data)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
    )

def to_json_response(data: List[Dict], filename: str):
    return StreamingResponse(
        io.BytesIO(json.dumps(data, indent=4).encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}.json"}
    )