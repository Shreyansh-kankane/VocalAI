from langchain.text_splitter import CharacterTextSplitter
 
from langchain_community.vectorstores import Weaviate
 
from langchain_community.document_loaders import TextLoader
from langchain.prompts import ChatPromptTemplate
 
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_openai.embeddings import OpenAIEmbeddings
from fastapi import FastAPI
from langchain.text_splitter import CharacterTextSplitter
 
from langchain_community.vectorstores import Weaviate
 
from langchain_community.document_loaders import TextLoader
from langchain.prompts import ChatPromptTemplate
 
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_openai.embeddings import OpenAIEmbeddings
from fastapi import FastAPI
# import weaviate
import os
from dotenv import load_dotenv
load_dotenv()

from weaviate_client import client
 
app = FastAPI()
 
async def setup_chain(max_tokens , redo , query):
    # Load the json data to LLM
    loader = TextLoader(
        file_path = 'data.txt' ,
        autodetect_encoding= True
    )
    data = loader.load()
 
    # Chunking documents
    text_splitter = CharacterTextSplitter(chunk_size=1000 , chunk_overlap=50)
    chunks = text_splitter.split_documents(data)
 
    #  Loading these chunks to vector database
    vectorstore = Weaviate.from_documents(
        client= client,
        documents = chunks,
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
   
    template2 = """
            ###Instructions
            ROLE : You are a customer support Assistant bot to help with queries asked by customers.
            IMPORTANT : Context is your only knowledge base.Don’t answer, if the information asked or relevant information in query is not mentioned in the Context. Answer only if the information is present in provided context.Recognize the keywords in Query and provide only the asked information if present in the Context. Provide reference website links only present in Context.Keep the tone of the responses as formal.When using Technical Jargons, try to provide a short explanation for it as well in order to maintain ease of understanding.
            If information is not present in Context just apologise for the inconveniece.DO NOT provide related information.
            Follow best practices that results in structured response for clarity. For reference, you can rely on these guidelines -
            -Use bold formatting for headings to highlight key sections.
            -Describe the summary utilizing bullet points.
            -Utilize bullet points to list essential pieces of information.
            -If you provide any links, make sure they are clickable.
            ###
           
            ###Examples to understand only and not use as context
                Context : "Docker is a containerization software and helps streamline devops process. Reference [http://www.docker.com]"
                Query : "What is devops and provide links for understanding how devops work ?"
                Answer : "Information not found in knowledge-base"
               
                Context : "Chocolate Cake is made up of flour , chocolate , eggs , butter and sugar and yeast. They are easy to make and are delicious to eat. Reference [http://www.Cakes.com]"
                Query : "What are Chocolate Cakes and provide link for references ?"
                Answer : "Chocolate Cakes are made up of flour , eggs , butter and sugar and are easy to make and are delicious to eat. Reference [http://www.Cakes.com]"
            ###
       
        The answer generated for this question  using above Instruction Template was not liked by the user. Please re-generate this answer from the provided Context with more relevant information and better structure and format.
        Question: {question}
        Context : {context}
    """
   
    prompt1 = ChatPromptTemplate.from_template(template)
    prompt2 =  ChatPromptTemplate.from_template(template2)
   
    if(redo):
        prompt = prompt2
    else:
        prompt = prompt1
 
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1, max_tokens=max_tokens, streaming=True, openai_api_key=os.getenv("OPENAI_KEY"))
 
    rag_chain = (
        {"context": retriever,  "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()  
    )
 
    return rag_chain.invoke(query)
   
@app.get('/')
async def function():
    response  = await setup_chain(1000 , False ,  "Who is the CEO of Google ?")
    return response
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
