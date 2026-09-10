import streamlit as st
import librosa
import numpy as np
import tempfile
import os
import json

# Configuración de la página
st.set_page_config(page_title="Analizador de Audio", page_icon="🎵")
st.title("Get BPM")
st.write("drag your song here.")

# El widget mágico de arrastrar y soltar
archivo_subido = st.file_uploader("upload MP3 or WAV", type=["mp3", "wav"])

if archivo_subido is not None:
    # Reproductor de audio integrado en la web
    st.audio(archivo_subido)
    
    with st.spinner("Analizing..."):
        # Streamlit necesita guardar el archivo temporalmente para que Librosa lo lea
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(archivo_subido.read())
            ruta_temp = temp_file.name

        try:
            # Nuestro viejo amigo Librosa haciendo el trabajo duro
            y, sr = librosa.load(ruta_temp, sr=None)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = tempo[0] if isinstance(tempo, np.ndarray) else tempo
            
            # Mostrar resultados visuales (cajas grandes de números)
            st.success("Success!")
            st.metric(label="BPM (Tempo)", value=round(float(bpm), 2))
            
            # Generar el JSON en memoria para el botón de descarga
            datos = {"bpm": float(bpm), "archivo": archivo_subido.name}
            json_string = json.dumps(datos, indent=4)
            
            # Botón de descarga directa
            st.download_button(
                label="⬇️ Download JSON",
                data=json_string,
                file_name="analisis_track.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"failed to find the directory: {e}")
        finally:
            # Limpiar la basura
            os.remove(ruta_temp)