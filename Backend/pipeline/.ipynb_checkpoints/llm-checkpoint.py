from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

#load environment variables from .env file
load_dotenv()

# Handles initialization of the groq LLM.
class LLMManager:

    def __init__(self):

		# to initialize llama 3.3 model via groq api
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )

	#return LLM instance
    def get_llm(self):

        return self.llm