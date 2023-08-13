## **Project Name:** 
### Integrated Intelligent Responses System via WhatsApp

## **General Description:** 
This project is designed to provide high-quality automated responses to users through WhatsApp, leveraging Artificial Intelligence. It consists of a modular architecture that integrates FastAPI as the main server, the WhatsApp API for messaging interaction, and connects to another backend that utilizes LLMs (Language Models) for AI-driven responses.

## **Main Components:**

1. **API with FastAPI:** 
   * FastAPI acts as the central core of our architecture, receiving and processing incoming requests from WhatsApp.
   * It is responsible for triggering events, processing data, and coordinating responses between WhatsApp and the AI backend.
   * Thanks to its asynchronous design, FastAPI ensures rapid responses and efficient handling of multiple simultaneous requests.

2. **WhatsApp API:** 
   * Allows for direct interaction with users through the WhatsApp messaging platform.
   * It receives messages from users and forwards them to FastAPI for processing.
   * Once a response is generated, whether immediately or through the AI backend, it sends it back to the user via WhatsApp.

3. **AI Backend with LLMs:**
   * This is an independent system that uses Language Models (LLMs) to generate contextually relevant responses based on user queries.
   * FastAPI sends user queries to this backend and awaits a response.
   * Once the response is generated, it's sent back to FastAPI for further dispatching via WhatsApp.

## **Workflow:**

1. A user sends a message through WhatsApp.
2. The WhatsApp API receives the message and forwards it to the FastAPI server.
3. FastAPI processes the message and, if needed, sends it to the AI backend for a response.
4. The AI backend analyzes the message using LLMs and generates an appropriate response.
5. The response is sent back to FastAPI.
6. FastAPI, through the WhatsApp API, sends the response back to the user.

## **Benefits:**

* **Quality Responses:** With the integration of LLMs, the system can provide high-quality and contextually relevant answers to user queries.
* **Familiar Interface:** By using WhatsApp as the interaction platform, a familiar interface to millions of users is leveraged, making adoption and usage easier.
* **Scalability:** The combination of FastAPI and its asynchronous architecture ensures the system can handle a large number of simultaneous requests.


## System requirements
python >= 3.9

## Clone repo
<pre>
git clone https://github.com/Crismarquez/wpp-api.git
cd wpp-api
</pre> 

## Virtual enviroment
<pre>
python3 -m venv .venv
source .venv/bin/activate
</pre> 

## Install dependencies
<pre>
python3 -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
export PYTHONPATH="${PYTHONPATH}:${PWD}"
</pre> 

## Run local API
Be sure to configure a .env file with secrets keys and database credentials, you can check example.env to explore the correct name of variables.

<pre>
uvicorn app:app --host 0.0.0.0 --port 5000
</pre> 


**you can use auto-docs for interact with the api**

<pre>
http://0.0.0.0:5000/docs or http://localhost:5000/docs
</pre> 