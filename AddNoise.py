from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image, ImageFilter
import os

def degrade_pdf(input_pdf_path, output_pdf_path, noise_intensity=1):
    """
    Degrades a PDF by converting pages to images, adding noise, and reassembling.

    Args:
        input_pdf_path (str): Path to the input PDF.
        output_pdf_path (str): Path to save the degraded PDF.
        noise_intensity (int): Amount of noise to add (higher = more noise).
    """
    if not os.path.exists("temp_images"):
        os.makedirs("temp_images")

    # Step 1: Convert PDF pages to images
    pages = convert_from_path(input_pdf_path, dpi=200)
    image_paths = []

    for page_num, page_image in enumerate(pages):
        image_path = f"temp_images/page_{page_num}.png"
        page_image.save(image_path, "PNG")
        image_paths.append(image_path)

    degraded_images = []

    # Step 2: Add noise or reduce quality
    for image_path in image_paths:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img = img.filter(ImageFilter.GaussianBlur(noise_intensity))  # Add blur for quality degradation

            degraded_image_path = image_path.replace("page_", "degraded_page_")
            img.save(degraded_image_path, "JPEG", quality=70)  # Save with reduced quality
            degraded_images.append(degraded_image_path)

    # Step 3: Reassemble the degraded images into a PDF
    images_to_pdf = [Image.open(path) for path in degraded_images]
    images_to_pdf[0].save(output_pdf_path, save_all=True, append_images=images_to_pdf[1:])

# Example usage
input_path = r""
output_path = r""
degrade_pdf(input_path, output_path, noise_intensity=1)
