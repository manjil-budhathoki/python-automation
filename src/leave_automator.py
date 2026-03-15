import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

# --- CONFIGURATION ---
TEMPLATE_FILE = "template/leave_template.pdf"
CONFIG_FILE = "form_config.json"
TEMP_OVERLAY_FILE = "temp_overlay.pdf"
ZOOM_FACTOR = 1.5

# Standard fields the CLI will ask for. 
# (You will type these exact names when drawing boxes in the GUI)
EXPECTED_FIELDS = [
    'emp_name', 'emp_title', 'emp_dept', 
    'Annual', 'Sick', 'LWOP', 'Emergency', 'Other', 
    'other_specify', 'begin_date', 'begin_time', 'end_date', 'end_time', 
    'total_days', 'total_hours', 'assumed_by'
]

# ==========================================
# 1. GUI MAPPER CLASS
# ==========================================
class PDFMapperApp:
    def __init__(self, root, pdf_path):
        self.root = root
        self.root.title("Navya Advisors - Setup Form Layout")
        self.coordinates = {}
        
        try:
            self.doc = fitz.open(pdf_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open {pdf_path}")
            self.root.destroy()
            return

        self.page = self.doc[0]
        self.pdf_width = self.page.rect.width
        self.pdf_height = self.page.rect.height

        mat = fitz.Matrix(ZOOM_FACTOR, ZOOM_FACTOR)
        pix = self.page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.tk_img = ImageTk.PhotoImage(img)

        # Top Bar with Instructions and Save Button
        top_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        top_frame.pack(fill=tk.X)
        
        lbl = tk.Label(top_frame, text="Drag boxes over the blank lines. Type the field name. Click Save when done.", bg="#f0f0f0", font=("Arial", 10))
        lbl.pack(side=tk.LEFT, padx=10)
        
        btn_save = tk.Button(top_frame, text="✅ SAVE & CONTINUE", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.save_and_exit)
        btn_save.pack(side=tk.RIGHT, padx=10)

        # Canvas Setup
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(frame, cursor="cross")
        
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.canvas.yview)
        hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # Mouse Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.start_x = None
        self.start_y = None
        self.rect = None

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        box_left = min(self.start_x, end_x)
        box_bottom = max(self.start_y, end_y)

        # Convert to true PDF coordinates
        pdf_x = box_left / ZOOM_FACTOR
        pdf_y = self.pdf_height - (box_bottom / ZOOM_FACTOR)

        field_list = "\n".join([f"- {f}" for f in EXPECTED_FIELDS])
        field_name = simpledialog.askstring("Map Field", f"Enter field name (e.g., emp_name, Sick, begin_date):\n\nExpected Fields:\n{field_list}")
        
        if field_name:
            self.coordinates[field_name] = (int(pdf_x), int(pdf_y))
            self.canvas.create_text(box_left, box_bottom - 5, anchor=tk.SW, text=field_name, fill="blue", font=("Arial", 12, "bold"))
        
        self.canvas.delete(self.rect)
        self.rect = None

    def save_and_exit(self):
        config_data = {
            "dimensions": {"width": self.pdf_width, "height": self.pdf_height},
            "coordinates": self.coordinates
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
        print("\n✅ Layout saved successfully!")
        self.root.destroy()

# ==========================================
# 2. PDF GENERATOR FUNCTION
# ==========================================
def safe_draw(c, config, key, text, is_checkbox=False):
    """Safely draws text only if the field was mapped in the GUI."""
    if key in config['coordinates'] and text:
        coords = config['coordinates'][key]
        if is_checkbox:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(coords[0], coords[1], "X")
        else:
            c.setFont("Helvetica", 11)
            c.drawString(coords[0], coords[1], str(text))

def generate_final_pdf(data, config, output_filename):
    width = config['dimensions']['width']
    height = config['dimensions']['height']

    # Draw exactly over the custom template dimensions
    c = canvas.Canvas(TEMP_OVERLAY_FILE, pagesize=(width, height))
    
    # Draw standard text fields
    text_fields = ['emp_name', 'emp_title', 'emp_dept', 'begin_date', 'begin_time', 
                   'end_date', 'end_time', 'total_hours', 'assumed_by', 'other_specify']
    for field in text_fields:
        safe_draw(c, config, field, data.get(field, ""))

    # Draw Checkbox
    safe_draw(c, config, data['leave_type'], "X", is_checkbox=True)

    # Custom logic for "total_days" to avoid overwriting default text
    if data['total_days'].lower() not in ["full day", "full", "-", ""]:
        if 'total_days' in config['coordinates']:
            coords = config['coordinates']['total_days']
            c.setFont("Helvetica-Bold", 11)
            c.drawString(coords[0], coords[1], f"({data['total_days']})")

    c.save()

    # Merge PDFs
    template_reader = PdfReader(TEMPLATE_FILE)
    template_page = template_reader.pages[0]
    
    overlay_reader = PdfReader(TEMP_OVERLAY_FILE)
    template_page.merge_page(overlay_reader.pages[0])
    
    writer = PdfWriter()
    writer.add_page(template_page)

    with open(output_filename, "wb") as f:
        writer.write(f)

    os.remove(TEMP_OVERLAY_FILE)

# ==========================================
# 3. MAIN WORKFLOW
# ==========================================
def main():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ ERROR: Put your blank PDF in this folder and name it '{TEMPLATE_FILE}'.")
        return

    print("=== 🚀 Navya Advisors: Automated Leave Form Generator ===")
    
    # Check if we already have a saved layout
    needs_mapping = True
    if os.path.exists(CONFIG_FILE):
        choice = input(f"📁 Found saved layout. Use it? [Y/n]: ").strip().lower()
        if choice == '' or choice == 'y':
            needs_mapping = False

    if needs_mapping:
        print("\nOpening Mapper UI. Please map your fields...")
        root = tk.Tk()
        root.geometry("1000x800")
        app = PDFMapperApp(root, TEMPLATE_FILE)
        root.mainloop()
        
        # Check if they actually saved the file before continuing
        if not os.path.exists(CONFIG_FILE):
            print("Mapping cancelled. Exiting.")
            return

    # Load the configuration
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    print("\n--- Let's fill out your application ---")
    today_str = datetime.today().strftime('%Y-%m-%d')
    
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

    print("\nSelect Leave Type: 1:Annual | 2:Sick | 3:LWOP | 4:Emergency | 5:Other")
    l_type = input("Choice (1-5) [2]: ") or "2"
    type_map = {"1":"Annual", "2":"Sick", "3":"LWOP", "4":"Emergency", "5":"Other"}
    data['leave_type'] = type_map.get(l_type, "Sick")
    
    data['other_specify'] = input("Specify Other Reason: ") if data['leave_type'] == "Other" else ""

    out_name = input(f"\nOutput File Name [Leave_{today_str}]: ") or f"Leave_{today_str}"
    output_filename = f"{out_name}.pdf"

    generate_final_pdf(data, config, output_filename)
    print(f"\n✅ Perfect! File saved as: {os.path.abspath(output_filename)}")

if __name__ == '__main__':
    main()