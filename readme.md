# Azure AISqlSense (Text-to-SQL) Service

### What is it?

An agent for generating Sql Queries from Natural Language. You configure that service to go against your database. You expose a chat app to your users. They make a request to see specific data. The service (1) transforms that request to a SQL Query and (2) executes it against the database. 

We use the SqlAgent feature from the Langchain framework which is considered one of the best agents for these operations. 

### Key Features

- Powered by LangChain: Built on top of the open-source LangChain framework, specifically using the SQL Agent feature.
- Azure Integration: Requires Azure OpenAI and Azure SQL Database for seamless integration with your data infrastructure.

    > [!NOTE]
    > The service consumes Azure Open AI and Azure SQL Database, but could easily be adapted for other environments.

- Development Flexibility: Compatible with both VS Code and PyCharm as development environments.

### Getting Started

1. Run the Jupyter Notebook:
   - Navigate to the `notebook folder`.
   - Run the code using Jupyter Notebook in either VS Code or PyCharm.
2. Explore the Source Code:
   - Navigate to the `src folder` for a full version of the source code, which can be run as an API.
3. Explore Source Code for connecting to Microsoft Fabric:
   - Navigate to the `Fabric folder` for source code that will go against Microsoft Fabric as a data source.

### Acknowledgments

Big thanks to `Pablo Marin` from Microsoft! We utilized parts of his work from the [GPT-Azure-Search-Engine](https://github.com/pablomarin/GPT-Azure-Search-Engine) repository. His repo offers a comprehensive set of examples for leveraging data and OpenAI—definitely worth checking out.

## License
MIT License
