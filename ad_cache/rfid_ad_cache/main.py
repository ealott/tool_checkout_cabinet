import json
import sys

with open('response.json') as f:
  data = json.load(f)

sys.getsizeof(data)