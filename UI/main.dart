import 'package:flutter/material.dart';
import 'screens/voice_chat_screen.dart';
import 'screens/chat_screen.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return MaterialApp(
            title: '홈쇼핑 AI 상담사',
            theme: ThemeData(primarySwatch: Colors.teal),
            home: MyHomePage(),
        );
    }
}

class MyHomePage extends StatelessWidget {
    void _startVoiceChat(BuildContext context) {
        Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => VoiceChatScreen()),
        );
    }

    void _startTextChat(BuildContext context) {
        Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => ChatScreen()),
        );
    }

    @override
    Widget build(BuildContext context) {
        return Scaffold(
            body: Container(
                decoration: BoxDecoration(
                    gradient: LinearGradient(
                        colors: [Colors.teal.shade200, Colors.white],
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                    ),
                ),
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: <Widget>[
                        CircleAvatar(
                            radius: 90,
                            backgroundImage: AssetImage('image/logo.png'),
                        ),
                        SizedBox(height: 20),
                        Text(
                            '스마트한 AI 상담사로\n편리한 쇼핑을 경험하세요!',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w500,
                                color: Colors.black87,
                            ),
                        ),
                        SizedBox(height: 40),
                        Card(
                            margin: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                            elevation: 4,
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                            ),
                            child: ListTile(
                                leading: Icon(Icons.mic, size: 40, color: Colors.teal),
                                title: Text(
                                    '음성으로 대화하기',
                                    style: TextStyle(fontSize: 18),
                                ),
                                onTap: () => _startVoiceChat(context),
                            ),
                        ),
                        Card(
                            margin: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                            elevation: 4,
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                            ),
                            child: ListTile(
                                leading: Icon(Icons.chat, size: 40, color: Colors.teal),
                                title: Text(
                                    '채팅으로 대화하기',
                                    style: TextStyle(fontSize: 18),
                                ),
                                onTap: () => _startTextChat(context),
                            ),
                        ),
                    ],
                ),
            ),
        );
    }
}

