# utils/agents.py

from crewai import Agent, Crew, Task
from langchain_openai import ChatOpenAI
from composio_langchain import App, ComposioToolSet

def create_agents(openai_api_key):
    # Initialize the language model with OpenAI API key and model name
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_api_key)

    # Setup tools using ComposioToolSet
    composio_toolset = ComposioToolSet()
    tools = composio_toolset.get_tools(apps=[App.SERPAPI])

    # Define the Investment Researcher agent
    researcher = Agent(
        role="Investment Researcher",
        goal=(
            "Use SERP to research the top 2 results based on the input "
            "given to you and provide a report"
        ),
        backstory=(
            "You are an expert Investment researcher. Using the information "
            "given to you, conduct comprehensive research using various sources "
            "and provide a detailed report. Don't pass in location as an "
            "argument to the tool."
        ),
        verbose=True,
        allow_delegation=True,
        llm=llm,
    )

    # Define the Investment Analyst agent
    analyser = Agent(
        role="Investment Analyst",
        goal=(
            "Analyse the stock based on information available to it, use all the tools"
        ),
        backstory=(
            "You are an expert Investment Analyst. You research on the given "
            "topic and analyse your research for insights. Note: Do not use "
            "SERP when you're writing the report."
        ),
        verbose=True,
        llm=llm,
    )

    # Define the Investment Recommendation agent
    recommend = Agent(
        role="Investment Recommendation",
        goal="Based on the analyst insights, you offer recommendations",
        backstory=(
            "You are an expert Investment Recommender. You understand "
            "the analyst insights and with your expertise suggest and offer "
            "advice on whether to invest or not. List the Pros and Cons as "
            "bullet points."
        ),
        verbose=True,
        llm=llm,
    )
    
    return researcher, analyser, recommend

def create_investment_crew(user_input, openai_api_key):
    researcher, analyser, recommend = create_agents(openai_api_key)
    
    analyst_task = Task(
        description=f"Research and analyze {user_input}",
        agent=analyser,
        expected_output="A comprehensive analysis and investment recommendation.",
        tools=None,  # Adjust if specific tools are needed by the analyst
    )

    investment_crew = Crew(
        agents=[researcher, analyser, recommend],
        tasks=[analyst_task],
        verbose=1,
    )
    
    return investment_crew
