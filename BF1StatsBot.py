# A Battlefield 1 stat bot for Discord, made by 360camera#5204

import discord
import requests
import configparser
import sys
from os import path
from discord.ext import commands
from discord.ext.tasks import loop

# Remove discord.py default commands

client = commands.Bot(command_prefix="$")
client.remove_command("help")
client.remove_command("invite")

# Parse config.txt

cParse = configparser.RawConfigParser()
cFilePath = path.join((path.abspath(path.dirname(sys.argv[0]))), "config.txt")
cParse.read(cFilePath)

botToken = cParse.get("BotConfig", "botToken")
footerMessage = cParse.get("BotConfig", "footerMessage")
networkingErrorMessage = cParse.get("BotConfig", "networkingErrorMessage")
apiLink = cParse.get("BotConfig", "apiLink")
inviteLink = cParse.get("BotConfig", "inviteLink")
helpMessage = cParse.get("BotConfig", "helpMessage")
regionNames = cParse.get("BotConfig", "regionNames")
githubLink = cParse.get("BotConfig", "githubLink")

# Basic function definitions

def parseArgs(args, nameBool): # Parse arguments, if nameBool is true split name and arguments
    formattedArgs = ""
    formattedName = ""
    setUsername = nameBool
    i = len(args)
    for arg in args:
        if setUsername:
            formattedName = str(arg)
            setUsername = False
            i -= 1
        else:
            formattedArgs = formattedArgs + str(arg)
            i -= 1
            if i != 0:
                formattedArgs = formattedArgs + " "
    return (formattedArgs, formattedName)

def topKills(killersType, data): # Returns top killers for topweapons and topkills commands, killersType should be either "weapon" or "vehicle"
    # Process data
    bestKillers = {}
    bestKillersTemp = ""
    bestKillsTemp = 0
    for i in range(25):
        for item in data[str(killersType + "s")]:
            if item["kills"] > bestKillsTemp and item[str(killersType + "Name")] not in bestKillers:
                bestKillersTemp = item[str(killersType + "Name")]
                bestKillsTemp = item["kills"]
        if bestKillsTemp > 0:
            bestKillers[bestKillersTemp] = bestKillsTemp
            bestKillsTemp = 0
        else:
            break
    # Format and return embed content
    embedContent = ""
    i = 0
    for killer in bestKillers.items():
        i += 1
        embedContent = embedContent + killer[0] + ": " + str(killer[1]) + " kills"
        if i != len(bestKillers):
            embedContent = embedContent + "\n"
    if len(bestKillers) < 25:
        embedContent = embedContent + "\n\nThis user has no kills with other " + killersType + "s, so less than 25 are displayed."

    return embedContent

# Startup definitions

@client.event
async def on_ready(): # On bot launch start updateStatus loop
    print("Bot is ready")
    updateStatus.start()

@loop(minutes=5)
async def updateStatus(): # Updates status with guild and member counts
    discordServerList = client.guilds
    discordMemberCount = 0
    for server in discordServerList:
        discordMemberCount += server.member_count-1
    await client.change_presence(activity=discord.Game(name="$help | In " + str(len(discordServerList)) + " servers with " + str(discordMemberCount) + " members"))

# Bot commmand definitons

@client.command()
async def help(ctx): # Help message
    embed = discord.Embed(title="Available commands:", description=helpMessage)
    embed.set_footer(text=footerMessage)
    await ctx.send(embed=embed)

@client.command()
async def invite(ctx): # Invite message
    embed = discord.Embed(title="Click this link to invite this bot to your own server.", url=inviteLink)
    embed.set_footer(text=footerMessage)
    await ctx.send(embed=embed)

@client.command()
async def github(ctx): # Link to Github page
    embed = discord.Embed(title="Click this link to visit the bot's Github page.", url=inviteLink)
    embed.set_footer(text=footerMessage)
    await ctx.send(embed=embed)

@client.command()
async def stats(ctx, player): # General stats
    rs = requests.get(apiLink + "/stats/?name=" + str(player))
    rp = requests.get(apiLink + "/progress/?name=" + str(player))
    if rs.status_code == 200 and rp.status_code == 200: # HTTP OK
        rs = rs.json()
        rp = rp.json()
        # Format and send message
        embed = discord.Embed(title="Stats for " + str(player), description="""Multiplayer:
        Rank: """ + str(rs["Rank"]) + """
        Skill: """ + str(rs["Skill"]) + """
        SPM: """ + str(rs["SPM"]) + """
        Win %: """ + rs["Win"] + """
        Best Class: """ + rs["Best Class"] + """
        Accuracy: """ + rs["Accuracy"] + """
        Headshots: """ + rs["Headshots"] + """
        Time played: """ + rs["Time played"] + """
        KDR: """ + str(rs["K/D"]) + """
        KPM: """ + str(rs["KPM"]) + """
        Infantry K/D: """ + str(rs["infantry K/D"]) + """
        Infantry KPM: """ + str(rs["infantry KPM"]) + """
        Kills: """ + str(rs["Kills"]) + """
        Deaths: """ + str(rs["Deaths"]) + """
        Matches played: """ + str(rs["roundsPlayed"]) + """
        Wins: """ + str(rs["Wins"]) + """
        Losses: """ + str(rs["Loses"]) + """
        Longest headshot: """ + str(rs["longestHeadShot"]) + """m
        Revives: """ + str(int(rs["revives"])) + """
        Dogtags Taken: """ + str(rs["dogtagsTaken"]) + """
        Highest Killstreak: """ + str(rs["highestKillStreak"]) + """
        
        Unlocks/Progress:
        Dogtags: """ + str(rp["progress"][0]["current"]) + "/" + str(rp["progress"][0]["total"]) + """
        Weapons: """  + str(rp["progress"][1]["current"]) + "/" + str(rp["progress"][1]["total"]) + """
        Vehicles: """ + str(rp["progress"][2]["current"]) + "/" + str(rp["progress"][2]["total"]) + """
        Medals: """ + str(rp["progress"][3]["current"]) + "/" + str(rp["progress"][3]["total"]) + """
        Assignments: """ + str(rp["progress"][4]["current"]) + "/" + str(rp["progress"][4]["total"]) + """
        Codex: """ + str(rp["progress"][5]["current"]) + "/" + str(rp["progress"][5]["total"]) + """
        Ribbons: """ + str(rp["progress"][6]["current"]) + "/" + str(rp["progress"][6]["total"]))
        embed.set_footer(text=footerMessage)
        embed.set_thumbnail(url=rs["avatar"])
        await ctx.send(embed=embed)
    else:
        await ctx.send(networkingErrorMessage)

@client.command()
async def cstats(ctx, player, bfClass): # Class stats
    classes = {
        "assault": "https://i.imgur.com/jLmi6BA.png",
        "medic": "https://i.imgur.com/bQQi2lP.png", 
        "support": "https://i.imgur.com/drRe129.png", 
        "scout": "https://i.imgur.com/ZWjoXn0.png", 
        "pilot": "https://i.imgur.com/Mo0V09L.png", 
        "tanker": "https://i.imgur.com/SBO8oY0.png", 
        "cavalry": "https://i.imgur.com/Qq5y0xe.png"
    }
    if str.lower(bfClass) in classes:
        r = requests.get(apiLink + "/classes/?name=" + str(player))
        if r.status_code == 200: # HTTP OK
            r = r.json()
            # For some reason the API shuffles around the class order. We need to figure out the order of the classes.
            classIndex = {}
            for i in range(7):
                classIndex[str(r["classes"][i]["className"]).lower()] = i
            formattedClassIndex = classIndex[str(bfClass).lower()]
            bfClassTimePlayed = r["classes"][formattedClassIndex]["timePlayed"][:len(r["classes"][formattedClassIndex]["timePlayed"])-4] # Removes last 4 digits of the timePlayed string (extra zeroes)
            # Format and send message
            embed = discord.Embed(title="Stats for " + str(player) + " as " + r["classes"][formattedClassIndex]["className"], description="Score: " + str(r["classes"][formattedClassIndex]["Score"]) + """
            Kills: """ + str(r["classes"][formattedClassIndex]["kills"]) + """
            KPM: """ + str(r["classes"][formattedClassIndex]["kpm"]) + """
            Time played: """ + bfClassTimePlayed)
            embed.set_footer(text=footerMessage)
            embed.set_thumbnail(url=classes[str.lower(bfClass)])
            await ctx.send(embed=embed)
        else:
            await ctx.send(networkingErrorMessage)
    else:
        await ctx.send("Error - incorrect class specified.")

@client.command()
async def wstats(ctx, *args): # Specific weapon stats
    weaponName, player = parseArgs(args, True)
    r = requests.get(apiLink + "/weapons/?name=" + player)
    if r.status_code == 200: # HTTP OK
        r = r.json()
        messageSent = False
        for weaponData in r["weapons"]:
            if weaponData["weaponName"].lower() == weaponName.lower(): # Get data for the right weapon
                embed = discord.Embed(title="Stats for " + str(player) + " with " + weaponData["weaponName"], description="Kills: " + str(weaponData["kills"]) + """
                KPM: """ + str(weaponData["killsPerMinute"]) + """
                Accuracy: """ + weaponData["accuracy"] + """
                Headshots: """ + weaponData["headshots"] + """
                Hits per kill: """ + str(weaponData["hitVKills"]))
                embed.set_footer(text=footerMessage)
                embed.set_thumbnail(url=weaponData["image"])
                await ctx.send(embed=embed)
                messageSent = True
                break
        if messageSent == False:
            await ctx.send("Error - weapon not found. Copy and paste weapon names from $weapons.")
    else:
        ctx.send(networkingErrorMessage)

@client.command()
async def topweapons(ctx, player): # Top 25 weapons
    rs = requests.get(apiLink + "/stats/?name=" + str(player))
    rw = requests.get(apiLink + "/weapons/?name=" + str(player))
    if rs.status_code == 200 and rw.status_code == 200: # HTTP OK
        rs = rs.json()
        rw = rw.json()
        embed = discord.Embed(title="Top 25 weapons for " + str(player) + " by kills:", description=topKills("weapon", rw))
        embed.set_footer(text=footerMessage)
        embed.set_thumbnail(url=rs["avatar"])
        await ctx.send(embed=embed)

@client.command()
async def weapons(ctx): # Send list of weapons
    embed = discord.Embed(title="BF1 Weapons List", url="https://pastebin.com/v7Lq8FxY", description="Due to Discord's character limit, the list of supported weapons can't be displayed in Discord. Click the link above to view the list. If the bot isn't returning data for a specific weapon, copy and paste a weapon name from the link. Due to its implementation in-game, data for the Burton LMR Trench cannot be grabbed.")
    embed.set_footer(text=footerMessage)
    await ctx.send(embed=embed)

@client.command()
async def vstats(ctx, *args): # Specific vehicle stats
    vehicleName, player = parseArgs(args, True)
    r = requests.get(apiLink + "/vehicles/?name=" + player)
    if r.status_code == 200: # HTTP OK
        r = r.json()
        messageSent = False
        for vehicleData in r["vehicles"]:
            if vehicleData["vehicleName"].lower() == vehicleName.lower():
                embed = discord.Embed(title="Stats for " + str(player) + " with " + vehicleName, description="Kills: " + str(vehicleData["kills"]) + """
                KPM: """ + str(vehicleData["killsPerMinute"]) + """
                Vehicles of this type destroyed: """ + str(vehicleData["destroyed"]))
                embed.set_footer(text=footerMessage)
                embed.set_thumbnail(url=vehicleData["image"])
                await ctx.send(embed=embed)
                messageSent = True
                break
        if messageSent == False:
            await ctx.send("Error - vehicle not found. Copy and paste vehicle names from $vehicles.")
    else:
        ctx.send(networkingErrorMessage)

@client.command()
async def topvehicles(ctx, player): # Top 25 vehicles
    rs = requests.get(apiLink + "/stats/?name=" + str(player))
    rv = requests.get(apiLink + "/vehicles/?name=" + str(player))
    if rs.status_code == 200 and rv.status_code == 200: # HTTP OK
        rs = rs.json()
        rv = rv.json()
        # Send the embed
        embed = discord.Embed(title="Top 25 vehicles for " + str(player) + " by kills:", description=topKills("vehicle", rv))
        embed.set_footer(text=footerMessage)
        embed.set_thumbnail(url=rs["avatar"])
        await ctx.send(embed=embed)

@client.command()
async def vehicles(ctx): # Send list of vehicles
    embed = discord.Embed(title="BF1 Vehicles List", url="https://pastebin.com/EpgrFXpv", description="Due to Discord's character limit, the list of supported vehicles can't be displayed in Discord. Click the link above to view the list. If the bot isn't returning data for a specific vehicle, copy and paste a vehicle name from the link.")
    embed.set_footer(text=footerMessage)
    await ctx.send(embed=embed)

@client.command()
async def gstats(ctx, player): # Stats for gamemodes
    rs = requests.get(apiLink + "/stats/?name=" + str(player))
    rg = requests.get(apiLink + "/gamemode/?name=" + str(player))
    if rs.status_code == 200 and rg.status_code == 200:
        rs = rs.json()
        rg = rg.json()
        i = 0
        # Format the embed message
        embedContent = ""
        for gamemode in rg["gamemodes"]:
            i += 1
            appendEmbed = "**" + gamemode["gamemodeName"] + """**
            Wins: """ + str(gamemode["wins"]) + """
            Losses: """ + str(gamemode["losses"]) + """
            Win %: """ + str(gamemode["winPrecentage"]) + """%
            Score: """ + str(gamemode["score"])
            embedContent = embedContent + appendEmbed
            if i != len(rg["gamemodes"]):
                embedContent = embedContent + "\n\n"
        embed = discord.Embed(title="Gamemode stats for " + str(player), description=embedContent)
        embed.set_footer(text=footerMessage)
        embed.set_thumbnail(url=rs["avatar"])
        await ctx.send(embed=embed)
    else:
        ctx.send(networkingErrorMessage)

@client.command()
async def ssearch(ctx, *args): # Server list search
    searchQuery = parseArgs(args, False)[0]
    # Make request and format embed content
    r = requests.get(apiLink + "/servers/?name=" + str(searchQuery))
    if r.status_code == 200: # HTTP OK
        r = r.json()
        embedContent = ""
        i = 0
        for server in r["servers"]:
            i += 1
            embedContent = embedContent + "**" + server["prefix"] + "**\nPlaying  " + server["mode"] + " on " + server["currentMap"] + "\n" + server["serverInfo"] + " players online (" + str(server["inQue"]) + " players in queue)"
            if i != len(r["servers"]):
                embedContent = embedContent + "\n\n"
        if len(r["servers"]) == 0:
            embedContent = "No servers were found matching your search."
        # Send embed along with map preview if only 1 server is found
        embed = discord.Embed(title="Results for search \"" + str(searchQuery) + "\"", description=embedContent)
        embed.set_footer(text=footerMessage)
        if len(r["servers"]) == 1:
            embed.set_thumbnail(url=r["servers"][0]["url"])
        await ctx.send(embed=embed)    
    else:
        await ctx.send(networkingErrorMessage)

@client.command()
async def sdetails(ctx, *args): # Specific server info
    serverName = parseArgs(args, False)[0]
    r = requests.get(apiLink + "/detailedserver/?name=" + str(serverName))
    if r.status_code == 200:
        r = r.json()
        # Format general body
        generalBody = "Server description: \"" + r["description"] + """\"
        Server location: """ + regionNames[r["region"]] + " - " + r["country"] + """
        This server has """ + r["favorites"] + """ favorites
        """ + str(r["playerAmount"]) + "/" + str(r["maxPlayerAmount"]) + " players online [" + str(r["inQueue"]) + """ players in queue]
        Playing """ + r["mode"] + " on " + r["currentMap"]
        # Format rotation section
        rotationBody = ""
        gamemodeMaps = {}
        for i in r["rotation"]:
            if i["mode"] in gamemodeMaps:
                gamemodeMaps[i["mode"]] = gamemodeMaps[i["mode"]] + ", " + i["mapname"]
            else:
                gamemodeMaps[i["mode"]] =  i["mode"] + " on " + i["mapname"]
        isFirst = True
        for i in gamemodeMaps.items():
            if not isFirst:
                rotationBody = rotationBody + "\n"
            rotationBody = rotationBody + i[1]
        # Format settings section
        settingsBody = ""
        isFirst = True
        for i in r["settings"].items():
            if not isFirst:
                settingsBody = settingsBody + "\n\n"
            else:
                isFirst = False
            isFirstNested = True
            for j in i[1].items(): # There are 5 seperate settings categories
                if not isFirstNested:
                    settingsBody = settingsBody + "\n"
                else:
                    isFirstNested = False
                settingsBody = settingsBody + j[0] + ": " + j[1]
        # Send embed
        embed = discord.Embed(title=r["prefix"], description=generalBody)
        embed.set_thumbnail(url=r["currentMapImage"])
        embed.add_field(name="Map Rotation", value=rotationBody, inline=False)
        embed.add_field(name="Settings", value=settingsBody, inline=False)
        await ctx.send(embed=embed)    
    else:
        ctx.send(networkingErrorMessage)

@client.command()
async def pop(ctx): # Server populations
    r = requests.get(apiLink + "/status")
    if r.status_code == 200:
        r = r.json()
        embed = discord.Embed(title="Battlefield 1 Playerbase Statistics")
        for region in r["regions"]:
            embedContent = "Servers: " + str(region["serverAmount"]) + """
            Players active: """ + str(region["soldierAmount"]) + """
            Players in queue: """ + str(region["queueAmount"]) + """
            Spectators: """ + str(region["spectatorAmount"])
            embed.add_field(name=regionNames[region["region"]], value=embedContent)
        embed.set_footer(text=footerMessage)
        await ctx.send(embed=embed)
    else:
        ctx.send(networkingErrorMessage)

# Error handling definition

@client.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        errorMessage = "Error - this command is missing one or more arguments. Use $help to view the proper usage of commands and make sure the player's name is correct."
    else:
        errorMessage = "An unknown error occured while running this command. Use $help to view the proper usage of commands and make sure the player's name is correct. If this error persists, contact 360camera#5204."
    embed = discord.embed(title="Error", description=errorMessage)
    embed.set_footer(text=footerMessage)
    await ctx.send(embed=embed)

client.run(botToken)