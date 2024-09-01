import os
import re
import json
import time
import requests
import itertools
import pyperclip as pc
import pyautogui as pg
import webbrowser as web
from tqdm import tqdm
from random import randrange
from operator import itemgetter

# remove unnecessary file
def remove_junk():
    if os.path.exists("PyWhatKit_DB.txt"):
        os.remove("PyWhatKit_DB.txt")


# get list with clients numbers, remove duplicates & sort with pending messages to send
def remove_dupl_and_sort(data):
    if os.path.exists("database.json"):
        with open("database.json", mode="r", encoding="utf8") as f:
            s_data = json.load(f)

        for item in data:
            s_data.append(item)

        sorted_data = sorted(s_data, key=itemgetter('number'))
        r_dupl = [next(g) for k,g in itertools.groupby(sorted_data, lambda x: x['number'])]
        return sorted(r_dupl, key=itemgetter('alreadySend'))
    else:
        sorted_data = sorted(data, key=itemgetter('number'))
        r_dupl = [next(g) for k,g in itertools.groupby(sorted_data, lambda x: x['number'])]
        return sorted(r_dupl, key=itemgetter('alreadySend'))


# get cookies from request har file
def get_cookies():
    # read HAR file
    try:
        with open("request.har", mode="r", encoding="utf8") as file:
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
                "number": number,
                "alreadySend": False
            })

        if len(clients) >= 200:
            f_clients = remove_dupl_and_sort(clients)
            # save all clients
            with open('database.json', mode='w', encoding="utf8") as fout:
                json.dump(f_clients, fout)

            clients = []
            counter = 0
            for c in f_clients:
                if c["alreadySend"] == False:
                    clients.append(c)
                    counter += 1
                else:
                    break

            if counter < 200:
                continue
            else:
                break

    print("\x1b[32m[+] " + str(len(clients)) + " ids collecteds!\x1b[0m")
    print("\x1b[32m database has been updated!\x1b[0m")


# Add a tag to client number
def send_message(num):
    f_message = open("template/text.txt", mode="r", encoding="utf8")
    message = f_message.read()
    try:
        pc.copy(f"https://web.whatsapp.com/send?phone={num}&text={message}")
        pg.hotkey('ctrl', 'l')
        pg.hotkey('ctrl', 'v')
        time.sleep(1)
        pg.press('enter')
        time.sleep(15)
        pg.press('enter')
        time.sleep(5)
    except:
        raise NameError('\x1b[31m ERROR:\x1b[0m Something wrong when tryed to send message!')


# handle messages to send text to all users in the database
def handle_messages():
    # check if database exists
    try:
        with open("database.json", mode="r", encoding="utf8") as f:
            data = json.load(f)
    except:
        raise NameError('\x1b[31m ERROR:\x1b[0m Missing \x1b[34m\x1b[1mdatabase.json\x1b[0m file!')

    print(f'\x1b[32m\x1b[0m Sending message to numbers:')
    print("\x1b[32m the database will be updated with each message sent!\x1b[0m")
    msg_send = 0
    print("\x1b[32m󰖟\x1b[0m Loading site!")
    web.open("https://web.whatsapp.com/")
    time.sleep(15)
    for client in tqdm(data):
        if client["number"] == "":
            raise NameError('\x1b[31m ERROR:\x1b[0m Wrong Client Number!')
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

        if client["alreadySend"] == False:
            send_message(f_num)
            client["alreadySend"] = True
            msg_send += 1
            with open('database.json', mode='w', encoding="utf8") as fout:
                json.dump(data, fout)
        else:
            break

    print(f'\x1b[32m\x1b[0m {msg_send} messages have been sent without errors!')


def main():
    f_logo = open("template/logo.txt", mode="r", encoding="utf8")
    logo = f_logo.read()
    print(logo)
    choice = int(input("Selecione uma opção: (1 ou 2)  "))
    if choice == 1:
        get_clients()
        handle_messages()
        remove_junk()
    elif choice == 2:
        handle_messages()
        remove_junk()
    else:
        raise NameError('\x1b[31m ERROR:\x1b[0m Wrong Option in Menu!')


if __name__ == "__main__":
    main()
