import json
import urllib.request
from typing import List

from ..core.db import SessionLocal
from ..users import repository as user_repo


EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def send_expo_push_notifications(tokens: List[str], title: str, body: str) -> None:
    """Send push notifications via Expo's free push notification service."""
    if not tokens:
        return
        
    messages = []
    for token in tokens:
        messages.append({
            "to": token,
            "sound": "default",
            "title": title,
            "body": body,
        })
        
    req = urllib.request.Request(
        EXPO_PUSH_URL,
        data=json.dumps(messages).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Accept-encoding": "gzip, deflate",
            "Content-Type": "application/json",
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            response.read()  # just to consume the response
    except Exception as e:
        print(f"Failed to send push notifications: {e}")


def send_daily_reminder_to_all() -> None:
    """Scheduled job to remind users to read their daily paper."""
    db = SessionLocal()
    try:
        users = user_repo.get_all_users(db)
        
        tokens = [u.push_token for u in users if u.push_token]
        if not tokens:
            print("No push tokens registered yet. Skipping notifications.")
            return
            
        send_expo_push_notifications(
            tokens=tokens,
            title="🔬 Daily AI Paper Ready!",
            body="A new trending AI paper has been summarized. Open the app to read it and keep your streak alive!"
        )
        print(f"Sent daily reminders to {len(tokens)} devices.")
    finally:
        db.close()
