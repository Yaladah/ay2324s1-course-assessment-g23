FROM ay2324s1-course-assessment-g23-base_api:latest

WORKDIR /

COPY ./app /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /app

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8004", "--workers", "4"]