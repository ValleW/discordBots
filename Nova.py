" Nova v0.00 "

" Imports "
import discord
import asyncio
import pickle
from discord.ext import commands

bot = commands.Bot(command_prefix='!', description='')
adminRoleId = '218073874703712257'
gameChannel = '222416075227136005'

helpMessage = "```Available Commands:\n!play - Enter the game(use once only)!\n!coins - Shows the amount of coins you have!\n!topic - Shows the current bet topic!\n!bet *amount* \"answer\" - type an amount and the answer to the topic, yay = 1, nay = 0 (e.g. !bet 10 yay)!\n!currentbets - Shows everyone's current bets!\n```"
adminHelpMessage = "%s```!startbet \"topic\" - Starts a bet with the written topic!\n!answer \"answer\" - Ends the current bet with the answer written!\n!setCoins *user* *amount* - Sets the users coins to specified amount('all' works for everyone)!\n!resetCoins *user* - Resets the users coins back to standard(all works for everyone)!\n```" % helpMessage


" File Handling "
players = ''
currentTopic = ''
answer = ''
bettings = ''
choices = ''

try:
    print('Loading file...')
    playersFile = open('players.dat', 'rb')
    players = pickle.load(playersFile)
    playersFile.close()
except Exception:
     print("Error: Open File @ play()")

"------------------------ Player Commands ------------------------"

@bot.event
async def on_ready():
    await bot.change_status(game=discord.Game(name='!commands for commands!'))
    bot.remove_command("help")
    print('Logged in as %s, ID: %s' % (bot.user.name, bot.user.id))

@bot.command(pass_context=True)
async def commands(ctx):
    if ctx.message.channel.id != gameChannel:
        return
    elif await isAdmin(ctx):
        await bot.say(adminHelpMessage)
    else:
        await bot.say(helpMessage)
        
" Joins a player into the playerbase "
@bot.command(pass_context=True)
async def play(ctx):
    oldPlayer = False
    
    if ctx.message.channel.id != gameChannel:
        return
    else:
        for x in players:
            if x == ctx.message.author.name:
                oldPlayer = True

        if oldPlayer == True:
            await bot.say('Welcome back %s!' % ctx.message.author.mention)
        else:
            await bot.say('Hello %s! Welcome to the Hive!' % ctx.message.author.mention)
            players[ctx.message.author.name] = 100

        print(players)
        
" Shows your current coins "
@bot.command(pass_context=True)
async def coins(ctx):
    if ctx.message.channel.id != gameChannel:
        return
    else:
        for x in players:
            if x == ctx.message.author.name:
                await bot.say('%s: %s coins.' % (ctx.message.author.mention, players[x]))

" Places a bet (yay = 1, nay = 0)"
@bot.command(pass_context=True)
async def bet(ctx, coins, choice):
    global bettings
    
    if ctx.message.channel.id != gameChannel:
        return
    elif not await isAPlayer(ctx.message.author.name):
        return
    else:
        if await isLegit(ctx.message.author.name, coins):
            await bot.say('Bet accepted!')
            bettings[ctx.message.author.name] += int(coins)
            players[ctx.message.author.name] -= int(coins)
            if choice.lower() == 'yay' or choice.lower() == 'yes':
                choices[ctx.message.author.name] = 1
            elif choice.lower() == 'nay' or choice.lower() == 'no':
                choices[ctx.message.author.name] = 0
            else:
                choices[ctx.message.author.name] = choice.lower()
        else:
            await bot.say('Bet not accepted!')
        

" Shows current bet "
@bot.command(pass_context=True)
async def topic(ctx):
    global currentTopic
    if ctx.message.channel.id != gameChannel:
        return
    else:
        if not await isBetLive():
            await bot.say('No bet ongoing!')
        else:
            await bot.say('Current Bet: ```%s```' % currentTopic)

" Shows current bets by players "
@bot.command(pass_context=True)
async def currentbets(ctx):
    global bettings
    message = ''

    if ctx.message.channel.id != gameChannel:
        return
    else:
        if await isBetLive():
            for x in bettings:
                message += ('```%s: %i, %s\n```' % (x, bettings[x], choices[x]))
            await bot.say(message)
        else:
            await bot.say('No bet ongoing!')

" Starts a bet with the topic specified "
@bot.command(pass_context=True)
async def startbet(ctx, topic):
    global currentTopic
    global bettings
    
    if ctx.message.channel.id != gameChannel or not await isAdmin(ctx):
        return
    else:
        if not await isBetLive():
            currentTopic = topic
            await bot.say('Current Bet: ```%s```' % currentTopic)
            await createBettingList()
        else:
            await bot.say('Bet already running!')

" Sets the answer and ends the bet "
@bot.command(pass_context=True)
async def answer(ctx, message):
    global answer
    
    if ctx.message.channel.id != gameChannel or not await isAdmin(ctx):
        return
    else:
        if message.lower() == 'yay' or message.lower() == 'yes':
            answer = '1'
        elif message.lower() == 'nay' or message.lower() == 'no':
            answer = '0'
        else:
            answer = message
        await endbet()

"------------------------ Bettings Functions ----------------------"
        
" Bot bettings functions "
@asyncio.coroutine
async def createBettingList():
    global bettings
    global choices

    bettings = players.copy()
    for x in bettings:
        bettings[x] = 0

    choices = bettings.copy()

" Checks for an ongoing bet "
@asyncio.coroutine
async def isBetLive():
    global currentTopic

    if currentTopic != '':
        return True
    else:
        return False
    
@asyncio.coroutine
async def isAPlayer(user):
    for x in bettings:
        if x == user:
            return True
    return False

" Ends the ongoing bet "
@asyncio.coroutine
async def endbet():
    global currentTopic
    
    if await isBetLive():
        currentTopic = ''
        totalPot = 0
        winners = 0
        winnersName = ''
        
        for x in bettings:
            totalPot += bettings[x]   

        for x in choices:
            if str(choices[x]) == answer:
                if bettings[x] != 0:
                    winners += 1
                
        if winners != 0:
            for x in choices:
                if str(choices[x]) == answer:
                    if bettings[x] != 0:
                        players[x] += int(bettings[x]*1.5)
        
        await bot.say('Bet ended!')
    else:
        await bot.say('No bet ongoing!')

" Checks if the parameter is an accepted number "
@asyncio.coroutine
async def isLegit(user, coins):
    
    try:
        checkInt = int(coins)
    except ValueError:
        return False
    
    else:
        if int(coins) < 1:
            return False
        elif coins[0] == '0':
            return False
        elif players[user] < int(coins):
            return False
        elif bettings[user] != 0:
            return False
        for x in bettings:
            if x == user:
                return True
        else:
            return True


"------------------------ Admin commands -------------------------"

" Resets coins for target "
@bot.command(pass_context=True)
async def resetCoins(ctx, target):
    if ctx.message.channel.id != gameChannel or not await isAdmin(ctx):
        return
    else:
        if target == 'all':
            for x in players:
                players[x] = 100
            print('Coins reset for everyone!')
        else:
            for x in players:
                if x == target:
                    players[x] = 100
            print('Coins reset for %s!' % target)

" Set amount of coins for target "
@bot.command(pass_context=True)
async def setCoins(ctx, target, amount):
    if ctx.message.channel.id != gameChannel or not await isAdmin(ctx):
        return
    else:
        if target == 'all':
            for x in players:
                players[x] = amount
            print('Coins set for everyone!')
        else:
            for x in players:
                if x == target:
                    players[x] = amount
            print('Coins set for %s at %s!' % (target, amount))

" Checks if ctx is Admin "
@asyncio.coroutine
async def isAdmin(ctx):
    isAdmin = False
    
    for x in ctx.message.author.roles:
       if x.id == adminRoleId:
           isAdmin = True
           return isAdmin
    return isAdmin

" Saves players"
@bot.command(pass_context=True)
async def savePlayers(ctx):
    if await isAdmin(ctx):
        pickle.dump(players, open("players.dat", 'wb'))
        print('Saved!')
    else:
        return

" Saves players and kills the bot "
@bot.command(pass_context=True)
async def killNova(ctx):
    if await isAdmin(ctx):
        pickle.dump(players, open("players.dat", 'wb'))
        await bot.logout()
        print('Killed!')
    else:
        return
