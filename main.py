import os
from fastapi import FastAPI, Request, HTTPException

from services.whatsapp import WhatsAppService

app = FastAPI()

whatsapp_service = WhatsAppService()

@app.get("/home")
async def bienvenido():
    return "Whatsapp Bot is running"

@app.get("/webhook")
async def check_token(hub_verify_token: str = None, hub_challenge: str = None):
    try:
        if hub_verify_token == os.environ.get("TOKEN") and hub_challenge:
            return hub_challenge
        else:
            raise HTTPException(status_code=403, detail="Token incorrecto")
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

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
        text = await whatsapp_service.get_wpp_message(message)

        await whatsapp_service.chatbot_action(text, number, messageId, name)
        return "enviado"
    except Exception as e:
        return "no enviado " + str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
