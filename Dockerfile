FROM python:3.9
LABEL maintainer="wbassler23@gmail.com"
COPY requirements.txt .
COPY ./src ./src
RUN pip install -r requirements.txt
CMD [ "python", "-u", "./src/main.py" ]