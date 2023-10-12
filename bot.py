import discord
import settings
import json
import datetime
import random
import requests 
import asyncio
import re
import mysql.connector
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from blackjack import Deck
from blackjack import Hand

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/',intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name='To /help'), status=discord.Status.idle)

musicChoose = [
    "https://open.spotify.com/playlist/3nmmz5EDaHjTCVV52CCiuM?si=dd25013f8c47424e",
    "https://open.spotify.com/playlist/0tXUsFhsnnxpUR7B73iYPJ?si=61e82d45edf243a3"
]

def check_winner(player_hand, dealer_hand, game_over=False):
    if not game_over:
        if player_hand.get_value() > 21:
            return {'status' : True, 'text' : "You busted. Dealer wins! 😭" , 'bet' : "LOSE"}
        elif dealer_hand.get_value() > 21:
            return {'status' : True, 'text' : "Dealer busted. You win! 😀" , 'bet' : "WIN"}      
        elif dealer_hand.is_blackjack() and player_hand.is_blackjack():
            return {'status' : True,'text' :"Both players have blackjack! Tie! 😑" , 'bet' : "TIE"} 
        elif player_hand.is_blackjack():
            return {'status' : True, 'text' : "You have blackjack. You win! 😀" , 'bet' : "WIN"}
        elif dealer_hand.is_blackjack():
            return {'status' : True, 'text' : "Dealer has blackjack. Dealer wins! 😭" , 'bet' : "LOSE"}
    else:
        if player_hand.get_value() > dealer_hand.get_value():
            return {'status' : True, 'text' : "You win! 😀" , 'bet' : "WIN"}
        elif player_hand.get_value() == dealer_hand.get_value():
            return {'status' : True, 'text' : "Tie! 😑" , 'bet' : "TIE"}
        elif dealer_hand.get_value() > 21:
            return {'status' : True, 'text' : "Dealer busted. You wins! 😀" , 'bet' : "WIN"}
        else:
            return {'status' : True, 'text' : "Dealer wins. 😭" , 'bet' : "LOSE"}
    return {'status': False, 'text' : "", 'bet' : ""}


@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('----------------------------------------------')

@bot.tree.command(name="help", description="Learn what my this bot can do")
async def help(interc=discord.integrations):
    
    embed = discord.Embed(title="What Ladui can do :",)
    embed.set_author(name="Ladui", icon_url="https://cdn.discordapp.com/attachments/1161253698438176850/1161253788330512414/Sekijoy_Megaira_in_hades_0dd0e692-0a10-4fb5-8317-747a601bb046.png?ex=6537a0de&is=65252bde&hm=8634c71d817ed3454272bd1e31f84fb0b43fc5d81350d1afe3faecbe36cbac8e&")

    embed.add_field(name="/Jim", value="This is know what the need your workout of today", inline=False)
    embed.add_field(name="/play", value="To invite a friends to join to your game and voice channel", inline=False)
    embed.add_field(name="/agent", value="What agent(valorant) you play today", inline=False)
    embed.add_field(name="/news", value="Indonesia News")
    embed.add_field(name="/winrate", value="Calculate your win to reach your expetasion winrate", inline=False)
    embed.add_field(name="/blackjack" , value="play 1 round of blackjack", inline=False)
    embed.add_field(name="Timeout feature", value="There is timeout feature for this bot, so if user type a bad word 25 times the user will be timeout for 5 minutes, ```NOTE \nYou need to give a premision for timeout, so the bot can timeout a user```", inline=False)
    embed.set_footer(text="rama16274@gmail.com \nfor contact any bug or question for this bot")
    
    await interc.response.send_message(embed=embed)

@bot.tree.command(name="jim", description="today workout")
async def jim(interc=discord.interactions):
        now = datetime.datetime.now()
        day = now.strftime("%A")

        with open('test.json', 'r') as file:
            data = json.load(file)

        if day in data:
            exercise_data = data[day]["exercise"]
            if isinstance(exercise_data, list):
                exercise_value = "\n".join(exercise_data)
            else:
                exercise_value = exercise_data
            embed = discord.Embed(title=data[day]["name"], color=discord.Color.random())
            embed.set_thumbnail(url="https://m.media-amazon.com/images/M/MV5BMWUzOWE4MGItNTVhYy00YTUzLWEzNzctYzVmYTc1MThhNWE5XkEyXkFqcGdeQXVyNjg5MjU3NjE@._V1_.jpg")
            embed.add_field(name=data[day]["name"], value=exercise_value)
            
            # Create a button with a URL
            button = discord.ui.Button(style=discord.ButtonStyle.success, label="Music", url=random.choice(musicChoose))
            
            # Add the button to the view
            view = discord.ui.View()
            view.add_item(button)
            
            # Send the embed with the button
            await interc.response.send_message(embed=embed, view=view)

@bot.tree.command(name="play", description="Make a list of player how want's to play a game")
@app_commands.describe(game="what the game we play ?", max_play="the max player of the game", voice_channel="the voice for member to join")
async def play(interc : discord.interactions, game : str, max_play : int, voice_channel: discord.VoiceChannel):
    if max_play <= 0:
        await interc.response.send_message("The max number of players must be greater than 0.", ephemeral=True)
    else:
        num = 1
        userJoin = f'{num}.{interc.user.name}'
        print(userJoin)
        view = View()

        # Create an embed
        embed = discord.Embed(
            title=game,
            description=f"Let's Play {game}",
            color=discord.Color.random()
        )
        embed.add_field(name="Member Join :", value=userJoin)

        join = Button(label="join", style=discord.ButtonStyle.success)
        async def joinCallBack(interc):
            nonlocal userJoin, view, num
            if num<max_play:
                if interc.user.name not in userJoin:
                    num += 1
                    userJoin += f'\n{num}.{interc.user.name}'
                    embed = discord.Embed(
                    title=game,
                    description=f"Let's Play {game}",
                    )
                    embed.add_field(name="Member Join :", value=userJoin)
                    await interc.response.edit_message(embed=embed, view=view)
                    await interc.followup.send(content=f'Join this voice channel {voice_channel.mention}', ephemeral=True)
                else:
                    await interc.response.send_message(content=f'You already join the game', ephemeral=True)
            else:
                join.style = discord.ButtonStyle.red
                join.label = "Full"
                join.disabled = True
                embed = discord.Embed(
                    title=game,
                    description=f"Let's Play {game}",
                )
                embed.add_field(name="Member Join:", value=userJoin)
                embed.set_footer(text="The member already full")
                await interc.response.edit_message(embed=embed, view=view)
                
        join.callback=joinCallBack
        view.add_item(join)

        await interc.response.send_message(content=f"@here \n {game}",embed=embed, view=view, allowed_mentions=discord.AllowedMentions(everyone=True))

@bot.tree.command(name="agent", description="What agent you play today ?")
async def agent(interc=discord.interactions):

    response = requests.get('https://valorant-api.com/v1/agents?isPlayableCharacter=true')
    response = response.json()
    agent = response['data']
    random_agent = random.choice(agent)


    embed = discord.Embed(
            title=random_agent['displayName'],
            description=f"This game You Playing {random_agent['role']['displayName']} :\n {random_agent['role']['description']}",
            color=discord.Color.random()
        )
    embed.set_image(url=random_agent['displayIconSmall'])
    embed.set_footer(text=random_agent['description'])


    await interc.response.send_message(embed=embed)

@bot.tree.command(name="news", description="News in indonesia")
async def news(interc=discord.interactions):
    
    num = 1
    response = requests.get(settings.NEWS_API)
    newsres = response.json()
    news = newsres['articles'][num]
    view = View()
    print(newsres.get('source'))



    embed = discord.Embed(
            title=news['title'],
            url=news['url'],
            description=f"Author {news['author']}",
            color=discord.Color.random()
    )
    embed.set_footer(text=news.get('publishedAt'))

    next = Button(style=discord.ButtonStyle.primary,emoji="⏭")
    back = Button(style=discord.ButtonStyle.primary,emoji="⏮")

    async def nextCallBack(interc):
            nonlocal news, view, num
            if num >= len(news):
                num = 1
                news = newsres['articles'][num]
                embed = discord.Embed(
                title=news['title'],
                url=news['url'],
                description=f"Author {news.get('author')}",
                color=discord.Color.random()
        )
                embed.set_footer(text=news.get('publishedAt'))
                await interc.response.edit_message(embed=embed, view=view)
            else:
                num += 1
                news = newsres['articles'][num]
                embed = discord.Embed(
                title=news['title'],
                url=news['url'],
                description=f"Author {news.get('author')}",
                color=discord.Color.random()
        )
                embed.set_footer(text=news.get('publishedAt'))
                await interc.response.edit_message(embed=embed, view=view)

    async def backCallBack(interc):
            nonlocal news, view, num
            num -= 1
            news = newsres['articles'][num]
            embed = discord.Embed(
            title=news['title'],
            url=news['url'],
            description=f"Author {news.get('author')}",
            color=discord.Color.random()
        )
            embed.set_footer(text=news.get('publishedAt'))
            await interc.response.edit_message(embed=embed, view=view)

    next.callback=nextCallBack
    back.callback=backCallBack
    view.add_item(back)
    view.add_item(next)


    await interc.response.send_message(embed=embed, view=view)


# @bot.tree.command(name="voice", description="this is only test")
# async def voice(interc : discord.interactions, voice_channel: discord.VoiceChannel):
#     await interc.response.send_message(content=f"lets join this {voice_channel.mention}")

@bot.tree.command(name="winrate", description="calculate need to win to get a certain win rate")
@app_commands.describe(total_match="example: 200", current_winrate="example: 50%", desire_winrate="example: 70%")
async def winrate(interc: discord.interactions, total_match: int, current_winrate: float, desire_winrate: float):
    current_winrate_decimal = current_winrate / 100
    desire_winrate_decimal = desire_winrate / 100

    wins_needed = ((total_match * desire_winrate_decimal - total_match * current_winrate_decimal) / (desire_winrate_decimal - current_winrate_decimal))

    if wins_needed >= 0:
        await interc.response.send_message(f'You need to win {wins_needed:.2f} matches to reach {desire_winrate}%')
    else:
        await interc.response.send_message(f'Your current win rate is already higher than the desired win rate.')



@bot.event
async def on_message(messsage):
    if messsage.author == bot.user:
        return
    
    con=mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    database = "discord_bot",
    password = ""
)
    cursor = con.cursor()
    content = messsage.content.lower()
    username = str(messsage.author)

    bad_words = [
    "nigga", "niga","nigger", "nig4","nigg4","memek","pepek","anjing","ajg","asu","bitch", "ngentot",
    "bangsat","jancuk","jancok","kontol","goblog", "goblok", "tolol","entot","ngontol","anj1ng","rama babi","kentod"
    ,"Anjwng"
        ]
    

    for bad_word in bad_words:
        pattern = rf"\b{re.escape(bad_word)}\w*\b"
        if re.search(pattern, content, re.IGNORECASE):
            query = "SELECT no, warn FROM user WHERE username = %s"
            cursor.execute(query, (username,))
            existing_user = cursor.fetchone()
            print(existing_user)
            if existing_user:
                no, warn = existing_user
                new_warn = warn + 1
                update_query = "UPDATE user SET warn = %s WHERE no = %s"
                cursor.execute(update_query, (new_warn, no))
                con.commit()
                warn_query ="SELECT warn FROM user WHERE no =%s" 
                cursor.execute(warn_query,(no,))
                warn_count = cursor.fetchone()   
                warn_message = await messsage.reply(f"{messsage.author.mention} Please watch your language sirrr, Your are gonna be timeout in {warn_count[0]} / 25", mention_author=False)
                
                async def delete_warning_message():
                        await asyncio.sleep(30)
                        await warn_message.delete()

                bot.loop.create_task(delete_warning_message())

                if warn_count[0] >= 25:
                    await timeout_user(messsage.author, messsage.channel)
                    reset_query = "UPDATE user SET warn = 0 WHERE no = %s"
                    cursor.execute(reset_query,(no,))
                    con.commit()

            else:
                insert_query = "INSERT INTO user (username, warn) VALUES (%s, 1)"
                cursor.execute(insert_query, (username,))
                con.commit()
                print(f"User '{username}' inserted with a warn count of 1.")
                warn_message = await messsage.reply(f"Heyy {messsage.author.mention} Please watch your language, There are childer in here", mention_author=False)

                async def delete_warning_message():
                        await asyncio.sleep(30)
                        await warn_message.delete()

                bot.loop.create_task(delete_warning_message())


async def timeout_user(user, channel):
    duration = datetime.timedelta(minutes=2)  
    await user.timeout(duration, reason="You have used inappropriate language")
    await channel.send(f"{user.mention} has been timed out for 2 minutes due to inappropriate language.")



@bot.tree.command(name="blackjack", description="play blackjack")
@app_commands.describe(amouth_bet = "Set amouth your bet $")
async def blackjack(interc : discord.interactions, amouth_bet : int):
    deck = Deck()
    deck.shuffle()
    view = View()
    player_hand = Hand()
    dealer_hand = Hand(dealer=True)

    def result_bet(result):
        if result == "WIN":
            return amouth_bet * 2
        elif result == "LOSE":
            return amouth_bet / 2
        else:
            return amouth_bet
    hit = Button(label="Hit", style=discord.ButtonStyle.success)
    stand = Button(label="Stand", style=discord.ButtonStyle.danger)
    
    def result_color(result):
        if result == "WIN":
            return discord.Color.green()
        elif result == "LOSE":
            return discord.Color.red()
        elif result == "TIE":
            return discord.Color.light_grey()
        else :
            return discord.Color.from_rgb(255, 215, 0) 
        

    for i in range(2):
        player_hand.add_card(deck.deal(1))
        dealer_hand.add_card(deck.deal(1))

    embed = discord.Embed(title="Welcome to blackjack",
                         description="--------------------------------"
                         ,color=discord.Color.from_rgb(255, 215, 0) )
    

    embed.add_field(name="Dealer's hand:", value=dealer_hand.display(), inline=False)
    embed.add_field(name="Your hand:", value=player_hand.display(), inline=False)
    embed.set_footer(text=f'Your bet is $ {amouth_bet}')

    player_hand_value = player_hand.get_value()
    dealer_hand_value = dealer_hand.get_value()  
    
    
    async def hitCallBack(interc):
        nonlocal dealer_hand_value, player_hand_value
        player_hand.add_card(deck.deal(1))
        dealer_hand_value = dealer_hand.get_value()
        player_hand_value = player_hand.get_value()
        if player_hand_value < 21:
            if dealer_hand_value < 17:
                dealer_hand.add_card(deck.deal(1))
            dealer_hand_value = dealer_hand.get_value()
            player_hand_value = player_hand.get_value()
            embed = discord.Embed(title="Welcome to blackjack" ,
                        description="--------------------------------",
                        color=discord.Color.from_rgb(255, 215, 0) )

            embed.add_field(name="Dealer's hand:", value=dealer_hand.display(), inline=False)
            embed.add_field(name="Your hand:", value=player_hand.display(), inline=False)
            await interc.response.edit_message(embed=embed, view=view)
        
        else:
            result = check_winner(player_hand, dealer_hand)
            resultBet = result_bet(result['bet'])
            resultColor = result_color(result['bet'])
            embed = discord.Embed(title=result['text'] ,
                        description="--------------------------------",
                        color=resultColor)
            embed.add_field(name="Dealer's hand:", value=dealer_hand.display(show_all_dealer_cards=True), inline=False)
            embed.add_field(name="Dealer's hand value:", value=dealer_hand_value, inline=False)
            embed.add_field(name="Your hand:", value=player_hand.display(), inline=False)
            embed.add_field(name="Your hand value:", value=player_hand_value, inline=False)
            embed.set_footer(text=f'Your get $ {resultBet}')
            hit.disabled = True
            stand.disabled = True
            await interc.response.edit_message(embed=embed, view=view)

    async def standCallBack(interc):
        nonlocal dealer_hand_value, player_hand_value
        if dealer_hand_value < 17:
            dealer_hand.add_card(deck.deal(1))
        dealer_hand_value = dealer_hand.get_value()
        result = check_winner(player_hand, dealer_hand, True)
        resultBet = result_bet(result['bet'])
        resultColor = result_color(result['bet'])
        print(result)
        embed = discord.Embed(title=result['text'] ,
                        description="--------------------------------",
                        color=resultColor)
        embed.add_field(name="Dealer's hand:", value=dealer_hand.display(show_all_dealer_cards=True), inline=False)
        embed.add_field(name="Dealer's hand value:", value=dealer_hand_value, inline=False)
        embed.add_field(name="Your hand:", value=player_hand.display(), inline=False)
        embed.add_field(name="Your hand value:", value=player_hand_value, inline=False)
        embed.set_footer(text=f'Your get $ {resultBet}')
        
        hit.disabled = True
        stand.disabled = True
        await interc.response.edit_message(embed=embed, view=view)

    
    hit.callback=hitCallBack
    stand.callback=standCallBack
    view.add_item(hit)
    view.add_item(stand)

    await interc.response.send_message(embed=embed, view=view)

bot.run(settings.TOKEN)











