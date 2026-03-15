import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter

# --- CONFIGURATION ---
TEMPLATE_FILE = "template/leave_template.pdf"
TEMP_OVERLAY_FILE = "temp_overlay.pdf"

# --- PIXEL-PERFECT COORDINATES (Extracted from Grid) ---
COORDINATES = {
    # Employee details box (Left-aligned at X:200)
    'emp_name': (200, 678),
    'emp_title': (200, 661),
    'emp_dept': (200, 644),
    
    # Checkbox 'X' marks (Centered in their respective boxes)
    'Annual': (115, 580),
    'Sick': (195, 580),
    'LWOP': (295, 580),
    'Emergency': (395, 580),
    'Other': (485, 580),
    
    # Reason box
    'other_specify': (310, 530),
    
    # Dates & Times (Row Baseline: Y:433)
    'begin_date': (105, 433),
    'begin_time': (245, 433),
    'end_date': (380, 433),
    'end_time': (490, 433),
    
    # Totals Row (Row Baseline: Y:416)
    'total_days': (210, 416),  # Prints slightly to the right of "Total Days: Full Day"
    'total_hours': (435, 416), # Prints right next to "Total Hours: "
    
    # Assumed By text (Top half of the box)
    'assumed_by': (350, 398)
}

def generate_overlay(data):
    """Creates a transparent PDF with only the text at specific coordinates"""
    c = canvas.Canvas(TEMP_OVERLAY_FILE, pagesize=A4)
    c.setFont("Helvetica", 11) 

    # 1. Draw standard details
    c.drawString(COORDINATES['emp_name'][0], COORDINATES['emp_name'][1], data['emp_name'])
    c.drawString(COORDINATES['emp_title'][0], COORDINATES['emp_title'][1], data['emp_title'])
    c.drawString(COORDINATES['emp_dept'][0], COORDINATES['emp_dept'][1], data['emp_dept'])

    # 2. Draw Checkbox 'X'
    leave_type = data['leave_type']
    if leave_type in COORDINATES:
        c.setFont("Helvetica-Bold", 14) # Make the 'X' bold and big
        c.drawString(COORDINATES[leave_type][0], COORDINATES[leave_type][1], "X")
        c.setFont("Helvetica", 11) # Revert font

    # 3. Draw specified reason if "Other"
    if data['other_specify']:
        c.drawString(COORDINATES['other_specify'][0], COORDINATES['other_specify'][1], data['other_specify'])

    # 4. Draw Dates & Times
    c.drawString(COORDINATES['begin_date'][0], COORDINATES['begin_date'][1], data['begin_date'])
    c.drawString(COORDINATES['begin_time'][0], COORDINATES['begin_time'][1], data['begin_time'])
    c.drawString(COORDINATES['end_date'][0], COORDINATES['end_date'][1], data['end_date'])
    c.drawString(COORDINATES['end_time'][0], COORDINATES['end_time'][1], data['end_time'])
    
    # 5. Draw Totals & Coverage
    c.drawString(COORDINATES['total_hours'][0], COORDINATES['total_hours'][1], data['total_hours'])
    c.drawString(COORDINATES['assumed_by'][0], COORDINATES['assumed_by'][1], data['assumed_by'])
    
    # Only print custom total days if they specify something other than Full Day
    if data['total_days'].lower() not in ["full day", "-", ""]:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(COORDINATES['total_days'][0], COORDINATES['total_days'][1], f"({data['total_days']})")

    c.save()

def apply_overlay_to_template(output_filename):
    """Merges the text overlay onto the actual company template"""
    template_reader = PdfReader(TEMPLATE_FILE)
    overlay_reader = PdfReader(TEMP_OVERLAY_FILE)
    writer = PdfWriter()

    page = template_reader.pages[0]
    overlay_page = overlay_reader.pages[0]
    page.merge_page(overlay_page)
    
    writer.add_page(page)

    with open(output_filename, "wb") as f:
        writer.write(f)

    os.remove(TEMP_OVERLAY_FILE)

def main():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ ERROR: Please put your blank company PDF in this folder and name it '{TEMPLATE_FILE}'")
        return

    print("=== Navya Advisors: Automated Leave Form Filler ===")
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    # Command Line Inputs
    data = {
        'emp_name': input("Employee Name [Manjil Budhathoki]: ") or "Manjil Budhathoki",
        'emp_title': input("Position [Backend Intern]: ") or "Backend Intern",
        'emp_dept': input("Department [Tech Department]: ") or "Tech Department",
        'begin_date': input(f"Begin Date [{today_str}]: ") or today_str,
        'begin_time': input("Begin Time [9:00]: ") or "9:00",
        'end_date': input(f"End Date [{today_str}]: ") or today_str,
        'end_time': input("End Time [6:00]: ") or "6:00",
        'total_days': input("Total Days (Leave blank for Full Day): ") or "Full Day",
        'total_hours': input("Total Hours [9]: ") or "9",
        'assumed_by': input("Duties assumed by [-]: ") or "-"
    }

    print("\nTypes: 1:Annual, 2:Sick, 3:LWOP, 4:Emergency, 5:Other")
    l_type = input("Select Leave Type (1-5) [2]: ") or "2"
    type_map = {"1":"Annual", "2":"Sick", "3":"LWOP", "4":"Emergency", "5":"Other"}
    data['leave_type'] = type_map.get(l_type, "Sick")
    
    data['other_specify'] = ""
    if data['leave_type'] == "Other":
        data['other_specify'] = input("Specify Other Reason: ")

    out_name = input(f"Output Name [Leave_Application_{today_str}]: ") or f"Leave_Application_{today_str}"
    output_filename = f"{out_name}.pdf"

    # Generate File
    generate_overlay(data)
    apply_overlay_to_template(output_filename)

    print(f"\n✅ Perfect! Form filled and saved as: {os.path.abspath(output_filename)}")

if __name__ == '__main__':
    main()