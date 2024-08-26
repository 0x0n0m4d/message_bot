import re
import json
import time
import dicts
import requests
from random import randrange
from tqdm import tqdm

# to simulate storage variables
clients = []

# Add a tag to client number
def add_tag(num):
    # @todo: create a function to add tags called 'Jhony' to numbers
    return num


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


def get_ids(link, cookies, headers):
    response = requests.get(link, cookies=cookies, headers=headers, timeout=10)
    time.sleep(3)
    filter = '<script id="__NEXT_DATA__" type="application/json">[^>]+'
    frame = re.search(filter, response.text)
    formated = frame.group(0).replace('<script id="__NEXT_DATA__" type="application/json">', '')
    formated = formated.replace('</script', '')
    return json.loads(formated)


# Get number of current client id
def get_number(link, cv_id, usr_id, hash):
    cookies = get_cookies()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": link,
        "x-auth-token": cookies["cactk"]
    }
    link = "https://www.catho.com.br/curriculos/api/resumes/" + str(cv_id) + "/candidate/" + str(usr_id) + "/phones/" + hash
    res = requests.get(link, cookies=cookies, headers=headers)
    time.sleep(3)
    return json.loads(res.text)["phones"][0]


# search clients and save their numbers in a simple database
def get_clients():
    cookies = get_cookies()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    print("\x1b[34m[󰀖] Gathering clients data!!!\x1b[0m")
    for page in tqdm(range(1, 1000)):
        link = "https://www.catho.com.br/curriculos/busca/?q=vendas&pais_id=31&estado_id[25]=25&regiaoId[-1]=-1&cidade_id[783]=783&zona_id[-1]=-1&page="+ str(page) +"&onde_buscar=todo_curriculo&como_buscar=todas_palavras&tipoBusca=busca_palavra_chave&idade[1]=1&empregado=false&dataAtualizacao=30&buscaLogSentencePai=111e5bd0-8cee-4ed4-8ff3-51f9669f13f3"
        data = get_ids(link, cookies, headers)

        infos = data["props"]['pageProps']['resumeSearch']['resumeSearchResult']['resumes']
        hashPage = data["props"]['pageProps']["hashPage"]

        if len(infos) == 0:
            break

        # add cv_id && usr_id in memory
        for client in infos:
            usr_id = client["usr_id"]
            cv_id = client["cv_id"]
            number = get_number(link, cv_id, usr_id, hashPage)
            usr = dicts.clients
            usr["usr_id"] = usr_id
            usr["cv_id"] = cv_id
            clients.append(usr)


    print("[+] \x1b[32m" + str(len(clients)) + "\x1b[0m ids collecteds!")


# send messages to all users in the database
# database with numbers should exist
def send_messages():
    add_tag("")
    # @todo: create a function to send messages
    # @> messages need be send in random times between 1s and 20s


def main():
    get_clients()
    send_messages()


if __name__ == "__main__":
    main()
