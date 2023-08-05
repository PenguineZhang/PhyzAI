# Notes (windows 10)
- check device index
```
import speech_recognition as sr
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
```
- torch cuda is default to fp32 if fp16 is not specified
- Some faster inference model than openai/whisper:
  - [faster-whisper fp16](https://github.com/guillaumekln/faster-whisper) is said to be 4x faster than openai/whisper 
    - tested on my computer (i5-12600K, RTX 3060, NVidia v522.04, CUDA 11.8)
      - 0.88 - 1.02 seconds
  - [whisper-cpp](https://github.com/ggerganov/whisper.cpp)


### Notes for Sarah

I separated speech recognition from microphone, transcription (I use a faster version of openai-whisper), GPT-3.5, and speech synthesis into individual classes so they become more manageable. `main.py` integrates them all. So running `main.py` should run all the elements. I analyzed the time to get response from GPT-3.5 and it averaged to 1.6 seconds, which is insignificant. I also tried connecting to a weak hotspot (2-bar) instead of WiFi and I got similar result. Adding voice filler (jokes, known phrases like "thinking", etc) is an interesting way to cover the awkward silence when waiting for chatbot's response. The way to achieve that is through threading. I spent several hours trying different threading strategies but not getting the expected behavior. It made me think whether we should continue with the voice filler to cover 1.6 seconds wait time. 

Another question: where is the voice transcription model running on? Is it running on CPU of the mini-computer? I am not sure the time duration of the transcription on that computer, but I run mine on a GPU so inference time is about 1 second. 

Please share what you think and we can discuss how to move forward.