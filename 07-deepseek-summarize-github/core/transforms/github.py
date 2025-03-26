from typing import Any, List
from core.actions import Action

class GithubIssueToChat(Action):

    def __init__(self, actionname: str = None):
        super().__init__(actionname)

    def do(self, issues:List, comments:List, *args:Any, **kwargs: Any) -> List:

        issue_body = issues[0]['body']
        issue_author = issues[0]['user']['login']
        messages = []


        messages.append({"role": "user", "content": issue_body})
        for comment in comments:
            author_association = comment['author_association']
            comment_author = comment['user']['login']
            if author_association == 'COLLABORATOR' and issue_author != comment_author:
                role = 'assistant'
            else:
                role = 'user'
            comment_body = comment['body']
            messages.append({"role": role, "content": comment_body})

        return messages

