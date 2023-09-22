from pydantic import BaseModel

class CreateQuestion(BaseModel):
    title: str
    description: str
    category: str
    complexity: str
    session_id: str

class GetQuestion(BaseModel):
    session_id: str

class UpdateQuestionInfo(BaseModel):
    question_id: str
    title: str
    description: str
    category: str
    complexity: str
    session_id: str

class DeleteQuestion(BaseModel):
    session_id: str
