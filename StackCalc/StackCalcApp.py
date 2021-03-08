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
    with open("YellowPages.txt", encoding="utf-8") as fil:
        phonebook = [i.strip().split(";") for i in fil.readlines()]
        phoneTable = {k: v for k, v in phonebook}
        return phoneTable


def calcVipps(playerInfo, phoneTable):
    playerInfoCopy = playerInfo.copy()
    vippsMessages = []

    while playerInfoCopy:
        playerInfoCopy.sort(key=lambda x: x[3], reverse=True)
        sender, bi, bo, net = playerInfoCopy.pop()
        if net == 0:
            continue

        receiver, rbi, rbo, rnet = playerInfoCopy.pop(0)
        if rnet == 0:
            playerInfoCopy.append((sender, bi, bo, net))

        rmob = phoneTable.get(receiver.lower(), "")
        sender = sender[0].upper() + sender[1:]
        receiver = receiver[0].upper() + receiver[1:]

        if abs(net) > abs(rnet):
            vippsMessages.append(f"{sender} sender {receiver} {abs(rnet)}kr. ({rmob})")
            playerInfoCopy.append((sender, bi, bo, net + rnet))

        elif abs(net) < abs(rnet):
            vippsMessages.append(f"{sender} sender {receiver} {abs(net)}kr. ({rmob})")
            playerInfoCopy.append((receiver, rbi, rbo, rnet + net))

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


def calcRawData(playerInfo):
    line_list = []
    game = "Holdem"
    game_format = "Cash"
    hands_played = "000"
    date_today = time.strftime("%d.%m.%Y")
    if not playerInfo:
        raise ValueError

    for x in playerInfo:
        name, bi, bo, net = x
        name = name[0].upper() + name[1:]
        line_list.append(f"{name},{game_format},{game},{date_today},{hands_played},{net}")

    return line_list


def poker_calc_vipps():
    """Get Adress, and retrieve ledger information
    """
    global player_info
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


def clear_text_box():
    lbl_result.delete("1.0", tk.END)


def retrieve_tableinfo():
    """
    Retrieves PlayerInfo to global
    """
    global player_info
    clear_text_box()

    try:
        myTable = ent_web_adress.get().split('?')[0]
        checkSite(myTable)
        myLedger = getTable(myTable)
        player_info.clear()
        player_info = getPlayerInfo(myLedger)
        clear_player_entry()
        show_player_names()
        show_ledger()
        ent_web_adress.delete(first=0, last=1000)
        ent_web_adress.insert(0, "Success!")


    except:
        result = msg_list[random.randint(0, 5)]
        ent_web_adress.delete(first=0, last=1000)
        ent_web_adress.insert(0, "Try again..")
        lbl_result.insert(1.0, result)


def show_ledger():
    """
    Displays ledger results
    """
    global player_info
    clear_text_box()
    try:
        result = "\n".join(calcNet(player_info))
        lbl_result.insert(1.0, result)
    except:
        result = msg_list[random.randint(0, 5)]
        lbl_result.insert(1.0, result)


def show_player_names():
    """
    Displays player names in player_entries
    """
    global player_info
    global player_entries

    for plr, entry in zip(player_info, player_entries):
        entry.delete(first=0, last=1000)
        entry.insert(0, plr[0])


def clear_player_entry():
    """
    Clears text from player entry
    """
    global player_entries
    for entry in player_entries:
        entry.delete(first=0, last=1000)


def change_name():
    global player_info
    global player_entries

    for plr_index, entry in zip(range(len(player_info)), player_entries):
        name, bi, bo, net = player_info[plr_index]
        new_name = entry.get()
        if new_name:
            player_info[plr_index] = (new_name, bi, bo, net)

    show_ledger()


def store_table_info():
    """
    Stores current Table Info
    """
    global player_info
    global player_info_storage

    player_info_storage = player_info.copy()


def get_stored_data():
    """
    Retrieves current Table Info
    """
    global player_info
    global player_info_storage
    if not player_info_storage:
        clear_text_box()
        lbl_result.insert(1.0, "Nothing in storage!")
        return

    player_info = player_info_storage.copy()
    player_info_storage.clear()
    show_player_names()
    show_ledger()


def merge_stored_and_current():
    """
    Merges two pokerNow ledgers
    """
    global player_info
    global player_info_storage
    player_info = player_info + player_info_storage
    merge_same_name()
    show_player_names()
    show_ledger()
    show_mergeInfo()


def show_mergeInfo():
    """
    Displays saved merge info
    """
    global merge_info
    lbl_result.insert(tk.END, "\n\n")
    lbl_result.insert(tk.END, "\n".join(merge_info))


def merge_same_name():
    """
    Merges players with same name.
    """
    change_name()
    global player_info
    global merge_info
    i = 0
    while i < len(player_info):
        name, bi, bo, net = player_info[i]
        k = i + 1
        while k < len(player_info):
            rname, rbi, rbo, rnet = player_info[k]
            if name == rname:
                merge_string = f"Merged {rname}: Net = {net} + {rnet}"

                bi = bi + rbi
                bo = bo + rbo
                net = net + rnet
                merge_info.append(merge_string)
                player_info[i] = (name, bi, bo, net)
                player_info.remove(player_info[k])

            else:
                k += 1
        i += 1
    clear_player_entry()
    show_player_names()
    show_ledger()
    show_mergeInfo()


# Global variables
msg_list = ["Error 404", "Help me!", "I don't understand?",
            "kill me.", "What is my purpose?", "Try inputting an actual link?"]
player_info = []
player_info_storage = []
merge_info = []

# MASTER    Set-up the window
window = tk.Tk()
window.title("PokerNow Converter")
window.resizable(width=20, height=20)

# ENTRY     Create entry frame with an Entry
frm_entry = tk.Frame(master=window)

# Create the info Button and result display Label
btn_get_data = tk.Button(
    master=frm_entry,
    text="Get Data \N{RIGHTWARDS BLACK ARROW}",
    command=retrieve_tableinfo
)


ent_web_adress = tk.Entry(master=frm_entry)
lbl_temp = tk.Label(master=frm_entry, text="Insert PokerNow web-adress")

# ENTRY     Layout the Entry in frm_entry
ent_web_adress.grid(row=0, column=0, sticky="e")
lbl_temp.grid(row=0, column=1, sticky="w")
btn_get_data.grid(row=0, column=2, sticky="w")

# P ENTRY   Create entry for playername
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
player11_entry = tk.Entry(master=plr_entry)
player12_entry = tk.Entry(master=plr_entry)
player13_entry = tk.Entry(master=plr_entry)
player14_entry = tk.Entry(master=plr_entry)
player15_entry = tk.Entry(master=plr_entry)
player16_entry = tk.Entry(master=plr_entry)
player17_entry = tk.Entry(master=plr_entry)
player18_entry = tk.Entry(master=plr_entry)
player19_entry = tk.Entry(master=plr_entry)
player20_entry = tk.Entry(master=plr_entry)

player_entries = [player1_entry, player2_entry, player3_entry, player4_entry,
                  player5_entry, player6_entry, player7_entry, player8_entry,
                  player9_entry, player10_entry, player11_entry, player12_entry,
                  player13_entry, player14_entry, player15_entry, player16_entry,
                  player17_entry, player18_entry, player19_entry, player20_entry]

# P ENTRY   Add Function Button

# Create the Change Name Button and display names
btn_change_names = tk.Button(
    master=plr_entry,
    text="Change \N{RIGHTWARDS BLACK ARROW}",
    command=change_name
)

# Create the Merge data by name Button and display results
btn_merge_names = tk.Button(
    master=plr_entry,
    text="Merge \N{RIGHTWARDS BLACK ARROW}",
    command=merge_same_name
)

# P ENTRY   LayoutPlayers
btn_change_names.grid(row=0, column=0, sticky="w", pady=2, padx=2)
btn_merge_names.grid(row=0, column=0, sticky="e", pady=2, padx=2)
for row, player in enumerate(player_entries, 1):
    player.grid(row=row, column=0, sticky="w", pady=0, padx=2)

button_frame = tk.Frame(master=window)

# Create the info Button to display result
btn_result = tk.Button(
    master=button_frame,
    text="Results \N{RIGHTWARDS BLACK ARROW}",
    command=show_ledger
)

# Create the buttom to display Raw data result
btn_raw_data = tk.Button(
    master=button_frame,
    text="Raw_data \N{RIGHTWARDS BLACK ARROW}",
    command=show_ledger
)

# Create the Vipps Button to display Vipps result
btn_vipps = tk.Button(
    master=button_frame,
    text="Vipps \N{RIGHTWARDS BLACK ARROW}",
    command=poker_calc_vipps
)

btn_store_data = tk.Button(
    master=button_frame,
    text="Store Data \N{RIGHTWARDS BLACK ARROW}",
    command=store_table_info
)

btn_get_stored = tk.Button(
    master=button_frame,
    text="Get Stored \N{RIGHTWARDS BLACK ARROW}",
    command=get_stored_data
)

btn_merge_stored = tk.Button(
    master=button_frame,
    text="Merge Stored & Current \N{RIGHTWARDS BLACK ARROW}",
    command=merge_stored_and_current
)

# BUTTON    Lables
lbl_display_results = tk.Label(master=button_frame, text="Results")
lbl_change_data = tk.Label(master=button_frame, text="Data access")


# BUTTON    Set-up the layout of button frame
lbl_display_results.grid(row=0, column=0, sticky="w", pady=2, padx=2)
btn_result.grid(row=1, column=0, sticky="w", pady=2, padx=2)
btn_vipps.grid(row=2, column=0, sticky="w", pady=2, padx=2)
btn_raw_data.grid(row=3, column=0, sticky="w", pady=2, padx=2)

lbl_change_data.grid(row=0, column=2, sticky="w", pady=2, padx=100)
btn_store_data.grid(row=1, column=2, sticky="w", pady=2, padx=100)
btn_get_stored.grid(row=2, column=2, sticky="w", pady=2, padx=100)
btn_merge_stored.grid(row=3, column=2, sticky="w", pady=2, padx=100)

# TEXTBOX   Make TextBox
lbl_result = tk.Text(master=window, height=50, relief="ridge", borderwidth=3)
lbl_result.insert(1.0, "What is my purpose?")

# MASTER    Set-up the layout using the .grid() geometry manager M
frm_entry.grid(row=0, column=0, sticky="W", pady=2, padx=2)
button_frame.grid(row=1, column=0, sticky="W", pady=2, padx=2)
lbl_result.grid(row=2, column=0, sticky="NW", pady=2, padx=2)
plr_entry.grid(row=2, column=1, sticky="NW", pady=2, padx=2)

# Run the application
window.mainloop()
