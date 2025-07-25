FROM python:3.13
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
EXPOSE 8000
COPY . /app
CMD ["fastapi", "run", "/app/main.py", "--port", "8000"]