from magic_numbers import *
import requests
import os
import hubspot


HUBSPOT_ACCESS_TOKEN = os.environ.get('HUBSPOT_TOKEN')
client = hubspot.Client.create(access_token=HUBSPOT_ACCESS_TOKEN)
hubspot_headers = {'Authorization': f'Bearer {HUBSPOT_ACCESS_TOKEN}'}

def who_is_the_chef(contact_id):
    endpoint_url = f"https://api.hubapi.com/crm/v4/objects/contacts/{contact_id}/associations/contacts"
    response = requests.get(endpoint_url, headers=hubspot_headers)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve associations: {response.text}")

    members = []
    results = response.json().get('results', [])

    for result in results:
        contact_id_2 = result['toObjectId']
        types = result['associationTypes']

        for assoc in types:
            if assoc['category'] == 'USER_DEFINED':
                label = assoc['label']
                ayant_droit = (contact_id_2, 'Chef de famille' if label != 'Ayant droit' else 'Ayant droit')
                chef = (contact_id, 'Chef de famille' if label == 'Ayant droit' else 'Ayant droit')

                if members:
                    members.append(ayant_droit)
                else:
                    members.extend([chef, ayant_droit])

    return members


def get_associated_deals(contact_id):
    endpoint_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/deals"
    response = requests.get(endpoint_url, headers=hubspot_headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve deals: {response.text}")
    return [deal['id'] for deal in response.json().get('results', [])]


def get_deal_details(deal_id):
    endpoint_url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    params = {
        'properties': ','.join(PROPERTY_NAME)  # Request all properties
    }
    response = requests.get(endpoint_url, headers=hubspot_headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve deal details: {response.text}")

    deal_data = response.json().get('properties', {})
    if deal_data['pipeline'] == '256106182':
        # Filter out properties that don't have a value or their value is 0
        deal_details = {key: value for key, value in deal_data.items() if
                        value is not None and (not isinstance(value, (int, float)) or value > 0)}
    else:
        deal_details = 'Pas de pipeline Vente Optique'

    return deal_details


def update_deal_property(deal_id, deal_details):
    endpoint_url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    data = {
        "properties": deal_details
    }

    response = requests.patch(endpoint_url, headers=hubspot_headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to update deal: {response.text}")
