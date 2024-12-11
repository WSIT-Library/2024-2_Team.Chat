import requests
from sklearn.metrics.pairwise import cosine_similarity
from kakao_koGPT import load_data, calculate_embeddings
from sentence_transformers import SentenceTransformer
import time

# 전역 변수 초기화
global_model, global_df = None, None
DATA_FILE_PATH = "C:\\Users\\Name_Oing\\Desktop\\개발튤\\capto\\dataset.xlsx"  # 데이터셋 경로
RASA_URL = "http://localhost:1000"

def initialize_kogpt2():
    """
    KoGPT2 모델과 데이터를 서버 시작 시 동기적으로 초기화
    """
    global global_model, global_df
    print("KoGPT2 모델 및 데이터 초기화 중...")
    start_time = time.time()
    try:
        # 모델 및 데이터 로드
        model = SentenceTransformer('all-MiniLM-L6-v2')  # 경량 모델 로드
        df = load_data(DATA_FILE_PATH)  # 데이터 로드
        df = calculate_embeddings(df, model)  # 임베딩 계산
        global_model, global_df = model, df
        print(f"KoGPT2 모델 및 데이터 초기화 완료. 소요 시간: {time.time() - start_time:.2f}초")
    except Exception as e:
        print(f"Error during KoGPT2 initialization: {e}")
        raise

def send_message_to_rasa(message):
    """
    Rasa에 메시지 전달 및 응답 수신
    """
    payload = {"message": message}
    try:
        response = requests.post(f"{RASA_URL}/webhooks/rest/webhook", json=payload)
        if response.status_code == 200:
            bot_responses = [res.get('text', '') for res in response.json()]
            return " ".join(bot_responses)
        return f"Rasa Error: {response.status_code}"
    except Exception as e:
        return f"Error sending to Rasa: {e}"

def send_gpt(message):
    """
    KoGPT2를 사용해 응답 생성
    """
    global global_model, global_df
    try:
        if global_model is None or global_df is None:
            raise Exception("모델과 데이터가 초기화되지 않았습니다.")

        # 사용자 입력 임베딩 생성
        embedding = global_model.encode(message)

        # 코사인 유사도 계산
        global_df['similarity'] = global_df['embedding'].apply(
            lambda x: cosine_similarity([embedding], [x]).squeeze()
        )

        # 가장 유사한 응답 반환
        best_match = global_df.loc[global_df['similarity'].idxmax()]
        return best_match['상담사']
    except Exception as e:
        print(f"Error in send_gpt: {e}")
        return "죄송합니다. 응답을 생성하지 못했습니다."
