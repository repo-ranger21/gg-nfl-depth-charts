from dotenv import load_dotenv
import os

# load nano.env from workspace root
load_dotenv(os.path.join(os.path.dirname(__file__), "nano.env"))

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
# filled-in default Database ID (can be overridden by nano.env or environment)
DATABASE_ID = os.getenv("DATABASE_ID", "f1dabed3429f4f1bafcc55cab695bd65")