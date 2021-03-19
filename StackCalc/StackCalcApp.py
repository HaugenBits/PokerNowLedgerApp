import dateutil.parser
import requests
import time
import tkinter as tk
import random
import csv

# Global variables
msg_list = ["Error 404", "Help me!", "I don't understand?",
            "kill me.", "What is my purpose?", "Try inputting an actual link?"]
player_info = {}
player_info_storage = {}
merge_info = []
game_date = ""
web_adress = ""
phone_table = {}

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
    for k in players.keys():
        players[k]["name"] = players[k]["names"][0]
        players[k]["hands"] = 0

    return players


def getPhones():
    global phone_table
    phone_table.clear()

    with open("YellowPages.csv", newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for line in spamreader:
            name = line["name"]
            phone_table[name] = line


def calcVippsChecker(): #TODO
    pass


def calcVipps():
    global player_info
    global phone_table
    playerInfoCopy = player_info.copy()
    vippsMessages = []

    while playerInfoCopy:
        max_val = 0
        min_val = 100000
        max_player = ""
        min_player = ""

        for k, v in playerInfoCopy.items():
            if v["net"]>max_val:
                max_val = v["net"]
                max_player = k
            elif v["net"] < min_val:
                min_val = v["net"]
                min_player = k

        if min_val == 0:
            playerInfoCopy.pop(min_player)

        if not (max_player and min_player):
            continue


        sender = playerInfoCopy[min_player]["name"]
        receiver = playerInfoCopy[max_player]["name"]
        rmob = phone_table.get(receiver.lower(), {}).get("number", "")

        sender = sender[0].upper() + sender[1:]
        receiver = receiver[0].upper() + receiver[1:]


        if abs(max_val) > abs(min_val):
            vippsMessages.append(f"{sender} sender {receiver} {abs(min_val)}kr. ({rmob})")
            playerInfoCopy[max_player]["net"]+=min_val
            playerInfoCopy.pop(min_player)

        elif abs(max_val) < abs(min_val):
            vippsMessages.append(f"{sender} sender {receiver} {abs(max_val)}kr. ({rmob})")
            playerInfoCopy[min_player]["net"]+=max_val
            playerInfoCopy.pop(max_player)

        else:
            vippsMessages.append(f"{sender} sender {receiver} {abs(max_val)}kr. ({rmob})")
            playerInfoCopy.pop(max_player)
            playerInfoCopy.pop(min_player)

    vippsMessages.sort()

    return vippsMessages


def calcNet(playerInfo):
    global game_date
    line_list = []
    date_today = time.strftime("%d/%m/%Y")
    if game_date:
        date_today = game_date
    line_list.append(f"{date_today}\tCash")
    if not playerInfo:
        raise ValueError

    for k in playerInfo:
        name = playerInfo[k]['name']
        bi = player_info[k]['buyInSum']
        bo = player_info[k]['buyOutSum']
        net = player_info[k]['net']
        line_list.append(f"{name[0].upper()}{name[1:]}\t{net}")

    return line_list


def calcRawData(playerInfo):
    global game_date
    line_list = []
    game = "Holdem"
    game_format = "Cash"
    date_today = time.strftime("%d.%m.%Y")
    if game_date:
        date_today = game_date
    if not playerInfo:
        raise ValueError

    for k in playerInfo:
        name = playerInfo[k]['name']
        bi = player_info[k]['buyInSum']
        bo = player_info[k]['buyOutSum']
        net = player_info[k]['net']
        hands_played = player_info[k]["hands"]
        name = name[0].upper() + name[1:]
        line_list.append(f"{name}\t{game_format}\t{game}\t{date_today}\t{hands_played}\t{net}")

    return line_list


def poker_calc_vipps():
    """Get Adress, and retrieve ledger information
    """
    global player_info
    result = ""
    lbl_result.delete(1.0, tk.END)

    lbl_result.insert(1.0, "Processing...")
    getPhones()
    result = "\n".join(calcVipps())

    lbl_result.delete(1.0, tk.END)
    lbl_result.insert(1.0, result)


def clear_text_box():
    lbl_result.delete("1.0", tk.END)

def getDateString(filename):
    my_date = ""
    with open(filename, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            my_date = row["at"]
            break

    return dateutil.parser.parse(my_date).date()


def getHandsPlayedDict(filename):

    myDict = {}
    with open(filename, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            entry = row["entry"]
            if "Player stacks" not in entry[:15]:
                continue
            for player_string in entry.split("|"):
                player_string = player_string[player_string.find('@')+2:]
                player_string = player_string[:player_string.find('"')]
                myDict[player_string] = myDict.get(player_string, 0) + 1

    return myDict


def add_hands(hands_played):
    global player_info
    for k in player_info.keys():
        player_info[k]["hands"] = hands_played.get(k,0)


def get_data_from_log():
    global game_date
    global web_adress

    try:
        filename = "PokerNowLogs/poker_now_log_"+web_adress.split("games/")[1]+".csv"
        game_date = getDateString(filename)
        hands_played= getHandsPlayedDict(filename)
        add_hands(hands_played)
        show_ledger()

    except:
        clear_text_box()
        result = "404 error"
        lbl_result.insert(1.0, result)


def retrieve_tableinfo():
    """
    Retrieves PlayerInfo to global
    """
    global player_info
    global web_adress
    clear_text_box()

    try:
        web_adress = ent_web_adress.get().split('?')[0]
        checkSite(web_adress)
        myLedger = getTable(web_adress)
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


def show_ledger_raw():
    """
    Displays ledger results in raw format
    """
    global player_info
    clear_text_box()
    try:
        result = "\n".join(calcRawData(player_info))
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

    for k, entry in zip(player_info, player_entries):
        entry.delete(first=0, last=1000)
        entry.insert(0, player_info[k]["name"])


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

    for k, entry in zip(player_info.keys(), player_entries):
        new_name = entry.get()
        if new_name:
            player_info[k]["name"] = new_name

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


def merge_stored_solver():
    global player_info
    global player_info_storage

    for k, v in player_info_storage.items():
        if k in player_info:
            name = player_info[k]["name"]
            net = player_info[k]["net"]
            rnet = player_info_storage[k]["net"]
            merge_string = f"Merged {name}: Net = {net} + {rnet}"
            merge_info.append(merge_string)

            for k2 in player_info[k].keys():
                if isinstance(player_info[k][k2], int):
                    player_info[k][k2] = player_info[k][k2] + player_info_storage[k][k2]
        else:
            player_info[k] = v


def merge_stored_and_current():
    """
    Merges two pokerNow ledgers
    """
    global player_info_storage

    merge_stored_solver()
    player_info_storage.clear()
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


def merge_same_solver():
    global player_info
    global merge_info

    keys_to_remove = []
    newDict = player_info.copy()

    for k in player_info.keys():
        newDict.pop(k)
        for j in newDict:
            name = player_info[k]["name"]
            rname = newDict[j]["name"]
            if name == rname:
                net = player_info[k]["net"]
                rnet = rname = newDict[j]["net"]
                merge_string = f"Merged {name}: Net = {net} + {rnet}"
                merge_info.append(merge_string)

                for pk in player_info[k].keys():
                    if isinstance(player_info[k][pk], int):
                        player_info[k][pk] += newDict[j][pk]

                keys_to_remove.append(j)

    for x in keys_to_remove:
        player_info.pop(x)


def merge_same_name():
    """
    Merges players with same name.
    """
    change_name()
    merge_same_solver()

    clear_player_entry()
    show_player_names()
    show_ledger()
    show_mergeInfo()




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
    command=show_ledger_raw
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
    text="Merge Data \N{RIGHTWARDS BLACK ARROW}",
    command=merge_stored_and_current
)


btn_get_from_log = tk.Button(
    master=button_frame,
    text="Get Log \N{RIGHTWARDS BLACK ARROW}",
    command=get_data_from_log

)

# BUTTON    Lables
lbl_display_results = tk.Label(master=button_frame, text="Results",font="Helvetica 14 bold")
lbl_change_data = tk.Label(master=button_frame, text="Data access",font="Helvetica 14 bold")
lbl_log_data = tk.Label(master=button_frame, text="Log access",font="Helvetica 14 bold")



# BUTTON    Set-up the layout of button frame
lbl_display_results.grid(row=0, column=0, sticky="w", pady=2, padx=2)
btn_result.grid(row=1, column=0, sticky="w", pady=2, padx=2)
btn_vipps.grid(row=2, column=0, sticky="w", pady=2, padx=2)
btn_raw_data.grid(row=3, column=0, sticky="w", pady=2, padx=2)

lbl_change_data.grid(row=0, column=2, sticky="w", pady=2, padx=50)
btn_store_data.grid(row=1, column=2, sticky="w", pady=2, padx=50)
btn_get_stored.grid(row=2, column=2, sticky="w", pady=2, padx=50)
btn_merge_stored.grid(row=3, column=2, sticky="w", pady=2, padx=50)

lbl_log_data.grid(row=0, column=3, sticky="w", pady=2, padx=2)
btn_get_from_log.grid(row=1, column=3, sticky="w", pady=2, padx=2)



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
