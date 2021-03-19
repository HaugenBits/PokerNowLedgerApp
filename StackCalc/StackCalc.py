import requests
import time


def checkSite(web_adress):
    """
    Checks if server is responding
    ServerResponse 200 = OK
    """
    hostname = web_adress+"/players_sessions"
    response = requests.get(hostname).status_code

    # and then check the response...
    if response == 200:
        print("Server", 'is up!\n')
        return True
    else:
        raise ConnectionError


def getCurrentLedger(web_adress):
    """
    Retrieves Ledger Json file
    """
    link = web_adress+"/players_sessions"
    session_log = requests.get(link).json()
    return session_log


def getCurrentLog(web_adress):
    """
    Retrieves Log Json file
    """
    link = web_adress+"/log"
    session_log = requests.get(link)
    return session_log


def getTable(myTable):
    """
    :param myTable: webadress
    :return:
    """
    mySesh = getCurrentLedger(myTable)
    players = {k: dict(v) for k, v in dict(mySesh["playersInfos"]).items()}
    return players


def getPlayerInfo(players):
    """
    :param players: Dictionary
    :return:
    """
    playerInfoList = []
    for k in players.keys():
        name = players[k]['names']
        bi = players[k]['buyInSum']
        bo = players[k]['buyOutSum']
        net = players[k]['net']
        myTuple = (set(name).pop(), bi, bo, net)
        playerInfoList.append(myTuple)
    return playerInfoList


def calcVipps(playerInfo, phoneTable):
    playerInfoCopy = playerInfo.copy()
    vippsMessages = []

    while playerInfoCopy:
        playerInfoCopy.sort(key=lambda x: x[3], reverse=True)
        sender, bi, bo, net = playerInfoCopy.pop()
        receiver, rbi, rbo, rnet = playerInfoCopy.pop(0)
        rmob = phoneTable.get(receiver.lower(), "")
        sender = sender[0].upper() + sender[1:]
        receiver = receiver[0].upper() + receiver[1:]

        if abs(net) > abs(rnet):
            vippsMessages.append(f"{sender} sender {receiver} {abs(rnet)}kr. ({rmob})")
            playerInfoCopy.append((sender, bi, bo, net+rnet))

        elif abs(net) < abs(rnet):
            vippsMessages.append(f"{sender} sender {receiver} {abs(net)}kr. ({rmob})")
            playerInfoCopy.append((receiver, rbi, rbo, rnet+net))

        else:
            vippsMessages.append(f"{sender} sender {receiver} {abs(rnet)}kr. ({rmob})")

    vippsMessages.sort()

    for x in vippsMessages:
        print(x)


def calcNet(playerInfo):
    print()
    print(time.strftime("%d.%m.%Y"), "Cash", sep=",")
    for x in playerInfo:
        name, bi, bo, net = x
        print(name[0].upper() + name[1:],bi, bo, net, sep=",")


def renamePlayers(playerInfo):
    for _ in playerInfo:
        navn, bi, bo, net = playerInfo.pop(0)
        nytt_navn = input("Hvem er {}\n".format(navn, " "))
        if nytt_navn:
            playerInfo.append((nytt_navn, bi, bo, net))
        else:
            playerInfo.append((navn,bi,bo,net))


def getPhones():
    with open("YellowPages.txt", "r") as fil:
        phonebook = [i.strip().split(";") for i in fil.readlines()]
        phoneTable = {k: v for k, v in phonebook}
        return phoneTable


def merge_same_name(player_info):
    i = 0
    while i < len(player_info):
        name, bi, bo, net = player_info[i]
        k = i + 1
        while k < len(player_info):
            rname, rbi, rbo, rnet = player_info[k]
            if name == rname:
                bi = bi + rbi
                bo = bo + rbo
                net = net + rnet
                player_info[i] = (name, bi, bo, net)
                player_info.remove(player_info[k])
            else:
                k += 1
        i += 1


def main():
    myTable = input("Input PokerNow Web-Adress :\n").split('?')[0]
    phoneTable = getPhones()

    try:
        checkSite(myTable)
        myLedger = getTable(myTable)
        playerInfo = getPlayerInfo(myLedger)
        print(myLedger)

    except:
        print("errors was made")


main()
