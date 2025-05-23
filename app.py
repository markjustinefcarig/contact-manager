from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(contacts)

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Missing required fields (name, email)'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO contacts (name, email, phone, relation, notes, address) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                data['name'], 
                data['email'], 
                data.get('phone', None), 
                data.get('relation', None),  
                data.get('notes', None),
                data.get('address', None)
            )
        )
        connection.commit()
        contact_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({
            'id': contact_id,
            'name': data['name'],
            'email': data['email'],
            'phone': data.get('phone'),
            'address': data.get('address'),
            'relation': data.get('relation'), 
            'notes': data.get('notes'),
        }), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:id>', methods=['GET'])
def get_contact(id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (id,))
    contact = cursor.fetchone()
    cursor.close()
    connection.close()

    if not contact:
        return jsonify({'error': 'Contact not found'}), 404

    return jsonify(contact)

@app.route('/api/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        updates = []
        values = []
        if 'name' in data:
            updates.append("name = %s")
            values.append(data['name'])
        if 'email' in data:
            updates.append("email = %s")
            values.append(data['email'])
        if 'phone' in data:
            updates.append("phone = %s")
            values.append(data['phone'])
        if 'address' in data:
            updates.append("address = %s")
            values.append(data['address'])    
        if 'relation' in data:  
            updates.append("relation = %s")
            values.append(data['relation'])
        if 'notes' in data:
            updates.append("notes = %s")
            values.append(data['notes'])

        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400

        query = f"UPDATE contacts SET {', '.join(updates)} WHERE id = %s"
        values.append(id)
        cursor.execute(query, tuple(values))

        if cursor.rowcount == 0:
            return jsonify({'error': 'Contact not found'}), 404

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Contact updated successfully'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = %s", (id,))

        if cursor.rowcount == 0:
            return jsonify({'error': 'Contact not found'}), 404

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Contact deleted successfully'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/filter', methods=['GET'])
def filter_by_relation():
    relation = request.args.get('relation')  # Get the relation query parameter

    if not relation:
        return jsonify({'error': 'Relation parameter is required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contacts WHERE relation LIKE %s", (f'%{relation}%',))  # Filter by relation
    contacts = cursor.fetchall()
    cursor.close()
    connection.close()

    if not contacts:
        return jsonify({'message': 'No contacts found with the specified relation'}), 404

    return jsonify(contacts), 200

@app.route('/api/contacts/export', methods=['GET'])
def export_contacts():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM contacts")
        contacts = cursor.fetchall()
        cursor.close()
        connection.close()

        if not contacts:
            return jsonify({'error': 'No contacts available to export'}), 404

        import json
        contacts_json = json.dumps(contacts, default=str)

        return app.response_class(
            contacts_json,
            mimetype='application/json',
            headers={"Content-Disposition": "attachment;filename=contacts.json"}
        )

    except Error as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
