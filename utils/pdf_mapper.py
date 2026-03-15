import fitz  # PyMuPDF
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk

# --- CONFIGURATION ---
TEMPLATE_FILE = "template/leave_template.pdf"
ZOOM_FACTOR = 1.5  # Makes the PDF bigger so it's easier to click accurately

class PDFMapper:
    def __init__(self, root, pdf_path):
        self.root = root
        self.root.title("Navya Advisors - PDF Coordinate Mapper")
        
        self.coordinates = {}

        # 1. Load PDF and render to image
        try:
            self.doc = fitz.open(pdf_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open {pdf_path}.\nMake sure it is in the same folder!")
            self.root.destroy()
            return

        self.page = self.doc[0]
        self.pdf_width = self.page.rect.width
        self.pdf_height = self.page.rect.height

        # Zoom matrix for higher quality rendering
        mat = fitz.Matrix(ZOOM_FACTOR, ZOOM_FACTOR)
        pix = self.page.get_pixmap(matrix=mat)

        # Convert to PIL Image -> Tkinter Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.tk_img = ImageTk.PhotoImage(img)

        # 2. Setup Scrollable UI Canvas
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

        # 3. Mouse Event Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.start_x = None
        self.start_y = None
        self.rect = None

        print("✅ Tool Opened! Drag boxes over the blank lines to capture coordinates.")

    def on_press(self, event):
        # Account for scrolling
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        # We want the Bottom-Left corner of the box they drew
        # Screen coordinates: (0,0) is Top-Left
        # ReportLab coordinates: (0,0) is Bottom-Left
        
        box_left = min(self.start_x, end_x)
        box_bottom = max(self.start_y, end_y)

        # Convert zoomed screen pixels back to standard PDF points
        pdf_x = box_left / ZOOM_FACTOR
        pdf_y = self.pdf_height - (box_bottom / ZOOM_FACTOR)

        # Ask user what field this is
        field_name = simpledialog.askstring("Input", "Enter field name (e.g., 'emp_name'):", parent=self.root)
        
        if field_name:
            # Save the coordinate (Rounded to whole numbers)
            self.coordinates[field_name] = (int(pdf_x), int(pdf_y))
            
            # Draw text on canvas so user knows it's saved
            self.canvas.create_text(box_left, box_bottom - 5, anchor=tk.SW, text=field_name, fill="blue", font=("Arial", 10, "bold"))
            
            self.print_dict()
        
        self.canvas.delete(self.rect)
        self.rect = None

    def print_dict(self):
        print("\n--- Current COORDINATES Dictionary ---")
        print("COORDINATES = {")
        for key, val in self.coordinates.items():
            print(f"    '{key}': {val},")
        print("}")
        print("--------------------------------------")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x800")
    app = PDFMapper(root, TEMPLATE_FILE)
    root.mainloop()