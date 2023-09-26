import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from discord import app_commands

token = 'DISCORD_BOT_TOKEN'

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_guild_join(guild):
    await update_activity()

@bot.event
async def on_guild_remove(guild):
    await update_activity()

async def update_activity():
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"porn in {len(bot.guilds)} servers")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await update_activity()
    await bot.tree.sync() 

@bot.tree.command(name="live_score", description="Get LIVE scorecard")
@app_commands.describe(team_short_name="Team Name")
async def live_score(interaction: discord.Interaction, team_short_name: str):
    url = 'https://www.cricbuzz.com/'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    live_anchors = soup.find_all('a', class_='cb-mat-mnu-itm cb-ovr-flo', string=lambda text: "Live" in text or "Break" in text or "Lunch" in text or "Tea" in text)

    if live_anchors:
        match_details = []
        for live_anchor in live_anchors:
            link = live_anchor['href']
            split_link = link.split('/')

            if len(split_link) > 2:
                extracted_number = split_link[2]
                api_url_2 = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{extracted_number}/comm"
                api_url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{extracted_number}/scard"
                

                headers = {
                    "X-RapidAPI-Key": "RAPIDAPI_CRICBUZZ_APIKEY",
                    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
                }

                try:
                    api_response = requests.get(api_url, headers=headers)
                    data = api_response.json()

                    api_response_2 = requests.get(api_url_2, headers=headers)
                    data_2 = api_response_2.json()

                    match_type = data['matchHeader']['matchType']
                    series_name = data["matchHeader"]["seriesDesc"]
                    valid_series_names = ["Indian Premier League", "Big Bash League", "Pakistan Super League", "Caribbean Premier League", "Major League Cricket", "Lanka Premier League", "One-Day Cup", "T20I", "County"]

                    team1_score = "`Yet to bat`"
                    team2_score = "`Yet to bat`"
                    flag1 = ""
                    flag2 = ""
                    target = ""
                    batting_message = ""
                    bowling_message = ""
                    partnership = ""

                    team_flag_mapping = {
                        "afg": ":flag_af:",
                        "aus": ":flag_au:",
                        "ban": ":flag_bd:",
                        "eng": ":england:",
                        "ind": ":flag_in:",
                        "ire": ":four_leaf_clover:",
                        "nz": ":flag_nz:",
                        "pak": ":flag_pk:",
                        "rsa": ":flag_za:",
                        "sl": ":flag_lk:",
                        "wi": ":palm_tree:",
                        "zim": ":flag_zw:",
                        "sco": ":scotland:",
                        "ned": ":flag_nl:",
                        "usa": ":flag_us:",
                        "oma": ":flag_om:",
                        "uae": ":flag_ae:",
                        "nam": ":flag_na:",
                        "nep": ":flag_np:",
                        "can": ":flag_ca:",
                        "hk": ":flag_hk:",
                        "mly": ":flag_my:",
                        "png": ":flag_pg:"
                    }

                    if match_type == "International" or any(name in series_name for name in valid_series_names):
                        match_info = data['scoreCard'][0]
                        team1 = data["matchHeader"]["matchTeamInfo"][0]["battingTeamShortName"]
                        team2 = data["matchHeader"]["matchTeamInfo"][0]["bowlingTeamShortName"]
                        team1_overs = match_info['scoreDetails']['overs']
                        team1_runs = match_info['scoreDetails']['runs']
                        run_rate1 = match_info['scoreDetails']['runRate']
                        team1_wickets = match_info['scoreDetails']['wickets']
                        status = data['matchHeader']['status']
                        rr1 = "CRR:"
                        rr2 = "CRR:"

                        timeline = data_2['miniscore']['recentOvsStats']
                        required_rate = data_2['miniscore']['requiredRunRate']

                        last_wkt = "empty"
                        try: 
                            last_wkt = data_2['miniscore']['lastWicket']
                        except Exception as e:
                            pass
        
                        last_ovrs_runs = "empty"
                        try:
                            last_ovrs_runs = data_2['miniscore']['latestPerformance'][0]['runs']
                            last_ovrs_wkts = data_2['miniscore']['latestPerformance'][0]['wkts']
                            label = data_2['miniscore']['latestPerformance'][0]['label']
                        except IndexError:
                            pass

                        parts = status.split("-")
                        unique_parts = list(set(parts))
                        status = "-".join(unique_parts)

                        team1_score = f"`{team1_runs}/{team1_wickets} ({team1_overs}) {rr1} {run_rate1}`"

                        if match_type == "International":

                            if any(abbreviation in team1.lower() for abbreviation in team_flag_mapping.keys()):
                                for abbreviation, flag in team_flag_mapping.items():
                                    if abbreviation in team1.lower():
                                        flag1 = flag
                                        break
                            else:
                                flag1 = ""

                            if any(abbreviation in team2.lower() for abbreviation in team_flag_mapping.keys()):
                                for abbreviation, flag in team_flag_mapping.items():
                                    if abbreviation in team2.lower():
                                        flag2 = flag
                                        break
                            else:
                                flag2 = ""

                        score_message = f"{flag1} {team1}                         {team1_score}\n\n{flag2} {team2}                         {team2_score}\n\n`{status}`"

                        for player_key in data['scoreCard'][0]['bowlTeamDetails']['bowlersData']:
                            player = data['scoreCard'][0]['bowlTeamDetails']['bowlersData'][player_key]
                            overs = player['overs']
                            if overs:
                                overs_float = float(overs)
                                decimal_part = overs_float - int(overs_float)
                                if 0.1 <= decimal_part <= 0.5:
                                    player_name = player['bowlShortName']
                                    player_runs = player['runs']
                                    player_wickets = player['wickets']
                                    player_overs = player['overs']
                                    bowling_message += f"{player_name} `{player_wickets}/{player_runs} ({player_overs})`\n"

                        for player_key in match_info['batTeamDetails']['batsmenData']:
                            player = match_info['batTeamDetails']['batsmenData'][player_key]
                            if player['outDesc'] == "batting":
                                player_name = player['batShortName']
                                player_runs = player['runs']
                                player_balls = player['balls']
                                batting_message += f"{player_name} `{player_runs} ({player_balls})`\n"

                        highest_x = max([int(key.split('_')[1]) for key in match_info["partnershipsData"]])
                        partnership_runs = match_info["partnershipsData"]["pat_" + str(highest_x)]["totalRuns"]
                        partnership_balls = match_info["partnershipsData"]["pat_" + str(highest_x)]["totalBalls"]
                        partnership += f"P'ship `{partnership_runs}({partnership_balls})`"

                        try:
                            match_info2 = data['scoreCard'][1]
                            rr1 = "RR:"
                            team2_overs = match_info2['scoreDetails']['overs']
                            team2_runs = match_info2['scoreDetails']['runs']
                            run_rate2 = match_info2['scoreDetails']['runRate']
                            team2_wickets = match_info2['scoreDetails']['wickets']

                            
                            team1_score = f"`{team1_runs}/{team1_wickets} ({team1_overs}) {rr1} {run_rate1}`"
                            team2_score = f"`{team2_runs}/{team2_wickets} ({team2_overs}) {rr2}{run_rate2}`"

                            score_message = f"{flag1} {team1}                         {team1_score}\n{flag2} {team2}                         {team2_score}\n\n`{status} (RRR: {required_rate})`" 

                            for player_key in data['scoreCard'][1]['bowlTeamDetails']['bowlersData']:
                                player = data['scoreCard'][1]['bowlTeamDetails']['bowlersData'][player_key]
                                overs = player['overs']
                                if overs:
                                    overs_float = float(overs)
                                    decimal_part = overs_float - int(overs_float)
                                    if 0.1 <= decimal_part <= 0.5:
                                        player_name = player['bowlShortName']
                                        player_runs = player['runs']
                                        player_wickets = player['wickets']
                                        player_overs = player['overs']
                                        bowling_message = f"{player_name} `{player_wickets}/{player_runs} ({player_overs})`\n"

                            for player_key in match_info2['batTeamDetails']['batsmenData']:
                                player = match_info2['batTeamDetails']['batsmenData'][player_key]
                                if player['outDesc'] == "batting":
                                    player_name = player['batShortName']
                                    player_runs = player['runs']
                                    player_balls = player['balls']
                                    batting_message += f"{player_name} `{player_runs} ({player_balls})`\n"

                            highest_x = max([int(key.split('_')[1]) for key in match_info2["partnershipsData"]])
                            partnership_runs = match_info2["partnershipsData"]["pat_" + str(highest_x)]["totalRuns"]
                            partnership_balls = match_info2["partnershipsData"]["pat_" + str(highest_x)]["totalBalls"]
                            partnership = f"P'ship: `{partnership_runs}({partnership_balls})`"

                        except IndexError:
                            pass

                        extra = ""
                        extra = f"\nBatting:\n{batting_message}\n{partnership}\n\nBowling:\n{bowling_message}\nTimeline:\n`{timeline}`"

                        if last_wkt != "empty":
                            extra += f"\n\nLast Wkt:\n`{last_wkt}`"
                        
                        if last_ovrs_runs != "empty":
                            extra += f"\n\n{label}\n`{last_ovrs_runs}/{last_ovrs_wkts}`"

                        match_state = data['matchHeader']['state']
                        extra = f"**{extra}**" if match_state == "In Progress" else ""
                        
                        match_info = f"**{series_name}**\n\n**{score_message}**\n{extra}"  
                        match_details.append(match_info)
                        
                        
                    else:
                        if len(live_anchors) == 1:
                            await interaction.response.send_message(embed = discord.Embed(title=f"No match found for `{team_short_name}`", description="", color=discord.Color.random())) 
                                             

                except Exception as e:
                    pass

        if team_short_name:
            team_short_name = team_short_name.lower()
            matching_matches = [match for match in match_details if team_short_name in match.lower()]
            if matching_matches:
                for match_info in matching_matches:
                    await interaction.response.send_message(embed = discord.Embed(title=f"", description=f"{match_info}", color=discord.Color.random()))  
                    
            else:
                await interaction.response.send_message(embed = discord.Embed(title=f"No match found for `{team_short_name}`", description="", color=discord.Color.random()))
        else:
            if len(match_details) == 1:
                
                await interaction.response.send_message(embed = discord.Embed(title=f"", description=f"{match_details[0]}", color=discord.Color.random()))  


            elif len(match_details) > 1:
                for match_info in match_details:
                    
                    await interaction.response.send_message(embed = discord.Embed(title=f"", description=f"{match_info}", color=discord.Color.random()))  

    elif team_short_name:
        await interaction.response.send_message(embed = discord.Embed(title=f"No match found for `{team_short_name}`", description="", color=discord.Color.random()))
    else:
        await interaction.response.send_message(embed = discord.Embed(title=f"No match found for `{team_short_name}`", description="", color=discord.Color.random()))
        
        
        
@bot.tree.command(name="invite", description="Invite CricBot to Your Server")
async def live_score(interaction: discord.Interaction):
    bot_invite_link = "BOT_INVITE_LINK" 
    server_invite_link = "SERVER_INVITE_LINK"
    await interaction.response.send_message(
            embed = discord.Embed(title="Invite Links", description=f"**[Click here to invite CricBot to your server]({bot_invite_link})\n\n[Click here to join Official CrikChat server]({server_invite_link})**", color=discord.Color.random())
    )

@bot.tree.command(name="help", description="Display all Commands")
async def live_score(interaction: discord.Interaction):
    await interaction.response.send_message(
            embed = discord.Embed(title="Stay in the game with CricBot: Your LIVE cricket score companion!", description=f"**Cricbot is used in over `{len(bot.guilds)}` servers, where cricket fans from all over the world always stay in the game.\n\nCommands:\n\n`/live_score` to view LIVE scorecard of an ongoing match.\n\n`/invite` to invite CricBot to your server.\n\n`/vote` to vote for Cricbot to keep it running.\n\n`/help` to display this message.**", color=discord.Color.random())
    )

bot.run(token)