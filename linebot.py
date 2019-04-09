import discord
import datetime
import asyncio
import re
from vroom import *
import pymysql.cursors

conn = pymysql.connect(user = '',
                       password = '',
                       host = '',
                       db = '',
                       cursorclass = pymysql.cursors.DictCursor)

JST = datetime.timezone(datetime.timedelta(hours=9), 'JST')

client = discord.Client()

guild_id #ギルドID
vroom_ctg_id = #VCを自動生成するカテゴリ
vroomtc_ctg_id = #TCを自動生成するカテゴリ
log_id = #ログを残すチャンネルのID
registertc_id = #ID登録チャンネルのID
mytoken = #トークン

mng = None

@client.event
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------------')
    global mng
    mng = Vroom_mng(client.get_guild(guild_id),vroom_ctg_id,vroomtc_ctg_id)

async def print_log(msg: str):
    now = datetime.datetime.now(JST)
    await client.get_channel(log_id).send(str(now.hour)+':'+str(now.minute)+':'+str(now.second)+'.'+str(now.microsecond)+' : '+msg)

async def print_VCroomlist(guild: discord.Guild):
    msg = '現在サーバーに存在するVC :'
    for item in guild.voice_channels:
        msg += item.name+' '
    await print_log(msg)

async def panic(member:discord.Member):
    await print_log('部屋作成の操作の取り消しを開始')
    for item in member.guild.voice_channels:
        if item.name != 'VC部屋作成':
            if item.members == []:
                await delete_VCroom(item)

async def register_id(message:discord.Message):
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM list WHERE id = %s',(message.author.id,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO list (id,name) VALUES (%s,%s)',(message.author.id,message.content))
            print('新規')
        else:
            cursor.execute('UPDATE list set name = %s WHERE id = %s',(message.content,message.author.id))
        conn.commit()

async def send_uplayname(member:discord.Member,vc:discord.VoiceChannel):
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM list WHERE id = %s',(member.id,))
        result = cursor.fetchone()
    target = mng.get(vc.id,'vc')
    if result is None:
        result = {'name':'未登録'}
    await target.tc.send(f'{member.mention} {member.name}さんが参加しました。 UplayID : {result["name"]}')

@client.event
async def on_voice_state_update(member,befor,after):
    global  Vroom_list
    global  Vroom_table

    if befor.channel == after.channel:
        return

    if befor.channel is not None:
        if befor.channel.category_id == vroom_ctg_id:
            await print_log(member.name+'さんが'+befor.channel.name+'から退出')
            try:
                await mng.left(member,befor.channel)
            except:
                await print_log('部屋退出エラー')
        if befor.channel.name != 'VC部屋作成':
            if befor.channel.members == []:
                await print_log('参加者なしのため'+befor.channel.name+'の削除を開始')
                try:
                    await mng.delete(befor.channel)
                except:
                    await print_log('部屋削除エラー')
                await print_VCroomlist(member.guild)
        elif after.channel == None:
            await print_log('部屋作成の中断を確認')
            await asyncio.sleep(7)
            await panic(member)

    if after.channel is not None:
        if after.channel.name == 'VC部屋作成':
            try:
                await mng.create(member)
            except:
                await print_log('VC部屋作成エラー')
        else :
            await print_log(member.name+'さんが'+after.channel.name+'に参加')
            try:
                await mng.join(member,after.channel)
            except:
                await print_log('部屋参加エラー')
            await send_uplayname(member,after.channel)
@client.event
async def on_message(message):
    global Vroom_table
    print(message.content+' by '+message.author.name)

    if message.author == client.user:
        return

    if message.channel.id != log_id:
        await print_log(f'{message.content} by {message.author.name}({message.author.id}) in {message.channel.name}')

    if message.channel.id == registertc_id:
        try:
            await register_id(message)
        except:
            await print_log('ID登録エラー')

    if message.channel.category_id == vroomtc_ctg_id:
        if re.match(r'roomname:.+',message.content):
            try:
                name = message.content.split(':')[1]
                await mng.edit_name(message,name)
            except:
                await print_log('部屋名変更エラー')

client.run(mytoken)
