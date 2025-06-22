import tower
import polars as pl
import os
import json


from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langsmith import Client as LangSmithClient  # For default prompts



# Function to fetch ticker data
def get_data_for_ticker(input_str: str) -> str:

    params = json.loads(input_str)

    app_params = {
        "PULL_DATE": f"{params['PULL_DATE']}",
        "TICKERS": f"{params['TICKER']}"
    }

    print(f"Calling data write app with parameters: {app_params}")
    run = tower.run_app("write-ticker-data-to-iceberg", parameters=app_params)
    run = tower.wait_for_run(run)

    if run.status_group == "successful":
        return f"Data for ticker {params['TICKER']} on date {params['PULL_DATE']} has been downloaded and upserted into the table.\n\n" 
    else:
        return f"Data for ticker {params['TICKER']} on date {params['PULL_DATE']} has not been downloaded and upserted into the table.\n\n"



# Define LangChain Tool
get_data_for_ticker_tool = Tool(
    name="get_data_for_ticker",
    func=get_data_for_ticker,
    description="""Retrieves the data for given ticker. 
Input must be a JSON string with PULL_DATE and TICKER keys.
Example input: {"PULL_DATE": "2025-05-25", "TICKER": "AAPL"}"""
)



# Function to check if the data for the given ticker and pull date is already available
def check_ticker_data_available(input_str: str) -> str:

    params = json.loads(input_str)

    table = tower.tables("daily_ticker_data").load()

    df = table.to_polars()

    # Filter for matching ticker and date
    matching_rows = df.filter(
        (pl.col("ticker") == params["TICKER"]) & 
        (pl.col("date") == params["PULL_DATE"])
    ).collect()

    if matching_rows.height > 0:
        return f"Data already exists for ticker {params['TICKER']} on date {params['PULL_DATE']}\n\n"
    else:
        return f"No data found for ticker {params['TICKER']} on date {params['PULL_DATE']}\n\n"


# Define LangChain Tool
check_ticker_data_available_tool = Tool(
    name="check_ticker_data_available",
    func=check_ticker_data_available,
    description="""Checks if the data for given ticker and pull date is already available.
Input must be a JSON string with PULL_DATE and TICKER keys.
Example input: {"PULL_DATE": "2025-05-25", "TICKER": "AAPL"}.
If the data is available, tool returns a message saying so.
If the data is not available, tool returns a message saying so.
"""
)

def main():
    """
    Create an agent that will maintain the ticker data for the given list of tickers
    """

    tools = [get_data_for_ticker_tool, check_ticker_data_available_tool]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    lsclient = LangSmithClient()
    prompt = lsclient.pull_prompt("hwchase17/react")

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    # Build the user prompt and action input
    user_input = os.getenv("USER_INPUT")
    if not user_input:
        user_input = """
        Get the ticker data for the given pull date and the given list of tickers. 
        Get the ticker data one by one. 
        Before getting the data for each ticker, check if it is already available.
        """

    tickers, pull_date = os.getenv("TICKERS"), os.getenv("PULL_DATE")
    input_params = {"PULL_DATE": pull_date, "TICKERS": tickers}
    full_input = f"{user_input}\n\nAction Input: {json.dumps(input_params)}"
 
    # Invoke the agent
    response = executor.invoke({"input": full_input})
    print(response)

if __name__ == "__main__":
    main()


