import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure with API key from environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Make sure this matches your .env variable name

# To actually see the models, you need to convert the generator to a list
models = list(genai.list_models())
print(models)