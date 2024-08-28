# #### Import Dependencies

# This code block imports necessary libraries and modules for connecting to databases, processing data, 
# and utilizing the LangChain framework for SQL generation from natural language. It also sets up 
# environment variables and defines a function for Markdown display in Jupyter notebooks.
import os
import pandas as pd
# # import pyodbc
import logging
import sys
import re
import json
import importlib.util

from dotenv import load_dotenv
from fastapi.responses import JSONResponse

# Enable logging
# Define a custom log format
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Python Logging Levels:
# DEBUG: Detailed information, typically of interest only when diagnosing problems.
# INFO: Confirmation that things are working as expected.
# WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g., ‘disk space low’). The software is still working as expected.
# ERROR: Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL: A very serious error, indicating that the program itself may be unable to continue running.

# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG, format=log_format)
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger('langchain')

# Import the Markdown module from IPython.display
from IPython.display import Markdown, HTML, display  

# Load environment variables from the credentials.env file
env_path = os.path.join(os.path.dirname(__file__), 'credentials.env')
load_dotenv(env_path)

azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if not azure_openai_api_version:
    logger.error("Required environment variables are not set. Exiting...")
    # Return a bad status code
    raise ValueError("Please set the AZURE_OPENAI_API_VERSION environment variable in the credentials.env file.")
else:
    logger.info("AZURE_OPENAI_API_VERSION: %s", azure_openai_api_version)

# Dynamically load the prompts.py module
prompts_path = os.path.join(os.path.dirname(__file__), 'prompts.py')
spec = importlib.util.spec_from_file_location("prompts", prompts_path)
prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompts)
MSSQL_AGENT_PREFIX = prompts.MSSQL_AGENT_PREFIX

# for reading prompt file
# from sql_agent.prompts import MSSQL_AGENT_PREFIX 
# from .prompts import MSSQL_AGENT_PREFIX
# from .prompts import MSSQL_AGENT_PREFIX

# # LangChain dependencies
from langchain_openai import AzureChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain.agents import initialize_agent
# from langchain.agents import Tool
from langchain.agents import create_sql_agent  # No longer in agent_toolkits
from langchain.sql_database import SQLDatabase  # Toolkit is replaced with SQLDatabase
# from langchain.agents import AgentExecutor
# from langchain.callbacks.base import BaseCallbackHandler
# from langchain.callbacks.manager import CallbackManager
# from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import get_openai_callback
# from langchain_openai import OpenAI
from langchain.agents.conversational_chat.prompt import PREFIX, SUFFIX
# from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool

from tiktoken import encoding_for_model

# Database dependencies
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL

# Function to print comments using markdown
def printmd(string):
    display(Markdown(string))

# Flag that controls whether to show query execution steps
show_query_execution_steps = True #False #True

logger.info("##### Dependencies loaded...")
printmd(f"##### Dependencies loaded...")

###################################
# Define the SQL Flow Function
###################################
def sql_flow_function(user_prompt: str) -> str:
    """Generate an SQL query using the user prompt and predefined prefix."""

    logger.info("Entered sql_flow_function with: %s", user_prompt)
    
    # Connect to Azure SQL Database using SQLAlchemy and pyodbc. 
    # Configuration for the database connection
    db_config = {
        'drivername': 'mssql+pyodbc',
        'username': os.environ["SQL_SERVER_USERNAME"] + '@' + os.environ["SQL_SERVER_NAME"],
        'password': os.environ["SQL_SERVER_PASSWORD"],
        'host': os.environ["SQL_SERVER_NAME"],
        'port': 1433,
        'database': os.environ["SQL_SERVER_DATABASE"],
        'query': {'driver': 'ODBC Driver 17 for SQL Server'},
    }

    # Create a URL object for connecting to the database
    db_url = URL.create(**db_config)

    #####################################################
    ## Following Blocks Test the Database Connection:
    # Connect to the Azure SQL Database using the URL string
    engine = create_engine(db_url)

    # Create instance of the SQLDatabase class. 
    try:
        # Under the hood,SqlAlchemy's create_engine is used to connect to DB's URI.
        # Once connected, SqlAlchemy's MetaData and inspector object are used to intrpspect the DB's schema, 
        # extracting information about tables, columns, and relationships.
        # Using SqlAlchemy's ORM, it can map tables to Python classes and provides methods to query data, 
        # fetch results, and interact with the databae. 
        #SqlAlchemy an ORM. It's phasing out the toolkit, so we will use the SQLDatabase class instead
        db = SQLDatabase.from_uri(db_url) 
    except Exception as e:
        print(f"An error occurred while connecting to the database: {e}")
        logger.error(f"An error occurred while connecting to the database: {e}")
        raise ConnectionError("Failed to connect to the database. Please check your database configuration.") from e
    
    # Test the connection to the database by fetching the table names
    if show_query_execution_steps:
        print("SqlDatabase Object Initialized. Found following tables:")
        print(db.get_usable_table_names())

    ##### Initialize AzureOpenAI and Sql Agent
    # Initialize instance of AzureChatOpenAI 
    # llm = AzureChatOpenAI(deployment_name=os.environ["GPT35_DEPLOYMENT_NAME"], temperature=0.2, max_tokens=2000, api_version=os.environ["AZURE_OPENAI_API_VERSION"])
       
    try:
        llm = AzureChatOpenAI(
           deployment_name=os.environ["GPT35_DEPLOYMENT_NAME"],
           temperature=0.2,
           max_tokens=2000,
          api_version=os.environ["AZURE_OPENAI_API_VERSION"]
        )
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        raise EnvironmentError(f"Required environment variable {e} is not set.") from e
    except Exception as e:
        logger.error(f"An error occurred while initializing AzureChatOpenAI: {e}")
        raise RuntimeError("Failed to initialize AzureChatOpenAI.") from e
    



    # llm = AzureChatOpenAI(
    #     azure_deployment="gpt-35-turbo",  # or your deployment
    #     api_version="2023-06-01-preview",  # or your api version
    #     temperature=0,
    #     max_tokens=None,
    #     timeout=None,
    #     max_retries=2,
        
    # printmd(f"LLM Created: {llm.deployment_name}")

    # system_prompt = """
    #     You are an SQL expert with deep expertise in generating accurate and efficient SQL queries from natural language.
    #     Your goal is to understand the user's intent expressed in natural language and translate it into a correct and optimized SQL query that can be executed against the database to retrieve the desired information.
    #     DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
    #     If the question does not seem related to the database, just return "I don't know" as the answer.
    # """
    
    # SQLDatabaseToolkit is a utility for interacting with a SQL database using a language model (LLM).
    # It facilitate the integration between the database and the language model, enabling more sophisticated
    # query generation, execution, and result handling.
    # Parameters in the SQLDatabase class and the LLM.
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create the SqlAgent
    # SqlAgent interacts with directly with the SQL database. 
    # It leverages the LLM to generate SQL queries from natural language input
    # and then execute these queries on the connected database. 
    # Note how the SqlAgent leverges the SQLDatabaseToolkit and the language model (LLM). 
    try:
        agent_executor = create_sql_agent(
            prefix=MSSQL_AGENT_PREFIX,
            llm=llm,
            #prompt=full_prompt,
            temperature=0.1,
            toolkit=toolkit,
            top_k=30,
            agent_type="openai-tools",
            verbose=show_query_execution_steps, #True,
            agent_executor_kwargs={"return_intermediate_steps": True}
            # system_prompt=system_prompt
            # stream_runnble=False
        )
    except Exception as e:
        print(f"An error occurred while creating the agent_executor: {str(e)}")
        agent_executor = None  # Set agent_executor to None or handle it as needed
        raise RuntimeError("Failed to create the SQL agent executor.") from e

    #prompts = agent_executor.get_prompts
    # for key in prompts.keys():
    #     print(key)

    # Continue with the rest of your code, checking if agent_executor was created successfully
    if agent_executor:
        printmd(f"##### Langchain SqlAgent Created")
        logger.info("##### Langchain SqlAgent Created...")

    # Invoke the SQL agent with the natural language question
    # The agent will generate a SQL query based on the input question   
    # and execute the query against the connected database.
    # The response contains the query result and other relevant information.
    # The response is a dictionary with keys such as 'query', 'result', 'intermediate_steps', and 'execution_time'.
    try:
        # get_openai_callback() is a context manager that provides a callback handler for OpenAI API calls
        # It can be used to track token useage and cost for API requests and responses 
        with get_openai_callback() as cb:
            response = agent_executor.invoke(user_prompt)
    except ConnectionError as e:
        response = f"Connection error: {str(e)}"
        raise RuntimeError("Connection error occurred.") from e
    except TimeoutError as e:
        response = f"Timeout error: {str(e)}"
        raise RuntimeError("Timeout error occurred.") from e
    except ValueError as e:
        response = f"Value error: {str(e)}"
        raise RuntimeError("Value error occurred.") from e
    except RuntimeError as e:
        response = f"Runtime error: {str(e)}"
        raise
    except Exception as e:
        response = f"An unexpected error occurred: {str(e)}"
        raise RuntimeError("An unexpected error occurred.") from e

    # Advanced logging block
    # Block iterates through the intermediate steps of the response 
    # and prints the action and observation for each step.
    # This is a common pattern for displaying detailed information based on 
    # the content of data structures and conditional flag in Python
    # Importantly, the block reveals the agent's decision-making process.
    if show_query_execution_steps: 
        # Iterate through each step in the 'intermediate_steps' list from the response
        for step in response['intermediate_steps']:
            # Check if the current step is a dictionary
            if isinstance(step, dict):
                # Extract 'action' and 'observation' from the step, defaulting to empty string if not found
                action = step.get('action', '')
                observation = step.get('observation', '')

            # Check if the current step is a tuple (assumed to be a pair of action and observation)
            elif isinstance(step, tuple):
                # Unpack the tuple directly into action and observation variables
                action, observation = step 

            else:
                # Handle unexpected step types by printing a warning and skipping the current iteration
                print(f"Unexpected step type: {type(step)}")
                continue  # Skip this step if it's neither dict nor tuple

            # Print the action and observation for the current step
            print(f"Action: {action}\nObservation: {observation}\n")

            # print(f"Total Tokens: {cb.total_tokens}")
            # print(f"Prompt Tokens: {cb.prompt_tokens}")
            # print(f"Completion Tokens: {cb.completion_tokens}")
            # print(f"Total Cost (USD): ${cb.total_cost}")
            
    # else:
    #     # If the flag to show details is not set, indicate that there are no details to show
    #     print("No details to show")

    # #### Final Answer

    # try:
    #     print(f"Type of response: {type(response)}")
    #     print(f"Content of response: {response}")
    # except Exception as e:
    #     print(f"An error occurred: {e}")


    class SqlResponseModel:
        def __init__(self, Prompt: str, FinalAnswer: str, Explanation: str,
                    SqlStatement: str, PromptTokens: int, CompletionTokens: int, TotalTokens: int, TotalCost: float):
            self.Prompt = Prompt
            self.FinalAnswer = FinalAnswer
            self.SqlStatement = SqlStatement
            self.PromptTokens = PromptTokens
            self.CompletionTokens = CompletionTokens
            self.TotalTokens = TotalTokens
            self.TotalCost = TotalCost
            self.Explanation = Explanation

    try:
        # print(cb)
        print("Total Tokens: {}".format(cb.total_tokens))
        print("Prompt Tokens: {}".format(cb.prompt_tokens))
        print("Completion Tokens: {}".format(cb.completion_tokens))
        print("Total Cost (USD): {}".format(cb.total_cost))
        print()  # Insert a newline

        # Extract the 'Final Answer' from the response["output"]
        match = re.search(r'Final Answer:.*?(?=\n\n|$)', response["output"], re.DOTALL)
        final_answer = match.group(0).strip() if match else "Final Answer not found."

        # Remove the "Final Answer:" part from the response["output"]
        explanation = re.sub(r'Final Answer:.*?(?=\n\n|$)', '', response["output"], flags=re.DOTALL).strip()

        # explanation2 = re.search(r'Explanation:.*?(?=\n\n|$)', response["output"], re.DOTALL)

        print("User Prompt: {}".format(user_prompt))
        print()  # Insert a newline

        print("Final Answer: {}".format(final_answer))
        print()  # Insert a newline

        # Extract the SQL statement from the response["output"]
        sql_match = re.search(r'SELECT.*?(?=Explanation:|$)', response["output"], re.DOTALL)
        sql_statement = sql_match.group(0).strip() if sql_match else "SQL statement not found."
        print("SQL Statement: {}".format(sql_statement))
        print()  # Insert a newline

        print("Explanation: {}".format(explanation))            
        print()  # Insert a newline

        sql_response = {
            "Prompt": "User Prompt: {}".format(user_prompt),
            "FinalAnswer": "Final Answer: {}".format(final_answer),
            "SqlStatement": "SQL Statement: {}".format(sql_statement),
            "PromptTokens": "Prompt Tokens: {}".format(cb.prompt_tokens),
            "CompletionTokens": "Completion Tokens: {}".format(cb.completion_tokens),
            "TotalTokens": "Total Tokens: {}".format(cb.total_tokens),
            "TotalCost": "Total Cost (USD): {}".format(cb.total_cost),
            "Explanation": "Explanation: {}".format(explanation),
            "PromptTokensInt": cb.prompt_tokens,
            "CompletionTokensInt": cb.completion_tokens,
            "TotalCostFloat": cb.total_cost            
        }


        # sql_response = {
        #     "Prompt": user_prompt,
        #     "FinalAnswer": final_answer,
        #     "SqlStatement": sql_statement,
        #     "PromptTokens": 145,
        #     "CompletionTokens": 30,
        #     "TotalTokens": 175,
        #     "TotalCost": 0.0011749999999999998,
        #     "Explanation": explanation
        # }

        # Return the dictionary directly
        return JSONResponse(content=sql_response)

        # sql_response = {
        #     "Prompt": user_prompt,
        #     "FinalAnswer": final_answer,
        #     "SqlStatement": sql_statement,
        #     "PromptTokens": cb.prompt_tokens,
        #     "CompletionTokens": cb.completion_tokens,
        #     "TotalTokens": cb.total_tokens,
        #     "TotalCost": cb.total_cost,
        #     "Explanation": explanation
        # }

        # return sql_response

        # response_json = json.dumps(sql_response)
        # print(response_json)  # Replace this with your return statement in your web framework
        # return response_json

        # SqlResponseModel = SqlResponseModel(
        #     Prompt="User Prompt: {}".format(user_prompt),
        #     # response=response["output"],
        #     FinalAnswer="Final Answer: {}".format(final_answer),
        #     # output_without_final_answer=explanation,
        #     SqlStatement="SQL Statement: {}".format(sql_statement),
        #     PromptTokens="Prompt Tokens: {}".format(cb.prompt_tokens),
        #     CompletionTokens="Completion Tokens: {}".format(cb.completion_tokens),
        #     TotalTokens="Total Tokens: {}".format(cb.total_tokens),
        #     TotalCost="Total Cost (USD): {}".format(cb.total_cost),
        #     Explanation="Explanation: {}".format(explanation)
        # )
        # printmd(f"Complete")
        # return SqlResponseModel
    except Exception as e:
        print(f"An error occurred: {e}")
        raise RuntimeError("An error occurred while extracting the SQL statement.") from e