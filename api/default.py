# default.py
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from setup import load_template_from_yaml
from config import GEMINI_API_KEY

# default_chain (사용자의 의미없는 입력값에 대해 정해진 답변을 할 때)

# template 불러오기
default_template = load_template_from_yaml("./prompts/default_template.yaml")
default_prompt = ChatPromptTemplate.from_template(default_template)

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
  | StrOutputParser()
)
