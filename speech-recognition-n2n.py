import argparse
import io
import os
import time
import threading
import random

import speech_recognition as sr
# import whisper
import openai
import torch
from faster_whisper import WhisperModel

from datetime import datetime, timedelta
from queue import Queue
import pyttsx3 

completion = None
jokes = []
isJokeDone = False

def getDadjokes():
	with open("dadjokes.txt", encoding="utf-8") as f:
		lines = f.readlines()

	for l in lines:
		jokes.append(l.split("<>"))
    
def play_dadjokes():
    global isJokeDone
    print("playing dadjokes")
    thread_engine = pyttsx3.init()
    thread_engine.setProperty("rate", 150)
    
    random_jokes = "here's a joke while you are waiting." + "".join(jokes[random.randint(0, len(jokes)-1)])

    thread_engine.say(random_jokes)
    thread_engine.runAndWait()

    time.sleep(0.25)

    isJokeDone = True

def chatGPTResponse(text):
    global completion, isJokeDone

    print("responding")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are a commedian that respond to the conversation with humor to teenagers. Try to keep the response to 2 to 3 sentenses"},
        {"role": "user", "content": text}
        ]
    )

def main():
    global completion, isJokeDone

    parser = argparse.ArgumentParser()
    # parser.add_argument("--model", default="medium", help="Model to use",
    #                     choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=5,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)  
    
    args = parser.parse_args()
    
    # The last time a recording was retreived from the queue.
    phrase_time = None
    
    # Current raw audio bytes.
    last_sample = bytes()

    # Thread safe Queue for passing data from the threaded 
    # recording callback.
    data_queue = Queue()

    # We use SpeechRecognizer to record our audio because 
    # it has a nice feauture where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold

    # Definitely do this, dynamic energy compensation lowers 
    # the energy threshold dramtically to a point where the 
    # SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False
    
    source = sr.Microphone(sample_rate=16000, device_index=2)

    # Load / Download model
    # model = args.model
    # if args.model != "large" and not args.non_english:
    #     model = model + ".en"
    # audio_model = whisper.load_model(model)
    
    audio_model = WhisperModel("large-v2", device="cuda", compute_type="float16")

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    transcription = ['']

    # def record_callback(_, audio:sr.AudioData) -> None:
    #     """
    #     Threaded callback function to recieve audio data when recordings finish.
    #     audio: An AudioData containing the recorded bytes.
    #     """
    #     # Grab the raw bytes and push it into the thread safe queue.
    #     data = audio.get_raw_data()
    #     data_queue.put(data)

    # # Create a background thread that will pass us raw audio bytes.
    # # We could do this manually but SpeechRecognizer provides a nice helper.
    # recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    
    # Cue the user that we're ready to go.
    print("Model loaded.\n")

    openai.api_key = os.getenv("OPENAI_API_KEY")

    engine = pyttsx3.init()

    t1 = threading.Thread(target=play_dadjokes)
    t1.daemon = False

    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            
            print("start listening")
            start_time = time.time()
            while True:
                with source:
                    recorder.adjust_for_ambient_noise(source)
                    audio = recorder.listen(source, phrase_time_limit=record_timeout)
                    if audio:
                        data_queue.put(audio.get_raw_data())
                        break
            print("time spend in recording: ", time.time() - start_time)

            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now

                start_time = time.time()
                # Concatenate our current audio data with the latest audio data.
                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data
                print("time spend in concatenating audio data: ", time.time() - start_time)

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                start_time = time.time()

                segments, _ = audio_model.transcribe(wav_data, beam_size=5)
                print("time spend in transcribing audio data: ", time.time() - start_time)

                text = ""
                for s in segments:
                    text += s.text

                print(text)

                # start_time = time.time()

                done = False
                t2 = threading.Thread(target=chatGPTResponse, args=[text])
                t2.start()

                while not done:
                    # print("is t1 alive? ", t1.is_alive())
                    # print("is joke done? ", isJokeDone)
                    # if completion == None and not t1.is_alive():
                    #     # t1 = threading.Thread(target=play_dadjokes)
                    #     t1.start()
                    
                    time.sleep(0.5)
                    
                    if completion != None:
                        done = True

                # print("time spend in GPT response: ", time.time() - start_time)

                # summary = completion.choices[0].message["content"]
                # print(summary)

                engine.say(completion.choices[0].message["content"])
                engine.runAndWait()

                completion = None
                isJokeDone = False

                # Infinite loops are bad for processors, must sleep.
                time.sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)


if __name__ == "__main__":
    getDadjokes()
    # print(jokes)
    main()