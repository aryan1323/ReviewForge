import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def sample_diff() -> str:
    return """\
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,6 +10,12 @@ def login(username, password):
     user = db.query(User).filter_by(username=username).first()
-    if user.password == password:
+    if user.password == password:  # BUG: plain text password comparison
         return generate_token(user)
+
+def admin_panel(user_id):
+    # No authorization check!
+    query = f\"SELECT * FROM users WHERE id = {user_id}\"
+    return db.execute(query)
"""


@pytest.fixture
def mock_openai_response():
    mock = MagicMock()
    mock.choices = [
        MagicMock(
            message=MagicMock(
                content='{"summary": "Found security issues.", "overall_severity": "critical", "issues": [{"file_path": "src/auth.py", "line_number": 13, "category": "security", "severity": "critical", "message": "SQL injection vulnerability", "suggestion": "Use parameterized queries"}]}'
            )
        )
    ]
    mock.usage = MagicMock(prompt_tokens=500, completion_tokens=150)
    return mock


@pytest.fixture
def webhook_payload() -> dict:
    return {
        "action": "opened",
        "pull_request": {
            "id": 12345,
            "number": 42,
            "title": "Add auth feature",
            "user": {"login": "dev-user"},
            "base": {"ref": "main"},
            "head": {"ref": "feature/auth", "sha": "abc123def456"},
            "diff_url": "https://github.com/owner/repo/pull/42.diff",
            "html_url": "https://github.com/owner/repo/pull/42",
            "state": "open",
            "created_at": "2024-01-15T10:00:00Z",
        },
        "repository": {"id": 99999, "full_name": "owner/repo"},
        "sender": {"login": "dev-user"},
    }
