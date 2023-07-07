FROM python:3.9-slim
WORKDIR /usr/src/app
RUN apt update -y
RUN apt upgrade -y
RUN apt install -y bash
RUN apt install -y libgl1
RUN apt install -y tesseract-ocr
RUN apt install -y libtesseract-dev
RUN apt install -y poppler-utils

COPY . .

EXPOSE 3040

RUN ["python3", "-m", "pip", "install", "-r", "./requirements.txt"]
CMD ["python3", "./manage.py"] 