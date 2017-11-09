" Ducktator v0.01 "

" Imports "
import discord
import asyncio
import aiohttp
from discord.ext import commands

bot = commands.Bot(command_prefix='!', description='')
adminRoleId = '218073874703712257'
timedOutUser = {'a': 10, 'b': 0, 'c': 3}
censoredList = []
                   
@bot.event
async def on_ready():
    bot.remove_command("help")
    print('Logged in as %s, ID: %s' % (bot.user.name, bot.user.id))

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

"----------------------------------------- Admin Commands ---------------------------------------------------------------------"

" Timeout "
@bot.command(pass_context=True)
async def timeout(ctx, target, time):
    if await isAdmin(ctx) is True:
        timedOutUser[target] = int(time);
        await bot.say('Timed out %s for %s minute(s)' % (target, time))

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
    
    " Time outs "
    for x in timedOutUser:
        if message.author.name == x and timedOutUser[x] != 0:
            await bot.delete_message(message)
        
    " Censoring "
    try:
        for word in censoredList:
            if word in message.content.lower().split() or word in message.content.lower():
                await bot.delete_message(message)
    except Exception:
        pass
    
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

" Kills the bot "
@bot.command(pass_context=True)
async def killDuck(ctx):
    if await isAdmin(ctx) == True:
        await bot.logout()
    else:
        return

" BOT Token "
bot.loop.create_task(timeDown())
