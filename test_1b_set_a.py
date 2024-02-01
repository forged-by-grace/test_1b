# This import modules
import textract
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec 
from config import OPENAI_API_KEY, PINECONE_API_KEY
import logging


# Load env variables
load_dotenv()

# Embedding model
MODEL = "text-embedding-ada-002"

# Initialize client
client = OpenAI(api_key=OPENAI_API_KEY) 

def create_embedding(chunk):
    # create embeddings
    res = client.embeddings.create(input=chunk, model=MODEL)
    embeds = [record['embedding'] for record in res['data']]

    return embeds


def get_embedding(query):
    return client.embeddings.create(input=query, model=MODEL)['data'][0]['embedding']


def init_pinecone():     
    pc = Pinecone(
        api_key=PINECONE_API_KEY    
    )

    # Now do stuff
    if 'openai' not in pc.list_indexes().names():   
        pc.create_index(
            name='openai',
            dimension=1536,
            metric='euclidean',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-west-2'
            )
        )
    
    # connect to index
    index = pc.Index('openai')

    return index
    

#Function to split long documents in to smaller parts
def split_text_into_chunks(plain_text, max_chars=2000):
    text_chunks = []
    current_chunk = ""
   
    # decode plain_text
    texts = plain_text.decode()

    for line in texts.split("\n"):
        if len(current_chunk) + len(line) + 1 <= max_chars:
            current_chunk += line + " "
        else:
            text_chunks.append(current_chunk.strip())
            current_chunk = line + " "
    if current_chunk:
        text_chunks.append(current_chunk.strip())
    return text_chunks


def addData(corpusData):
    index = init_pinecone()
    id  = index.describe_index_stats()['total_vector_count']
    for i in range(len(corpusData)):
        # Get a chunk
        chunk=corpusData[i]

        # Create embeddings
        embeds = create_embedding(chunk=chunk)
        
        # prep metadata
        chunkInfo=(str(id+i), embeds, {'context': chunk}) #In metadata we are storing the original text here as context. 
        
        # Upset batch
        index.upsert(vectors=[chunkInfo])


#This function is responsible for matching the input string with alread existing data on vector database.
def find_match(query,k=2): 
    # Init pinecone
    index = init_pinecone()  

    # Get embeddings 
    embbeds = get_embedding(query=query)

    # Query vector db
    res = index.query([embbeds], top_k=k, include_metadata=True)
    
    # Return context from response
    return [res['matches'][i]['metadata']['context'] for i in range(k)]


def create_prompt(context,query):
    #Todo: Should be generated with the context/contexts we find by doing semantaic search
    prompt = f"Using the context '{context}', {query}"
    return prompt
    

def generate_answer(prompt):     
    try:        
        # Make request
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": prompt}]
        )

        # Return response
        return response.choices[0].message.content
    except Exception as err:
        logging.error(f"Unable to get response from gpt due to error: {err}")
        return None


def user_query(query):    
    
    # Check vector db to return a context
    contexts = find_match(query)

    # Create prompts based on the query and context
    prompts = [create_prompt(context, query) for context in contexts]

    # Generate responses
    answers = [generate_answer(prompt=prompt) for prompt in prompts]

    # Return the response
    return answers


def upload_texts_to_vector_db():
    # Task 1: Read text from docx
    texts = textract.process ("./DataLaw.docx")

    # Task 2: Split data
    text_chunks = split_text_into_chunks(texts)

    # Task 3: Add data to vector db
    addData(text_chunks)

# This function adds texts to the vector database
upload_texts_to_vector_db()

user_query("How can I do this?")