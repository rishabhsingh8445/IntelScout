import os

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DISABLE_SCHEDULER", "1")
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
