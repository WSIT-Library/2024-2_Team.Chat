import csv
import os

def save_chat_csv(name, chat, time):
    # 고정된 파일 경로
    path = 'C:\\Users\\Name_Oing\\Desktop\\개발튤\\capto\\kakao_chat'
    file_path = os.path.join(path, name)
    
    # 파일이 없을 경우 헤더 포함하여 생성
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # 파일이 없을 때만 헤더 작성
        if not file_exists:
            writer.writerow(['Chat', 'Time'])
        
        # 데이터 추가
        writer.writerow([chat, time])