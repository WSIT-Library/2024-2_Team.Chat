import pandas as pd
from sentence_transformers import SentenceTransformer

# 경량 SentenceTransformer 모델 선택
MODEL_NAME = 'all-MiniLM-L6-v2'

async def load_model():
    """
    비동기로 모델 로드
    """
    print("모델 로드 중... 잠시만 기다려 주세요.")
    return SentenceTransformer(MODEL_NAME)

def load_data(file_path):
    """
    엑셀 데이터 로드 및 임베딩 생성
    """
    df = pd.read_excel(file_path)
    df = df.dropna()
    return df

def calculate_embeddings(df, model):
    """
    데이터프레임의 '고객' 열에 대한 임베딩 생성
    """
    df['embedding'] = df['고객'].map(lambda x: list(model.encode(x)))
    return df

async def initialize_model_and_data(file_path):
    """
    모델 및 데이터를 초기화하는 함수
    """
    # 모델 비동기로 로드
    model = await load_model()

    # 데이터 로드 및 임베딩 계산
    df = load_data(file_path)
    df = calculate_embeddings(df, model)
    return model, df
