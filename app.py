from flask import Flask, request, jsonify
from family_helper import *
from optimum_helper import *

app = Flask(__name__)


# HUBSPOT_TOKEN = 'pat-eu1-72ceb19e-51ad-41ac-825f-c1b454b1ae82'

@app.route('/hubspot_webhook', methods=['POST'])
def main():
    try:
        contact_infos = request.json
        contact_id_hubspot = contact_infos[HS_HUBSPOT_ID]  # Assuming HS_HUBSPOT_ID is defined somewhere
        print(contact_id_hubspot)
        labels = who_is_the_chef(contact_id_hubspot)
        print(f"The chief is: {contact_id_hubspot}")
        print(f"Common Association Labels: {labels}")
        deals_id_chief = get_associated_deals(labels[0][0])
        deals_details = get_deal_details(deals_id_chief[0])
        print(deals_details)

        for label in labels[1:]:
            associated_contact = label[0]
            deals_id_associated_contacts = get_associated_deals(associated_contact)
            update_deal_property(deals_id_associated_contacts[0], deals_details)
            print(f'Contact ID Updated: {associated_contact}')
            print(f'Deal ID Updated: {deals_id_associated_contacts[0]}')
            print('-' * 100)

        return jsonify({'message': 'Process completed successfully'}), 200

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/optimum_webhook', methods=['POST'])
def optimum():
    """
    Wrapper function to manage the process of finding or creating a user,
    creating a visit, and handling propositions.
    """
    try:
        contact_infos = request.json
        print(contact_infos)
        # CONTACT
        civilite = 1
        lastname = contact_infos[LASTNAME] if contact_infos[LASTNAME] else ''
        firstname = contact_infos[FIRSTNAME] if contact_infos[FIRSTNAME] else ''
        birth_date = convert_timestamp_to_date(contact_infos[BIRTH_DATE]) if contact_infos[BIRTH_DATE] else ''
        address = contact_infos[ADDRESS] if contact_infos[ADDRESS] else ''
        zip_code = contact_infos[ZIP_CODE] if contact_infos[ZIP_CODE] else ''
        city = contact_infos[CITY] if contact_infos[CITY] else ''
        email = contact_infos[EMAIL] if contact_infos[EMAIL] else ''
        phone = contact_infos[PHONE] if contact_infos[PHONE] else ''

        # VISITE

        date_prescription = '17/01/2021'
        type_prescription = 1

        # STOCK
        type_eq = contact_infos[TYPE_EQ]
        article_type_id = 3 if type_eq == LUNETTE else 1
        code_fabricant = '1331'
        code_fournisseur = '1331'
        code_article = '65d5cb69455ca'

        # DEVIS

        montant_rbsm = contact_infos[MONTANT_RBSM] if contact_infos[MONTANT_RBSM] else ''
        prix_de_vente = montant_rbsm
        lot_mouvement_id = 12325267

        client_id = get_user(lastname, firstname)
        if client_id is None:
            client_id = create_user(civilite, lastname, firstname, birth_date, address, zip_code, city, email, phone)
            print(client_id)
            if client_id is None:
                return jsonify({'error': str("Failed to get or create user.")}), 404

        visit_id = create_visit(client_id, date_prescription, type_prescription)
        if visit_id is None:
            return jsonify({'error': str("Failed to create a visit.")}), 404

        proposition = create_proposition(client_id, visit_id, article_type_id, code_fabricant, code_fournisseur,
                                         code_article,
                                         prix_de_vente, lot_mouvement_id)
        if proposition is None:
            return jsonify({'error': str("Failed to create a proposition.")}), 404

        print(f"Process completed successfully. Client ID: {client_id}, Visit ID: {visit_id}")
        offre_id = proposition.get('offre_id')  # Adjust the key based on the actual JSON structure
        print(f"Offre ID: {offre_id}")
        devis = generer_devis(client_id, offre_id, proposition)
        if devis is None:
            return jsonify({'error': str("Failed to generate a devis.")}), 404
        return jsonify({'message': f"Process completed successfully. Client ID: {client_id}, Visit ID: {visit_id}, Offre ID: {offre_id}, Devis: {devis}"}), 200
    except Exception as e:
        return jsonify({'message': f"Exception : {e}"}), 500
