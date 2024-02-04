from seatable_api import Base, context
import requests
from enum import Enum

class Platform(Enum):
    feishu = 1
    wecom = 2
    dingtalk = 3

def decide_platform(webhook):
    if "feishu" in webhook:
        return Platform.feishu
    assert 0

def feishu_handler(webhook: str, content: str) -> None:
    r = requests.post(
        webhook,
        json = {
            "msg_type": "interactive",
            "card": {
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content
                    }
                ]
            }
        }
    )

    return r.json()

# ================ Auth ================
base = Base(context.api_token, context.server_url)
base.auth()

# ================ Load & update buffer ================

# ================ Danger Zone Starts ================
rows = base.list_rows("Buffer")
rows = [row for row in rows if row.get("Content") is not None]
rows.sort(key = lambda row: row["_mtime"])
target_row = rows[0]

base.update_row("Buffer", target_row["_id"], {"Name": None, "Content": None})
# ================ Danger Zone Ends ================

name = target_row.get("Name")
content = target_row.get("Content")

# ================ Load mapping ================

default_, *others = base.list_rows("Mapping")

webhook = None

if name is None:
    # no name argument => sends to default webhook
    webhook = default_.get("Webhook")
else:
    for item in others:
        if item.get("Name") == name:
            webhook = item.get("Webhook")
            break
    if webhook is None:
        webhook = default_.get("Webhook")

platform = decide_platform(webhook)

handler = {
    Platform.feishu: feishu_handler
}[platform]

ret = handler(webhook, content)

print(ret)