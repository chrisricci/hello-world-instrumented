FROM python:alpine
COPY app.py /app/
COPY requirements.txt /app/ 
WORKDIR /app
RUN pip install -r requirements.txt
USER 1001
ENTRYPOINT ["python"]
CMD ["app.py"]
