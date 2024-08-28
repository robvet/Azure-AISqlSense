import logging

# # Import the sql_flow_function from the sql_flow_service module
# from .sql_agent.sql_agent_service import sql_flow_function
# from .sql_agent.prompts import MSSQL_AGENT_PREFIX

# Use absolute imports instead of relative imports
from sql_agent.sql_agent_service import sql_flow_function
from sql_agent.prompts import MSSQL_AGENT_PREFIX


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This is a an orchestrator class. It's a design pattern used to manage and coordinate
# the flow of data and control between different components or services in an application. 
# It provides:
#   - A centralized location to manage the flow of data and control between components.
#   - A way to encapsulate complex logic and functionality into a single class.
#   - A clear separation of concerns between different parts of the application.
#   - A way to improve code readability, maintainability, and scalability.

# This function takes a natural language prompt as input and generates an SQL query.
# It leverages the nl2sql_function to perform the conversion from natural language to SQL.
# The generated SQL query is returned as a string.
def generate_sql_query(prompt: str) -> str:
    """
    Generate an SQL query based on a natural language prompt.

    Parameters:
    - prompt (str): The natural language prompt provided by the user.

    Returns:
    - str: The generated SQL query as a string.
    """

    logger.info("Entered generate_sql_query with prompt: %s", prompt)

    # Call the sql_flow_function with the provided prompt and return the result
    SqlResponse = sql_flow_function(prompt)
    logger.info("Generated SQL query: %s", SqlResponse)
    return SqlResponse
  