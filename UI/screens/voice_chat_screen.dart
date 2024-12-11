import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:io';

class VoiceChatScreen extends StatefulWidget {
  @override
  _VoiceChatScreenState createState() => _VoiceChatScreenState();
}

class _VoiceChatScreenState extends State<VoiceChatScreen> {
  final stt.SpeechToText _speech = stt.SpeechToText();
  final AudioPlayer _audioPlayer = AudioPlayer();
  final List<Map<String, String>> _messages = [];
  String _recognizedText = "";
  String _statusMessage = "마이크를 눌러 음성 인식을 시작하세요.";
  bool _isListening = false;
 // final String serverUrl = 'http://192.168.35.197:1234/process_audio'; // Flask 서버 URL
  final String serverUrl = 'http://192.168.174.192:1234/process_audio'; // Flask 서버 URL
  @override
  void initState() {
    super.initState();
    _requestMicrophonePermission();
  }

  Future<void> _requestMicrophonePermission() async {
    var status = await Permission.microphone.request();
    if (status.isGranted) {
      setState(() {
        _statusMessage = "마이크를 눌러 음성 인식을 시작하세요.";
      });
    } else if (status.isDenied) {
      setState(() {
        _statusMessage = "마이크 권한이 필요합니다.";
      });
    } else if (status.isPermanentlyDenied) {
      openAppSettings();
    }
  }

  void _startListening() async {
    if (await Permission.microphone.isGranted) {
      bool available = await _speech.initialize();
      if (available) {
        setState(() {
          _isListening = true;
          _statusMessage = "음성을 인식 중입니다...";
        });
        _speech.listen(onResult: (result) {
          setState(() {
            _recognizedText = result.recognizedWords;
          });
        });
      } else {
        setState(() {
          _statusMessage = "음성 인식을 초기화할 수 없습니다.";
        });
      }
    } else {
      setState(() {
        _statusMessage = "마이크 권한이 필요합니다.";
      });
      _requestMicrophonePermission();
    }
  }

  void _stopListening() {
    setState(() {
      _isListening = false;
      _statusMessage = "음성 인식이 완료되었습니다.";
    });
    _speech.stop();

    if (_recognizedText.isNotEmpty) {
      _sendVoiceMessage();
    }
  }

  Future<void> _sendVoiceMessage() async {
    if (_recognizedText.isEmpty) return;

    setState(() {
      _messages.add({"text": _recognizedText, "sender": "user"});
      _statusMessage = "서버로 메시지를 전송 중입니다...";
    });

    final url = Uri.parse(serverUrl);
    final headers = {"Content-Type": "application/json"};
    final body = jsonEncode({"text": _recognizedText});

    try {
      final response = await http.post(url, headers: headers, body: body);

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        final aiMessage = jsonResponse['response'] ?? "응답 없음";
        final audioBase64 = jsonResponse['audio'];

        setState(() {
          _messages.add({"text": aiMessage, "sender": "ai"});
          _statusMessage = "응답을 받았습니다.";
        });

        if (audioBase64 != null) {
          final bytes = base64Decode(audioBase64);
          final tempDir = await getTemporaryDirectory();
          final filePath = '${tempDir.path}/response.mp3';
          final file = File(filePath);
          await file.writeAsBytes(bytes);

          // 최신 audioplayers 방식으로 파일 재생
          await _audioPlayer.play(DeviceFileSource(filePath));
        }
      } else {
        setState(() {
          _statusMessage = "서버에서 응답하지 않습니다.";
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = "네트워크 오류가 발생했습니다.";
      });
      print("오류 발생: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('음성 대화')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message['sender'] == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    padding: EdgeInsets.symmetric(vertical: 10, horizontal: 14),
                    margin: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                    decoration: BoxDecoration(
                      color: isUser ? Colors.blue[100] : Colors.green[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      message['text']!,
                      style: TextStyle(
                        color: isUser ? Colors.blue[800] : Colors.green[800],
                        fontSize: 16,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          Text(
            _statusMessage,
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.teal),
            textAlign: TextAlign.center,
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                icon: Icon(
                  _isListening ? Icons.mic : Icons.mic_none,
                  size: 40,
                  color: Colors.teal,
                ),
                onPressed: _isListening ? _stopListening : _startListening,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
