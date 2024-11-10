import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer
import fitz  # PyMuPDF

model = AutoModel.from_pretrained(
    "model\MiniCPM-Llama3-V-2_5", trust_remote_code=True, torch_dtype=torch.float16
)
# model = model.to(device="cuda")

# tokenizer = AutoTokenizer.from_pretrained(
#     "model\MiniCPM-Llama3-V-2_5", trust_remote_code=True
# )
# model.eval()

# pdf_path = r"CVs\CV_AI_Engineer.pdf"
# pdf_document = fitz.open(pdf_path)

# images = []

# # Loop through each page in the PDF
# for page_number in range(len(pdf_document)):
#     page = pdf_document.load_page(page_number)
#     pix = page.get_pixmap()
#     img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

#     images.append(img)

# question = """Extract all the text in this image.
# If there is a header or a footer, just ignore it.
# Extract tables as markdown tables.
# Don't use the subtitles for the list items, just return the list as text.
# """
# msgs = [{"role": "user", "content": question}]

# res = model.chat(
#     image=images[0],
#     msgs=msgs,
#     tokenizer=tokenizer,
#     sampling=True,
#     temperature=0.7,
#     # system_prompt="" # pass system_prompt if needed
# )
# with open(r'extract_files\llm_vision.txt', 'w', encoding='utf-8') as file:
#     file.write(res)
# print(res)