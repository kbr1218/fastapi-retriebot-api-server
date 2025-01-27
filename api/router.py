# router.py
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnablePassthrough
from setup import load_template_from_yaml
from config import GEMINI_API_KEY

# StructuredOutputParser 사용하여 체인의 출력값 구조를 고정
response_schemas = [
  ResponseSchema(name="type",
                 description="사용자의 입력을 세 가지 범주('정보검색', '추천요청', '일반대화') 중 하나로 구분")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# 출력 지시사항 파싱
format_instructions = output_parser.get_format_instructions()

# template 불러오기
classification_template = load_template_from_yaml("./prompts/router_template.yaml")
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