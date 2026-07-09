import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend import cms_helper

try:
    print("Testing CMS connection...")
    user = cms_helper.get_user_by_username("user")
    print("Result (safe repr):")
    print(ascii(user))
except Exception as e:
    import traceback
    traceback.print_exc()
