from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import tempfile
import os
from .ocr_utils import extract_text_from_file

class OCRView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        # Get uploaded file
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Create temp file with original extension
        file_ext = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            # Write uploaded file to temp location
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Process with existing ocr_utils
            extracted_text = extract_text_from_file(temp_file_path)
            
            # Print extracted text to console (for testing)
            print("\n" + "="*50)
            print("EXTRACTED TEXT:")
            print(extracted_text)
            print("="*50 + "\n")
            
            return Response({
                "text": extracted_text,
                #"filename": uploaded_file.name,
                #"status": "success"
            })
            
        except Exception as e:
            return Response({
                "error": str(e),
                "filename": uploaded_file.name,
                "status": "failed"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass