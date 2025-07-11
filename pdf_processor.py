import PyPDF2
import io
from typing import Optional

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor."""
        pass
    
    def extract_text(self, pdf_file) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_file: File object or file-like object containing PDF data
            
        Returns:
            Extracted text as string
        """
        try:
            # Handle different input types
            if hasattr(pdf_file, 'read'):
                # It's a file-like object (like Streamlit's UploadedFile)
                pdf_content = pdf_file.read()
                pdf_file.seek(0)  # Reset file pointer for potential reuse
            else:
                # It's bytes
                pdf_content = pdf_file
            
            # Create a BytesIO object from the content
            pdf_stream = io.BytesIO(pdf_content)
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                raise Exception("PDF is encrypted. Please provide an unencrypted PDF.")
            
            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Clean up the text
            text = self._clean_text(text)
            
            if not text.strip():
                raise Exception("No text could be extracted from the PDF. The PDF might be image-based or corrupted.")
            
            return text
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace from each line
            cleaned_line = line.strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join lines with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text
    
    def get_pdf_info(self, pdf_file) -> dict:
        """
        Get basic information about the PDF.
        
        Args:
            pdf_file: File object or file-like object containing PDF data
            
        Returns:
            Dictionary with PDF information
        """
        try:
            # Handle different input types
            if hasattr(pdf_file, 'read'):
                pdf_content = pdf_file.read()
                pdf_file.seek(0)  # Reset file pointer
            else:
                pdf_content = pdf_file
            
            pdf_stream = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            
            info = {
                'num_pages': len(pdf_reader.pages),
                'is_encrypted': pdf_reader.is_encrypted,
                'has_metadata': bool(pdf_reader.metadata),
                'file_size': len(pdf_content)
            }
            
            # Add metadata if available
            if pdf_reader.metadata:
                info['metadata'] = {
                    'title': pdf_reader.metadata.get('/Title', 'Unknown'),
                    'author': pdf_reader.metadata.get('/Author', 'Unknown'),
                    'creator': pdf_reader.metadata.get('/Creator', 'Unknown'),
                    'producer': pdf_reader.metadata.get('/Producer', 'Unknown'),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', 'Unknown'),
                    'modification_date': pdf_reader.metadata.get('/ModDate', 'Unknown')
                }
            
            return info
            
        except Exception as e:
            return {'error': f"Failed to get PDF info: {str(e)}"}
    
    def validate_pdf(self, pdf_file) -> dict:
        """
        Validate a PDF file and check if it's suitable for text extraction.
        
        Args:
            pdf_file: File object or file-like object containing PDF data
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Get PDF info
            info = self.get_pdf_info(pdf_file)
            
            if 'error' in info:
                validation_result['is_valid'] = False
                validation_result['errors'].append(info['error'])
                return validation_result
            
            # Check if encrypted
            if info.get('is_encrypted', False):
                validation_result['is_valid'] = False
                validation_result['errors'].append("PDF is encrypted")
            
            # Check number of pages
            if info.get('num_pages', 0) == 0:
                validation_result['is_valid'] = False
                validation_result['errors'].append("PDF has no pages")
            elif info.get('num_pages', 0) > 10:
                validation_result['warnings'].append("PDF has many pages - text extraction might be slow")
            
            # Check file size (warn if very large)
            file_size = info.get('file_size', 0)
            if file_size > 10 * 1024 * 1024:  # 10MB
                validation_result['warnings'].append("PDF file is very large")
            
            # Try to extract a small amount of text to verify it's possible
            if validation_result['is_valid']:
                try:
                    text_sample = self.extract_text(pdf_file)
                    if not text_sample.strip():
                        validation_result['warnings'].append("PDF appears to contain no extractable text")
                    elif len(text_sample) < 50:
                        validation_result['warnings'].append("PDF contains very little text")
                except Exception as e:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"Text extraction failed: {str(e)}")
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"PDF validation failed: {str(e)}")
        
        return validation_result
