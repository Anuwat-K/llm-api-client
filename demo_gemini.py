import os
import google.generativeai as genai
from google.cloud import texttospeech
from playsound import playsound
import speech_recognition as sr
import time
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'demo_service_account.json'
client = texttospeech.TextToSpeechClient()

API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def list_microphones():
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{index}: {name}")

def gemini_api(text):
    response = model.generate_content(text)
    text_block = response.text
    print("response",response.text)
    return text_block

def tts_api(text_block):
    synthesis_input = texttospeech.SynthesisInput(text=text_block)

    voice = texttospeech.VoiceSelectionParams(
        language_code="th-TH", 
        name = 'th-TH-Standard-A'
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, 
        voice=voice, 
        audio_config=audio_config
    )
    return response

def save_audio(response):
    if os.path.exists("output.mp3"):
        os.remove("output.mp3")

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

def recognize_speech_from_mic(mic_index=0):
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=mic_index)
    while True:
        with mic as source:
            print("กำลังฟัง... กรุณาพูด")
            # recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                print("กำลังแปลงเสียงเป็นข้อความ...")
                text = recognizer.recognize_google(audio, language="th")
                print("ข้อความที่ได้: ", text)
                text_block = gemini_api(text)
                response = tts_api(text_block)
                save_audio(response)
                playsound('output.mp3')
            except sr.UnknownValueError:
                print("ไม่สามารถเข้าใจเสียงได้")
            except sr.RequestError:
                print("เกิดข้อผิดพลาดในการเชื่อมต่อกับ Google API")
            time.sleep(2)

if __name__ == "__main__":
    print("รายการไมโครโฟนที่ใช้ได้:")
    list_microphones()
    mic_index = int(input("เลือกหมายเลขไมโครโฟน: "))
    recognize_speech_from_mic(mic_index)