FROM python:3.7-slim
RUN apt-get -y update
RUN apt install -y libgl1-mesa-glx
RUN apt install -y libglib2.0-0
RUN apt install -y libsm6 libxext6 libxrender-dev
WORKDIR /app
COPY . .
EXPOSE 5000
RUN pip3 install -r requirements.txt
CMD [ "python", "app.py"]
####
