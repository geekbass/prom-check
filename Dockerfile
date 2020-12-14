FROM python:3.9
COPY requirements.txt .
COPY ./main.py ./main.py
COPY ./healthz.py ./healthz.py
RUN pip install -r requirements.txt
CMD [ "python", "-u", "./main.py" ]