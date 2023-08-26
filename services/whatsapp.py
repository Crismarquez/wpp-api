import os
import time
import json
from typing import Tuple, Union
import asyncio
import requests

import httpx

from services.speechtext import WhisperClass
from services.utils import manage_download, convertir_ogg_a_mp3
from config.config import stickers, logger

class WhatsAppService:
    def __init__(self):
        self.whatsapp_token = os.environ.get("WHATSAPP_TOKEN")
        self.whatsapp_url = os.environ.get("WHATSAPP_URL")
        self.sqlchatbot_endpoint = os.environ.get("AI_ENDPOINT")

        self.transcriber = WhisperClass("whisper-1")

    def get_wpp_message(self, message: dict) -> str:
        if 'type' not in message :
            text = 'mensaje no reconocido'
            return text
        typeMessage = message['type']
        if typeMessage == 'text':
            text = message['text']['body']
        elif typeMessage == 'button':
            text = message['button']['text']
        elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
            text = message['interactive']['list_reply']['title']
        elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
            text = message['interactive']['button_reply']['title']
        elif typeMessage== 'audio':
            logger.info("audio message")
            logger.info(message)
            download_path = manage_download(message['audio']['id'], message['from'], "audio")
            if isinstance(download_path, tuple):
                logger.info("no se pudo descargar el audio")
                text = f"Informa al usuario que no se pudo descargar el audio, el error interno es : {download_path[1]}"
            # else:
            #     text = f"Informa al usuario que el id del audio es: {message['audio']['id']}"
            else:
                if download_path.exists():
                    audio_file = open(str(download_path), "rb")
                    text = self.transcriber.transcribe(audio_file)
                    if text == "":
                        text = f"Informa al usuario que no se pudo transcribir el audio id: {message['audio']['id']}"
                else:
                    text = f"Informa al usuario que no se pudo transcribir el audio en la ruta {download_path}"
        else:
            text = 'mensaje no procesado'
        
        return text

    def send_wpp_message(self, data: str) -> Tuple[str, int]:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.whatsapp_token}'
        }
        response = requests.post(self.whatsapp_url, 
                                        headers=headers, 
                                        data=data)
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code

    def chatbot_action(self, text: str, number: str, messageId: str, name: str):
        text = text.lower() #mensaje que envio el usuario
        list = []
        print("mensaje del usuario: ",text)

        markRead = self.mark_read_message(messageId)
        list.append(markRead)
        time.sleep(2)

        conversation_payload = {
            "celphone": number,
            "message": text,
            "history": [
                {"role": "user", "content": text}
            ]
        }

        response = requests.post(self.sqlchatbot_endpoint, json=conversation_payload)
        logger.info(f"SQLChatbot response: {response.status_code}")
            
        # Asegúrate de manejar posibles errores en la respuesta.
        if response.status_code == 200:
            response_data = response.json()
            # Aquí, supongo que la respuesta contiene un campo 'content' con el mensaje del asistente.
            # Ajusta según la estructura real de tu respuesta.
            assistant_reply = response_data.get("answer", "No tengo una respuesta para eso.")
        else:
            assistant_reply = "Lo siento, no pude obtener una respuesta en este momento."


        data = self.text_message(number, assistant_reply)
        list.append(data)

        for item in list:
            self.send_wpp_message(item)

    def text_message(self, number: str, text: str) -> str:
        data = json.dumps(
                {
                    "messaging_product": "whatsapp",    
                    "recipient_type": "individual",
                    "to": number,
                    "type": "text",
                    "text": {
                        "body": text
                    }
                }
        )
        return data

    def button_reply_message(self, number: str, options: list, body: str, footer: str, sedd: str, messageId: str) -> str:
        ...
        buttons = []
        for i, option in enumerate(options):
            buttons.append(
                {
                    "type": "reply",
                    "reply": {
                        "id": sedd + "_btn_" + str(i+1),
                        "title": option
                    }
                }
            )
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": body
                    },
                    "footer": {
                        "text": footer
                    },
                    "action": {
                        "buttons": buttons
                    }
                }
            }
        )
        return data
    
    def list_reply_message(self, number: str, options: list, body: str, footer: str, sedd: str, messageId: str) -> str:
        rows = []
        for i, option in enumerate(options):
            rows.append(
                {
                    "id": sedd + "_row_" + str(i+1),
                    "title": option,
                    "description": ""
                }
            )

        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {
                        "text": body
                    },
                    "footer": {
                        "text": footer
                    },
                    "action": {
                        "button": "Ver Opciones",
                        "sections": [
                            {
                                "title": "Secciones",
                                "rows": rows
                            }
                        ]
                    }
                }
            }
        )
        return data

    def document_message(self, number: str, url: str, caption: str, filename: str) -> str:
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "document",
                "document": {
                    "link": url,
                    "caption": caption,
                    "filename": filename
                }
            }
        )
        return data

    def sticker_message(self, number: str, sticker_id: str) -> str:
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "sticker",
                "sticker": {
                    "id": sticker_id
                }
            }
        )
        return data

    def get_media_id(self, media_name: str, media_type: str) -> Union[str, None]:
        media_id = ""
        if media_type == "sticker":
            media_id = stickers.get(media_name, None)
        #elif media_type == "image":
        #    media_id = sett.images.get(media_name, None)
        #elif media_type == "video":
        #    media_id = sett.videos.get(media_name, None)
        #elif media_type == "audio":
        #    media_id = sett.audio.get(media_name, None)
        return media_id

    def reply_reaction_message(self, number: str, messageId: str, emoji: str) -> str:
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "reaction",
                "reaction": {
                    "message_id": messageId,
                    "emoji": emoji
                }
            }
        )
        return data

    def reply_text_Message(self, number: str, messageId: str, text: str) -> str:
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "context": { "message_id": messageId },
                "type": "text",
                "text": {
                    "body": text
                }
            }
        )
        return data

    def mark_read_message(self, messageId: str) -> str:
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id":  messageId
            }
        )
        return data

    @staticmethod
    def replace_start(s: str) -> str:
        if s.startswith("521"):
            return "52" + s[3:]
        else:
            return s


# def administrar_chatbot(text,number, messageId, name):
#     text = text.lower() #mensaje que envio el usuario
#     list = []
#     print("mensaje del usuario: ",text)

#     markRead = markRead_Message(messageId)
#     list.append(markRead)
#     time.sleep(2)

#     if "hola" in text:
#         body = "¡Hola! 👋 Bienvenido a Bigdateros. ¿Cómo podemos ayudarte hoy?"
#         footer = "Equipo Bigdateros"
#         options = ["✅ servicios", "📅 agendar cita"]

#         replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
#         replyReaction = replyReaction_Message(number, messageId, "🫡")
#         list.append(replyReaction)
#         list.append(replyButtonData)
#     elif "servicios" in text:
#         body = "Tenemos varias áreas de consulta para elegir. ¿Cuál de estos servicios te gustaría explorar?"
#         footer = "Equipo Bigdateros"
#         options = ["Analítica Avanzada", "Migración Cloud", "Inteligencia de Negocio"]

#         listReplyData = listReply_Message(number, options, body, footer, "sed2",messageId)
#         sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

#         list.append(listReplyData)
#         list.append(sticker)
#     elif "inteligencia de negocio" in text:
#         body = "Buenísima elección. ¿Te gustaría que te enviara un documento PDF con una introducción a nuestros métodos de Inteligencia de Negocio?"
#         footer = "Equipo Bigdateros"
#         options = ["✅ Sí, envía el PDF.", "⛔ No, gracias"]

#         replyButtonData = buttonReply_Message(number, options, body, footer, "sed3",messageId)
#         list.append(replyButtonData)
#     elif "sí, envía el pdf" in text:
#         sticker = sticker_Message(number, get_media_id("pelfet", "sticker"))
#         textMessage = text_Message(number,"Genial, por favor espera un momento.")

#         enviar_Mensaje_whatsapp(sticker)
#         enviar_Mensaje_whatsapp(textMessage)
#         time.sleep(3)

#         document = document_Message(number, sett.document_url, "Listo 👍🏻", "Inteligencia de Negocio.pdf")
#         enviar_Mensaje_whatsapp(document)
#         time.sleep(3)

#         body = "¿Te gustaría programar una reunión con uno de nuestros especialistas para discutir estos servicios más a fondo?"
#         footer = "Equipo Bigdateros"
#         options = ["✅ Sí, agenda reunión", "No, gracias." ]

#         replyButtonData = buttonReply_Message(number, options, body, footer, "sed4",messageId)
#         list.append(replyButtonData)
#     elif "sí, agenda reunión" in text :
#         body = "Estupendo. Por favor, selecciona una fecha y hora para la reunión:"
#         footer = "Equipo Bigdateros"
#         options = ["📅 10: mañana 10:00 AM", "📅 7 de junio, 2:00 PM", "📅 8 de junio, 4:00 PM"]

#         listReply = listReply_Message(number, options, body, footer, "sed5",messageId)
#         list.append(listReply)
#     elif "7 de junio, 2:00 pm" in text:
#         body = "Excelente, has seleccionado la reunión para el 7 de junio a las 2:00 PM. Te enviaré un recordatorio un día antes. ¿Necesitas ayuda con algo más hoy?"
#         footer = "Equipo Bigdateros"
#         options = ["✅ Sí, por favor", "❌ No, gracias."]


#         buttonReply = buttonReply_Message(number, options, body, footer, "sed6",messageId)
#         list.append(buttonReply)
#     elif "no, gracias." in text:
#         textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tienes más preguntas. Recuerda que también ofrecemos material gratuito para la comunidad. ¡Hasta luego! 😊")
#         list.append(textMessage)
#     else :
#         data = text_Message(number,"Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?")
#         list.append(data)

#     for item in list:
#         enviar_Mensaje_whatsapp(item)