"""Keep automated tests deterministic and independent of external model services."""

import os


os.environ["MODEL_BACKEND"] = "local"
os.environ["MODEL_API_URL"] = ""
os.environ["MODEL_API_KEY"] = ""
