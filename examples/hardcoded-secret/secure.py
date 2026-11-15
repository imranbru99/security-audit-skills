# Safe counterpart to vulnerable.py.
# Credentials are required from the environment. They are not defaulted from source.
import os

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
BILLING_API_TOKEN = os.environ["BILLING_API_TOKEN"]
