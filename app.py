from gtts import gTTS
from mutagen.mp3 import MP3 
import base64
import streamlit as st
import os
import openai
import time
import whisper
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from audiorecorder import audiorecorder
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
        SystemMessage,
        HumanMessage,
        AIMessage
    )

# Load Whisper Model
model = whisper.load_model("medium")

#This will take some more time to run initially, need to download the model 
openai.api_key = os.getenv('OPENAI_API_KEY')
st.set_page_config(page_title="nepaliGPT - A Nepali ChatGPT Streamlit Conversational Bot")
st.title(':red[ne]GPT - A :red[nepali] ChatGPT Streamlit Conversational Bot')

def play_audio(filepath, length):
    with open(filepath, "rb") as aud:
        data = aud.read()
        b64 = base64.b64encode(data).decode()
        md  = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        sound = st.empty()
        sound.markdown(
                md, 
                unsafe_allow_html=True,
            )
        time.sleep(int(length)+5)
        sound.empty()

def aud_to_text(audio):
    response_ = whishper_model.transcribe(audio, language='ne')['text']
    return response_

chat = ChatOpenAI(temperature=0)
if "messages" not in st.session_state:
    st.session_state.messages=[SystemMessage(content='You are an AI Assistant, Can you please translate your responses to Nepali')]

audio_bytes = audiorecorder("Click to record", "Its Recording...")

if len(audio_bytes) > 0:
    st.audio(audio_bytes.tobytes())
    wav_file = open("audio.mp3", "wb")
    wav_file.write(audio_bytes.tobytes())
    user_input = model.transcribe(wav_file.name, language='ne')['text']

if len(audio_bytes) > 0:
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.spinner("Processing..."):
        response = chat(st.session_state.messages)
        print(response.content)

        tts = gTTS(response.content, language='ne')
        tts.save('response.mp3')
        aud = MP3('response.mp3')
        autoplay_audio('response.mp3', aud.info.length)
    st.session_state.messages.append(AIMessage(content=response.content))
messages = st.session_state.get('messages',[])

for i, msg in enumerate(messages[1:]):
    if i% 2 == 0:
        message(msg.content,is_user=True,key=str(i)+'_user')
    else:
        message(msg.content,is_user=False,key=str(i)+'_ai')
        
