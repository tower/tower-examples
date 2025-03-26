
from core.readers.github import ReadGithubIssue

from core.inference.huggingface import InferWithHuggingfaceHub
from core.inference.ollama import InferWithOllamaChat
from core.transforms.github import GithubIssueToChat
from core.writers.dlt import WriteFile
import os

from pprint import pprint


# Get Parameters that will be passed in any Environment
gh_repo_owner = os.getenv("gh_repo_owner")
gh_repo = os.getenv("gh_repo")
gh_issue_number = os.getenv("gh_issue_number")

out_last_response_bucket_url = os.getenv("out_last_response_bucket_url")
out_full_chat_bucket_url = os.getenv("out_full_chat_bucket_url")

model_to_use = os.getenv("model_to_use")


# Create a Github reader action that will read from Github and store in memory (readitems attributes of the class)
# This reader will read the main issue and all comments for a specific issue number
read_issue = ReadGithubIssue()
read_issue(repo_owner=gh_repo_owner, repo=gh_repo, issue_number=gh_issue_number)
issues= read_issue.readitems['issues']
comments = read_issue.readitems['comments']

# Start building inputs into an LLM. Issues and comments get converted into a chat-like thread
# Each message in the chat are tagged with one of 3 roles: system, assistant, user
# The first message is by 'system' and instructs our LLM how to behave
messages = []
messages.append({"role": "system", "content": "Summarize this GitHub Issue thread and identify options for addressing the original issue! Output as markdown."})

# Now convert all comments from Github that we read earlier
convert_gh_issue = GithubIssueToChat()
chat = convert_gh_issue(issues=issues,comments = comments)
messages.extend(chat)

# Use local inference when the app is run locally
# Use a serverless inference provider when the app is run in Tower cloud
tower_env = os.getenv("TOWER_ENVIRONMENT")
tower_env = "local" if tower_env is None or tower_env == "" else tower_env

if tower_env == "local":
    # Use Ollama for local inference using Apple GPUs
    infer_with_ollama = InferWithOllamaChat()
    response = infer_with_ollama(model="deepseek-r1:14b", messages=messages)
else:
    # Get the Huggingface token (a Tower Secret)
    HF_TOKEN = os.getenv("HF_TOKEN")
    inference_provider = os.getenv("inference_provider") 
    max_tokens = os.getenv("max_tokens") # this parameter is relevant for external providers who charge by the token
    max_tokens = int(max_tokens) if max_tokens else 1000
    
    # Use HuggingFace Hub to route inference calls to inference prividers when executed in Tower cloud 
    infer_with_hf_hub = InferWithHuggingfaceHub(provider=inference_provider,api_key=HF_TOKEN)
    response = infer_with_hf_hub(inputs=messages, model=model_to_use, max_tokens=max_tokens)


# Format and print the response
print("\n" + "="*80 + "\n" + "SUMMARY OF RECOMMENDATIONS FOR GITHUB ISSUE" + "\n" + "="*80)
print(response)
print("="*80)


# Start preparing outputs.
response_message = {"role": "assistant", "content":response}
#response_message = {**response_message, **nsfw_score}
messages.append(response_message)

# Write the last response and the full chat to local files
write_last_response = WriteFile(
    "github_bot", bucket_url=out_last_response_bucket_url)
write_last_response([response_message],loader_file_format="jsonl")

write_full_chat = WriteFile(
    "github_bot", bucket_url=out_full_chat_bucket_url)
write_full_chat(messages,loader_file_format="jsonl")


