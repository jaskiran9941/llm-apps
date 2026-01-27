"""
Extract images from PDFs using PyMuPDF
"""
from typing import List
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
import io
from ..common.models import ImageInfo
from ..common.utils import generate_id
from ..common.config import Config


class ImageExtractor:
    """Extract images from PDF documents"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Config.IMAGES_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_images(self, pdf_path: str, render_pages: bool = True) -> List[ImageInfo]:
        """
        Extract all images from PDF.

        Args:
            pdf_path: Path to PDF file
            render_pages: If True, also render pages as images (captures vector graphics)
        """
        images = []

        try:
            # Open PDF
            doc = fitz.open(pdf_path)

            # Iterate through pages
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_has_embedded_images = False

                # Get embedded images on page
                image_list = page.get_images()

                for img_index, img in enumerate(image_list):
                    try:
                        # Extract image
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]

                        # Save image
                        image_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                        image_path = self.output_dir / image_filename

                        # Convert to PIL Image and save
                        image = Image.open(io.BytesIO(image_bytes))

                        # Skip very small images (likely icons/bullets)
                        if image.width < 50 or image.height < 50:
                            continue

                        image.save(image_path)
                        page_has_embedded_images = True

                        # Create ImageInfo
                        image_info = ImageInfo(
                            image_path=str(image_path),
                            page=page_num + 1,
                            image_id=generate_id(f"{pdf_path}_{page_num}_{img_index}"),
                            metadata={
                                "width": image.width,
                                "height": image.height,
                                "format": image.format,
                                "source_pdf": pdf_path,
                                "type": "embedded"
                            }
                        )
                        images.append(image_info)

                    except Exception as e:
                        print(f"Error extracting image {img_index} from page {page_num}: {e}")
                        continue

                # If render_pages enabled and page has no embedded images or has vector graphics,
                # render the entire page as an image
                if render_pages and not page_has_embedded_images:
                    try:
                        # Check if page has drawings/vector content
                        drawings = page.get_drawings()
                        text_len = len(page.get_text())

                        # Render page if it has drawings or minimal text (likely visual)
                        if drawings or text_len < 500:
                            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

                            image_filename = f"page_{page_num + 1}_full.png"
                            image_path = self.output_dir / image_filename
                            pix.save(image_path)

                            image_info = ImageInfo(
                                image_path=str(image_path),
                                page=page_num + 1,
                                image_id=generate_id(f"{pdf_path}_{page_num}_full"),
                                metadata={
                                    "width": pix.width,
                                    "height": pix.height,
                                    "source_pdf": pdf_path,
                                    "type": "page_render"
                                }
                            )
                            images.append(image_info)
                    except Exception as e:
                        print(f"Error rendering page {page_num}: {e}")

            doc.close()

        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {e}")

        return images

    def extract_page_as_image(self, pdf_path: str, page_num: int) -> str:
        """
        Render entire PDF page as image.
        Useful for complex layouts.
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc[page_num]

            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for quality

            # Save
            image_filename = f"page_{page_num + 1}_full.png"
            image_path = self.output_dir / image_filename

            pix.save(image_path)
            doc.close()

            return str(image_path)

        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")
            return ""

    def clear_images(self):
        """Clear extracted images directory"""
        for file in self.output_dir.glob("*.png"):
            file.unlink()
