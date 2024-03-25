import requests
import json
import datetime
import os

# Define the base URL and the endpoint
base_url_test = "https://demo.livebyoptimum.com/api"
OPTIMUM_TOKEN_TEST = os.environ.get('OPTIMUM_TOKEN_TEST')
headers_test = {
    "X-API-KEY": OPTIMUM_TOKEN_TEST,
    "Content-Type": "application/json"  # Assuming JSON payload
}

def get_user(lastname, firstname):
    """
    Searches for a specific user and returns the user ID.
    """
    endpoint_search = f'/clients/?nom={lastname}&prenom={firstname}'
    url = base_url_test + endpoint_search
    try:
        response = requests.get(url, headers=headers_test)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx or 5xx
        clients = response.json()
        if not clients:
            return None
        return clients[0]['client_id']
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def create_user(civilite, lastname, firstname, birth_date, address, zip_code, city, email, phone):
    """
    Creates a new user and returns the user ID.
    """
    endpoint = "/clients"
    url = base_url_test + endpoint
    client_data = {
        "civilite_type": civilite,
        "nom": lastname,
        "prenom": firstname,
        "date_naissance": birth_date,
        "ligne_1": address,
        "code_postal": zip_code,
        "ville": city,
        "email": email,
        "telephone_portable": phone
    }
    print(client_data)
    try:
        response = requests.post(url, headers=headers_test,
                                 json=client_data)  # Use json= to automatically set content-type
        response.raise_for_status()
        print("Client created successfully.")
        return response.json()[0]['client_id']
    except Exception as e:
        print(f"Failed to create client: {e}")
        return None


def create_visit(client_id, date_prescription, type_prescription):
    """
    Creates a visit for the specified user.
    """
    endpoint_create_visit = f'/clients/{client_id}/visites/'
    url_visit = base_url_test + endpoint_create_visit
    client_visit = {
        'date_prescription': date_prescription,
        'type_prescription': type_prescription
    }
    try:
        response_visit = requests.post(url_visit, headers=headers_test, json=client_visit)
        response_visit.raise_for_status()
        print("Visit created successfully.")
        return response_visit.json()['visite_id']
    except Exception as e:
        print(f"Failed to create visit: {e}")
        return None


def create_proposition(client_id, visit_id, article_type_id, code_fabricant, code_fournisseur, code_article,
                       prix_de_vente, lot_mouvement_id):
    """
    Creates a proposition for the specified visit of a user.
    """
    endpoint_proposition = f'/clients/{client_id}/visites/{visit_id}/offres'
    url_create_prop = base_url_test + endpoint_proposition
    client_proposition = {
        'articles_stock': [{
            'article_type_id': article_type_id,
            'code_fabricant': code_fabricant,
            'code_fournisseur': code_fournisseur,
            'code_article': code_article,
            'prix_de_vente': prix_de_vente,
            'lot_mouvement_id': lot_mouvement_id
        }]
    }
    try:
        response_prop = requests.post(url_create_prop, headers=headers_test, json=client_proposition)
        print("Proposition created successfully.")
        return response_prop.json()
    except Exception as e:
        print(f"Failed to create proposition: {e}")
        return None


def generer_devis(client_id, offre_id, proposition_data):
    """
    Generates a devis based on the proposition data.
    """
    endpoint_devis = f'/clients/{client_id}/offres/{offre_id}/proposition2devis'
    url_devis = base_url_test + endpoint_devis
    try:
        # Make the PUT request using the proposition data
        response = requests.put(url_devis, headers=headers_test, data=json.dumps(proposition_data))
        response.raise_for_status()  # This will raise an error for HTTP error responses
        print("Devis generated successfully.")
        return response.json()  # Assuming the response contains JSON data
    except Exception as e:
        print(f"Failed to generate devis: {e}")
        return None


def convert_timestamp_to_date(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp_sec = timestamp_ms / 1000
    # Convert timestamp to datetime object
    date_obj = datetime.datetime.utcfromtimestamp(timestamp_sec)
    # Format datetime object as required
    formatted_date = date_obj.strftime('%d/%m/%Y')
    return formatted_date
