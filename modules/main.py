import keyboard
import time

from listener import Listener
from speaker import Speech2TextModel

import multiprocessing
from functools import partial

def playSound(queue: multiprocessing.Queue):
    from speech_synthesis import SpeechSynthesis
    talker = SpeechSynthesis()

    while True:
        if queue.empty():
            talker.say("thinking")
        else:
            talker.say(queue.get())
            break

def chatbotRespond(text: str, queue: multiprocessing.Queue):
    from chatgpt import Chat
    chatbot = Chat()
    response = chatbot.respond(text)
    queue.put(response)

def main():
    listener = Listener()
    transcriber = Speech2TextModel()

    print("whisper model loaded")
    queue = multiprocessing.Queue()

    while True:
        try:
            if keyboard.is_pressed('1'):
                listener.listen()
            
                audio_data = listener.get_audio_data()
                if audio_data:
                    text = transcriber.transcribe(audio_data)

                    # spawn two processes - on playsound process, it will keep playing "thinking" 
                    # while getting response from the chatbotRespond process 
                    func1 = partial(chatbotRespond, text)
                    process1 = multiprocessing.Process(target=func1, args=(queue, ))
                    process2 = multiprocessing.Process(target=playSound, args=(queue, ))

                    process2.start()
                    process1.start()

                    process2.join()
                    process1.join()

        except KeyboardInterrupt:
            break

        time.sleep(0.25)

if __name__ == "__main__":
    main()