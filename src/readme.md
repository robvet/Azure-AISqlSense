# Azure AISqlSense (Text-to-SQL) Service

Azure AISqlSense is an agent designed to generate SQL queries from natural language (text). It’s built on top of the SQL Agent feature from the open-source LangChain framework.

### Contents

- `main.py`: Creates a FastAPI API to handle incoming requests and defines an endpoint for generating SQL queries based on user prompts.

- `orchestration_service.py`: Orchestrates the flow of data and control between different components and services in the application.

- `sql_agent\sql_agent_service.py`: Converts natural language prompts into SQL queries, handles the processing and execution of these queries, and returns the results to the user.

- `sql_agent\prompts.py`: Contains system prompts that define persona and directives on how to process user inputs, guiding the application in generating appropriate responses or actions.

- `sql_agent\credentials.env`: Stores secrets and sensitive information required for the service.

### How Do I Run It?

To run the engine locally as an API:

1. Install Dependencies:
        - Install the necessary Python FastAPI packages:
        ```bash
        pip install fastapi uvicorn
        ```
2. Navigate to the `src` folder:
    - Change directory to the `src` folder.

3. Start the FastAPI Server:
    - From the command line, run the following command:
        ```bash
        uvicorn main:app --reload
        ```
   - You should see the following in your terminal: 
        ```plantext
        **INFO**: Started server process.
        **INFO**: Waiting for application startup.
        **INFO**: Application startup complete.
        ```
    > [!NOTE]
    > At this point, the Fast API Server is running.

4. Test the API:
   - Open to your favorite `API Client Tool` (PostMan, Insomnia, Thunderclient) and make an HTTP POST request to:
        ```json
        Service URI: http://127.0.0.1:8000/generate-sql/
        Service HTTP Verb: POST
        HTTP Body:  {
	        "prompt": "what is the most popular menu item?"
        }
        ```

   - When complete, you should receive an HTTP status code of 200 and a JSON object that deserializes into the following model class:

        ```charp
        public class SqlResponseModel
        {
            public string Prompt { get; set; }
            public string FinalAnswer { get; set; }
            public string SqlStatement { get; set; }
            public string PromptTokens { get; set; }
            public string CompletionTokens { get; set; }
            public string TotalTokens { get; set; }
            public string TotalCost { get; set; }
            public string Explanation { get; set; }
            public string PromptTokensInt { get; set; }
            public string CompletionTokensInt { get; set; }
            public string TotalCostFloat { get; set; }
        }
        ```

    

### Secrts and Connection Information

In the `credentials.env`, file you'll need to define secrets and configuration for both Azure OpenAI and that for Azure SqlDatabase:

# Azure OpenAI Secrets
```plaintext
AZURE_OPENAI_ENDPOINT="< URL for Azure OpenAI service>/"
AZURE_OPENAI_API_KEY="< Azure OpenAI Key>"
GPT4_DEPLOYMENT_NAME="< Name of your Model Deployment >"
GPT35_DEPLOYMENT_NAME="< Name of your Model Deployment >"
```

# Azure SqlDatabase Secrets
```plaintext
SQL_SERVER_NAME="< xxxxxxxxxxx.database.windows.net >"  
SQL_SERVER_DATABASE="< Name of Sql Database >"
SQL_SERVER_USERNAME="< UserName >"
SQL_SERVER_PASSWORD="< Password >"
```

## License
MIT License

