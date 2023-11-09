# import streamlit as st
# import openai
# import io
# from pydub import AudioSegment
# from audio_recorder_streamlit import audio_recorder

# openai.api_key = "sk"


# st.title("Audio Recorder")
# audio = audio_recorder("Click to record", "Click to stop recording", sample_rate=12000)
# data = io.BytesIO(audio)
# if audio is not None:
#     if len(audio) > 0:
#         # To play audio in frontend:
#         st.audio(audio)

#         # To save audio to a file, use pydub export method:
#         audio = AudioSegment.from_raw(data,sample_width=4,frame_rate=12000, channels=1)
#         audio.export("test.mp3", format='mp3')
        
#         audio_file = open("./test.mp3", "rb")
#         transcript = openai.Audio.transcribe("whisper-1", audio_file)
#         st.write(transcript)


import streamlit as st
import openai
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import os

# Define the audio class with the recording method
class audio:
    
    @classmethod
    def record(cls):
        freq = 44100  # Sampling frequency
        duration = 15  # Recording duration in seconds
        st.write("Recording your voice for the next 15 seconds...")
        recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)
        sd.wait()  # Wait until recording is finished
        os.makedirs("recordings", exist_ok=True)
        write("recordings/recording0.wav", freq, recording)
        wv.write("recordings/recording.wav", recording, freq, sampwidth=2)
        st.write("Audio recording saved")
        return "recordings/recording.wav"

# Define the transcription method
def transcribe(file: str):
    openai.api_key = "sk"
    st.write("Transcribing the audio...")
    with open(file, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    st.write("Successfully Transcribed the audio.")
    return transcript["text"]

# Streamlit interface
def main():
    st.title("Audio Recorder and Transcriber")

    if st.button("Record Audio"):
        filename = audio.record()
        st.session_state["last_recorded_file"] = filename

    if st.button("Transcribe Audio"):
        if "last_recorded_file" in st.session_state:
            transcription = transcribe(st.session_state["last_recorded_file"])
            st.write(transcription)
        else:
            st.write("Please record an audio first.")

# Run the main function
if __name__ == "__main__":
    main()
