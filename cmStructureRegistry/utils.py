import requests
from django.conf import settings

roman_numerals = [
        "I", "II", "III", "IV", "V",
        "VI", "VII", "VIII", "IX", "X",
        "XI", "XII", "XIII", "XIV", "XV",
        "XVI", "XVII", "XVIII", "XIX", "XX"
    ]


def get_system_api_info(system_id):
    baseUrl = settings.ESI_API_URL
    email = settings.ESI_USER_CONTACT_EMAIL
    url = f'{baseUrl}latest/universe/systems/{system_id}/'
    headers = {
        'User-Agent': email, 
        'Accept': 'application/json'
    }

    ##try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    system_data = response.json()  # Convert response to JSON
    return system_data
    #except requests.exceptions.RequestException as e:
    #    # Handle request exceptions (connection errors, timeouts, etc.)
    #    print(f"Error fetching system data: {e}")
    #    return url

def solar_system_lookup(solar_system_name):
    baseUrl = settings.ESI_API_URL
    email = settings.ESI_USER_CONTACT_EMAIL
    url = f'{baseUrl}latest/universe/ids/'
    headers = {
        'User-Agent': email,  
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    data = [solar_system_name]

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise error for bad status codes

        json = response.json()
        systems = json.get("systems", [])

        if systems and len(systems) == 1:
            return systems[0]
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def corporation_lookup(corporation_name):
    baseUrl = settings.ESI_API_URL
    email = settings.ESI_USER_CONTACT_EMAIL
    url = f'{baseUrl}latest/universe/ids/'
    headers = {
        'User-Agent': email,  # Replace with your app's user-agent
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    data = [corporation_name]

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise error for bad status codes

        json = response.json()
        corporations = json.get("corporations", [])

        if corporations and len(corporations) == 1:
            return corporations[0]
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_corporation_api_info(corporation_id):
    baseUrl = settings.ESI_API_URL
    email = settings.ESI_USER_CONTACT_EMAIL
    url = f'{baseUrl}latest/corporations/{corporation_id}'
    headers = {
        'User-Agent': email,
        'Accept': 'application/json',
    }

    ##try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    corporation_data = response.json()  # Convert response to JSON
    return corporation_data
    #except requests.exceptions.RequestException as e:
    #    # Handle request exceptions (connection errors, timeouts, etc.)
    #    print(f"Error fetching system data: {e}")
    #    return url       

def get_alliance_api_info(alliance_id):
    baseUrl = settings.ESI_API_URL
    email = settings.ESI_USER_CONTACT_EMAIL   
    url = f'{baseUrl}latest/alliances/{alliance_id}'
    headers = {
        'User-Agent': email,  # Replace with your app's user-agent
        'Accept': 'application/json',
    }

    ##try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    corporation_data = response.json()  # Convert response to JSON
    return corporation_data
    #except requests.exceptions.RequestException as e:
    #    # Handle request exceptions (connection errors, timeouts, etc.)
    #    print(f"Error fetching system data: {e}")
    #    return url


def get_roman_numeral(number):
    return roman_numerals[int(number) - 1]

