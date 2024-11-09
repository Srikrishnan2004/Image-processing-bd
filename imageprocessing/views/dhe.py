from django.http import JsonResponse, HttpResponse
from django.views import View
from django.core.files.base import ContentFile
import numpy as np
import matplotlib.colors
import imageio.v2 as imageio
import scipy, scipy.signal
import io
from PIL import Image

class ImageEnhancer:
    @staticmethod
    def build_is_hist(img):
        hei = img.shape[0]
        wid = img.shape[1]
        ch = img.shape[2]
        Img = np.zeros((hei+4, wid+4, ch))
        for i in range(ch):
            Img[:,:,i] = np.pad(img[:,:,i], (2,2), 'edge')
        hsv = (matplotlib.colors.rgb_to_hsv(Img.astype(np.float32) / 255.0))  # Convert image to float32
        hsv[:,:,0] = hsv[:,:,0] * 255
        hsv[:,:,1] = hsv[:,:,1] * 255
        hsv[hsv>255] = 255
        hsv[hsv<0] = 0
        hsv = hsv.astype(np.uint8).astype(np.float64)
        fh = np.array([[-1.0,0.0,1.0],[-2.0,0.0,2.0],[-1.0,0.0,1.0]])
        fv = fh.conj().T

        H = hsv[:,:,0]
        S = hsv[:,:,1]
        I = hsv[:,:,2]

        dIh = scipy.signal.convolve2d(I, np.rot90(fh, 2), mode='same')
        dIv = scipy.signal.convolve2d(I, np.rot90(fv, 2), mode='same')
        dIh[dIh==0] = 0.00001
        dIv[dIv==0] = 0.00001
        dI = np.sqrt(dIh**2+dIv**2).astype(np.uint32)
        di = dI[2:hei+2,2:wid+2]

        dSh = scipy.signal.convolve2d(S, np.rot90(fh, 2), mode='same')
        dSv = scipy.signal.convolve2d(S, np.rot90(fv, 2), mode='same')
        dSh[dSh==0] = 0.00001
        dSv[dSv==0] = 0.00001
        dS = np.sqrt(dSh**2+dSv**2).astype(np.uint32)
        ds = dS[2:hei+2,2:wid+2]

        h = H[2:hei+2,2:wid+2]
        s = S[2:hei+2,2:wid+2]
        i = I[2:hei+2,2:wid+2].astype(np.uint8)

        Imean = scipy.signal.convolve2d(I,np.ones((5,5))/25, mode='same')
        Smean = scipy.signal.convolve2d(S,np.ones((5,5))/25, mode='same')

        Rho = np.zeros((hei+4,wid+4))
        for p in range(2,hei+2):
            for q in range(2,wid+2):
                tmpi = I[p-2:p+3,q-2:q+3]
                tmps = S[p-2:p+3,q-2:q+3]
                corre = np.corrcoef(tmpi.flatten('F'),tmps.flatten('F'))
                Rho[p,q] = corre[0,1]

        rho = np.abs(Rho[2:hei+2,2:wid+2])
        rho[np.isnan(rho)] = 0
        rd = (rho*ds).astype(np.uint32)
        Hist_I = np.zeros((256,1))
        Hist_S = np.zeros((256,1))

        for n in range(0,255):
            temp = np.zeros(di.shape)
            temp[i==n] = di[i==n]
            Hist_I[n+1] = np.sum(temp.flatten('F'))
            temp = np.zeros(di.shape)
            temp[i==n] = rd[i==n]
            Hist_S[n+1] = np.sum(temp.flatten('F'))

        return Hist_I, Hist_S

    @staticmethod
    def dhe(img, alpha=0.5):
        hist_i, hist_s = ImageEnhancer.build_is_hist(img)
        hist_c = alpha * hist_s + (1 - alpha) * hist_i
        hist_sum = np.sum(hist_c)
        hist_cum = hist_c.cumsum(axis=0)

        hsv = matplotlib.colors.rgb_to_hsv(img.astype(np.float32) / 255.0)  # Convert image to float32
        h = hsv[:,:,0]
        s = hsv[:,:,1]
        i = hsv[:,:,2].astype(np.uint8)

        c = hist_cum / hist_sum
        s_r = (c * 255)
        i_s = np.zeros(i.shape)
        for n in range(0, 255):
            i_s[i == n] = s_r[n + 1] / 255.0
        i_s[i == 255] = 1
        hsi_o = np.stack((h, s, i_s), axis=2)
        result = matplotlib.colors.hsv_to_rgb(hsi_o)

        result = result * 255
        result[result > 255] = 255
        result[result < 0] = 0
        return result.astype(np.uint8)


class DynamicHistogramEqualizationView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the image from the request body
            img_file = request.FILES.get('image')

            if img_file is None:
                return JsonResponse({"error": "No image file provided"}, status=400)

            # Convert the uploaded image to numpy array
            img = Image.open(img_file)
            img = np.array(img)

            # Process the image using the ImageEnhancer class
            enhanced_img = ImageEnhancer.dhe(img)

            # Convert processed image back to a PIL Image
            result_img = Image.fromarray(enhanced_img)

            # Save the result to a BytesIO buffer
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Return the image in response
            return HttpResponse(img_byte_arr, content_type='image/png')

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
