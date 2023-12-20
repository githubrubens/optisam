from flask import Flask, request, jsonify
from magic_numbers import *
import os
import hubspot


HUBSPOT_ACCESS_TOKEN = "pat-eu1-33f2be59-2212-44d1-828e-bdb6be1adbb5"
app = Flask(__name__)
client = hubspot.Client.create(access_token=HUBSPOT_ACCESS_TOKEN)
hubspot_headers = {'Authorization': f'Bearer {HUBSPOT_ACCESS_TOKEN}'}


#######################################################################################
# ------------------------------ >> OPTISAM << ---------------------------------
#######################################################################################


@app.route('/sales_automation', methods=['POST'])
def hubspot_endpoint():
    contact_infos = request.json
    contact_id = contact_infos[INFO_ID]
    print(contact_id)



if __name__ == "__main__":
    app.run()
