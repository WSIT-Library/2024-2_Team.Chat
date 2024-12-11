import requests
import asyncio
from kakao_chat_CSV import save_chat_csv
from kakao_koGPT import initialize_model_and_data  # 모델과 데이터를 초기화하는 함수
from queue import Queue
from sklearn.metrics.pairwise import cosine_similarity

# 전역 변수로 모델과 데이터를 저장
global_model = None
global_df = None

# Rasa 서버 URL
RASA_URL = "http://localhost:1000"  # Rasa 서버의 URL을 여기에 입력하세요

# 메시지 큐 설정
send_chat_queue = Queue()
receive_chat_list = []

# Rasa에 메시지 송신
def send_message_to_rasa(rasa_send_message):
    payload = {
        "message": rasa_send_message  # 보낼 메시지
    }
    
    try:
        response = requests.post(f"{RASA_URL}/webhooks/rest/webhook", json=payload)
        if response.status_code == 200:
            handle_response(response.json())
        else:
            print(f"Error sending message to Rasa: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Rasa 요청 중 오류 발생: {e}")

# Rasa에 메시지 수신
def handle_response(response):
    for bot_response in response:
        receive_chat(bot_response['text'])  # bot_response.get('text') 사용
        print(f"라사 : {bot_response.get('text')}")

def send_chat(chat):
    send_message_to_rasa(chat)  # Rasa로 메시지를 전송
    print("라사에 메시지 전송")

def receive_chat(chat):
    global receive_chat_list 
    receive_chat_list.append(chat)  # 수신 채팅 추가

def answer_chat():
    while receive_chat_list:
        current_chat = receive_chat_list.pop(0)  # 첫 번째 요소부터 차례대로 처리
        print("챗봇 대답", current_chat)
        return current_chat  # 응답 메시지 반환

def chat_duplicate_check(chat):
    send_chat_queue.put(chat)  # 큐에 메시지 추가
    
    while not send_chat_queue.empty():
        current_chat = send_chat_queue.get()  # 큐에서 메시지 가져오기
        
        file_path = "C:\\Users\\Name_Oing\\Desktop\\개발튤\\capto\\rasa.txt"   
        try:
            # 파일을 줄 단위로 읽기
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file.readlines()]  # 각 줄을 리스트로 가져오기

            # 중복 확인 및 처리
            if current_chat.strip() in lines:  # 입력 텍스트가 줄 중 하나와 일치하는지 확인
                send_chat(current_chat)  # Rasa로 메시지 전송
            else:
                asyncio.run(send_gpt(current_chat))  # GPT로 처리
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

def chat_insert(name, chat, time):
    save_chat_csv(name, chat, time) 
    chat_duplicate_check(chat)

async def initialize_global_model_and_data(file_path="dataset.xlsx"):
    global global_model, global_df
    if global_model is None or global_df is None:
        # 모델과 데이터가 로드되지 않은 경우에만 초기화
        global_model, global_df = await initialize_model_and_data(file_path)
        print("모델과 데이터가 초기화되었습니다.")
    else:
        print("이미 로드된 모델과 데이터를 사용합니다.")

async def send_gpt(chat):
    global global_model, global_df

    # 모델과 데이터가 초기화되지 않았다면 로드
    if global_model is None or global_df is None:
        await initialize_global_model_and_data()

    # 사용자 입력 임베딩 생성
    embedding = global_model.encode(chat)

    # 각 데이터와의 코사인 유사도 계산
    global_df['similarity'] = global_df['embedding'].map(lambda x: cosine_similarity([embedding], [x]).squeeze())

    # 유사도가 가장 높은 응답 선택
    answer = global_df.loc[global_df['similarity'].idxmax()]
    response = answer['상담사']
    
    # 수신 채팅에 추가
    receive_chat(response)
    print(f"유사도 응답: {response}")

def chat_bot_answer():
    answer_chat() 



    