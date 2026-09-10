import streamlit as st
import librosa
import numpy as np
import tempfile
import os
import json
import asyncio
from shazamio import Shazam

st.set_page_config(page_title="DJ Analyzer", page_icon="🎧")
st.title("🎧 Track Analyzer")
st.write("Upload a song to get BPM, title, and cover.")

async def buscar_track(ruta):
    shazam = Shazam()
    return await shazam.recognize_song(ruta)

archivo_subido = st.file_uploader("Upload MP3 or WAV", type=["mp3", "wav"])

if archivo_subido is not None:
    st.audio(archivo_subido)
    
    with st.spinner("Analyzing audio..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(archivo_subido.read())
            ruta_temp = temp_file.name

        try:
            # 1. LIBROSA (BPM)
            y, sr = librosa.load(ruta_temp, sr=None)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = tempo[0] if isinstance(tempo, np.ndarray) else tempo
            
            # 2. SHAZAMIO
            resultado_shazam = asyncio.run(buscar_track(ruta_temp))
            
            titulo = "Unknown"
            artista = "Unknown"
            imagen_url = None
            encontrado = False
            
            if 'track' in resultado_shazam:
                encontrado = True
                track_info = resultado_shazam['track']
                titulo = track_info.get('title', 'Unknown')
                artista = track_info.get('subtitle', 'Unknown')
                imagen_url = track_info.get('images', {}).get('coverart')

            # 3. INTERFAZ GRÁFICA
            st.success("Done!")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if imagen_url:
                    st.image(imagen_url, use_container_width=True)
                else:
                    st.warning("No cover found.")
                    
            with col2:
                st.subheader(f"🎵 {titulo}")
                st.write(f"**Artist:** {artista}")
                st.metric(label="BPM", value=round(float(bpm), 2))
                if encontrado:
                    st.caption("✅ Verified by Shazam")

            # 4. DESCARGA DEL JSON
            datos = {
                "bpm": float(bpm), 
                "title": titulo, 
                "artist": artista
            }
            json_string = json.dumps(datos, indent=4)
            
            st.download_button(
                label="⬇️ Download JSON",
                data=json_string,
                file_name="track_data.json",
                mime="application/json"
            )

        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            os.remove(ruta_temp)
