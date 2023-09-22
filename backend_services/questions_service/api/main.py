import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .utils import requestModels as rm
from .controllers import questions_controller as qc

# create app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/questions", status_code=200)
async def create_question(r: rm.CreateQuestion, request: Request):
    question_id = str(uuid.uuid4())
    return qc.create_question(question_id, r.title, r.description, r.category, r.complexity, r.session_id)

@app.get("/questions/{question_id}", status_code=200)
async def get_question(question_id: str, r: rm.GetQuestion):
    return qc.get_question(question_id, r.session_id)

@app.put("/questions", status_code=200)
async def update_question_info(r: rm.UpdateQuestionInfo):
    return qc.update_question_info(r.question_id, r.title, r.description, r.category, r.complexity, r.session_id)

@app.delete("/questions/{question_id}", status_code=200)
async def delete_question(question_id: str, r: rm.DeleteQuestion):
    return qc.delete_question(question_id, r.session_id)