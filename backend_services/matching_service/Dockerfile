FROM ay2324s1-course-assessment-g23-base_api:latest

WORKDIR /

COPY ./app /app

WORKDIR /app

# MUST run with 1 worker only, else there'll be
# duplicate queues on different threads.
CMD uvicorn main:app --host 0.0.0.0 --port 8003 --workers 1
