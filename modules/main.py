import keyboard
import time
import concurrent.futures as future
from queue import Queue

from listener import Listener
from stt import Speech2TextModel
from chatgpt import Chat
from speech_synthesis import SpeechSynthesis

done = False

def talker(joker: SpeechSynthesis, q: Queue):
    if q.empty():
        joker.sayJokes()

def chatbot_respond(chatbot: Chat, text: str, q: Queue):
    response = chatbot.respond(text)
    q.put(response)

def main():
    listener = Listener()
    transcriber = Speech2TextModel()
    chatbot = Chat()
    speaker = SpeechSynthesis()

    print("whisper model loaded")

    q = Queue()

    while True:
        try:
            if keyboard.is_pressed('1'):
                listener.listen()
            
                audio_data = listener.get_audio_data()
                if audio_data:
                    text = transcriber.transcribe(audio_data)
                    
                    with future.ThreadPoolExecutor() as executor:
                        chatbot_future = executor.submit(chatbot_respond, chatbot, text, q)
                        talker_future = executor.submit(talker, speaker, q)

                        future.wait([chatbot_future, talker_future])

        except KeyboardInterrupt:
            break

        time.sleep(0.25)
        

if __name__ == "__main__":
    main()