import os
from pathlib import Path
import shutil
import requests
from pydub import AudioSegment

from config.config import media_types

def manage_download(media_id, number, message):
    media_info = get_media_info(media_id)
    if isinstance(media_info, tuple):
        return media_info
    media_url = media_info['url']
    # mime_type = media_info['mime_type']

    ext = "mp3"
    root = Path.cwd()
    directory = Path(root / f"media/{number}/{ext}")
    # delete_media_dir(directory)

    directory.mkdir(parents=True, exist_ok=True)

    file_name = "audio" + "." + ext
    file_path = Path(directory, file_name)

    download_result = download(media_url, file_path)
    if isinstance(download_result, tuple):
        return download_result
    else:
        return file_path

def get_media_info(media_id):
    url_media = f"https://graph.facebook.com/v17.0/{media_id}/"
    headers = {"Authorization": f"Bearer {os.environ.get('WHATSAPP_TOKEN')}"}

    try:
        response = requests.get(url_media, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Http Error:", err)
        return ("error", err)
    except Exception as err:
        print("Other error:", err)
        return ("error", err)
    return response.json()
    
def delete_media_dir(directory):
    if not os.path.exists(directory):
        return

    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path) 
        except Exception as e:
            print(e)

def download(url, file_path):
    headers = {"Authorization": f"Bearer {os.environ.get('WHATSAPP_TOKEN')}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Http Error:", err)
        return ("error", err)
    except Exception as err:
        print("Other error:", err)
        return ("error", err)

    with open(file_path, "wb") as f:
        f.write(response.content)
        f.close()
    return response.content


def convertir_ogg_a_mp3(archivo_ogg, archivo_mp3):
    # Cargamos el archivo OGG
    audio = AudioSegment.from_file(archivo_ogg)
    
    # Convertimos a MP3 (o M4A si lo prefieres)
    audio.export(archivo_mp3, format="mp3")