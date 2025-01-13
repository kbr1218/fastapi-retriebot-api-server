# router.py
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnablePassthrough
from config import GEMINI_API_KEY

# StructuredOutputParser 사용하여 체인의 출력값 구조를 고정
response_schemas = [
  ResponseSchema(name="type",
                 description="사용자의 입력을 세 가지 범주('정보검색', '추천요청', '일반대화') 중 하나로 구분")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# 출력 지시사항 파싱
format_instructions = output_parser.get_format_instructions()

# 사용자 입력값 유형 분류용 프롬프트
classification_template = """사용자의 입력을 다음 세 가지 범주 중 하나로 분류하세요:
1️⃣ **"정보검색"**: 특정 영화, 드라마, 배우, 감독, 러닝타임, 개봉 연도, 수상 내역, 필모그래피 등 **사실적인 정보를 찾는 질문**
   - 기대되는 응답 예시: 배우가 출연한 드라마/영화 목록, 특정 연도의 개봉작 리스트 등
2️⃣ **"추천요청"**: 특정 장르, 배우, 테마(예: 좀비, 시간여행), 감성(예: 힐링, 긴장감) 등에 대한 **추천을 요청하는 질문**
   - 기대되는 응답 예시: 특정 조건을 만족하는 영화/드라마 추천
3️⃣ **"일반대화"**: 서비스와 무관한 일반적인 대화 (예: 날씨, AI 관련 질문, 잡담)

#### **예시 형식**
{format_instructions}

<user_input>
{user_input}
</user_input>
"""
classification_prompt = ChatPromptTemplate.from_template(classification_template,
                                                         partial_variables={'format_instructions': format_instructions})


# Google Gemini 모델 생성
def load_gemini():
    model = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0,
        max_tokens=500,
        api_key=GEMINI_API_KEY
    )
    print(">>>>>>> model loaded from router chain...")
    return model
calssification_llm = load_gemini()


# 라우터 체인 구성
classification_chain = (
  {"user_input": RunnablePassthrough()}
  | classification_prompt
  | calssification_llm
  | output_parser
)