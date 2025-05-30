import os


API_ID: int = int(os.getenv("API_ID", '3898418'))

API_HASH: str = os.getenv("API_HASH", "5a82313211da04d63297bd4de436228c")

SESSION_STRING: str = os.getenv("SESSION_STRING", "")

OWNER_ID = [int(id.strip()) for id in os.getenv("OWNER_ID", "7822547078").split(",")]

LOG_GROUP_ID: int = int(os.getenv("LOG_GROUP_ID", '-1001747680884'))

PREFIX: str = str(".")

RPREFIX: str = str("$")


# No Need To Edit Below This

LOG_FILE_NAME: str = "YMusic.txt"
