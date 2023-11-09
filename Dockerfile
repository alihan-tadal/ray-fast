
# Use the official Python image as the base image
FROM python:3.10-slim-buster

WORKDIR /app
# copy all except venv folder
COPY . /app


RUN pip install opencv-contrib-python
RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc curl ca-certificates python3 && \
    apt clean
RUN apt install ffmpeg libsm6 libxext6 wkhtmltopdf -y
RUN pip install --trusted-host --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["serve", "run", "-h", "0.0.0.0", "entrypoint:app"]

# docker build -t ray-serve-app 