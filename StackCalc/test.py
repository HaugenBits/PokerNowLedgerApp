import requests

def getCurrentLedger(web_adress):
    """
    Retrieves Ledger Json file
    """
    link = web_adress+"/players_sessions"
    session_log = requests.get(link).json()
    return session_log


def main():
    myTable = input("Input PokerNow Web-Adress :\n").split('?')[0]
    json_file = getCurrentLedger(myTable)
    print(json_file)


if __name__ == '__main__':
    main()
