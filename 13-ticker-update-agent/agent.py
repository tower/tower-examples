import tower
import polars as pl
import os


from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder



def get_llm():

    model_to_use = os.getenv("MODEL_TO_USE")
    inference_server_base_url = os.getenv("INFERENCE_SERVER_BASE_URL")
    temperature = 0.0 # to avoid randomness in reasoning

    if inference_server_base_url:
        return ChatOpenAI(model=model_to_use, temperature=temperature, base_url=inference_server_base_url)
    else:
        return ChatOpenAI(model=model_to_use, temperature=temperature)


def get_ticker_price(TICKER: str, PULL_DATE: str):
    """
    Gets the price for a given ticker and pull date from the database.
    Returns the price value if matching rows are found, None otherwise.
    """
    table = tower.tables("daily_ticker_data").load()
    df = table.to_polars()

    # Filter for matching ticker and date
    matching_rows = df.filter(
        (pl.col("ticker") == TICKER) & (pl.col("date") == PULL_DATE)
    ).collect()

    if matching_rows.height > 0 and "close" in matching_rows.columns:
        return matching_rows["close"][0]
    else:
        return None


# Function to check if the data for the given ticker and pull date is already available
@tool 
def check_if_ticker_data_is_already_available(PULL_DATE: str, TICKER: str) -> str:
    """
    Checks if data for ticker + pull date combination is already available in the database.
    Returns a message that indicates if the data is already available in the database.
    """

    print(f"Checking if data is available for ticker {TICKER} on date {PULL_DATE}")

    price = get_ticker_price(TICKER, PULL_DATE)
    available = price is not None

    if available:
        retmsg = f"Data for {TICKER} is ALREADY AVAILABLE. Price of {TICKER} on {PULL_DATE} is {price}. Processing for {TICKER} is COMPLETE. Move to next."
    else:
        retmsg = f"Data for {TICKER} is MISSING."
    
    return retmsg


# Function to fetch and store ticker data
@tool
def fetch_and_store_data_for_ticker_into_database(PULL_DATE: str, TICKER: str) -> str:
    """
    Fetches the ticker price from an External API and inserts data for a given ticker + pull date into the database. 
    Returns a message that indicates if the data was fetched and stored into the database.
    """

    print(f"Fetching and storing data for ticker {TICKER} on date {PULL_DATE}")
    
    app_params = {
        "PULL_DATE": str(PULL_DATE),
        "TICKERS": str(TICKER),
    }

    run = tower.run_app("write-ticker-data-to-iceberg", parameters=app_params)
    run = tower.wait_for_run(run)

    fetched = run.status_group == "successful"

    if fetched:
        price = get_ticker_price(TICKER, PULL_DATE)
        retmsg = f"Data for {TICKER} has been FETCHED. Price of {TICKER} on {PULL_DATE} is {price}. Processing for {TICKER} is COMPLETE. Move to next."
    else:
        retmsg = f"Data for {TICKER} has NOT been FETCHED. Processing for {TICKER} is INCOMPLETE. Move to next."

    return retmsg

def main():

    tools = [fetch_and_store_data_for_ticker_into_database, check_if_ticker_data_is_already_available]
    llm = get_llm()
    
    business_rules = """
        Goal: Return ticker price for every ticker in a given list while minimizing the number of external API calls.

        Instructions:
        1. You can get stock ticker price either from a database or fetch it from an external source.
        2. Getting from the database is preferred because it saves time.
        3. When you fetch from an external source, you also save it in the database and can use the result later.
        4. When you receive a list of tickers, determine the stock price one ticker after another.
        5. Once you have checked (and optionally fetched) EVERY ticker in the list, you MUST respond with "All tickers processed".
        6. Once you are done, you MUST respond with a summary of the prices of all the tickers.
        """

    system_prompt = """
        You are an agent that returns the stock ticker price for a given list of tickers on a given date. 
        Use the tools provided to you to return the ticker price.
        """ + business_rules


    # Use OpenAI tools agent prompt (works with function-calling models)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True,
        max_iterations=10,
        early_stopping_method="force",
        return_intermediate_steps=False,
        handle_parsing_errors=True)

    # Build the user prompt and action input
    user_input = os.getenv("USER_INPUT")
    user_input = user_input + "\n\n" + business_rules

    tickers, pull_date = os.getenv("TICKERS"), os.getenv("PULL_DATE")
    full_input = f"{user_input}\n\nTickers: {tickers}\nPull Date: {pull_date}"
 
    # Invoke the agent
    response = executor.invoke({"input": full_input})
    print(response)

if __name__ == "__main__":
    main()


