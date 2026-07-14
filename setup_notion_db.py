import os
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables from .env
load_dotenv()

notion_token = os.environ.get("NOTION_TOKEN")
database_id = os.environ.get("NOTION_DATABASE_ID")

if not notion_token or not database_id:
    print("Error: NOTION_TOKEN or NOTION_DATABASE_ID is missing in .env")
    exit(1)

client = Client(auth=notion_token)

print(f"Connecting to Notion to update database: {database_id}...")

try:
    # Update the database to add the required properties
    client.databases.update(
        database_id=database_id,
        properties={
            # "Title" is typically the default Name property in Notion, 
            # we must rename whatever the title property currently is to "Title"
            "Title": {"title": {}},
            "Methods": {"rich_text": {}},
            "Experiments": {"rich_text": {}},
            "Limitations": {"rich_text": {}},
            "Summary": {"rich_text": {}}
        }
    )
    print("✅ Success! Your Notion database has been updated with the correct columns.")
except Exception as e:
    print(f"❌ Failed to update database: {e}")
