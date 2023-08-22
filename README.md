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
