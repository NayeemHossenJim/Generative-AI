from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

model = ChatAnthropic(model='claude-3-5-sonnet-20241022',temperature=1.2,max_tokens_to_sample=10)

result = model.invoke('Lets try to know each other better. What is your name?')

print(result.content)