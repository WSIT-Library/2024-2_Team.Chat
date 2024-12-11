import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ChatScreen extends StatefulWidget {
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  List<Map<String, String>> _messages = [];
  //final String serverUrl = 'http://192.168.35.197:1234/send_message'; // Flask 서버 URL
  final String serverUrl = 'http://192.168.174.192:1234/send_message'; // Flask 서버 URL
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadMessages();
  }

  Future<void> _sendMessage(String message) async {
    if (message.isEmpty) return;

    setState(() {
      _isLoading = true;
      _messages.add({"text": message, "sender": "user"});
      _controller.clear();
    });

    final url = Uri.parse(serverUrl);
    final headers = {"Content-Type": "application/json"};
    final body = jsonEncode({"message": message});

    try {
      final response = await http.post(url, headers: headers, body: body);

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        final aiMessage = jsonResponse['response'] ?? "응답 없음";

        setState(() {
          _messages.add({"text": aiMessage, "sender": "ai"});
        });

        // 메시지 저장
        _saveMessages();
      } else {
        _addErrorMessage("오류: 서버에서 응답하지 않습니다.");
      }
    } catch (e) {
      _addErrorMessage("네트워크 오류: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _addErrorMessage(String errorMessage) {
    setState(() {
      _messages.add({"text": errorMessage, "sender": "ai"});
    });
    _saveMessages();
  }

  Future<void> _loadMessages() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    List<String>? savedMessages = prefs.getStringList('chat_messages');
    if (savedMessages != null) {
      setState(() {
        _messages = savedMessages.map((msg) {
          final parts = msg.split('::');
          return {"text": parts[0], "sender": parts[1]};
        }).toList();
      });
    }
  }

  Future<void> _saveMessages() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    List<String> savedMessages = _messages.map((msg) {
      return '${msg['text']}::${msg['sender']}';
    }).toList();
    prefs.setStringList('chat_messages', savedMessages);
  }

  Future<void> _deleteAllMessages() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    prefs.remove('chat_messages');
    setState(() {
      _messages.clear();
    });
  }

  void _deleteMessage(int index) async {
    setState(() {
      _messages.removeAt(index);
    });
    _saveMessages();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('채팅방'),
        actions: [
          IconButton(
            icon: Icon(Icons.delete_forever),
            onPressed: _deleteAllMessages,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message['sender'] == 'user';
                return GestureDetector(
                  onLongPress: () => _deleteMessage(index), // 길게 누르면 개별 메시지 삭제
                  child: Align(
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
                  ),
                );
              },
            ),
          ),
          if (_isLoading)
            Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(),
            ),
          Padding(
            padding: EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(labelText: '메시지 입력'),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send),
                  onPressed: () => _sendMessage(_controller.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
