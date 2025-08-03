import os
from pprint import pprint

from core.readers.github import ReadGithubIssue
from core.transforms.github import GithubIssueToChat

import tower
import pyarrow as pa



def save_messages_to_table(messages, repo_owner, repo, issue_number):
    """
    Save messages to a Tower table.
    
    Args:
        messages (list): List of message dictionaries with 'role' and 'content' keys
        repo_owner (str): GitHub repository owner
        repo (str): GitHub repository name
        issue_number (str): GitHub issue number
        
    Returns:
        table
    """
    # Convert messages list to PyArrow table
    data = {
        'repo_owner': [repo_owner] * len(messages),
        'repo': [repo] * len(messages),
        'issue_number': [int(issue_number)] * len(messages),
        'thread_seq': list(range(len(messages))),
        'role': [msg['role'] for msg in messages],
        'content': [msg['content'] for msg in messages]
    }
    arrow_table = pa.Table.from_pydict(data)

    # Define table schema
    table_schema = pa.schema([
        ("repo_owner", pa.string()),
        ("repo", pa.string()),
        ("issue_number", pa.int64()),
        ("thread_seq", pa.int64()),
        ("role", pa.string()),
        ("content", pa.string()),
    ])

    # Get or create table reference
    table = tower.tables("issue_threads", namespace="github").create_if_not_exists(table_schema)
    
    # Upsert data
    table = table.upsert(arrow_table, join_cols=['repo_owner','repo','issue_number','thread_seq'])
    
    stats = table.rows_affected()

    # Print upsert statistics
    print("\nApp Statistics:")
    print(f"Total issue thread messages processed: {len(messages)}")
    print(f"Inserted {stats.inserts} messages")
    print(f"Updated {stats.updates} messages")
        
    return table 



def main():

    # Get Parameters that will be passed in any Environment
    gh_repo_owner, gh_repo, gh_issue_number = os.getenv("gh_repo_owner"), os.getenv("gh_repo"), os.getenv("gh_issue_number")
    model_to_use = os.getenv("model_to_use")
    max_tokens_str = os.getenv("max_tokens")
    max_tokens = int(max_tokens_str) if max_tokens_str and max_tokens_str.strip() else None

    ###
    # Step 1: Data Retrieval: Read the issue and all comments from Github
    ###
    readitems = ReadGithubIssue()(repo_owner=gh_repo_owner, repo=gh_repo, issue_number=gh_issue_number)
    issues, comments= readitems['issues'], readitems['comments']

    ###
    # Step 2: Feature Transformation: Convert the issue and comments into a chat-like thread
    #   Each message in the chat are tagged with one of 3 roles: system, assistant, user
    #   The first message is the prompt by 'system' and instructs our LLM how to behave
    ###
    chat = GithubIssueToChat()(issues,comments)
    messages = [{"role": "system", "content": "Summarize this GitHub Issue thread and identify options for addressing the original issue! Output as markdown."}]
    messages.extend(chat)

    ###
    # Step 3: Inference: Ask the LLM to summarize the issue and provide recommendations
    #   Call the chat completion API of Ollama or HuggingFace
    ###
 
    llm = tower.llms(model_to_use)
    response = llm.complete_chat(messages)
    
    ###
    #  Step 4: Print the response and save it to a Tower table
    ###
    print("\n" + "="*80 + "\n" + "SUMMARY OF RECOMMENDATIONS FOR GITHUB ISSUE" + "\n" + "="*80)
    print(response)
    print("="*80)

    response_message = {"role": "assistant", "content":response}
    messages.append(response_message)

    table = save_messages_to_table(messages, gh_repo_owner, gh_repo, gh_issue_number)


if __name__ == "__main__":
    main()


