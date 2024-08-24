import json
import dicts
import requests
from random import randrange

# to simulate storage variables
clients = []

# Delay in seconds to send message to client
def random_delay():
    return randrange(1, 20)


# Add a tag to client number
def add_tag(num):
    # @todo: create a function to add tags called 'Jhony' to numbers
    return num


# get headers from request har file
def get_headers():
    # read HAR file
    with open("request.har", "r") as file:
        har_data = json.load(file)

    # extract headers
    har_headers = har_data["log"]["entries"][0]["request"]["headers"]

    # get important headers
    res = dicts.headers
    for header in har_headers:
        if header["name"] == "User-Agent":
            res["User-Agent"] = header["value"]

        if header["name"] == "Accept":
            res["Accept"] = header["value"]

    if res["User-Agent"] == "" or res["Accept"] == "":
        raise NameError('Missing Important Headers!')

    return res


# get cookies from request har file
def get_cookies():
    # read HAR file
    with open("request.har", "r") as file:
        har_data = json.load(file)

    # extract cookies
    har_cookies = har_data["log"]["entries"][0]["request"]["cookies"]

    # get important cookies
    res = dicts.cookies
    for cookie in har_cookies:
        if cookie["name"] == "session_id":
            res["session_id"] = cookie["value"]

        if cookie["name"] == "cactk":
            res["cactk"] = cookie["value"]

    if res["session_id"] == "" or res["cactk"] == "":
        raise NameError('Missing Important Cookies!')

    return res


# Get number of current client id
def get_number(id):
    # @todo: create a function to requests numbers of current id
    return id


# search clients and save their numbers in a simple database
def get_clients():
    cookies = get_cookies()
    headers = get_headers()
    link = "https://www.catho.com.br/curriculos/busca/?q=vendas&pais_id=31&estado_id[-1]=-1&regiaoId[-1]=-1&cidade_id[-1]=-1&zona_id[-1]=-1&page=1&onde_buscar=todo_curriculo&como_buscar=todas_palavras&tipoBusca=busca_palavra_chave&idade[1]=1&empregado=false&dataAtualizacao=30&buscaLogSentencePai=111e5bd0-8cee-4ed4-8ff3-51f9669f13f3"
    response = requests.get(link, cookies=cookies, headers=headers)
    print(response.status_code)
    print(response.content)
    # get_number("")
    # @todo: this should get id of clients
    # @todo: and get numbers of ids


# send messages to all users in the database
# database with numbers should exist
def send_messages():
    add_tag("")
    # @todo: create a function to send messages
    # @> messages need be send in random times between 1s and 20s


def main():
    get_clients()
    # @info: should send messages from json database
    send_messages()


if __name__ == "__main__":
    main()
