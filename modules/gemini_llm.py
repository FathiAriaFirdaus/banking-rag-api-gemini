from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_CONFIG

class GeminiLLM:
    def __init__(self):
        self.model = None

    def setup(self):
        """
        This functiun setup llm using gemini API key and model name as input,
        then setup the llm and return it as self.model
        """

        # Setup Gemini API
        api_key = GEMINI_CONFIG['api_key']

        # Check API
        if api_key == 'your gemini api here':
            raise ValueError("please set your gemini apu in config")
        
        # Configure API key and model
        try:
            self.model = ChatGoogleGenerativeAI(
                model=GEMINI_CONFIG['model'],
                google_api_key=api_key,
                temperature=GEMINI_CONFIG['temperature'],
                max_output_tokens=GEMINI_CONFIG['max_tokens']
            )

            print('Gemini LLM (Langchain) Ready')
            return self.model
        except Exception as e:
            print(f"Error saat setup Gemini LLM: {e}")
            raise

    
    def ask(self, prompt):
        # Check if model exist
        if self.model is None:
            self.setup()

        # Create content
        try:
            response = self.model.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
        