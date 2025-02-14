# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import requests
from api.router import classification_chain
from api.default import default_chain
import json

app = FastAPI()

MODEL_SERVER_URL = "http://192.168.0.130:8000/"

@app.get('/')
def load_root():
  return {'hallo': "api server is running(port: 8001)💭"}

@app.websocket('/{user_id}/chat')
async def classify_user_input(websocket: WebSocket, user_id: str):
  await websocket.accept()
  try:
    ### 1. 웹소켓 연결 시 먼저 벡터스토어에 시청 기록이 있는 사용자인지 확인 ###
    print(">>>>>>>", user_id)
    model_server_endpoint = f"{MODEL_SERVER_URL}{user_id}/api/connect"
    try:
      response = requests.post(model_server_endpoint)
      # 사용자 확인 시 code 200 반환
      if response.status_code == 200:
        # await websocket.send_json({"success": "✔️model server 연결 성공"})
        await websocket.send_json(response.json())
      # 사용자를 찾을 수 없다면 웹소켓 close
      else:
        await websocket.send_json({"error": f"model server return status {response.status_code}"})
        await websocket.close()
        return
    # API 요청 중 예외 처리
    except requests.exceptions.RequestException as e:
      await websocket.send_json({"error": f"✖️model server 연결 실패: {str(e)}"})
      await websocket.close()
      return
    
    ### 2. 웹소켓에 연결 + 사용자 확인된 상태 ###
    while True:
      ### 2-1. 클라이언트가 웹소켓으로 데이터를 보냄 ###
      data = await websocket.receive_json()
      event = data.get("event", "")

      ### 2-2. 사용자가 시청하기 버튼을 누름 ###
      if event == "watch_now":
        # asset_id 가져오기
        asset_id = data.get("asset_id", "")
        runtime = float(data.get("runtime", 0))
        if not asset_id:
          await websocket.send_json({"error": "Asset ID 없음!"})
          continue
        
        # model server에 asset_id 전송
        watch_endpoint = f"{MODEL_SERVER_URL}{user_id}/api/watch"
        try:
          response = requests.post(watch_endpoint, json={"asset_id": asset_id})
          if response.status_code == 200:
            await websocket.send_json(response.json())
          else:
            await websocket.send_json({"error": f"시청기록 저장 실패. status code: {response.status_code}"})
        except requests.exceptions.RequestException as e:
          await websocket.send_json({"error": f"model server에 api 전송 실패: {str(e)}"})
        continue

      ### 2-3. 사용자가 채팅을 보냄 ###
      else:
        # 사용자 input 가져오기
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
          print(f"------------- Default Chain 실행 -------------")

          response_data = default_chain.invoke({"classification_result": "default", "user_input": user_input})
        # 사용자의 입력 유형이 "정보검색" 또는 "추천요청"일 경우 모델서버 호출
          print(f"testhere-----------------------------{response_data}")
          if isinstance(response_data, str):
            try:
              response = json.loads(response_data)
            except json.JSONDecodeError:
              response = {"error": "챗봇 응답 처리 불가능"}
          elif isinstance(response_data, dict):
            response = response_data
          else:
            response = {"error": "알 수 없는 응답"}

        else:
          model_server_endpoint = f"{MODEL_SERVER_URL}{user_id}/api/{model_endpoint}"
          try:
            response = requests.post(model_server_endpoint, json={"user_input": user_input}).json()
          except requests.exceptions.RequestException as e:
            await websocket.send_json({"error": f"model server API 요청 실패: {str(e)}"})
            continue

        # 클라이언트에게 값 전송
        await websocket.send_json(response)

  except WebSocketDisconnect:
    print(f"WebSocket disconnected for user_id: {user_id}")