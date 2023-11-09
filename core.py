import cv2
import jinja2
from PIL import Image
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
import torch
import numpy as np
import imgkit
from diffusers.utils import load_image

def init_model():
  controlnet = ControlNetModel.from_pretrained(
      "lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16)
  pipe = StableDiffusionControlNetPipeline.from_pretrained(
      "runwayml/stable-diffusion-v1-5", controlnet=controlnet, safety_checker=None, torch_dtype=torch.float16)
  pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
  pipe.enable_model_cpu_offload()
  return pipe

def generate_image(image_url, prompt, hex_code, pipe):
  image = load_image(image_url)
  image = np.array(image)

  low_threshold = 100
  high_threshold = 200

  image = cv2.Canny(image, low_threshold, high_threshold)
  image = image[:, :, None]
  image = np.concatenate([image, image, image], axis=2)
  image = Image.fromarray(image)
  image = pipe(prompt + f" including {hex_code} hex coded color", image, num_inference_steps=20).images[0]
  return image 

def generate_ad(image_url, logo_url, theme_color, punchline, button_text):
    TEMPLATE_FILE = "basic.html"
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(TEMPLATE_FILE)
    
    data = {
        "image": image_url,
        "logo": logo_url,
        "color": theme_color,
        "punchline": punchline,
        "buttontext": button_text,
    }

    html = template.render(data)
    with open("./lightroom/out.html", "w") as f:
        f.write(html)
    options = {"format": "png", "encoding": "UTF-8", "enable-local-file-access": None}
    imgkit.from_file("./lightroom/out.html", "./lightroom/output.png", options=options)
