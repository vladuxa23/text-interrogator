FROM python:3.9-slim
WORKDIR /usr/src/app
RUN apt update && apt upgrade && apt install bash
RUN apt install -y libgl1
RUN apt install -y tesseract-ocr
RUN apt install -y libtesseract-dev

COPY . .

EXPOSE 8000

RUN ["python3", "-m", "pip", "install", "-r", "./requirements.txt"]
CMD ["python3", "./manage.py"] 