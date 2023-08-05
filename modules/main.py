import keyboard
import time

from listener import Listener
from stt import Speech2TextModel
from chatgpt import Chat
from speech_synthesis import SpeechSynthesis

def main():
    listener = Listener()
    transcriber = Speech2TextModel()
    chatbot = Chat()
    speaker = SpeechSynthesis()

    print("whisper model loaded")

    while True:
        try:
            if keyboard.is_pressed('1'):
                listener.listen()
            
                audio_data = listener.get_audio_data()
                if audio_data:
                    text = transcriber.transcribe(audio_data)
                    response = chatbot.respond(text)
                    speaker.say(response)

        except KeyboardInterrupt:
            break

        time.sleep(0.25)

if __name__ == "__main__":
    main()