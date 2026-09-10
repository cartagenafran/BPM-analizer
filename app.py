import streamlit as st
import librosa
import numpy as np
import tempfile
import os
import json

st.set_page_config(page_title="BPM Analyzer", page_icon="🎵")
st.title("BPM Analyzer")
st.write("Drag a song to get its BPM.")

archivo_subido = st.file_uploader("Upload MP3 or WAV", type=["mp3", "wav"])

if archivo_subido is not None:
    st.audio(archivo_subido)
    
    with st.spinner("Analyzing BPM..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(archivo_subido.read())
            ruta_temp = temp_file.name

        try:
            # Solo Librosa trabajando
            y, sr = librosa.load(ruta_temp, sr=None)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = tempo[0] if isinstance(tempo, np.ndarray) else tempo
            
            # Interfaz simple
            st.success("Done!")
            st.metric(label="BPM", value=round(float(bpm), 2))
            
            # Descarga
            datos = {"bpm": float(bpm), "file": archivo_subido.name}
            json_string = json.dumps(datos, indent=4)
            
            st.download_button(
                label="⬇️ Download JSON",
                data=json_string,
                file_name="bpm_data.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            os.remove(ruta_temp) 
