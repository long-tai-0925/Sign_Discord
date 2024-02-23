from discord.ext import commands
import discord
import random
import datetime
from discord_slash import SlashCommand
from discord_slash.model import SlashCommandOptionType
from discord_slash import SlashContext
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import matplotlib.pyplot as plt
import asyncio
import math


bot = commands.Bot(command_prefix='.')
slash = SlashCommand(bot, sync_commands=True)


daily_member_counts = []


def load_user_data(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return {int(user_id): User(**user_data) for user_id, user_data in data.items()}
    except FileNotFoundError:
        return {}


def save_user_data(users, filename):
    data = {str(user_id): users[user_id].__dict__ for user_id in users}
    with open(filename, 'w') as file:
        json.dump(data, file)


class User:
    def __init__(self, id, name, coin=0, last_sign=None, guess_record=None):
        self.id = id
        self.name = name
        self.coin = coin
        self.last_sign = last_sign
        self.guess_record = guess_record or {"correct": 0, "incorrect": 0}


    def add_coin(self, amount):
        self.coin += amount


    def remove_coin(self, amount):
        if self.coin - amount < 0:
            return False
        self.coin -= amount
        return True


    def record_guess(self, correct):
        if correct:
            self.guess_record["correct"] += 1
        else:
            self.guess_record["incorrect"] += 1


users = load_user_data('user_data.json')




@bot.event
async def on_ready():
    print(f'目前登入身份： {bot.user}\nID：{bot.user.id}')
    bot.loop.create_task(update_member_count())
async def update_member_count():
    await bot.wait_until_ready()
    while not bot.is_closed():
        member_count = len(bot.guilds[0].members)
        daily_member_counts.append((datetime.datetime.utcnow(), member_count))
        await asyncio.sleep(60 * 60 * 24)


@slash.slash(name="ping", description="檢查機器人的延遲")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! 延遲：{latency} 毫秒')
    print(f'Pong! 延遲：{latency} 毫秒')


@slash.slash(name="sign", description="每日簽到")
async def sign(ctx):
    user_id = ctx.author.id
    user_name = ctx.author
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # 設定特殊身分組
    specific_role_id_1 = 1168840339105259561 ##中科大學生
    specific_role_id_2 = 1194979984243179541 ##Server Booster

    # 已經簽到過
    if user_id in users and users[user_id].last_sign == today: ##查資料庫有沒有簽到
        await ctx.send(f'{ctx.author.mention} 你今天已經簽到過了！', hidden=True)
        print(f'{ctx.author.mention} 你今天已經簽到過了！')
        return ## 退出 if else
    
    # 第一個簽到 if else (specific_role_id_1 先)
    if specific_role_id_1 in [role.id for role in ctx.author.roles]: ##判斷有沒有 specific_role_id_1

        # 有 specific_role_id_1 身分組 及 specific_role_id_2 身分組
        if specific_role_id_2 in [role.id for role in ctx.author.roles]: ##判斷有沒有 specific_role_id_2

            coin_reward = random.randint(60, 100) * 1.35  ## 隨機 60~100 的數字 並 *1.35
            print(f"隨機分數：{coin_reward}")

            coin_reward = round(coin_reward, 1)  ## 把小數點取消
            print(f"移除小數：{coin_reward}")

            if coin_reward > 100: ## coin_reward 如果大於100
                coin_reward = 100 ## coin_reward設定100
                print(f"限制一百：{coin_reward}")

            if user_id not in users: ## 如果用戶不在資料庫
                users[user_id] = User(user_id, ctx.author.name) ## 創建新用戶資料串
            users[user_id].add_coin(coin_reward) ## 資料數設定原分數加簽到分數
            users[user_id].last_sign = today ## 最後簽到時間(last_sign)設定簽到時間

            await ctx.send(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward} 小考分數！\n `你受到中科之神眷顧 逢考畢及格 及 分數*1.35`')
            print(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward} 小考分數！\n `你受到中科之神眷顧 逢考畢及格 及 分數*1.35`')
            
        # 有 specific_role_id_1 身分組
        else: ## 否則(只有 specific_role_id_1 身分組)

            coin_reward = random.randint(0, 100)*1.35 ## 隨機 0~100 的數字 並 *1.35
            print(f"隨機分數：{coin_reward}")

            coin_reward = round(coin_reward, 1)  ## 把小數點取消
            print(f"移除小數：{coin_reward}")

            if coin_reward > 100: ## coin_reward 如果大於100
                coin_reward = 100 ## coin_reward設定100
                print(f"限制一百：{coin_reward}")

            if user_id not in users: ## 如果用戶不在資料庫
                users[user_id] = User(user_id, ctx.author.name) ## 創建新用戶資料串
            users[user_id].add_coin(coin_reward) ## 資料數設定原分數加簽到分數
            users[user_id].last_sign = today ## 最後簽到時間(last_sign)設定簽到時間

            await ctx.send(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward*1.35} 小考分數！\n `你受到中科之神眷顧 分數*1.35 (原分數：{coin_reward})`')
            print(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward*1.35} 小考分數！\n `你受到中科之神眷顧 分數*1.35 (原分數：{coin_reward})`')
    
    # 第一個簽到 if else (specific_role_id_1 先)
    elif specific_role_id_2 in [role.id for role in ctx.author.roles]: ##判斷有沒有 specific_role_id_2

        # 有 specific_role_id_2 身分組 及 specific_role_id_1 身分組
        if specific_role_id_1 in [role.id for role in ctx.author.roles]: ##判斷有沒有 specific_role_id_1

            coin_reward = random.randint(60, 100)*1.35 ## 隨機 60~100 的數字 並 *1.35
            print(f"隨機分數：{coin_reward}")

            coin_reward = round(coin_reward, 1)  ## 把小數點取消
            print(f"移除小數：{coin_reward}")

            if coin_reward > 100: ## coin_reward 如果大於100
                coin_reward = 100 ## coin_reward設定100
                print(f"限制一百：{coin_reward}")

            if user_id not in users: ## 如果用戶不在資料庫
                users[user_id] = User(user_id, ctx.author.name) ## 創建新用戶資料串
            users[user_id].add_coin(coin_reward) ## 資料數設定原分數加簽到分數
            users[user_id].last_sign = today ## 最後簽到時間(last_sign)設定簽到時間

            await ctx.send(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward} 小考分數！\n `你受到中科之神眷顧 逢考畢及格 及 分數*1.35`')
            print(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward} 小考分數！\n `你受到中科之神眷顧 逢考畢及格 及 分數*1.35`')

        # 有 specific_role_id_2 身分組
        else: ## 否則(只有 specific_role_id_2 身分組)
            coin_reward = random.randint(60, 100) ## 隨機 60~100 的數字
            print(f"隨機分數：{coin_reward}")

            coin_reward = round(coin_reward, 1)  ## 把小數點取消
            print(f"移除小數：{coin_reward}")

            if coin_reward > 100: ## coin_reward 如果大於100
                coin_reward = 100 ## coin_reward設定100
                print(f"限制一百：{coin_reward}")

            if user_id not in users: ## 如果用戶不在資料庫
                users[user_id] = User(user_id, ctx.author.name) ## 創建新用戶資料串
            users[user_id].add_coin(coin_reward) ## 資料數設定原分數加簽到分數
            users[user_id].last_sign = today ## 最後簽到時間(last_sign)設定簽到時間

            await ctx.send(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward} 小考分數！\n `你受到中科之神眷顧 逢考畢及格`')
            print(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward} 小考分數！\n `你受到中科之神眷顧 逢考畢及格`')

    # 沒有特殊身分組
    else:
        coin_reward = random.randint(0, 100) ## 隨機 00~100 的數字
        print(f"隨機分數：{coin_reward}")

        coin_reward = round(coin_reward, 1) ## 把小數點取消
        print(f"移除小數：{coin_reward}")

        if coin_reward > 100: ## coin_reward 如果大於100
            coin_reward = 100 ## coin_reward設定100
            print(f"限制一百：{coin_reward}")

        if user_id not in users: ## 如果用戶不在資料庫
            users[user_id] = User(user_id, ctx.author.name) ## 創建新用戶資料串
        users[user_id].add_coin(coin_reward) ## 資料數設定原分數加簽到分數
        users[user_id].last_sign = today ## 最後簽到時間(last_sign)設定簽到時間

        await ctx.send(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward} 小考分數！')
        print(f'{ctx.author.mention} 簽到成功！獲得 {coin_reward} 小考分數！')

    save_user_data(users, 'user_data.json') ## 存用戶簽到資料



@slash.slash(name="coin", description="查看你的小考分數")
async def coin(ctx):
    user_id = ctx.author.id
    user_name = ctx.author
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if user_id not in users:
        await ctx.send(f'{ctx.author.mention} 你還沒有獲得任何小考分數！')
        return
    coin = users[user_id].coin
    await ctx.send(f'{ctx.author.mention} 你目前擁有 {coin} 小考分數！')


@slash.slash(name="addcoin", description="神奇小魔法幫你加分")
async def addcoin(ctx, member: discord.User, amount: int):
    user_name = ctx.author
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if ctx.author.id != 795328745103556608:
        await ctx.send(f'{ctx.author.mention} 你沒有權限給其他人增加小考分數！', hidden=True)
        return
    if member.id not in users:
        users[member.id] = User(member.id, member.name)
    users[member.id].add_coin(amount)
    await ctx.send(f'{member.mention} 成功給你增加了 {amount} 小考分數！')
    save_user_data(users, 'user_data.json')


@slash.slash(name="removecoin", description="老師覺得你考不好，扣分 扣分")
async def removecoin(ctx, member: discord.User, amount: int):
    user_name = ctx.author
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if ctx.author.id != 795328745103556608:
        await ctx.send(f'{ctx.author.mention} 你沒有權限移除其他人的小考分數！', hidden=True)
        return
    if member.id not in users:
        await ctx.send(f'{member.mention} 還沒有獲得任何小考分數！', hidden=True)
        return
    success = users[member.id].remove_coin(amount)
    if success:
        await ctx.send(f'{member.mention} 成功移除了 {amount} 小考分數！')
    else:
        await ctx.send(f'{member.mention} 移除失敗！', hidden=True)
    save_user_data(users, 'user_data.json')


@slash.slash(name="shutdown", description="Bot關機", guild_ids=[1165839193264627724])
async def shutdown(ctx):
    user_name = ctx.author
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if str(ctx.author.id) == "795328745103556608":
        await ctx.send("正在關機...")
        save_user_data(users, 'user_data.json')
        print(f'---------嘗試關機---------\n用戶：{user_name}\n日期{today}\n狀態：(已關機)\n')
        with open('shutdown.txt', 'a') as f:
            f.write(f'---------嘗試關機---------\n用戶：{user_name}\n日期{today}\n狀態：(已關機)\n')
        await bot.close()
       
    else:
        await ctx.send("抱歉，您沒有權限執行此操作。", hidden=True)
        save_user_data(users, 'user_data.json')
        print(f'---------嘗試關機---------\n用戶：{user_name}\n日期{today}\n狀態：(無權限關機)\n')
        with open('shutdown.txt', 'a') as f:
            f.write(f'---------嘗試關機---------\n用戶：{user_name}\n日期{today}\n狀態：(無權限關機)\n')


@slash.slash(name="ranking", description="查看小考分数排行榜")
async def ranking(ctx):
    user_name = ctx.author
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    sorted_users = sorted(users.values(), key=lambda user: user.coin, reverse=True)
    top_10_users = sorted_users[:38]
    ranking_info = "\n".join([f"第{rank}名 <@{user.id}> 分數：{user.coin}  最後簽到：{user.last_sign}" for rank, user in enumerate(top_10_users, start=1)])
    await ctx.send(f'分數排行榜：\n{ranking_info}', hidden=True)
    print(f'---------查看排行榜---------\n用戶：{user_name}\n日期{today}\n排行：\n{ranking_info}\n')
    with open('ranking.txt', 'a') as f:
        f.write(f'---------查看排行榜---------\n用戶：{user_name}\n日期{today}\n排行：\n{ranking_info}\n')




@slash.slash(name="guess", description="猜一個介於1和5之間的數字")
async def guess(ctx: SlashContext, number: int):
    user_name = ctx.author.name
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    user_id = ctx.author.id
    correct_number = random.randint(1, 5)
    point_cost = 50


    correct_guess = number == correct_number


    if correct_guess:
        users[user_id].add_coin(point_cost)
        await ctx.send(f'恭喜，{ctx.author.mention}！你猜中了正確的數字！你獲得了 {point_cost} 分。')
        print(f'---------猜數字遊戲---------\n用戶：{user_name}\n日期{today}\n數字：{correct_number}\n')
        with open('guess.txt', 'a') as f:
            f.write(f'---------猜數字遊戲---------\n用戶：{user_name}\n日期{today}\n數字：{correct_number}\n')
    else:
        users[user_id].remove_coin(point_cost)
        await ctx.send(f'抱歉，{ctx.author.mention}。正確的數字是 {correct_number}。你失去了 {point_cost} 分。')
        print(f'---------猜數字遊戲---------\n用戶：{user_name}\n日期{today}\n數字：{correct_number}\n')
        with open('guess.txt', 'a') as f:
            f.write(f'---------猜數字遊戲---------\n用戶：{user_name}\n日期{today}\n數字：{correct_number}\n')
    users[user_id].record_guess(correct_guess)
    save_user_data(users, 'user_data.json')




@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        save_user_data(users, 'user_data.json')
        return
    raise error


bot.run("Bot_Token", bot=True, reconnect=True)
