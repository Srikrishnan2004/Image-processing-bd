# myapp/views.py
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure as ex
import imageio
import io
from django.http import HttpResponse
from django.views import View
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views.decorators.csrf import csrf_exempt


def histogram_equalization(img):
    """Apply histogram equalization to an image."""
    if len(img.shape) == 2:  # Grayscale
        out_img = ex.equalize_hist(img[:, :]) * 255
    elif len(img.shape) == 3:  # RGB
        out_img = np.zeros((img.shape[0], img.shape[1], 3))
        for channel in range(img.shape[2]):
            out_img[:, :, channel] = ex.equalize_hist(img[:, :, channel]) * 255

    out_img[out_img > 255] = 255
    out_img[out_img < 0] = 0
    return out_img.astype(np.uint8)

class HistogramEqualizationView(View):
    # @csrf_exempt
    def post(self, request, *args, **kwargs):
        # Check if an image file is in the request
        image_file = request.FILES.get('image')
        
        if not image_file:
            return HttpResponse('No image uploaded', status=400)
        
        # Read the image into a NumPy array
        img = imageio.imread(image_file)
        
        # Perform histogram equalization
        result_img = histogram_equalization(img)
        
        # Convert the result image to a format suitable for HTTP response
        pil_img = Image.fromarray(result_img)
        buf = io.BytesIO()
        pil_img.save(buf, format='PNG')
        buf.seek(0)
        
        # Return the image as an HTTP response
        return HttpResponse(buf, content_type='image/png')
