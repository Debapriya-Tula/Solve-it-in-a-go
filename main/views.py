from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from selenium.common import exceptions

from .utils import *

import os
import torch
import numpy as np
import PIL.Image

# Create your views here.

def home(request):
    context = dict()
    if request.method == 'POST':
        # take image
        img = request.FILES.get('input-image', None)
        name = img.name
        print(os.path.join(settings.MEDIA_ROOT, img.name))
        img_path = os.path.join(settings.MEDIA_ROOT, name)
        if not img: # if no image is uploaded
            return render(request, 'main/home.html', context={'nothing': True})

        PIL.Image.open(img).save(img_path) # saving the image temporarily
        img = np.array(PIL.Image.open(img))

        # if len(img.shape) == 2:
        #     img = np.expand_dims(img, axis=-1)
        # img = np.rollaxis(img, axis=-1) # changing to channels first
        # img = np.expand_dims(img, axis=0) # for batch_size dimension
        # img = torch.FloatTensor(img)
        # run model on image, get expn
        _, expn = get_expn_from_image(preprocess_img(img))
        print(f"Expression Latex: {''.join(expn[:-1])}")
        # take expression
        parsed, step_page = get_solution(''.join(expn[:-1]))
        # get solution steps
        steps = parse_steps(step_page)
        # filter the steps
        steps = [s for s in steps if '<' not in s]
        rows = len(steps)
        answer = steps[-1]
        print(f"Answer: {answer}")
        steps = '\n'.join(steps[1:])
        context = {
            'steps': steps,
            'answer': answer,
            'parsed_latex': ''.join(expn[:-1]),
            'parsed': parsed,
            'area_rows': rows,
            'answer_length': len(answer)
        } # context for template
    return render(request, "main/home.html", context=context)


class PredictAPI(APIView):
    def get(self, request):
        curr_image = request.data.get('image', None)
        if not curr_image:
            return Response({
                'err': 'No image received'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            assert type(curr_image) == str
        except AssertionError as ae:
            return Response({
                'err': 'Received something other than a base64 string'
            }, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        try:
            resp = model_pipeline_api(curr_image)
            return Response(resp, status=status.HTTP_200_OK)
        except exceptions.TimeoutException:
            return Response({
                'err': 'Expression currently not supported. Server timed out.'
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
