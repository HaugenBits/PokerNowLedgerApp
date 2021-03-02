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

    """
    mySesh = getCurrentLedger(myTable)
    players = {k: dict(v) for k, v in dict(mySesh["playersInfos"]).items()}
    return players


def getPlayerInfo(players):
    """

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


def getPhones():
    with open("YellowPages.txt", "r") as fil:
        phonebook = [i.strip().split(";") for i in fil.readlines()]
        phoneTable = {k: v for k, v in phonebook}
        return phoneTable


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

    return vippsMessages


def calcNet(playerInfo):
    line_list = []
    date_today = time.strftime("%d.%m.%Y")
    line_list.append(f"{date_today},Cash")
    if not playerInfo:
        raise ValueError

    for x in playerInfo:
        name, bi, bo, net = x
        line_list.append(f"{name[0].upper()}{name[1:]},{net}")

    return line_list


def poker_calc_vipps():
    """Get Adress, and retrieve ledger information
    """
    global player_info
    print(player_info, "pokercalc")
    result = ""
    lbl_result.delete(1.0, tk.END)

    try:
        lbl_result.insert(1.0, "Processing...")
        phoneTable = getPhones()
        result = "\n".join(calcVipps(player_info, phoneTable))

    except:
        result = msg_list[random.randint(0, 5)]

    lbl_result.delete(1.0, tk.END)
    lbl_result.insert(1.0, result)


def retrieve_tableinfo():
    """
    Retrieves PlayerInfo to global
    """
    global player_info
    lbl_result.delete("1.0", tk.END)
    try:
        myTable = ent_web_adress.get().split('?')[0]
        checkSite(myTable)
        myLedger = getTable(myTable)
        player_info.clear()
        player_info = getPlayerInfo(myLedger)
        show_player_names()
        to_poker_csv()
        ent_web_adress.delete(first=0, last=1000)
        ent_web_adress.insert(0, "Success!")

    except:
        result = msg_list[random.randint(0, 5)]
        ent_web_adress.delete(first=0, last=1000)
        ent_web_adress.insert(0, "Try again..")
        lbl_result.insert(1.0, result)

    print(player_info, "retrieve")


def to_poker_csv():
    """Retrieve ledger information
    """
    global player_info
    lbl_result.delete("1.0", tk.END)
    try:
        result = "\n".join(calcNet(player_info))
        lbl_result.insert(1.0, result)
    except:
        result = msg_list[random.randint(0, 5)]
        lbl_result.insert(1.0, result)


def show_player_names():
    global player_info
    global player_entries

    for plr, entry in zip(player_info, player_entries):
        entry.delete(first=0, last=1000)
        entry.insert(0, plr[0])


def clear_player_entry():
    global player_entries
    for entry in player_entries:
        entry.delete(first=0, last=1000)


def change_name():
    global player_info
    global player_entries

    for plr_index, entry in zip(range(len(player_info)),player_entries):
        name, bi, bo, net = player_info[plr_index]
        new_name = entry.get()
        if new_name:
            player_info[plr_index]= (new_name, bi, bo, net)

    to_poker_csv()


def merge_same_name():
    change_name()
    global player_info
    i = 0
    while i<len(player_info):
        name, bi, bo, net = player_info[i]
        k = i+1
        while k < len(player_info):
            rname, rbi, rbo, rnet = player_info[k]
            if name == rname:
                bi = bi+rbi
                bo = bo+rbo
                net = net+rnet
                player_info[i] = (name, bi,bo,net)
                player_info.remove(player_info[k])

            else:
                k+=1
        i+=1
    clear_player_entry()
    show_player_names()
    to_poker_csv()


# Global variables
msg_list = ["Error 404", "Help me!", "I don't understand?",
            "kill me.", "What is my purpose?", "Try inputting an actual link?"]
player_info = []


# Set-up the window
window = tk.Tk()
window.title("PokerNow Converter")
window.resizable(width=20, height=20)

# Create entry frame with an Entry
# widget and label in it
frm_entry = tk.Frame(master=window)

# Create the info Button and result display Label
btn_get_data = tk.Button(
    master=frm_entry,
    text="Get Data \N{RIGHTWARDS BLACK ARROW}",
    command=retrieve_tableinfo
)

ent_web_adress = tk.Entry(master=frm_entry)
lbl_temp = tk.Label(master=frm_entry, text="Insert PokerNow web-adress")


# Layout the Entry and Label in frm_entry
# using the .grid() geometry manager
ent_web_adress.grid(row=0, column=0, sticky="e")
lbl_temp.grid(row=0, column=1, sticky="w")
btn_get_data.grid(row=0, column=2, sticky="w")


# Create entry for playername
plr_entry = tk.Frame(master=window, width=40)

player1_entry = tk.Entry(master=plr_entry)
player2_entry = tk.Entry(master=plr_entry)
player3_entry = tk.Entry(master=plr_entry)
player4_entry = tk.Entry(master=plr_entry)
player5_entry = tk.Entry(master=plr_entry)
player6_entry = tk.Entry(master=plr_entry)
player7_entry = tk.Entry(master=plr_entry)
player8_entry = tk.Entry(master=plr_entry)
player9_entry = tk.Entry(master=plr_entry)
player10_entry = tk.Entry(master=plr_entry)

#Add Function Button
# Create the Vipps Button and result display Label
btn_change_names = tk.Button(
    master=plr_entry,
    text="Change \N{RIGHTWARDS BLACK ARROW}",
    command=change_name
)

btn_merge_names = tk.Button(
    master=plr_entry,
    text="Merge \N{RIGHTWARDS BLACK ARROW}",
    command= merge_same_name
)

#LayoutPlayers
player_entries = [player1_entry, player2_entry, player3_entry, player4_entry,
                 player5_entry, player6_entry, player7_entry, player8_entry,
                 player9_entry, player10_entry]

btn_change_names.grid(row=0, column=0, sticky="w", pady=2, padx=2)
btn_merge_names.grid(row=0, column=0, sticky="e", pady=2, padx=2)
for col, player in enumerate(player_entries, 1):
    player.grid(row=col, column=0, sticky="w", pady=2, padx=2)


# Make TextBox.
lbl_result = tk.Text(master=window, relief="ridge", borderwidth=3)
lbl_result.insert(1.0, "What is my purpose?")


# Create the info Button and result display Label
btn_result = tk.Button(
    master=window,
    text="Results \N{RIGHTWARDS BLACK ARROW}",
    command=to_poker_csv
)

# Create the Vipps Button and result display Label
btn_vipps = tk.Button(
    master=window,
    text="Vipps \N{RIGHTWARDS BLACK ARROW}",
    command=poker_calc_vipps
)

# Set-up the layout using the .grid() geometry manager
frm_entry.grid(row=0, column=0, sticky="W", pady=2, padx=2)
btn_result.grid(row=1, column=0,sticky="W", pady=2, padx=2)
btn_vipps.grid(row=1, column=0,sticky="N", pady=2, padx=2)
lbl_result.grid(row=2, column=0, sticky="W", pady=2, padx=2)
plr_entry.grid(row=2, column=1, sticky="W", pady=2, padx=2)

# Run the application
window.mainloop()
