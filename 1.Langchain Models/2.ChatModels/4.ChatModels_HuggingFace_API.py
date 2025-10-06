import os
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load API key
load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")

# Your model
repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Step 1: Create base LLM from langchain_huggingface (not langchain_community)
base_llm = HuggingFaceEndpoint(repo_id=repo_id,huggingfacehub_api_token=api_key,temperature=0.7,max_new_tokens=256) 

# Step 2: Wrap it into ChatHuggingFace
llm = ChatHuggingFace(llm=base_llm)

# Step 3: Prompt
prompt = PromptTemplate(input_variables=["question"],template="You are a helpful AI assistant. Answer the following question:\n\n{question}",)

# Step 4: LLM Chain
chain = LLMChain(prompt=prompt, llm=llm)

# Step 5: Run test
response = chain.run("Explain LangChain integration with Hugging Face in simple terms.")
print(response)