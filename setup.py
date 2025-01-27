# setup.py
from langchain_teddynote import logging
import yaml
from config import LOGGING_NAME

# langsmith 추적 설정
logging.langsmith(LOGGING_NAME)


# yaml에서 template 불러오는 함수
def load_template_from_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data['template']