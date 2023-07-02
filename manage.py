import cv2
import io
import logging
import numpy as np
import os
import pytesseract
import random
import string
import time
import uvicorn
from fastapi import FastAPI, File
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
import pdfminer.high_level as pdfminerHL
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
import io

from utils.logger import logger

app = FastAPI(docs_url=f"/", openapi_url="/openapi.json", redoc_url=None)
app.mount('/static', StaticFiles(directory='static'), name='static')


@app.middleware("http")
async def log_requests(request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(
        f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
    )

    return response


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.handlers.RotatingFileHandler(os.path.join(
        'logs', 'api.log'),
                                                   mode="a",
                                                   maxBytes=100 * 1024,
                                                   backupCount=3)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css")


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


def read_img(img):
    text = pytesseract.image_to_string(img)
    return text


@app.post("/interrogate_image")
async def extract_image(file: bytes = File()):
    image_stream = io.BytesIO(file)
    image_stream.seek(0)
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    label = read_img(frame)

    return {"result": label}


@app.post("/interrogate_pdf")
async def extract_pdf(file: bytes = File()):
    text_memory_file = io.StringIO()

    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, text_memory_file, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # get first 3 pages of the pdf file
    
    for page in PDFPage.get_pages(file, pagenos=(0, 1)):
        interpreter.process_page(page)
    text = text_memory_file.getvalue()
    text_memory_file.close()
    return text




if __name__ == "__main__":
    uvicorn.run("manage:app", host="0.0.0.0", port=8000, reload=False)
