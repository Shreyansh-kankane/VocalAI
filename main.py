# from langchain.text_splitter import CharacterTextSplitter

# from langchain_community.vectorstores import Weaviate

# from langchain_community.document_loaders import TextLoader
# from langchain.prompts import ChatPromptTemplate

# from langchain_community.chat_models.openai import ChatOpenAI
# from langchain.schema.runnable import RunnablePassthrough
# from langchain.schema.output_parser import StrOutputParser
# from langchain_openai.embeddings import OpenAIEmbeddings
# from fastapi import FastAPI
# from langchain.text_splitter import CharacterTextSplitter

# from langchain_community.vectorstores import Weaviate

# from langchain_community.document_loaders import TextLoader
# from langchain.prompts import ChatPromptTemplate

# from langchain_community.chat_models.openai import ChatOpenAI
# from langchain.schema.runnable import RunnablePassthrough
# from langchain.schema.output_parser import StrOutputParser
# from langchain_openai.embeddings import OpenAIEmbeddings
# from fastapi import FastAPI
# # import weaviate
# import os
# from dotenv import load_dotenv
# load_dotenv()

# from weaviate_client import client

# app = FastAPI()

# async def setup_chain(max_tokens , query):
#     # Load the json data to LLM
#     loader = TextLoader(
#         file_path = 'data.txt' ,
#         autodetect_encoding= True
#     )
#     data = loader.load()

#     # Chunking documents
#     text_splitter = CharacterTextSplitter(chunk_size=1000 , chunk_overlap=50)
#     chunks = text_splitter.split_documents(data)

#     #  Loading these chunks to vector database
#     vectorstore = Weaviate.from_documents(
#         client= client,
#         documents = chunks,
#         embedding=OpenAIEmbeddings(api_key=os.getenv("OPENAI_KEY")),
#         by_text=False
#     )

#     retriever = vectorstore.as_retriever()

#     template = """
#         ###Instructions###
#         ROLE : You are a Chat Bot Assistant bot to help with queries asked by customers.
#         IMPORTANT : Context is your only knowledge base.Don’t answer, if the information asked or relevant information in query is not mentioned in the Context. Answer only if the information is present in provided context.Recognize the keywords in Query and provide only the asked information if present in the Context. Provide reference website links only present in Context.Keep the tone of the responses as formal.When using Technical Jargons, try to provide a short explanation for it as well in order to maintain ease of understanding.
#         If information is not present in Context just provide an apologise for not providing an answer in a format "I'm sorry I could not find a suitable response. If you have any other questions or need assistance with anything else, please feel free to ask.". DO NOT provide related information.
#         Follow best practices that results in structured response for clarity. For reference, you can rely on these guidelines -
#         -Use bold formatting for headings to highlight key sections.
#         -Describe the summary utilizing bullet points.
#         -Utilize bullet points to list essential pieces of information.
#         -If you provide any links, make sure they are clickable.
       
#         ###Examples to understand only and not use as context
#             Context : "Docker is a containerization software and helps streamline devops process. Reference [http://www.docker.com]"
#             Query : "What is devops and provide links for understanding how devops work ?"
#             Answer : "Information not found in knowledge-base"
           
#             Context : "Chocolate Cake is made up of flour , chocolate , eggs , butter and sugar and yeast. They are easy to make and are delicious to eat. Reference [http://www.Cakes.com]"
#             Query : "What are Chocolate Cakes and provide link for references ?"
#             Answer : "Chocolate Cakes are made up of flour , eggs , butter and sugar and are easy to make and are delicious to eat. Reference [http://www.Cakes.com]"
#         ###
       
       
#         ###Information###
#         Context : {context}
#         Question : {question}
       
#     """
 
#     prompt = ChatPromptTemplate.from_template(template)


#     llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1 , max_tokens=max_tokens ,
#                      openai_api_key=os.getenv("OPENAI_KEY")
#     )

#     rag_chain = (
#         {"context": retriever,  "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()  
#     )

#     return rag_chain.invoke(query)

# @app.get('/')
# async def function():
#     response  = await setup_chain(1000 ,"Who is the CEO of Google ?")
#     return response

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import asyncio
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Weaviate
from langchain_community.document_loaders import TextLoader
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_openai.embeddings import OpenAIEmbeddings
from weaviate_client import client
import time
import requests

load_dotenv()

app = FastAPI()
rag_chain = None

class Query(BaseModel):
    question: str

@app.on_event("startup")
async def startup_event():
    global rag_chain
    rag_chain = await initialize_chain()

async def initialize_chain():
    # Load the json data to LLM
    loader = TextLoader(
        file_path='data.txt',
        autodetect_encoding=True
    )
    data = loader.load()

    # Chunking documents
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunks = text_splitter.split_documents(data)

    # Loading these chunks to vector database
    vectorstore = Weaviate.from_documents(
        client=client,
        documents=chunks,
        embedding=OpenAIEmbeddings(api_key=os.getenv("OPENAI_KEY")),
        by_text=False
    )

    retriever = vectorstore.as_retriever()

    template = """
        ###Instructions###
        ROLE : You are a Chat Bot Assistant bot to help with queries asked by customers.
        IMPORTANT : Context is your only knowledge base.Don’t answer, if the information asked or relevant information in query is not mentioned in the Context. Answer only if the information is present in provided context.Recognize the keywords in Query and provide only the asked information if present in the Context. Provide reference website links only present in Context.Keep the tone of the responses as formal.When using Technical Jargons, try to provide a short explanation for it as well in order to maintain ease of understanding.
        If information is not present in Context just provide an apologise for not providing an answer in a format "I'm sorry I could not find a suitable response. If you have any other questions or need assistance with anything else, please feel free to ask.". DO NOT provide related information.
        Follow best practices that results in structured response for clarity. For reference, you can rely on these guidelines -
        -Use bold formatting for headings to highlight key sections.
        -Describe the summary utilizing bullet points.
        -Utilize bullet points to list essential pieces of information.
        -If you provide any links, make sure they are clickable.
       
        ###Examples to understand only and not use as context
            Context : "Docker is a containerization software and helps streamline devops process. Reference [http://www.docker.com]"
            Query : "What is devops and provide links for understanding how devops work ?"
            Answer : "Information not found in knowledge-base"
           
            Context : "Chocolate Cake is made up of flour , chocolate , eggs , butter and sugar and yeast. They are easy to make and are delicious to eat. Reference [http://www.Cakes.com]"
            Query : "What are Chocolate Cakes and provide link for references ?"
            Answer : "Chocolate Cakes are made up of flour , eggs , butter and sugar and are easy to make and are delicious to eat. Reference [http://www.Cakes.com]"
        ###
       
       
        ###Information###
        Context : {context}
        Question : {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1, max_tokens=1000,
                     openai_api_key=os.getenv("OPENAI_KEY"))

    rag_chain = (
        {"context": retriever,  "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

@app.post('/query')
async def query_chain(query: Query):
    global rag_chain
    print(query.question)
    st = time.time()
    response = rag_chain.invoke(query.question)
    dg_tts(response)
    end = time.time()
    response = response.replace("\n", " ")
    response = response + " Time taken to transcribe: " + str(end-st)
    return response

def dg_tts(response):
# Define the API endpoint
   url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
# Set your Deepgram API key
   api_key = "146803b865c9c2ea49f6a2f67d599431242d4b8e"
# Define the headers
   headers = {
       "Authorization": f"Token {api_key}",
       "Content-Type": "application/json"
   }
# Define the payload
   payload = {
       "text": response
   }
# Make the POST request
   response_tts = requests.post(url, headers=headers, json=payload)

# Check if the request was successful
   if response_tts.status_code == 200:
   # Save the response content to a file
       with open("audio.mp3", "wb") as f:
           f.write(response_tts.content)
       print("File saved successfully.")
   else:
       print(f"Error: {response_tts.status_code} - {response_tts.text}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

