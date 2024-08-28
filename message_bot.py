import os
import re
import json
import time
import requests
import pywhatkit
from tqdm import tqdm
import webbrowser as web
from random import randrange


def remove_junk():
    if os.path.exists("PyWhatKit_DB.txt"):
        os.remove("PyWhatKit_DB.txt")

# get cookies from request har file
def get_cookies():
    # read HAR file
    try:
        with open("request.har", "r") as file:
            har_data = json.load(file)
    except:
        raise NameError('\x1b[31m ERROR:\x1b[0m Missing \x1b[34m\x1b[1mrequest.har\x1b[0m file!')

    # extract cookies
    har_cookies = har_data["log"]["entries"][0]["request"]["cookies"]

    # get important cookies
    res = {
        "session_id": "",
        "cactk": ""
    }
    for cookie in har_cookies:
        if cookie["name"] == "session_id":
            if cookie["value"] == "":
                raise NameError('\x1b[31m ERROR:\x1b[0m Missing Important Cookies In File!')
            else:
                res["session_id"] = cookie["value"]

        if cookie["name"] == "cactk":
            if cookie["value"] == "":
                raise NameError('\x1b[31m ERROR:\x1b[0m Missing Important Cookies In File!')
            else:
                res["cactk"] = cookie["value"]

    return res


# Get ids in api to search numbers
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
    if res.text == "Too Many Requests":
        time.sleep(3)
        res2 = requests.get(link, cookies=cookies, headers=headers)
        return json.loads(res2.text)["phones"][0]
    else:
        return json.loads(res.text)["phones"][0]


# search clients and save their numbers in a simple database
def get_clients():
    cookies = get_cookies()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    clients = []

    for page in range(1, 1000):
        link = "https://www.catho.com.br/curriculos/busca/?q=vendas&pais_id=31&estado_id[25]=25&regiaoId[-1]=-1&cidade_id[783]=783&zona_id[-1]=-1&page="+ str(page) +"&onde_buscar=todo_curriculo&como_buscar=todas_palavras&tipoBusca=busca_palavra_chave&idade[1]=1&empregado=false&dataAtualizacao=30&buscaLogSentencePai=111e5bd0-8cee-4ed4-8ff3-51f9669f13f3"
        data = get_ids(link, cookies, headers)

        infos = data["props"]['pageProps']['resumeSearch']['resumeSearchResult']['resumes']
        hashPage = data["props"]['pageProps']["hashPage"]

        if len(infos) == 0:
            break

        print(f'\x1b[34m\x1b[0m Gathering clients data in page:')

        for client in tqdm(infos, desc="\x1b[32m\x1b[1m"+str(page)+"\x1b[0m 󰁕"):
            usr_id = client["usr_id"]
            cv_id = client["cv_id"]
            number = get_number(link, cv_id, usr_id, hashPage)
            clients.append({
                "usr_id": usr_id,
                "cv_id": cv_id,
                "number": number
            })

        if len(clients) >= 200:
            break


    print("[+] \x1b[32m" + str(len(clients)) + "\x1b[0m ids collecteds!")

    # if `database.json` exist, the file will be overriden
    with open('database.json', 'w') as fout:
        json.dump(clients, fout)


# Add a tag to client number
def send_message(num):
    f_message = open("template/text.txt", "r")
    message = f_message.read()
    pywhatkit.sendwhatmsg_instantly(
        num,
        message,
        30,
        True,
    )
    return True


# handle messages to send text to all users in the database
def handle_messages():
    # check if database exists
    try:
        with open("database.json", "r") as f:
            data = json.load(f)
    except:
        raise NameError('\x1b[31m ERROR:\x1b[0m Missing \x1b[34m\x1b[1mdatabase.json\x1b[0m file!')

    for client in data:
        # formatting and send message to numbers
        f_num = "+55"
        for l in client["number"]:
            if l == "(" or \
               l == ")" or \
               l == " " or \
               l == "-":
                f_num = f_num + ""
            else:
                f_num = f_num + l

        if send_message(f_num):
            counter += 1
        else:
            continue

        break


def main():
    get_clients()
    handle_messages()
    remove_junk()


if __name__ == "__main__":
    main()
