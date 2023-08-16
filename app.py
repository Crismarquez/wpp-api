import os
from fastapi import FastAPI, Request, HTTPException

from services.whatsapp import WhatsAppService
from config.config import logger, ENV_VARIABLES

app = FastAPI()

whatsapp_service = WhatsAppService()

@app.get("/home")
async def bienvenido():
    return "Whatsapp Bot is running"

@app.get("/webhook")
async def verificar_token(request: Request):
    logger.info("Verificando token")
    if request.query_params.get('hub.mode') == "subscribe" and request.query_params.get("hub.challenge"):
        if not request.query_params.get('hub.verify_token') == os.environ.get("TOKEN"): #os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return int(request.query_params.get('hub.challenge'))
    return "Hello world", 200

@app.post("/webhook")
async def receive_messages(request: Request):
    try:
        body = await request.json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = WhatsAppService.replace_start(message['from'])
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = whatsapp_service.get_wpp_message(message)

        whatsapp_service.chatbot_action(text, number, messageId, name)
        return "enviado"
    except Exception as e:
        return "no enviado " + str(e)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
