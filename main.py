# main.py
from fastapi import FastAPI, WebSocket
import requests
from api.router import classification_chain
from api.default import default_chain
# from websocket_test import html

app = FastAPI()

MODEL_SERVER_URL = "http://127.0.0.1:8000/api/"

@app.get('/')
def load_root():
  return {'hallo': "api server is running(port: 8001)💭"}
  # return HTMLResponse(html)

@app.websocket('/ws/{user_id}/classify')
async def classify_user_input(websocket: WebSocket, user_id: str):
  await websocket.accept()
  while True:
    try:
      data = await websocket.receive_json()
      user_input = data.get("user_input", "")

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

      # 사용자 입력 유형이 "일반대화"일 경우 default_chain 실행
      if model_endpoint == "default":
        response = default_chain.invoke({"classification_result": "default", "user_input": user_input})
      # 사용자의 입력 유형이 "정보검색" 또는 "추천요청"일 경우 모델서버 호출
      else:
        model_server_endpoint = f"{MODEL_SERVER_URL}{user_id}/{model_endpoint}"
        response = requests.post(model_server_endpoint, json={"user_input": user_input}).json()

      # 클라이언트에게 전송하는 값
      await websocket.send_json({"response": response})
    except Exception as e:
      await websocket.send_json({"error": f">>>>>> Websocket error: {str(e)}"})
