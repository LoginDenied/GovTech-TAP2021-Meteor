FROM python:3.7-buster

COPY ./ /flask
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r /flask/requirements.txt

WORKDIR /flask
CMD ["python3", "app.py"]
EXPOSE 5000:5000