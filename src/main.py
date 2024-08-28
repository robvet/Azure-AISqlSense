import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import the generate_sql_query function using an absolute import
from orchestration_service import generate_sql_query


# from fastapi import FastAPI
# from pydantic import BaseModel
# from .orchestration_service import generate_sql_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cardinal rule: Keep the endpoint logic separate from the FastAPI application instance.
# Use this class only to define the FastAPI application instance and the endpoints and receive requests.

# Creates instance of FastAPI class and assigns it to the variable app.
# App is the entry point for this app. It handles all incoming requests
# and routes them to the appropriate endpoint.
app = FastAPI()

# Set up a local model class entitled UserPrompt using Pydantic, a library 
# that helps ensure the data is correct and follows the specified format.
# You're passing an object that contains a string attribute, rather than 
# just a native string value. This approach provides several benefits:
#   Validation: Automatically validates the data to ensure it conforms to the specified format.
#   Clarity: Makes the data type explicit and clear, improving code readability and maintainability.
#   Extensibility: Add more attributes to the request body in the future, without changing 
#   the endpoint's signature.
class UserPrompt(BaseModel):
    # The model has a single attribute 'prompt' which is a string
    prompt: str


# # Define a POST endpoint at the path "/generate-sql/"
# @app.post("/generate-sql/")
# def generate_sql(user_prompt: UserPrompt):
@app.post("/generate-sql/")
def generate_sql(user_prompt: UserPrompt):
    """
    Generate SQL query based on user prompt.
    Parameters:
    - user_prompt (UserPrompt): The user prompt provided in the request body as a JSON object.
    Returns:
    - dict: A JSON response containing the generated SQL query.
    """
    logger.info("Entered generate_sql endpoint with user_prompt: %s", user_prompt)



    try:
        # Call the generate_sql_query function with the prompt from the request body
        SqlResponse = generate_sql_query(user_prompt.prompt)
        logger.info("Generated SQL query: %s", SqlResponse)
        # Return the generated SQL query in a JSON response
        return {"SqlResponse": SqlResponse}
    except ValueError as e:
        logger.error("ValueError in generate_sql: %s", str(e))
        # If a ValueError occurs, return a 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Exception in generate_sql: %s", str(e))
        # For all other exceptions, return a 500 Internal Server Error
    #     raise HTTPException(status_code=500, detail=str(e))

    @app.on_event("shutdown")
    async def shutdown_event():
        print("Application shutdown")

    @app.on_event("startup")
    async def startup_event():
        print("Application startup")

    # try:
    #     # Call the generate_sql_query function with the prompt from the request body
    #     sql_query = generate_sql_query(user_prompt.prompt)
    #     logger.info("Generated SQL query: %s", sql_query)
    #     # Return the generated SQL query in a JSON response
    #     return {"sql_query": sql_query}
    # except ValueError as e:
    #     logger.error("ValueError in generate_sql: %s", str(e))
    #     # If a ValueError occurs, return a 400 Bad Request
    #     raise HTTPException(status_code=400, detail=str(e))
    # except Exception as e:
    #     logger.error("Exception in generate_sql: %s", str(e))
    #     # For all other exceptions, return a 500 Internal Server Error
    #     raise HTTPException(status_code=500, detail=str(e))
   
# The following code is the entry point of the FastAPI application. It ensures that the application
# runs only when the script is executed directly, not when it is imported as a module in another script.
# This is achieved by checking if __name__ is equal to "__main__", which is a special variable in Python
# that is set to "__main__" when the script is run directly.
if __name__ == "__main__":
    # Import the uvicorn module, which is an ASGI server implementation for running FastAPI applications
    import uvicorn
    
    # Log the startup message
    logger.info("Starting FastAPI application with uvicorn...")

    # Run the FastAPI application using uvicorn
    # - `app` is the FastAPI instance defined earlier in the script
    # - `host="0.0.0.0"` makes the server accessible externally, not just from localhost
    # - `port=8000` specifies the port on which the server will listen for incoming requests
    uvicorn.run(app, host="0.0.0.0", port=8000)

     # Log the shutdown message
    logger.info("FastAPI application has been started.")