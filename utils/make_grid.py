import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter

def create_coordinate_grid(template_name="template/leave_template.pdf", output_name="template_with_grid.pdf"):
    print("Generating Grid Overlay...")
    
    # 1. Create a transparent PDF with grid lines
    c = canvas.Canvas("temp_grid.pdf", pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 8)

    # Draw fine lines every 10 points (Light Gray)
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    for x in range(0, int(width), 10): c.line(x, 0, x, height)
    for y in range(0, int(height), 10): c.line(0, y, width, y)

    # Draw major lines every 50 points and add Labels
    for x in range(0, int(width), 50):
        c.setStrokeColorRGB(0.6, 0.6, 0.6)
        c.line(x, 0, x, height)
        c.setFillColorRGB(1, 0, 0) # Red text for X axis
        c.drawString(x + 2, height - 15, f"X:{x}")
        c.drawString(x + 2, 15, f"X:{x}")

    for y in range(0, int(height), 50):
        c.setStrokeColorRGB(0.6, 0.6, 0.6)
        c.line(0, y, width, y)
        c.setFillColorRGB(0, 0, 1) # Blue text for Y axis
        c.drawString(5, y + 2, f"Y:{y}")
        c.drawString(width - 30, y + 2, f"Y:{y}")

    c.save()

    # 2. Merge the Grid with your Company Template
    template = PdfReader(template_name)
    grid = PdfReader("temp_grid.pdf")
    writer = PdfWriter()

    page = template.pages[0]
    page.merge_page(grid.pages[0])
    writer.add_page(page)

    with open(output_name, "wb") as f:
        writer.write(f)

    os.remove("temp_grid.pdf")
    print(f"✅ Grid created! Open '{output_name}' to see your coordinates.")

if __name__ == '__main__':
    create_coordinate_grid()