import requests

# API Configuration
BASE_URL = "http://localhost:5000/api/"


def display_menu():
    print("\n" + "=" * 50)
    print("contact_manager".center(50))
    print("=" * 50)
    print("1. Add new contact")
    print("2. Edit contact details")
    print("3. Delete contact")
    print("5. Filter by relation")
    print("6. Export contacts")
    print("7. List all contacts")
    print("8. Exit")
    print("=" * 50)


def list_contacts():
    try:
        response = requests.get(f"{BASE_URL}/contacts")
        if response.status_code != 200:
            print(f"\nError: {response.text}")
            return

        contacts = response.json()
        if not contacts:
            print("\nNo contacts found.")
            return

        print("\nContact List:")
        print("-" * 130)
        print(f"{'ID':<5}{'Name':<30}{'Phone':<15}{'Email':<20}{'Address':<20}{'Relation':<20}{'Notes':<20}")
        print("-" * 130)

        for contact in contacts:
            raw_phone = contact.get('phone', '')
            phone = str(int(float(raw_phone))) if isinstance(raw_phone, (int, float)) else str(raw_phone)
            print(
                f"{str(contact.get('id', '')):<5}"
                f"{str(contact.get('name', ''))[:30]:<30}"
                f"{phone[:15]:<15}"
                f"{str(contact.get('email', '') or '')[:20]:<50}"
                f"{str(contact.get('address', '') or '')[:20]:<30}"
                f"{str(contact.get('relation', '') or '')[:20]:<30}"
                f"{str(contact.get('notes', '') or '')[:20]:<20}"
            )
        print("-" * 130)
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def view_contact():
    contact_id = input("\nEnter contact ID: ")
    try:
        response = requests.get(f"{BASE_URL}/contacts/{contact_id}")
        if response.status_code == 200:
            contact = response.json()
            print("\n" + "-" * 50)
            print("CONTACT DETAILS".center(50))
            print("-" * 50)
            print(f"ID: {contact['id']}")
            print(f"Name: {contact['name']}")
            print(f"Phone: {contact['phone']}")
            print(f"Email: {contact.get('email', 'N/A')}")
            print(f"Address: {contact.get('address', 'N/A')}")
            print(f"Relation: {contact.get('relation', 'N/A')}")
            print(f"Notes: {contact.get('notes', 'N/A')}")
            print("-" * 50)
        elif response.status_code == 404:
            print("\nContact not found!")
        else:
            print(f"\nError: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def add_contact():
    print("\nEnter contact details:")
    name = input("Name: ")
    phone = input("Phone: ")
    email = input("Email: ")
    address = input("Address: ")
    relation = input("Relation: ")
    notes = input("Notes: ")

    if not name or not phone:
        print("\nName and phone are required!")
        return

    try:
        phone = int(phone)
    except ValueError:
        print("\nPhone must be a number!")
        return

    contact_data = {
        "name": name,
        "phone": phone,
        "email": email,
        "address": address,
        "relation": relation,
        "notes": notes
    }

    try:
        response = requests.post(f"{BASE_URL}/contacts", json=contact_data)
        if response.status_code == 201:
            print("\nContact added successfully!")
            print(f"New contact ID: {response.json()['id']}")
        else:
            print(f"\nError adding contact: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def edit_contact_details():
    contact_id = input("\nEnter contact ID to edit: ")

    try:
        response = requests.get(f"{BASE_URL}/contacts/{contact_id}")
        if response.status_code != 200:
            print(f"\nError: {response.text if response.status_code != 404 else 'Contact not found!'}")
            return

        current_contact = response.json()

        print("\nCurrent contact details:")
        for key in ['id', 'name', 'phone', 'email', 'address', 'relation', 'notes']:
            print(f"{key.capitalize()}: {current_contact.get(key, 'N/A')}")
        print("-" * 50)

        print("\nEnter new values (leave blank to keep current):")
        updates = {}
        for field in ['name', 'phone', 'email', 'address', 'relation', 'notes']:
            value = input(f"New {field}: ")
            if value:
                updates[field] = value

        if not updates:
            print("\nNo changes made!")
            return

        response = requests.put(f"{BASE_URL}/contacts/{contact_id}", json=updates)
        if response.status_code == 200:
            print("\nContact updated successfully!")
        else:
            print(f"\nError updating contact: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def delete_contact():
    contact_id = input("\nEnter contact ID to delete: ")
    confirm = input(f"Are you sure you want to delete contact {contact_id}? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    try:
        response = requests.delete(f"{BASE_URL}/contacts/{contact_id}")
        if response.status_code == 200:
            print("\nContact deleted successfully!")
        else:
            print(f"\nError deleting contact: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def search_contacts():
    search_term = input("\nEnter name to search: ")
    try:
        response = requests.get(f"{BASE_URL}/contacts/search", params={"name": search_term})
        if response.status_code == 200:
            contacts = response.json()
            if not contacts:
                print("\nNo contacts found!")
                return

            print("\n" + "-" * 130)
            print(f"{'ID':<5}{'Name':<30}{'Phone':<15}{'Email':<20}{'Address':<20}{'Relation':<20}{'Notes':<20}")
            print("-" * 130)
            for contact in contacts:
                print(
                    f"{contact['id']:<5}{contact['name']:<30}{contact['phone']:<15}"
                    f"{contact.get('email', '')[:20]:<20}{contact.get('address', '')[:20]:<20}"
                    f"{contact.get('relation', '')[:20]:<20}{contact.get('notes', '')[:20]:<20}"
                )
            print("-" * 130)
        else:
            print(f"\nError fetching contacts: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def filter_by_relation():
    relation = input("\nEnter relation to filter by: ")
    try:
        response = requests.get(f"{BASE_URL}/contacts/filter", params={"relation": relation})
        if response.status_code == 200:
            contacts = response.json()
            if not contacts:
                print("\nNo contacts found!")
                return

            print("\n" + "-" * 130)
            print(f"{'ID':<5}{'Name':<30}{'Phone':<15}{'Email':<20}{'Address':<20}{'Relation':<20}{'Notes':<20}")
            print("-" * 130)
            for contact in contacts:
                print(
                    f"{contact['id']:<5}{contact['name']:<30}{contact['phone']:<15}"
                    f"{contact.get('email', '')[:20]:<20}{contact.get('address', '')[:20]:<20}"
                    f"{contact.get('relation', '')[:20]:<20}{contact.get('notes', '')[:20]:<20}"
                )
            print("-" * 130)
        else:
            print(f"\nError fetching contacts: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def export_contacts():
    file_name = input("\nEnter file name to export contacts (e.g., contacts.json): ")
    try:
        response = requests.get(f"{BASE_URL}/contacts/export")
        if response.status_code == 200:
            with open(file_name, 'w') as file:
                file.write(response.text)
            print(f"\nContacts exported successfully to {file_name}!")
        else:
            print(f"\nError exporting contacts: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def main():
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-8): ")

        if choice == '1':
            add_contact()
        elif choice == '2':
            edit_contact_details()
        elif choice == '3':
            delete_contact()
        elif choice == '4':
            search_contacts()
        elif choice == '5':
            filter_by_relation()
        elif choice == '6':
            export_contacts()
        elif choice == '7':
            list_contacts()
        elif choice == '8':
            print("\nExiting the program. Goodbye!")
            break
        else:
            print("\nInvalid choice! Please enter a number between 1 and 8.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
