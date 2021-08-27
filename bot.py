import asyncio
import discord
import os
from crawler import TWcfg
from discord.ext import commands, tasks
import openpyxl
import twint
import nest_asyncio
import itertools
import pandas as pd
nest_asyncio.apply()

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_rows', None)

crawl = TWcfg()
tCrawl = TWcfg()
crawlPeriod = 3
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Testing...")


@bot.command(pass_context=True)
async def info(ctx: object, *keyword: str):
    '''
    await asyncio.gather(
        asyncio.to_thread(crawl.keyword(keyword)),
        asyncio.to_thread(crawl.run()),
        asyncio.sleep(1))
        :type ctx: object
   '''
    keyword = ' '.join(keyword)
    await ctx.send(keyword)
    result = crawl.output(keyword)
    ret = result['link'].to_dict()
    text = 'Result:'
    ### embed = discord.Embed(title="Result", description="",color=0x5CD1E5)
    for i, (key, val) in enumerate(ret.items(), start=1):
        if i % 5 == 0:
            text = '\n'.join([text, f'{key}: {val}'])
            await ctx.send(text)
            text = '-----------------'
            continue
        else:
            text = '\n'.join([text,f'{key}: {val}'])
    await ctx.send(text)
    ### await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send("pong")


@bot.command(pass_context=True)
async def cfg(ctx, cfgobj, *cfgval):
    cfgval = ' '.join(cfgval)
    #tCrawl.cfg(cfgobj=cfgval)
    proccfg(cfgobj, cfgval)
    await ctx.send(f'{cfgobj}의 값이 {cfgval}로 변경되었습니다.')


def proccfg(cfgobj, cfgval):
    global crawlPeriod
    if cfgobj == "limit":
        val = int(cfgval) // 5
        tCrawl.cfg(Limit=val)
    if cfgobj == "period":
        print(f'{str(int(cfgval))}')
        crawlPeriod = int(cfgval)
    if cfgobj == "keyword":
        tCrawl.cfg(Search=str(cfgval))


@bot.command(pass_context=True)
async def on(ctx):
    await ctx.send(f'자동 크롤러가 켜졌습니다. 이제 {crawlPeriod}분마다 자동으로 크롤링됩니다.')
    await cyclecrawl(ctx)

@bot.command(pass_context=True)
async def limit(ctx, newlim):
    newlim = int(newlim) // 5
    crawl.Limit = int(newlim)
    await ctx.send(f'수동 크롤러의 limit이 {newlim*5}으로 변경되었습니다.')

@tasks.loop(minutes=crawlPeriod)
async def cyclecrawl(ctx):
    await asyncio.sleep(0)
    result = asyncio.to_thread(crawl.run())
    file = discord.File(result.xlslfy)
    await ctx.send("File", file=file)


if __name__ == "__main__":
    bot.run('ODc5NDk0MTM5MDAyMTI2NDA2.YSQivg.khDr7Ulvu2PYKvB0-nLW10jh7gg')