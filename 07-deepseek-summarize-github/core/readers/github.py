from core.readers.dlt import Read
import dlt
from dlt.sources.helpers import requests
from typing import Any, Dict, Optional, List


class ReadGithub(Read):

    def __init__(self, actionname:str = None):
        super().__init__(actionname)

    def fetch_github_data(self, base_github_url, suburl, params={}):
        """Fetch data from GitHub API based on endpoint and params."""
        url = f"{base_github_url}/{suburl}"

        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()
            yield response.json()

            # Get next page
            if "next" not in response.links:
                break
            url = response.links["next"]["url"]

    @dlt.source
    def github_source(self, base_github_url, entityspecs):

        def project_fields(doc: Dict, keep_fields: Optional[List[str]] = None) -> Dict:
            #out = {k:doc[k] for k in keep_fields if k in doc}
            out = {}
            for k in keep_fields:
                if k in doc:
                    out[k]=doc[k]
            return out


        for e in entityspecs:
            entity = e["entity"]

            params = e.get("params",{})
            if "per_page" not in params:
                params["per_page"] = 100

            # TODO investigate why the last fields value gets passed to all dlt resources
            # created in this loop in this statement .add_map(lambda doc: project_fields(doc, fields))
            fields = e["fields"]

            suburl = e.get("suburl",entity)

            yield dlt.resource(
                self.fetch_github_data(base_github_url, suburl, params),
                name=entity,
                write_disposition="merge",
                primary_key="id",
            ).add_map(lambda doc: project_fields(doc, fields))

    def build_entityspec(self,
                         entity : str,
                         state : str = None,
                         issue_number : str = None) -> Dict:
        out = {}
        params = {}
        suburl = None

        out["entity"] = entity

        if entity == "issues":
            out["fields"] = ['id', 'url', 'title', 'issue_url', 'author_association', 'body', 'user']
            if state is not None:
                params["state"] = state
            if issue_number is not None:
                suburl = f"issues/{issue_number}"
        elif entity == "comments":
            out["fields"] = ['id', 'url', 'title', 'issue_url', 'author_association', 'body', 'user']
            if issue_number is not None:
                suburl = f"issues/{issue_number}/comments"

        if params:
            out["params"] = params

        if suburl is not None:
            out["suburl"] = suburl

        return out

    def do(self, base_github_url, endpoints, *args:Any, **kwargs: Any):
            # sso 3/9/25
            source = self.github_source(self, base_github_url=base_github_url, entityspecs=endpoints)
            super().do(source, *args, **kwargs )


class ReadGithubIssue(ReadGithub):

    def do(self, repo_owner, repo, issue_number, *args:Any, **kwargs: Any):
        base_github_url = f"https://api.github.com/repos/{repo_owner}/{repo}"
        issues_endpoint = self.build_entityspec(entity="issues", issue_number=issue_number)
        comments_endpoint = self.build_entityspec(entity="comments", issue_number=issue_number)
        endpoints = [issues_endpoint,comments_endpoint]
        super().do(base_github_url, endpoints, *args, **kwargs)

