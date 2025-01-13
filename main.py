# main.py
from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
import requests
from api.router import classification_chain

from fastapi.responses import HTMLResponse
from websocket_test import html

app = FastAPI()

MODEL_SERVER_URL = "http://127.0.0.1:8000/api/"

# 사용자 입력값 데이터 모델 정의
class UserInput(BaseModel):
  input_text: str
  user_id: str

@app.get('/')
def load_root():
  return {'hallo': "api server is running(port: 8001)💭"}
  # return HTMLResponse(html)

@app.websocket('/ws/classify')
async def classify_user_input(websocket: WebSocket):
  await websocket.accept()
  while True:
    try:
      data = await websocket.receive_json()
      user_input = data.get("input_text", "")
      user_id = data.get("user_id", "")

      # 라우터 체인으로 사용자 입력 유형 분류
      classification_result = classification_chain.invoke({"user_input": user_input})
      user_input_type = classification_result.get("type", "일반대화")

      # 유형에 따라 엔드포인트 변경
      endpoint_mapping = {
        "일반대화": "default",
        "추천요청": "recommend",
        "정보검색": "search"
      }
      model_endpoint = endpoint_mapping.get(user_input_type, "default")

      model_server_endpoint = f"{MODEL_SERVER_URL}{user_id}/{model_endpoint}"
  
      response = requests.post(model_server_endpoint, json={"input_text": user_input})
      model_response = response.json()

      await websocket.send_json({"user_id": user_id, "response": model_response})
    except Exception as e:
      await websocket.send_json({"error": f">>>>>> Websocket error: {str(e)}"})
