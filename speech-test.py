import pyttsx3

thread_engine = pyttsx3.init()
voice = thread_engine.getProperty("voices")
thread_engine.setProperty("rate", 150)
thread_engine.say("here's a joke while you are waiting.")
thread_engine.runAndWait()