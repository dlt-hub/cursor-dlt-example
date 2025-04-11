This repository contains an example of Cursor rules and LLM-friendly docs that you can use for building REST API sources with Cursor.

Useful prompts (make sure the right docs and rules are added)

- First prompt:
"Please build a REST API (dlthub) pipeline using the details from {documentation name you added in context}. Please include all endpoints you find and try to capture the incremental logic you can find. Use the build rest api cursor rule."

Recovery:
- "Here's a docs snippet {}"