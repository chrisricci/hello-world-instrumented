FROM python:3.6-alpine3.6
COPY app.py /app/
COPY requirements.txt /app/ 
WORKDIR /app
RUN pip install -r requirements.txt
USER 1001
ENTRYPOINT ["python"]
EXPOSE 8080
CMD ["app.py"]
