# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from api.router import classification_chain

app = FastAPI()

MODEL_SERVER_URL = "http://127.0.0.1:8000/api/"

# 사용자 입력값 데이터 모델 정의
class UserInput(BaseModel):
  input_text: str
  user_id: str

@app.get('/')
def load_root():
  return {'hallo': "api server is running(port: 8001)💭"}

@app.post('/api/classify')
def classify_user_input(user_input: UserInput):
  # 라우터 체인으로 사용자 입력 유형 분류
  classification_result = classification_chain.invoke({"user_input": user_input.input_text})
  user_input_type = classification_result.get("type", "일반대화")

  # 유형에 따라 엔드포인트 변경
  endpoint_mapping = {
    "일반대화": "default",
    "추천요청": "recommend",
    "정보검색": "search"
  }
  model_endpoint = endpoint_mapping.get(user_input_type, "default")

  model_server_endpoint = f"{MODEL_SERVER_URL}{user_input.user_id}/{model_endpoint}"
  try:
    response = requests.post(model_server_endpoint, json={"input_text": user_input.input_text})
    return response.json()
  except requests.exceptions.RequestException as e:
    raise HTTPException(status_code=500, detail=f">>>>>> Model server request failed: {str(e)}")
