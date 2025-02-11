# default.py
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from setup import load_template_from_yaml
from config import GEMINI_API_KEY

# default_chain (사용자의 의미없는 입력값에 대해 정해진 답변을 할 때)
# StructuredOutputParser 사용하여 체인의 출력값 구조를 고정
response_schemas = [
  ResponseSchema(name="answer",
                 type="string",
                 description="사용자의 의미없는 입력값에 대한 정해진 답변")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# 출력 지시사항 파싱
format_instructions = output_parser.get_format_instructions()

# template 불러오기
default_template = load_template_from_yaml("./prompts/default_template.yaml")
default_prompt = ChatPromptTemplate.from_template(default_template,
                                                  partial_variables={'format_instructions': format_instructions})

# Google Gemini 모델 생성
def load_gemini():
    model = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0,
        max_tokens=500,
        api_key=GEMINI_API_KEY
    )
    print(">>>>>>> model loaded from default chain...")
    return model

default_llm = load_gemini()

# langchain 체인 구성
default_chain = (
  {"classification_result": RunnablePassthrough(),
   "user_input": RunnablePassthrough()}
  | default_prompt
  | default_llm
  | output_parser
)
