from flask import Flask
import mutant_client

app = Flask(__name__)


@app.route('/')
def hello():
    return(str(mutant_client.fetch_new_labels()))