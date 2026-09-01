from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium


source = Path(r"C:\Users\69596\Downloads\2024.findings-acl.285.pdf")
text_output = Path(r"E:\Info_AI\tmp\MouEtAl2024HiSim_pages.txt")
render_dir = Path(r"E:\Info_AI\tmp\MouEtAl2024HiSim_pages")
render_dir.mkdir(parents=True, exist_ok=True)

with pdfplumber.open(source) as pdf:
    pages = []
    for page_number, page in enumerate(pdf.pages, start=1):
        pages.append(f"\n===== PDF PAGE {page_number} =====\n")
        pages.append(page.extract_text(x_tolerance=2, y_tolerance=3) or "")
    text_output.write_text("\n".join(pages), encoding="utf-8")

document = pdfium.PdfDocument(str(source))
for page_number in (1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 16, 17, 18, 20, 21):
    page = document[page_number - 1]
    image = page.render(scale=2.0).to_pil()
    image.save(render_dir / f"page_{page_number:02d}.png")

print(f"pages={len(document)}")
print(f"text={text_output}")
print(f"renders={render_dir}")
