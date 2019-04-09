import discord

class Vroom_mng:
    def __init__(self,guild:discord.Guild,vroom_ctg_id:int,vroomtc_ctg_id):
        self.rooms = dict()
        self.used_num = []
        self.guild = guild
        self.vroom_ctg_id = vroom_ctg_id
        self.vroomtc_ctg_id = vroomtc_ctg_id
        print('ルームマネージャ準備完了')

    async def create(self,member:discord.Member):
        #空番号の取得関数作成予定
        num = 1
        while True:
            if num in self.used_num:
                num = num + 1
            else:
                break

        self.used_num.append(num)

        name = f'room {num}'

        #役職作成
        role = await member.guild.create_role(name=f'in {name}')
        role.permissions.none()
        await role.edit(hoist=True)

        #VC部屋作成
        room = await member.guild.create_voice_channel(name,category=member.guild.get_channel(self.vroom_ctg_id),position=num)

        #権限設定の作成
        overwrites = {
            member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True,send_messages=True)
        }

        #TC部屋作成
        roomtc = await member.guild.create_text_channel(name,category=member.guild.get_channel(self.vroomtc_ctg_id),overwrites=overwrites,position=num)

        #リストへ格納
        newroom = Vroom(num,name,role,room,roomtc)
        self.rooms.update([(num,newroom)])

        await member.move_to(room) #作成したVCへメンバーを移動

    async def delete(self,vc:discord.VoiceChannel):
        target = self.pop_by_vc(vc.id)
        await target.vc.delete()
        await target.tc.delete()
        await target.role.delete()
        self.used_num.remove(target.num)

    async def edit_name(self,message:discord.Message,name:str):
        target = self.get(message.channel.id,'tc')

        await target.vc.edit(name=name)
        await target.tc.edit(name=name)
        await target.role.edit(name=f'in {name}')

    async def join(self,member:discord.Member,vc:discord.VoiceChannel):
        vroom = self.get(vc.id,'vc')
        await member.add_roles(vroom.role)

    async def left(self,member:discord.Member,vc:discord.VoiceChannel):
        vroom = self.get(vc.id,'vc')
        await member.remove_roles(vroom.role)

    def get(self,id:int,mode:str):
        if mode == 'vc':
            return self.get_by_vc(id)
        elif mode == 'tc':
            return self.get_by_tc(id)

    def get_by_tc(self,tc_id:int):
        for key in self.rooms.keys():
            if self.rooms[key].tc.id == tc_id:
                return self.rooms[key]

    def get_by_vc(self,vc_id:int):
        for key in self.rooms.keys():
            if self.rooms[key].vc.id == vc_id:
                return self.rooms[key]

    def pop_by_vc(self,vc_id:int):
        for key in self.rooms.keys():
            if self.rooms[key].vc.id == vc_id:
                return self.rooms.pop(key)

class Vroom:
    def __init__(self,num:int,name:str,role:discord.Role,vc:discord.VoiceChannel,tc:discord.TextChannel):
        self.num = num
        self.name = name
        self.role = role
        self.vc = vc
        self.tc = tc
