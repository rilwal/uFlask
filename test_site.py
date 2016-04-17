#!/usr/bin/env python3

from uflask import Flask

app = Flask()

@app.route("/")
def home():
    return """<html><head><title>Hello</title></head><body><h1>HTML PAGE YAY</h1>
    </body></html>"""

@app.route("/api/example")
def example():
    return "{'Item': ['list', 'of', 'items']}"

print(app.views)
app.run()
