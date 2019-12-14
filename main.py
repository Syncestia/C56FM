import discord, os, datetime, threading, requests, time, pickle, asyncio, random


# metadata
META = {"version":[0.7, False], "place":"", "replyCh":False, "msgCount":0, "scanning":False}
SHENANIGANS = {"channel":False, "guild":False, "member":False, "avoid":False, "avoidList":[], "annoy":False, "annoyed":0, "annoyChannel":False}
LOCALMETA = {"replyCh":False}

DATA = {"servers":{},"channels":{},"users":{}}
NAME = {}

client = discord.Client()

class cmd:
    def __init__(self, name, methods=False):
        if name == "admin" or name == "debug":
            self.perms = "manage_server"
        else:
            self.perms = False
        if name == "impersonate":
            self.cd = 0
        self.run = eval(name)
        if type(methods) is list:
            for method in methods:
                self.method[0] = self.method[1]

class cacheAuthor:
    def __init__(self, name, id):
        self.name = name
        self.id = id

class cacheMsg:
    def __init__(self, content, author, date, id):
        self.content = content
        self.author = author
        self.date = date
        self.id = id

def tryLoad(file, default):
    try:
        return pickle.load(open(file, "rb"))
    except (FileNotFoundError):
        log("Oh wow, no file data for {0}, creating new file.".format(file))
        pickle.dump(default, open(file, "wb"))
        return default

def sP(newPlace):
    META["place"] = newPlace

def checkPath(path):
    if os.path.isdir(path):
        return
    os.mkdir(path)

def lowerCD():
    while CMDS["impersonate"].cd != 0:
        CMDS["impersonate"].cd -= 1
        time.sleep(1)

def log(message, Type=False):
    if Type == False:
        Type = META["place"]
    try:
        logs = os.getcwd() + "\\logs\\"
        checkPath(logs)
        message += " | {0}".format(datetime.datetime.now())
        print("Log: {0} for {1}".format(Type, message))
        f = open(logs+Type+".txt", "a")
        f.write(message+"\n")
        f.close()
    except (UnicodeEncodeError):
        print("Fuck it, it's unicode.")

async def reply(sendables):
    await META["replyCh"].send(sendables)

def loadData(save=False):
    sP("load_data")
    data = os.getcwd() + "\\data\\"
    checkPath(data)
    if not save:
        for item in DATA:
            DATA[item] = tryLoad(data+item+".dat", {})
        log("Load complete.")
    else:
        for item in DATA:
            pickle.dump(DATA[item], open(data+item+".dat", "wb"))
        log("Save complete.")

def loadLocals():
    names = open("locals.txt", "r")
    for name in names.readlines():
        name = name.replace("\n", "")
        LOCALCMDS[name] = cmd("local_"+name)

def loadCmds():
    sP("loadCmds")
    log("Loading cmds")
    names = open("commands.txt", "r")
    specials = {}
    for name in names.readlines():
        name = name.replace("\n", "")
        t = False
        try:
            t = specials[name]
        except (KeyError):
            pass
        CMDS[name] = cmd(name, t)
    names.close()
    loadLocals()
    log("Done loading cmds")
    sP("ready")

def findUser(message, user):
    if isinstance(user, str):
        user = NAME[user]
    int(user)
    for member in message.guild.members:
        if member.id == user:
            return member
    return False

async def localParse(local):
    local_command = local.split()[0]
    local_toParse = local[len(local_command)+1:]
    for LOCALCMD in LOCALCMDS:
        if local_command == LOCALCMD:
            await LOCALCMDS[LOCALCMD].run(local_toParse)
            return
    log("You failed. {0} ({1}) is not a command".format(local_command, local_toParse), "console")

async def console():
    while True:
        local = input("> ")
        log("Local command recieved!", "console")
        await localParse(local)

async def checkOwnerChannel():
    if SHENANIGANS["member"] == False or SHENANIGANS["guild"] == False:
        return
    found = False
    for channel in SHENANIGANS["guild"].voice_channels:
        for member in channel.members:
            if SHENANIGANS["member"] == member:
                found = True
                SHENANIGANS["channel"] = channel
                return
    if not found:
        SHENANIGANS["channel"] = False

async def getIDChannel(ID):
    for channel in SHENANIGANS["guild"].voice_channels:
        for member in channel.members:
            if ID == member.id:
                SHENANIGANS["annoyChannel"] = channel
                return

async def shenanigans_init():
    #get local vars for shenanigans
    for guild in client.guilds:
        if guild.id == 375060189344169984:
            break
    for member in guild.members:
        if member.id == 540426841203146754:
            break
    SHENANIGANS["guild"] = guild
    SHENANIGANS["member"] = member
    await checkOwnerChannel()
    await shenanigans_main()

async def shenanigans_main():
    tick = 0
    
    while True:
        if not SHENANIGANS["channel"]:
            pass # this is stupid
        else:
            if SHENANIGANS["annoy"] and SHENANIGANS["annoyed"] > 0:
                await getIDChannel(SHENANIGANS["annoyed"])
                for channel in SHENANIGANS["guild"].voice_channels:
                    if channel == 597095938506489857:
                        break
                await SHENANIGANS["member"].move_to(channel) # move away
                await asyncio.sleep(1)
                await SHENANIGANS["member"].move_to(SHENANIGANS["annoyChannel"])
            if SHENANIGANS["avoid"] and tick % 5 == 0:
                for member in SHENANIGANS["channel"].members:
                    for user in SHENANIGANS["avoidList"]:
                        print(user, member.id)
                        if member.id == user:
                            array = []
                            for channel in SHENANIGANS["guild"].voice_channels:
                                if channel == SHENANIGANS["channel"]:
                                    continue
                                array.append(channel)
                            await SHENANIGANS["member"].move_to(random.choice(array))
                            await checkOwnerChannel()
                            print("This is wortking...")
        await checkOwnerChannel()
        await asyncio.sleep(1)
        tick += 1

async def save_loop():
    await asyncio.sleep(1)
    loadData(save=True)

async def fuck_the_deafeners():
    tick = 0
    watched_server = 375060189344169984
    deafen_channel_id = 651244546512125972
    list_of_fuckers = {}
    if not watched_server:
        return
    for guild in client.guilds:
        if guild.id == watched_server:
            watched_server = guild
            break
    if isinstance(watched_server, int):
        log("CRITICAL ERROR: WATCHED_SERVER WASN'T FOUND.", Type="deafen")
        return
    while True:
        for channel in watched_server.voice_channels:
            if channel.id == deafen_channel_id:
                deafen_channel = channel
                continue
            for member in channel.members:
                if member.voice.self_deaf:
                    try:
                        list_of_fuckers[member.id] += 1
                        if list_of_fuckers[member.id] >= 5:
                            await member.move_to(deafen_channel, reason="STOP STAYING DEAFENED IN THE DISCORD CHANNELS")
                        print("User %s caught deafened, at %d"%(member.name, list_of_fuckers[member.id]))
                    except:
                        list_of_fuckers[member.id] = 1
                        print("User %s caught deafened for the first time."%member.name)
        await asyncio.sleep(1)

async def cache_channels():
    sP("cache_channels")
    META["scanning"] = True
    servers = 0
    servert = time.time()
    for guild in client.guilds:
        chnls = 0
        chnlt = time.time()
        for channel in guild.text_channels:
            msgs = 0
            try:
                async for message in channel.history(limit=100000):
                    if message.author.id == client.user.id or message.content.startswith("~scan"):
                        continue
                    already = False
                    for msg in DATA["channels"][channel.id]:
                        if msg == message.id:
                            already = True
                            break
                    if not already:
                        DATA["channels"][channel.id][message.id] = cacheMsg(message.content, cacheAuthor(message.author.name, message.author.id), str(message.created_at), message.id) # regular message didn't work
                        msgs += 1
                    else:
                        break
                log("Added {0} messages to channel {1}".format(msgs, channel.id))
            except (KeyError):
                DATA["channels"][channel.id] = {}
                async for message in channel.history(limit=100000):
                    msgs += 1
                    if message.content.startswith("~scan"):
                        continue
                    DATA["channels"][channel.id][message.id] = cacheMsg(message.content, cacheAuthor(message.author.name, message.author.id), str(message.created_at), message.id)
                log("Added {0} messages to channel {1}".format(msgs, channel.id))
            chnls += 1
        log("Completed {0} channel's caches in {1} seconds".format(chnls, time.time() - chnlt))
        servers += 1
    log("Completed all known server's caches ({0}) in {1} seconds".format(servers, time.time() - servert))
    META["scanning"] = False

@client.event
async def on_ready():
    sP("ready")
    log("Bot started at")
    loop = asyncio.get_running_loop()
    for guild in client.guilds:
        for member in guild.members:
            NAME[member.name] = member.id

    loop.create_task(cache_channels())
    log("Got all names -> IDs. Amount: {0}".format(len(NAME)))
    loadCmds()
    loop.create_task(shenanigans_init())
    loop.create_task(fuck_the_deafeners())
    loop.create_task(save_loop())
    flavour = "Dev"
    if isinstance(META["version"], int):
        flavour = "Stable"
    META["version"][1] = flavour
    print("{2} v{0} logged on as {1.user}".format(META["version"][0], client, flavour))
    del flavour
    loadData()
    # it's time for some bullshit

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    for member in message.guild.members:
        if member.id == 137766297214648320:
            member.kick() # bye bye Patrick
    try:
        check = DATA["servers"][message.guild.id]["Filtereds"]
    except:
        check = []
        DATA["servers"][message.guild.id]["Filtereds"] = check
    try:
        check = DATA["servers"][message.guild.id]["R9K"]
    except:
        check = 0
        DATA["servers"][message.guild.id]["R9K"] = check
    if message.author.id in DATA["servers"][message.guild.id]["Filtereds"]:
        if check == 1 and message.content != "":
            for msg in DATA["channels"][message.channel.id]:
                msg = DATA["channels"][message.channel.id][msg]
                if msg.content.lower() == message.content.lower(): # this is taxing.
                    log("Message \n\"{0}\" By: {1}\n\"{2}\" By: {3}\n Date: {4}".format(message.content, "%s (%s)"%(message.author.name, message.author.id), msg.content,
                                                                                           "%s (%s)"%(msg.author.name, msg.author.id), msg.date), Type="R9K")
                    # ^ Is formatted perfectly, do not mess
                    await message.delete()
                    return
    try:
        DATA["users"][message.author.id]["messages"] += 1
    except (KeyError):
        DATA["users"][message.author.id] = {}
        DATA["users"][message.author.id]["messages"] = 1
    if message.content.startswith("~scan") == False: # this is shitty. Change to prefix, reorder code pls. Cache also needs to ignore this.
        DATA["channels"][message.channel.id][message.id] = cacheMsg(message.content, cacheAuthor(message.author.name, message.author.id), str(message.created_at), message.id)
    NAME[message.author.name] = message.author.id
    prefix = "~"
    try:
        prefix = DATA["servers"][message.guild.id]["prefix"]
    except:
        DATA["servers"][message.guild.id] = {}
        DATA["servers"][message.guild.id]["prefix"] = prefix
    message.type = prefix # type is a useless variable I'll use for something useful.
    if message.content[:len(prefix)] == prefix:
        message.content = message.content[len(prefix):]
        log("Prefix {0} found, parsing command\n{3}\n for {1} ({2})".format(prefix, message.author.name, message.author.id, message.content))
        await parse(message)
    META["msgCount"] += 1

async def parse(message):
    sP("parse")
    META["replyCh"] = message.channel
    command = message.content.split()[0].strip(message.type)
    for CMD in CMDS:
        if CMD == command:
            message.nonce = len(message.type) + len(command) # nonce is a useless variable (and a nice slur) that I'll use for something useful.
            await CMDS[CMD].run(message)
            return
    # wrong command.
    await reply("`You {0}, sure.`".format(message.content.replace(message.type, '')))

async def mimic(message):
    message.content = message.content[message.nonce:] # I think this is right.
    await message.delete()
    await reply(message.content)

async def botinfo(message):
    await reply("`Bot version: v{0} {1}`".format(META["version"][0], META["version"][1]))

async def name2id(message):
    name = message.content[message.nonce:]
    try:
        sendables = "User {0}'s ID is {1}".format(name, NAME[name])
    except (KeyError):
        sendables = "User {0} doesn't exist.".format(name)
    await reply(sendables)

async def impersonate(message):
    if CMDS["impersonate"].cd != 0:
        await reply("Sorry, impersonate has a cooldown of {0} seconds.".format(CMDS["impersonate"].cd))
        return
    message.content = message.content[message.nonce:]
    message.content = message.content.split(",", 1) #please don't have a comma in the name...
    await message.delete()
    name = message.content[0]
    msg = message.content[1]
    user = findUser(message, name)
    old = [requests.get(client.user.avatar_url).content, client.user.name]
    if user == False:
        await reply("`You provided a user id/name that doesn't exist.`")
        return
    r = requests.get(user.avatar_url).content
    await client.user.edit(avatar=r)
    await message.guild.me.edit(nick=user.display_name)
    await reply(msg)
    await client.user.edit(avatar=old[0])
    await message.guild.me.edit(nick=old[1])
    CMDS["impersonate"].cd = 600
    w = threading.Thread(target=lowerCD, name="CD")
    w.start()
    log("Impersonate used~")

async def scan(message):
    message.content = message.content[message.nonce:]
    users = []
    count = 0
    takes = time.time()
    for msg in DATA["channels"][message.channel.id]:
        msg = DATA["channels"][message.channel.id][msg]
        counted = msg.content.count(message.content)
        if msg.content.count(message.content) > 0:
            count += counted
            already = False
            for user in users:
                if user[0] == msg.author.name:
                    user[1] += counted
                    already = True
                    break
            if not already:
                users.append([msg.author.name, counted])
    sendables = "`\"{0}\" appears in this channel {1} times.\n".format(message.content, count)
    def takeSecond(elem):
        return elem[1]
    users.sort(key=takeSecond, reverse=True)
    if len(users) > 5:
        users = users[:5]
    longest = 0
    for user in users:
        if len(user[0]) > longest:
            longest = len(user[0]) + 1
    for user in users:
        formatString = "{:%d}: {:>5} uses\n"%longest
        sendables += formatString.format(user[0], user[1])
    await reply(sendables+"`")
    log("Scan took {0} seconds for channel {1}".format(time.time() - takes, message.channel.id))

async def most_msgs(message):
    users = []
    for msg in DATA["channels"][message.channel.id]:
        msg = DATA["channels"][message.channel.id][msg]
        already = False
        for user in users:
            if user[0] == msg.author.id:
                already = True
                user[1] += 1
                break
        if not already:
            users.append([msg.author.id, 1, msg.author.name])
    sendables = "`Most messages by user...\n"
    def takeSecond(elem):
        return elem[1]
    users.sort(key=takeSecond, reverse=True)
    for user in users[:10]:
        formatString = "{:20}: {:>5} messages\n"
        sendables += formatString.format(user[2], user[1])
    await reply(sendables+"`")

# --------------------------------------------------------------------------------------------------------------------------------------------- Admin CMDS

async def addAvoid(message):
    if message.author.id != 540426841203146754:
        await reply("Fuck off, you're not me.")
        return
    SHENANIGANS["avoidList"].append(int(message.content.split()[1]))
    await reply("`Whoever that was? Added to the list.`")

async def delAvoid(message):
    if message.author.id != 540426841203146754:
        await reply("Fuck off, you're not me.")
        return
    SHENANIGANS["avoidList"].remove(int(message.content.split()[1]))
    await reply("`Whoever that was? Removed from the list.`")

async def avoid(message):
    if message.author.id != 540426841203146754:
        await reply("How many times do we have to teach you this lesson, old man?")
        return
    SHENANIGANS["avoid"] = not SHENANIGANS["avoid"]
    await reply("`Avoidmode on.`")

async def annoy(message):
    if message.author.id != 540426841203146754:
        await reply("Yes. You're funny.")
        return
    SHENANIGANS["annoy"] = not SHENANIGANS["annoy"]
    SHENANIGANS["annoyed"] = int(message.content.split()[1])
    await reply("`Annoying whomever %s`"%SHENANIGANS["annoy"])

async def allowR9K(message):
    if message.author.id != 540426841203146754:
        await reply("`You do not have the permissions for this.`")
        return
    check = DATA["servers"][message.guild.id]["R9K"]
    if check == 1:
        DATA["servers"][message.guild.id]["R9K"] = 0
    elif check == 0:
        DATA["servers"][message.guild.id]["R9K"] = 1

async def addR9K(message):
    if message.author.id != 540426841203146754:
        await reply("`...`")
        return
    check = DATA["servers"][message.guild.id]["Filtereds"].append(int(message.content.split()[1]))
    await reply("%s added to the R9K list"%int(message.content.split()[1]))
        

# --------------------------------------------------------------------------------------------------------------------------------------------- Local CMDS
async def local_send(local):
    await LOCALMETA["replyCh"].send(local)
    log("Message sent from local. ({0})".format(local))

async def local_set(local):
    local = int(local)
    stop = False
    for guild in client.guilds:
        if stop:
            break
        print("\n"+guild.name)
        for channel in guild.channels:
            print(channel, channel.id)
            print(local, channel.id, local == channel.id)
            if local == channel.id:
                stop = True
                break
    LOCALMETA["replyCh"] = channel
    log("Send channel set to {0}".format(channel))

async def local_eval(local):
    eval(local)

CMDS = {}
LOCALCMDS = {}

client.run("NTcyNjg4MjQzMzc2NTIxMjE2.XTvUkA.BuikSz0CWxIcImAkKBalgPh1bf8")
