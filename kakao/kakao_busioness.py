import time, threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from kakao_common_functions import chat_insert, answer_chat

# Chrome 드라이버 경로 설정
chrome_driver_path = 'C:\\Users\\Name_Oing\\Desktop\\개발튤\\capto\\chromedriver\\chromedriver.exe'

# Service 객체로 드라이버 경로 설정
service = Service(executable_path=chrome_driver_path)

# 웹드라이버 생성
driver = webdriver.Chrome(service=service)

# 카카오톡 채널 페이지로 이동
driver.get('https://center-pf.kakao.com/_uYIxhn/chats')  # 카카오톡 채널 페이지 URL로 대체

# 메모장에서 로그인 정보 읽기
with open('kakao.txt', 'r') as f:
    kakao_email = f.readline().strip()  # 첫 번째 줄 (이메일)
    kakao_password = f.readline().strip()  # 두 번째 줄 (비밀번호)

# 페이지가 로드될 때까지 기다림
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'loginId--1')))

# 이메일 입력
email_input = driver.find_element(By.ID, 'loginId--1')  # ID로 이메일 입력 필드 찾기
email_input.send_keys(kakao_email)

# 비밀번호 입력
password_input = driver.find_element(By.ID, 'password--2')  # ID로 비밀번호 입력 필드 찾기
password_input.send_keys(kakao_password)

# 로그인 버튼 클릭
login_button = driver.find_element(By.CSS_SELECTOR, 'button.btn_g.highlight.submit')  # CSS Selector로 로그인 버튼 찾기
login_button.click()

# 페이지가 로드될 때까지 기다림
time.sleep(20)

# 플래그 변수 및 Lock 객체 초기화
is_processing_chat = False
chat_lock = threading.Lock()

# 채팅 내용을 처리하는 함수
def process_chat():
    global is_processing_chat
    with chat_lock:  # Lock을 사용하여 쓰레드 안전성 확보
        is_processing_chat = True  
        print("Processing chat...")
        find_chat()  # Find_chat 호출
        is_processing_chat = False
        print("Chat processing finished.")

def find_chat():
    try:
        # 새 창으로 전환
        new_window = driver.window_handles[-1]  # 마지막으로 열린 창 핸들
        driver.switch_to.window(new_window)  # 새 창으로 전환

        time.sleep(15) 

        # <strong class="tit_user">에서 사용자 이름을 인식
        tit_user_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'strong.tit_user')))
        recognized_username = tit_user_element.text  # 사용자의 이름을 저장
        print(f"인식된 사용자 이름: {recognized_username}")
        
        # <strong class="txt_user">에서 동일한 이름을 가진 요소 찾기
        users = driver.find_elements(By.CSS_SELECTOR, 'strong.txt_user')

        # 인식된 사용자 이름과 일치하는 요소만 필터링
        target_user_elements = [user for user in users if user.text == recognized_username]

        if target_user_elements:
            # 가장 마지막에 있는 <strong class="txt_user">인식된 이름</strong> 요소 선택
            last_user_element = target_user_elements[-1]

            # 해당 요소 바로 밑에 있는 <p class="txt_chat"><span>채팅내용</span></p> 요소들 찾기
            chat_elements = last_user_element.find_elements(By.XPATH, './/following::p[@class="txt_chat"]/span')

            # 해당 요소 밑에 있는 <span class="txt_time"><span>오전 or 오후</span><span class="num_txt"><span>시간:분</span></span></span> 요소 찾기
            chat_ap = last_user_element.find_element(By.XPATH, './/following::span[@class="txt_time"]/span[1]')
            chat_time = last_user_element.find_element(By.XPATH, './/following::span[@class="num_txt"]')
            chat_realtime = f"{chat_ap.text} {chat_time.text}"  # 시간을 텍스트로 결합

            if chat_elements: 
                # 채팅 내용 전부 추출
                chat_messages = [chat.text for chat in chat_elements]
                print("채팅 내용들:")
                for chat_message in chat_messages:
                    print(chat_message)
                
                # 인식된 사용자 이름과 채팅 내용을 chat_insert 함수로 전달
                for message in chat_messages:
                    chat_insert(recognized_username, message, chat_realtime)  

                    # 챗봇의 응답을 가져오기 (chat_bot_answer 함수 호출)
                    bot_response = answer_chat()
                    print(bot_response)

                    # 응답을 <textarea>에 넣고 전송 버튼을 누름
                    if bot_response:
                        enter_chat_response(bot_response)  # 응답 입력 함수 호출

            else:
                print("채팅 내용을 찾을 수 없습니다.")
        else:
            print(f"사용자 '{recognized_username}'을 찾을 수 없습니다.")
        
        # 원래 창으로 돌아가기
        driver.switch_to.window(driver.window_handles[0])  # 원래 창으로 돌아가기
    except Exception as e:
        print(f"오류 발생: {e}")

def enter_chat_response(response):
    try:
        textarea = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "chatWrite")))
        textarea.clear()         
        textarea.send_keys(response)

        send_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_g.btn_submit")))
        
        # 버튼이 비활성화 상태일 경우 활성화 대기
        if send_button.get_attribute("disabled") == "true":
            print("버튼이 비활성화 상태입니다. 버튼이 활성화될 때까지 대기합니다.")        
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_g.btn_submit:not(.disabled)")))

        send_button.click()
        print("메시지를 전송했습니다.")
    except Exception as e:
        print(f"응답 전송 중 오류 발생: {e}")

try:    
    while True:
        # 1. a.link_snb 안에 있는 num_round 탐색 및 처리
        link_snb_elements = driver.find_elements(By.CSS_SELECTOR, 'a.link_snb .num_round')
        for num_round in link_snb_elements:
            num_text = num_round.text.strip()
            if num_text.isdigit() and int(num_text) > 0:
                print(f"새로운 채팅 {num_text}개가 있습니다.")

        # 2. strong.tit_info 아래의 span.txt_name과 num_round 탐색 및 출력
        info_sections = driver.find_elements(By.CLASS_NAME, 'tit_info')
        for info_section in info_sections:
            try:
                # span.txt_name 요소 찾기
                txt_name_element = info_section.find_element(By.CLASS_NAME, 'txt_name')
                txt_name_text = txt_name_element.text.strip()
                
                # num_round 요소 찾기
                num_round_element = info_section.find_element(By.CLASS_NAME, 'num_round')
                num_round_text = num_round_element.text.strip()
                
                # span.txt_name과 num_round의 텍스트 출력
                print(f"이름: {txt_name_text}, 채팅 수: {num_round_text}")
                
                if num_round_text.isdigit() and int(num_round_text) > 0:
                    # num_round의 부모에서 link_chat 요소 찾기
                    chat_link = num_round_element.find_element(By.XPATH, './ancestor::a[@class="link_chat"]')
                    
                    # link_chat 요소를 클릭 (채팅창 열기)
                    chat_link.click()
                    print(f"{txt_name_text}의 채팅창을 엽니다.")
                    
                    # 채팅 내용을 처리하는 작업 수행
                    threading.Thread(target=process_chat).start()
                    break  # 내부 for 루프 탈출
            except NoSuchElementException:
                continue  # 요소가 없으면 계속 진행
            
        # 0.5초 대기 후 다시 탐색
        time.sleep(0.5)

except KeyboardInterrupt:
    print("사용자에 의해 강제 종료.")

finally:
    # 브라우저를 종료하지 않고 유지
    print("Press Enter to close the browser...")
    input()  # 사용자가 Enter 키를 누를 때까지 대기

    # 드라이버 종료
    driver.quit()       
