from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-2.5-pro')

result = model.invoke('Where is the Eiffel Tower located? is it in Bangladesh?')

print(result.content)