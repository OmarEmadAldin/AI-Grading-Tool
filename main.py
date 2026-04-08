import uvicorn
from api.api import app
import os
# from dotenv import load_dotenv

if __name__ == "__main__":
    # load_dotenv()  # Load environment variables from .env file

    uvicorn.run(app, host="localhost", port=8000)
  