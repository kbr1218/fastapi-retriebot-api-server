# setup.py
from langchain_teddynote import logging
from config import LOGGING_NAME

# langsmith 추적 설정
logging.langsmith(LOGGING_NAME)
