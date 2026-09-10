import streamlit as st
import librosa
import numpy as np
import tempfile
import os
import json
import acoustid
import musicbrainzngs
import requests

# Credenciales de AcoustID y MusicBrainz
ACOUSTID_KEY = 'jWlWqRztOh'

musicbrainzngs.set_useragent(
    "AnalizadorDJ_App", 
    "1.0", 
    "https://metabrainz.org/profile" 
)

# Configuración de la página
st.set_page_config(page_title="DJ Analyzer", page_icon="🎧")
st.title("🎧 Track Analyzer")
st.write("Upload a song to get BPM, title, and cover.")

archivo_subido = st.file_uploader("Upload MP3 or WAV", type=["mp3", "wav"])

if archivo_subido is not None:
    st.audio(archivo_subido)
    
    with st.spinner("Analyzing audio and searching database..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(archivo_subido.read())
            ruta_temp = temp_file.name

        try:
            # --- PARTE 1: Librosa (BPM) ---
            y, sr = librosa.load(ruta_temp, sr=None)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = tempo[0] if isinstance(tempo, np.ndarray) else tempo

            # --- PARTE 2: Búsqueda en MusicBrainz ---
            resultados = acoustid.match(ACOUSTID_KEY, ruta_temp)
            
            encontrado = False
            titulo = "Unknown"
            artista = "Unknown"
            imagen_url = None

            for score, recording_id, title, artist in resultados:
                if score > 0.1:  # Exigencia baja para que reconozca más temas
                    encontrado = True
                    titulo = title
                    artista = artist
                    
                    try:
                        mb_data = musicbrainzngs.get_recording_by_id(recording_id, includes=["releases"])
                        releases = mb_data.get('recording', {}).get('release-list', [])
                        
                        if releases:
                            release_id = releases[0]['id']
                            imagen_url = f"https://coverartarchive.org/release/{release_id}/front"
                            
                            r = requests.head(imagen_url)
                            if r.status_code != 200:
                                imagen_url = None
                    except Exception:
                        pass
                    
                    break

            # --- PARTE 3: Mostrar en pantalla ---
            st.success("Success!")
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
                    st.caption("✅ Verified by MetaBrainz")

            # --- PARTE 4: Botón de descarga actualizado ---
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

        except acoustid.NoBackendError:
            st.error("🚨 ERROR: 'fpcalc' is missing.")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            os.remove(ruta_temp)
