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
import dotenv
import jdatetime
nest_asyncio.apply()

dotenv.load_dotenv(verbose=True)
BOT_TOKEN = os.getenv('BOT_TOKEN')

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_rows', None)

crawl = TWcfg()
tCrawl = TWcfg()
crawlPeriod = 3
bot = commands.Bot(command_prefix="!", help_command=None)


@bot.event
async def on_ready():
    print("Testing...")


@bot.command(pass_context=True)
async def help(ctx:object, *keyword: str):
    '''
    !info <keyword> : 크롤링.
    !on : 킨다.
    !ping : 봇이 죽었는지 살았는지 확인한다.
    !TODO : TODO 추가.
    !help <command> : <command>에 대한 설명
    !help : 명령어 목록
    !geo <longtitude> <latitude> <radius> : 위치를 기준으로 트윗을 검색합니다.
    '''
    keyword = ' '.join(keyword)
    print(keyword)
    embed = discord.Embed(title="Discord crawling bot, AlertBot", description="", color=0x5CD1E5)
    if keyword == "TODO":
        embed.add_field(name='!TODO <text>', value='아직 구현 안 됨', inline=False)
    elif keyword == "geo" or keyword == "GEO" or keyword == "Geo":
        embed.add_field(name='!geo <longtitude> <latitude> <radius>', value='위치를 기준으로 트윗을 검색합니다.', inline=False)
    else:
        embed.add_field(name='!info <keyword>', value='<keyword>에 해당하는 트윗을 약 20개 긁어온다.', inline=False)
        embed.add_field(name='!on <configure>', value='자동 크롤러를 킨다. 현재 버그 있어서 키면 디스코드 봇 마비되니 사용 X', inline=False)
        embed.add_field(name='!ping', value='봇 생존 여부 확인', inline=False)
        embed.add_field(name='!TODO <text>', value='<text>를 TODO에 추가한다. 개발자만 사용 가능. 아직 구현 안 됨', inline=False)
        embed.add_field(name='!help <command>', value='<command>에 대한 설명을 출력한다. 현재 구현 안 됨', inline=False)
        embed.add_field(name='!help', value='모든 명령어를 출력한다.', inline=False)
        embed.add_field(name='!geo <longtitude> <latitude> <radius>', value='위치를 기준으로 트윗을 검색합니다.', inline=False)
        embed.add_field(name='!date <year>/<month>/<day>', value='이란력을 그레고리력으로 변환합니다.', inline=False)
        embed.add_field(name='!date now', value='현재 날짜를 이란력으로 출력합니다.', inline=False)
        embed.add_field(name='!fromGregorian <year>/<month>/<day>', value='그레고리력을 이란력으로 변환합니다.', inline=False)
    await ctx.send(embed=embed)


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
        await ctx.send(f'{key}: {val}')
    ### await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send("pong")

@bot.command(pass_context=True)
async def geo(ctx, lng, lat, rat):
    embed = discord.Embed(title="", description="", color=0x5CD1E5)
    embed.add_field(name='Geolocation', value=f'{lng}, {lat}', inline=False)
    embed.add_field(name='Distance', value=f'{rat}', inline=False)
    await ctx.send(embed=embed)
    result = crawl.geo(lng, lat, rat)
    ret = result['link'].to_dict()
    text = 'Result:'
    ### embed = discord.Embed(title="Result", description="",color=0x5CD1E5)
    for i, (key, val) in enumerate(ret.items(), start=1):
        await ctx.send(f'{key}: {val}')

@bot.command(pass_context=True)
async def date(ctx, str):
    if str == "now":
        await ctx.send(f'오늘은 이란력으로 {jdatetime.datetime.now().strftime("%Y년 %m월 %d일")}입니다.')
    else:
        jDate = str.split("/")
        await ctx.send(f'{jdatetime.date(int(jDate[0]),int(jDate[1]),int(jDate[2])).togregorian().strftime("%Y/%m/%d")}')

@bot.command(pass_context=True)
async def fromGregorian(ctx, str):
    jDate = str.split("/")
    await ctx.send(f'{jdatetime.date.fromgregorian(year=int(jDate[0]),month=int(jDate[1]),day=int(jDate[2])).strftime("%Y/%m/%d")}')

@bot.command(pass_context=True)
async def cfg(ctx, cfgobj, *cfgval):
    cfgval = ' '.join(cfgval)
    #tCrawl.cfg(cfgobj=cfgval)
    proccfg(cfgobj, cfgval)
    await ctx.send(f'{cfgobj}의 값이 {cfgval}로 변경되었습니다.')


def proccfg(cfgobj, cfgval):
    global crawlPeriod
    if cfgobj == "limit":
        val = int(cfgval) 
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
    bot.run(BOT_TOKEN)
