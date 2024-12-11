from flask import Flask, request, jsonify
from flask_kogpt2 import send_gpt, send_message_to_rasa, initialize_kogpt2
import os
from gtts import gTTS
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Rasa 메시지 리스트 로드
def load_rasa_messages(file_path="rasa.txt"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []

RASA_MESSAGES = load_rasa_messages()

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """
    음성 데이터를 텍스트로 변환하고 Rasa 또는 KoGPT2로 응답 생성
    """
    try:
        # 클라이언트에서 전달받은 JSON 데이터 확인
        data = request.get_json()
        if 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        message = data['text']
        
        # 메시지 처리: Rasa 또는 KoGPT2 응답 생성
        if message in RASA_MESSAGES:
            response_text = send_message_to_rasa(message)
        else:
            response_text = send_gpt(message)

        # TTS 음성 생성
        tts = gTTS(response_text, lang='ko')
        tts_file = "response.mp3"
        tts.save(tts_file)

        # TTS 음성을 Base64로 인코딩
        with open(tts_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        # 사용 후 파일 삭제
        if os.path.exists(tts_file):
            os.remove(tts_file)

        return jsonify({
            'response': response_text,
            'audio': audio_base64
        }), 200

    except Exception as e:
        print(f"Error in process_audio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    """
    사용자 텍스트 메시지 처리
    """
    try:
        data = request.get_json()
        message = data.get('message', '')

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        if message in RASA_MESSAGES:
            response = send_message_to_rasa(message)
        else:
            response = send_gpt(message)

        return jsonify({'response': response}), 200
    except Exception as e:
        print(f"Error in send_message: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("서버 시작 중...")
    initialize_kogpt2()  # KoGPT2 모델 초기화
    app.run(host='0.0.0.0', port=1234)
