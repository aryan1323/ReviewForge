from pydantic import BaseModel


class GitHubUser(BaseModel):
    login: str


class GitHubRepo(BaseModel):
    id: int
    full_name: str


class GitHubPRHead(BaseModel):
    sha: str
    ref: str


class GitHubPRBase(BaseModel):
    ref: str


class GitHubPullRequest(BaseModel):
    id: int
    number: int
    title: str
    user: GitHubUser
    base: GitHubPRBase
    head: GitHubPRHead
    diff_url: str
    html_url: str
    state: str
    created_at: str


class GitHubWebhookPayload(BaseModel):
    action: str
    pull_request: GitHubPullRequest
    repository: GitHubRepo
    sender: GitHubUser
