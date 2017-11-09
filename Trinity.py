" Ducktator v0.01 "

" Imports "
import discord
import asyncio
import aiohttp
from discord.ext import commands

bot = commands.Bot(command_prefix='!', description='')
adminRoleId = '218073874703712257'
timedOutUser = {'a': 10, 'b': 0, 'c': 3}
helpMessage = "```Available Commands:\n!hug *Name* - Give a hug to someone!\n!pew - Pew pews!\n!streams - Shows the status of our streamers!\n!umbasa *Name* - Umbasa!```"
adminHelpMessage = "%s ```Admin Commands:\n!timeout *Name* *Time* - Times a user out for the time measured in minutes\n!allow *Name* - Removes the user from timeout```" % helpMessage
                   
@bot.event
async def on_ready():
    await bot.change_status(game=discord.Game(name='!commands for commands!'))
    bot.remove_command("help")
    print('Logged in as %s, ID: %s' % (bot.user.name, bot.user.id))

" Welcome message for new members! "
@bot.event
async def on_member_join(member):
    await asyncio.sleep(1)
    await bot.send_message(bot.get_channel('218071354929446913'), 'Welcome %s to %s!' % (member.mention, bot.get_server('218071354929446913').name))

" Help command! "
@bot.command(pass_context=True)
async def commands(ctx):
    if await isAdmin(ctx) is True:
        await bot.say(adminHelpMessage)
    else:
        await bot.say(helpMessage)

" Pew! "
@bot.command()
async def pew():
    await bot.say('(づ｡◕‿‿◕｡)づ Pew pew!')

" Hug! "
@bot.command(pass_context=True)
async def hug(ctx, target):
    target = ctx.message.server.get_member_named(target)
    if target != None:
        await bot.say('Everything will be fine! (っ◕‿◕)っ %s' % target.mention)
        
" Umbasa! "
@bot.command(pass_context=True)
async def umbasa(ctx, target):
    victim = ctx.message.server.get_member_named(target)
    if victim != None:
        await bot.say('Umbasa %s!' % victim.mention)

" Streaming Interactions! "
@bot.command()
async def streams():
    
    " Add new streamers to the lists below and change '4' to the number of streamers " 
    streamList = ['https://api.twitch.tv/kraken/streams/vallew/?client_id=8rtrj6sidvvf8zoh0xtvkum20tphwga', 'https://api.twitch.tv/kraken/streams/frozenpanini/?client_id=8rtrj6sidvvf8zoh0xtvkum20tphwga', 'https://api.twitch.tv/kraken/streams/xcyle/?client_id=8rtrj6sidvvf8zoh0xtvkum20tphwga', 'https://api.twitch.tv/kraken/streams/ZeroTypeXX/?client_id=8rtrj6sidvvf8zoh0xtvkum20tphwga']
    streamers = ['Ducky', 'Frozenpanini', 'Xcyle', 'ZeroTypeXX']
    status = [''] * 4
    message = ''
    x = 0

    msg = await bot.say('Checking streams...')
    for stream in streamList:
        async with aiohttp.get(stream) as req:
            data = await req.json()
            if data.get('stream') != None:
                status[x] = "%s's online, playing %s at %s\n\n" % (streamers[x], data.get('stream').get('game'), data.get('stream').get('channel').get('url'))
            else:
                status[x] = "%s's offline.\n\n" % streamers[x]
            x = x + 1
        
    async with aiohttp.get('http://api.hitbox.tv/user/xcyle') as req2:
        data2 = await req2.json()
        if data2.get('is_live') == '1':
            status[2] = "%s's online on hitbox! http://www.hitbox.tv/Xcyle\n" % streamers[2]
            
    for x in status:
        message += x

    await bot.edit_message(msg, message)

"----------------------------------------- Admin Commands ---------------------------------------------------------------------"

" Timeout "
@bot.command(pass_context=True)
async def timeout(ctx, target, time):
    if await isAdmin(ctx) is True:
        timedOutUser[target] = int(time);
        await bot.say('Timed out %s for %s minutes' % (target, time))

" Allow "
@bot.command(pass_context=True)
async def allow(ctx, target):
    if await isAdmin(ctx) is True:
        for x in timedOutUser:
            if target == x:
                timedOutUser[x] = 0
                
" Timeout Checker, removes messages"
@bot.event
async def on_message(message):
    for x in timedOutUser:
        if message.author.name == x and timedOutUser[x] != 0:
            await bot.delete_message(message)
    await bot.process_commands(message)

" Fix Timeouts "
async def timeDown():
    await bot.wait_until_ready()
    while not bot.is_closed:
        for x in timedOutUser:
            if timedOutUser[x] != 0:
                timedOutUser[x] -= 1
        await asyncio.sleep(60)

" Checks if ctx is Admin "
@asyncio.coroutine
async def isAdmin(ctx):
    isAdmin = False
    
    for x in ctx.message.author.roles:
       if x.id == adminRoleId:
           isAdmin = True
           return isAdmin
    return isAdmin

" Saves players and kills the bot "
@bot.command(pass_context=True)
async def killTrinity(ctx):
    if await isAdmin(ctx) == True:
        await bot.logout()
    else:
        return

" BOT Token "
bot.loop.create_task(timeDown())
