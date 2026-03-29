import os
from dotenv import load_dotenv

load_dotenv()

kill_session_updater_thread = False

USERNAME = os.environ.get("TB_USERNAME", "")
PASSWORD = os.environ.get("TB_PASSWORD", "")
device_access_token = os.environ.get("TB_DEVICE_ACCESS_TOKEN", "")
device_id = os.environ.get("TB_DEVICE_ID", "")
url = os.environ.get("TB_SERVER_URL", "localhost:8080")
