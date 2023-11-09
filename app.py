
import os
import logging
from ray import serve
from contextlib import asynccontextmanager
from fastapi import File, UploadFile, Form, FastAPI
from fastapi.responses import FileResponse

from core import generate_image, init_model, generate_ad

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up")
    yield
    log.info("Shutting down")
    os.system("rm -rf ./lightroom/*")
    os.system("rm -rf ./__pycache__")
    log.info("Cleaned up")

fastapi_app = FastAPI(lifespan=lifespan)

@serve.deployment(
    name="ad_generator"
)
@serve.ingress(fastapi_app)
class FastAPIIngress:
    def __init__(self):
        self.pipe = init_model()
        # pass
    
    @fastapi_app.post("/paint")
    async def paint(self, image: UploadFile = File(...), prompt: str = Form(...), theme_color: str = Form(...)):
    
        with open("./lightroom/raw_image.png", "wb") as buffer:
            buffer.write(image.file.read())
        
        generated_image = generate_image("./lightroom/raw_image.png", prompt, theme_color, self.pipe)
        generated_image.save("./lightroom/generated_image.png")
        return FileResponse("./lightroom/generated_image.png")
    
    @fastapi_app.post("/generate")
    async def generate_ad_handler(
        self,
        ad_image: UploadFile = File(...),
        logo: UploadFile = File(...),
        theme_color: str = Form(...),
        punchline: str = Form(...),
        button_text: str = Form(...),
    ):
        with open("./lightroom/ad_image.png", "wb") as buffer:
            buffer.write(ad_image.file.read())

        with open("./lightroom/ad_logo.png", "wb") as buffer:
            buffer.write(logo.file.read())        
        generate_ad("ad_image.png", "ad_logo.png", theme_color, punchline, button_text)
        return FileResponse("./lightroom/output.png")