import requests
import time
import tkinter as tk
import random


def checkSite(web_adress):
    """
    Checks if server is responding
    ServerResponse 200 = OK
    """
    hostname = web_adress + "/players_sessions"
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
    link = web_adress + "/players_sessions"
    session_log = requests.get(link).json()
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


def calcNet(playerInfo):
    line_list = []
    date_today = time.strftime("%d.%m.%Y")
    line_list.append(f"{date_today},Cash")

    for x in playerInfo:
        name, bi, bo, net = x
        line_list.append(f"{name[0].upper()}{name[1:]},{net}")

    return line_list


def adress_to_poker_info():
    """Get Adress, and retrieve ledger information
    """
    myTable = ent_web_adress.get().split('?')[0]
    result = ""
    lbl_result.delete("1.0", tk.END)

    try:
        checkSite(myTable)
        myLedger = getTable(myTable)
        playerInfo = getPlayerInfo(myLedger)
        result = "\n".join(calcNet(playerInfo))

    except:
        msg_list = ["Error 404", "Help me!", "I don't understand?",
                    "kill me.","What is my purpose?", "Try inputting an actual link?"]
        result = msg_list.pop(random.randint(0, 5))

    lbl_result.insert(1.0, result)


# Set-up the window
window = tk.Tk()
window.title("PokerNow Converter")
window.resizable(width=20, height=20)

# Create entry frame with an Entry
# widget and label in it
frm_entry = tk.Frame(master=window)
ent_web_adress = tk.Entry(master=frm_entry, width=40)
lbl_temp = tk.Label(master=frm_entry, text="Insert PokerNow web-adress")

# Layout the Entry and Label in frm_entry
# using the .grid() geometry manager
ent_web_adress.grid(row=0, column=0, sticky="e")
lbl_temp.grid(row=0, column=1, sticky="w")

# Create the conversion Button and result display Label
btn_convert = tk.Button(
    master=window,
    text="\N{RIGHTWARDS BLACK ARROW}",
    command=adress_to_poker_info
)
lbl_result = tk.Text(master=window)
lbl_result.insert(1.0, "What is my purpose?")


# Set-up the layout using the .grid() geometry manager
frm_entry.grid(row=0, column=0)
btn_convert.grid(row=0, column=1,)
lbl_result.grid(row=1, column=0, sticky="nsew")

# Run the application
window.mainloop()