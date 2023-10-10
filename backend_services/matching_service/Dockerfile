FROM ay2324s1-course-assessment-g23-base_api:latest

WORKDIR /

COPY ./app /app

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "4"]