import asyncio
import discord
from discord.ext import commands
import json
import random
import os
import datetime
from time import sleep
from bs4 import BeautifulSoup
import requests
from ctypes.util import find_library

class utils:
    def get_drink_icon(drink):
        drink = drink.replace(" ", "_").title()
        page = requests.get("http://va11halla.wikia.com/wiki/"+drink)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text)
            element = soup.find('img', {"class":"pi-image-thumbnail"})
            url = element["src"]
            return url
        return None

    def is_owner_check(message):
        if message.author.id == "105800900521570304":
            return True
        return False

    def is_owner():
        return commands.check(lambda ctx: is_owner_check(ctx.message))

    def is_default_channel(channel):
        if channel == channel.server.default_channel:
            return True
        return False

    def is_not_default_channel():
        return commands.check(lambda ctx: is_default_channel(ctx.message.channel))

class bartender:
    """Welcome to the Bar!"""
    def __init__(self, bot):
        self.bot = bot
        self.drinkspath = "./data/bartender/drinks.json"
        self.quotespath = "./data/bartender/quotes.json"
        self.workpath = "./data/bartender/work.json"
        if not os.path.exists(self.drinkspath.replace("/drinks.json", "")) or not os.path.isfile(self.drinkspath):
            self.make_files("drinks")
        if not os.path.exists(self.quotespath.replace("/quotes.json", "")) or not os.path.isfile(self.quotespath):
            self.make_files("quotes")
        if not os.path.exists(self.workpath.replace("/work.json", "")) or not os.path.isfile(self.workpath):
            self.make_files("work")
        self.embed_footer_first = "\"I see this is your first time here, I hope I can be of service!\" (I hope they don't mention the dogshit smell)"
        self.embed_footer_icon = "http://vignette2.wikia.nocookie.net/va11halla/images/1/1b/Jill.png"
        self.boss_pic = "http://vignette3.wikia.nocookie.net/va11halla/images/2/29/Dana.png"
        with open(self.drinkspath) as data:
            self.drinks = json.load(data)
        flavors = [self.drinks[item]["Flavor"] for item in self.drinks]
        self.flavors = list(set(flavors))
        types = [self.drinks[item]["Type"] for item in self.drinks]
        self.types = list(set(types))
        with open(self.quotespath) as data:
            self.quotes = json.load(data)
        self.greetings = self.quotes["greetings"]
        self.qdrinks = self.quotes["drinks"]
        self.tut_text = "Hello, Welcome to Va-11 Hall-A. A cyberpunk themed bar.\nJust like any bar, we serve drinks.\n\nEvery Drink is listed under *Drinks*.\nThose drinks have flavors, and are listed under *Drink Flavors*\nEach drink is under a category known as type, listed under *Drink Types*\n\nThere is multiple ways of ordering drinks:\n\t- Ordering from drink name: \n\t\t`cow.bar order Piano Man`\n\t- Ordering a random drink with that flavor: \n\t\t`cow.bar order Sweet`\n\t- Ordering a random drink from that type: \n\t\t`cow.bar order Classy`\n\t- Order a random drink:\n\t\t`cow.bar order`\n\nPlease enjoy your stay!"
        self.work_tut_text = "Working in this bar is like working in the outside world; You'll get paid minimum wage per hour for that job. All jobs have minimum and maximum hours, and the amount of hours I'll give you is inbetween that time frame.\n\nWhen your work is done, you'll have to wait a full day plus the amount of hours you worked. Say if you cleaned for 2 hours, you'll have to wait 1 day and 2 hours before requesting for work again.\n\nAlso, if I see you doing a better than average at what I gave you, I'll might even give you extra money."
        self.embed_color = discord.Color(value=8600006)

    def make_files(self, filetype):
        if filetype == "drinks":
            dic = DRINKS_DICT
            path = self.drinkspath
        elif filetype == "quotes":
            dic = QUOTES_DICT
            path = self.quotespath
        elif filetype == "work":
            dic = WORK_DICT
            path = self.workpath
        else:
            return

        with open(path, "w") as f:
            json.dump(dic, f)

    @commands.group(invoke_without_command=True, pass_context=True)
    async def bar(self, ctx):
        """Relax in our cyberpunk bar. Order drinks or make friends. (Is the central hub for all commands)"""
        a = account(ctx.message.author)
        path = a.fpath
        with open(path) as f:
            data = json.load(f)
        embed = discord.Embed(title="Welcome to the bar. What can I get you?", color=self.embed_color, description="Please use the categories or types of drinks below. Know something you like, tell me and I'll make it.\n\nHelp: `cow.bar help`")
        footer = random.choice(self.greetings)
        embed.set_thumbnail(url=self.embed_footer_icon)
        if a.firsttime:
            embed.add_field(name="It's always great to see a new face!", value=self.tut_text+"\n(This Help can be revisted using `cow.bar help`. This will only shown once.)")
            footer = self.embed_footer_first
            data["firsttime"] = False
            with open(path, "w") as f:
                json.dump(data, f)
        embed.set_footer(text=footer)
        embed.add_field(name="Drink Types:", value=str(", ".join(self.types)).title(), inline=False)
        embed.add_field(name="Drink Flavors:", value=str(", ".join(self.flavors)).title(), inline=False)
        embed.add_field(name="Drinks:", value=str(", ".join(self.drinks)).title(), inline=False)
        msg = await self.bot.say(embed=embed)

    @bar.command(name="reload")
    async def reload_drinks(self):
        with open(self.drinkspath) as f:
            drinks = json.load(f)
        self.drinks = drinks
        pass

    @bar.command(name="help", pass_context=True)
    async def bar_help(self):
        """Shows help about how to use the command"""
        embed = discord.Embed(title="So this is how it works.", color=self.embed_color, description=self.tut_text)
        embed.set_thumbnail(url=self.embed_footer_icon)
        await self.bot.say(embed=embed)
        pass

    @bar.group(invoke_without_command=True, pass_context=True)
    async def order(self, ctx, *, drinkType : str = "random"):
        """Orders drinks"""
        member = ctx.message.author
        if drinkType.lower() != "random":
            alllists = list([str(drink) for drink in self.drinks])
            matching = [s for s in alllists if drinkType.title() in s]
            if len(matching) > 0:
                drinkType = matching[0]
        if drinkType.title() in self.drinks:
            type_of_drink = "specific"
        elif drinkType.title() in self.flavors:
            type_of_drink = "flavor"
        elif drinkType.title() in self.types:
            type_of_drink = "type"
        else:
            type_of_drink = "random"

        if type_of_drink == "specific":
            rawdrink = drinkType.lower()
        elif type_of_drink == "flavor":
            while True:
                rawdrink, temp = random.choice(list(self.drinks.items()))
                if temp["Flavor"].lower() == drinkType.lower():
                    del temp
                    break
        elif type_of_drink == "type":
            while True:
                rawdrink, temp = random.choice(list(self.drinks.items()))
                if temp["Type"].lower() == drinkType.lower():
                    del temp
                    break
        elif type_of_drink == "random":
            rawdrink, temp = random.choice(list(self.drinks.items()))
            del temp
        else:
            rawdrink = None

        a = account(member)

        if rawdrink != None:
            drink = self.drinks[rawdrink.title()]
            name = rawdrink.lower().title()
            dtype = drink["Type"]
            ddesc = drink["Description"]
            dflavor = drink["Flavor"]
            dtech = drink["Techniques"]
            dprice = drink["Price"]
            try:
                qdrink = random.choice(self.qdrinks[dflavor])
            except KeyError:
                qdrink = random.choice(self.qdrinks["General"])
            except:
                raise


            bought_text = ""
            if not a.can_buy(dprice):
                bought_text = "\"I'm not giving this drink out for free.\""
            if a.can_buy(dprice):
                original_amount = a.amount
                new_amount = int(a.amount) - int(dprice)
                bought_text = qdrink

            embed = discord.Embed(title=discord.Embed.Empty, color=self.embed_color)
            icon = utils.get_drink_icon(name)
            url = "http://va11halla.wikia.com/wiki/"+name.replace(" ", "_")
            if not icon:
                url = discord.Embed.Empty
                try:
                    icon = self.drinks[name]["custom_icon"]
                except KeyError:
                    icon = ""
                except:
                    raise
            embed.set_author(name="Drink Requested: "+rawdrink.title(), url=url, icon_url=icon)
            embed.set_thumbnail(url=self.embed_footer_icon)
            if not a.can_buy(dprice):
                embed.add_field(name="You Cannot Buy the Drink!", value="You lack the required funds for this drink! You need ${} more!".format(int(int(dprice) - int(account(member).amount))), inline=False)
            if a.can_buy(dprice):
                embed.add_field(name="You Can Buy the Drink!", value="Money will be deducted from your account!\nYour current Tab Amount: ${}\nAmount that'll be deducted: ${}\nTab Amount After Purchase: ${}".format(original_amount, dprice, new_amount), inline=False)
                embed.add_field(name="Would you like to Buy?", value="Type `Yes` to Purchase, `No` to cancel, or `For <User>` to give the drink to that member.", inline=False)
            embed.add_field(name="Flavor:", value=dflavor, inline=True)
            embed.add_field(name="Type:", value=dtype, inline=True)
            embed.add_field(name="Price:", value="$"+dprice, inline=True)
            embed.add_field(name="Techniques:", value=str(", ".join(dtech)).title(), inline=True)
            embed.add_field(name="Description:", value=ddesc, inline=False)
            embedmsg = await self.bot.say(embed=embed)
            if not a.can_buy(dprice):
                return
            while True:
                msg = await self.bot.wait_for_message(timeout=7.5, channel=ctx.message.channel, author=ctx.message.author)
                if msg == None:
                    yes = None
                    break
                elif msg.content.lower() in ["yes","y","yea","yeah"]:
                    yes = True
                    break
                elif msg.content.lower() in ["no","n","nah","nope"]:
                    yes = False
                    break
                elif msg.content.lower().startswith("for") and msg.mentions and len(msg.mentions) >= 1:
                    mentions = msg.mentions
                    yes = -1
                elif msg.mentions and len(msg.mentions) == 0:
                    await self.bot.say("\"You need to tell me who you want to give it to!\"")
                else:
                    pass

            if yes == True:
                if a.can_buy(dprice):
                    a.buy(dprice)
                    name = "You Bought the Drink!"
                    value = "Money has been deducted from your account!\nYour Original Tab Amount: ${0}\nAmount that has been deducted: ${1}\nYour New Tab Amount: ${2}".format(original_amount, dprice, new_amount)
                else:
                    return
            elif yes == False:
                name = "You canceled the order!"
                value = "Your order has been canceled and you will not be charged."
            elif yes == None:
                name = "Order Canceled!"
                value = "You took too long to answer, so I canceled the order. You will not be charged."
            elif yes == -1 and len(mentions) != 0:
                purchase_amount = dprice*len(mentions)
                a.buy(purchase_amount)
                name = "You bought a drink for `{}`!".format(", ".join([m.display_name for m in mentions]))
                value = "Money has been deducted from your account!\nYour Original Tab Amount: ${0}\nAmount that has been deducted: ${1}\nYour New Tab Amount: ${2}".format(original_amount, dprice, new_amount-(purchase_amount))
                if len(mentions) > 1:
                    value = "You have been charged for each drink towards the each member\n"+value
            else:
                return

            embed.set_field_at(0, name=name, value=value, inline=False)
            embed.remove_field(1)
            await self.bot.edit_message(embedmsg, embed=embed)

    @bar.command(name="info", pass_context=True)
    async def drink_info(self, ctx, *, drink):
        """Don't know about a drink. Get info about it here."""
        if drink.lower() != "random":
            alllists = list([str(drink) for drink in self.drinks])
            matching = [s for s in alllists if drink.title() in s]
            if len(matching) > 0:
                drink = matching[0]
        if drink.title() in self.drinks:
            type_of_drink = "specific"
        elif drink.title() in self.flavors:
            type_of_drink = "flavor"
        elif drink.title() in self.types:
            type_of_drink = "type"
        elif drink.lower() == "random":
            type_of_drink = "random"
        else:
            type_of_drink = "none"

        if type_of_drink == "specific":
            rawdrink = drink.lower()
        elif type_of_drink == "flavor":
            while True:
                rawdrink, temp = random.choice(list(self.drinks.items()))
                if temp["Flavor"].lower() == drink.lower():
                    del temp
                    break
        elif type_of_drink == "type":
            while True:
                rawdrink, temp = random.choice(list(self.drinks.items()))
                if temp["Type"].lower() == drink.lower():
                    del temp
                    break
        elif type_of_drink == "random":
            rawdrink, temp = random.choice(list(self.drinks.items()))
            del temp
        else:
            rawdrink = None

        if rawdrink != None:
            drink = self.drinks[rawdrink.title()]
            name = rawdrink.lower().title()
            ddesc = drink["Description"]
            dtype = drink["Type"]
            dspecial = None
            if dtype == "Special":
                dspecial = drink["Special"]
            dflavor = drink["Flavor"]
            dtech = drink["Techniques"]
            dprice = drink["Price"]
            icon = utils.get_drink_icon(name)
            url = "http://va11halla.wikia.com/wiki/"+name.replace(" ", "_")
            if not icon:
                url = discord.Embed.Empty
                try:
                    icon = self.drinks[name]["custom_icon"]
                except KeyError:
                    icon = ""
                except:
                    raise
            embed = discord.Embed(title="Info for drink: {0}".format(rawdrink.title()), url=url, color=self.embed_color, description="*{}*".format(ddesc))
            embed.set_thumbnail(url=icon)
            embed.add_field(name="Flavor:", value=dflavor, inline=True)
            embed.add_field(name="Type:", value=dtype, inline=True)
            if dspecial:
                embed.add_field(name="Special:", value=dspecial, inline=True)
            embed.add_field(name="Price:", value="$"+dprice, inline=True)
            #embed.add_field(name="Can You Buy?:", value=str(account(ctx.message.author).can_buy(dprice)), inline=True)
            embed.add_field(name="Techniques:", value=str(", ".join(dtech)).title(), inline=True)
            await self.bot.say(embed=embed)

    @bar.group(aliases=["account"], pass_context=True, invoke_without_command=True)
    async def tab(self, ctx, *, member : discord.Member = None):
        """The perfect money system. (Has 1 subcommand)"""
        extra = ""
        if member == None or not utils.is_owner():
            member = ctx.message.author
        if member != ctx.message.author and utils.is_owner():
            extra = " for member: {0.name}#{0.discriminator} ({0.id})".format(member)
        a = account(member).amount
        embed = discord.Embed(title="Tab Amount!"+extra, color=self.embed_color, description="This shows your current amount in your tab. With this money you can buy drinks.\nTo gain more money, you can work for the bar. `cow.bar work`")
        embed.set_thumbnail(url=self.embed_footer_icon)
        embed.add_field(name="Amount:",value="${}".format(a))
        footer = random.choice(self.quotes["amount"])
        embed.set_footer(text=footer)
        await self.bot.say(embed=embed)

    @tab.command(name="transfer", aliases=["trans","give"], pass_context=True)
    async def transfer_money_to_member(self, ctx, amount = None, member : discord.Member = None):
        """Transfers money from your account into another's account."""
        if amount == None or member == None or amount == "0":
            return
        from_member = ctx.message.author
        to_member = member
        from_account = account(from_member)
        to_account = account(to_member)

        if from_account.can_buy(amount):
            from_account.buy(amount)
            to_account.add(amount)
            approved = True
        else:
            approved = False

        embed = discord.Embed(title="Transaction:", color=self.embed_color, description="{0} {3} ${1} {3} {2}".format(from_member.display_name, amount, to_member.display_name, "✖️️" if not approved else "➡️️"))
        embed.set_thumbnail(url=self.embed_footer_icon)
        embed.add_field(name="Transaction Complete!" if approved else "Not Enough Money!", value="Congrats {0.mention}, {1.display_name} gave you ${2}!".format(to_member, from_member, amount) if approved else discord.Embed.Empty)
        await self.bot.say(embed=embed)
        pass

    @bar.command(aliases=["job"], pass_context=True)
    async def work(self, ctx, *, workType : str = None):
        """Get paid for doing work or odd jobs."""
        work = Work(ctx.message.author)
        acc = account(ctx.message.author)
        if workType != None and workType.lower() == "help":
            embed = discord.Embed(title="How it works:", description=self.work_tut_text)
            embed.set_thumbnail(url=self.boss_pic)
            await self.bot.say(embed=embed)
        elif workType == None or workType.lower() not in work.workTypes:
            embed = discord.Embed(title="Looking for work!", description="Working allows for you to gain money like the good old days. The Current work you can do is below!\n\nHelp: `cow.bar work help`\nUsage: `cow.bar work (type of work)`")
            workTypes = work.workTypes
            embed.set_thumbnail(url=self.boss_pic)
            if not acc.data["met_boss"]:
                embed.add_field(name="How it works:", value=self.work_tut_text+ "\n(`cow.bar work help` for help. This only appears once.)", inline=False)
                j = acc.data
                j["met_boss"] = True
                with open(acc.fpath, "w") as f:
                    json.dump(j, f)
            embed.add_field(name="Types of work you can do:", value=str(", ".join(workTypes)).title(), inline=False)
            if not work.can_work():
                hoursleft = work.get_hours_left()
                embed.add_field(name="Hours til you can work again:", value="Less than {}left".format(hoursleft), inline=False)
            for item in workTypes:
                break
                desc = work.workdata[item]["desc"]
                minhours = work.workdata[item]["minhours"]
                maxhours = work.workdata[item]["maxhours"]
                minwage = work.workdata[item]["minwage"]
                embed.add_field(name=item.title(), value="Description: {}\nMin Hours: {}\nMax Hours: {}\nMin Wage: {}".format(desc, minhours, maxhours, minwage), inline=True)
            await self.bot.say(embed=embed)
            return
        elif workType.lower() in work.workTypes:
            can_work = work.can_work()
            item = workType.lower()
            if can_work:
                embed = discord.Embed(title="You wanna do this job?", description="Are you sure you want to do this job? `Yes` or `No`")
                embed.set_thumbnail(url=self.boss_pic)
                desc = work.workdata[item]["desc"]
                minhours = work.workdata[item]["minhours"]
                maxhours = work.workdata[item]["maxhours"]
                minwage = work.workdata[item]["minwage"]
                embed.add_field(name="Description:", value=desc, inline=False)
                embed.add_field(name="Min/Max Hours:", value="{}/{}".format(minhours, maxhours), inline=True)
                embed.add_field(name="Minimum Wage:", value=minwage, inline=True)
                embedmsg = await self.bot.say(embed=embed)
                while True:
                    msg = await self.bot.wait_for_message(timeout=5.0, channel=ctx.message.channel, author=ctx.message.author)
                    if msg == None:
                        yes = None
                        break
                    elif msg.content.lower() == "yes" or msg.content.lower() == "y":
                        yes = True
                        break
                    elif msg.content.lower() == "no" or msg.content.lower() == "n":
                        yes = False
                        break
                    else:
                        pass
                if yes:
                    worked = work.work(item)
                    did_work = worked[0]
                    if did_work:
                        hours = worked[1]
                        amount = worked[2]
                        boss_likes = worked[3]
                        embed.title = "Nice Work on the job!"
                        embed.description = "Nice job!"+(" Hey, go buy something nice. (+$500)" if boss_likes else "")
                        embed.add_field(name="Hours Worked:", value="{} hours".format(hours), inline=True)
                        embed.add_field(name="Money Earned:", value="${}".format(amount)+(" (+$500 for a job well done)" if boss_likes else ""), inline=True)
                        embed.add_field(name="You can work again in:", value="{} hours".format(str(24 + hours)))
                        await self.bot.edit_message(embedmsg, embed=embed)
                    else:
                        await self.bot.delete_message(embedmsg)
                        await self.bot.say("ERROR: "+worked[1])
            elif not can_work:
                hoursleft = work.get_hours_left()
                embed = discord.Embed(title="No can do!", description="You're trying to work too early, you still have {} left.".format(hoursleft))
                embed.set_thumbnail(url=self.boss_pic)
                await self.bot.say(embed=embed)
            else:
                return
            return
        pass

class account(object):
    def __init__(self, member):
        self.member = member
        self.mid = member.id
        self.path = "./data/bartender/customers/{}".format(self.mid)
        self.filename = "data.json"
        self.fpath = self.path+"/"+self.filename
        self.strtime = "%d-%m-%y %H-%M-%S-%f"
        if not os.path.exists(self.path) and not os.path.isfile(self.fpath):
            self.make_tab_account()
        with open(self.fpath) as f:
            self.data = json.load(f)
        self.amount = int(self.data["money"])
        self.firsttime = bool(self.data["firsttime"])

    def make_tab_account(self):
        mid = self.mid
        path = self.path
        filename = self.filename
        fpath = self.fpath
        if os.path.exists(path) == False:
            os.makedirs(path)
        if not os.path.isfile(fpath):
            with open(fpath, "w") as f:
                pass
        if os.path.exists(path) and os.path.getsize(fpath) != 0:
            return
        j = {
            "memberid":mid,
            "money":"1000",
            "lastworked":(datetime.datetime.utcnow()-datetime.timedelta(days=1)).strftime(self.strtime),
            "lastordered":datetime.datetime.utcnow().strftime(self.strtime),
            "firsttime":True,
            "met_boss":False,
            "met_alma":False,
            "met_dorothy":False,
            "met_gill":False
        }
        with open(fpath, "w") as f:
            json.dump(j, f)

    def buy(self, price : int):
        if not self.can_buy(price):
            return False
        data = self.data
        data["money"] = str(int(data["money"]) - int(price))
        with open(self.fpath, "w") as f:
            json.dump(data, f)
        return True


    def can_buy(self, price : int):
        amount = self.amount
        if int(price) <= int(amount):
            return True
        else:
            return False

    def add(self, price : int):
        data = self.data
        data["money"] = str(int(data["money"]) + int(price))
        with open(self.fpath, "w") as e:
            json.dump(data, e)

class Work(object):
    def __init__(self, member):
        self.member = member
        self.account = account(member)
        self.mid = member.id
        self.path = self.account.path
        self.filename = self.account.filename
        self.fpath = self.account.fpath
        with open(self.fpath) as f:
            self.data = json.load(f)
        self.workfilepath = "./data/bartender/work.json"
        with open(self.workfilepath) as w:
            self.workdata = json.load(w)
        self.workTypes = [t for t in self.workdata]
        self.amount = int(self.data["money"])
        self.firsttime = bool(self.data["firsttime"])
        self.strtime = self.account.strtime
        self.lastworked = datetime.datetime.strptime(self.data["lastworked"], self.strtime)

    def get_hours_left(self):
        now = datetime.datetime.utcnow()
        future = self.lastworked + datetime.timedelta(days=1)
        if now >= future:
            return "0 mins "
        diff = future - now
        seconds = diff.total_seconds()
        m, s = divmod(seconds, 60)
        hours, minutes = divmod(m, 60)
        if float(hours) < 1.0:
            return str(minutes)+" mins "
        else:
            return "{} hours and {} mins ".format(str(int(hours)), str(int(minutes)))

    def can_work(self):
        now = datetime.datetime.utcnow()
        then = self.lastworked
        diff = datetime.timedelta(days=1)
        now2 = then + diff
        if now >= now2:
            return True
        else:
            return False

    def work(self, work):
        member = self.member
        if not self.can_work():
            return [False, "cantwork"]
        boss_likes = random.random()
        if boss_likes >= 0.375:
            boss_likes = True
        else:
            boss_likes = False

        extra = 0
        if boss_likes:
            extra = 500

        work = work.lower()
        types = self.workdata
        if work in self.workTypes:
            min_hours = int(types[work]["minhours"])
            max_hours = int(types[work]["maxhours"])
            min_wage = int(types[work]["minwage"])
        else:
            return [False, "cantfind"]

        hours = random.randint(min_hours, max_hours)

        amount = int(hours * min_wage)
        amount_to_add = amount + extra
        data = self.data
        data["money"] = str(int(data["money"]) + int(amount_to_add))
        with open(self.fpath, "w") as e:
            json.dump(data, e)
        self.add_hours(hours=hours, reset=True)
        return [True, hours, amount, boss_likes]

    def add_hours(self, hours=0, mins=0, reset=False):
        delta = datetime.timedelta(hours=hours, minutes=mins)
        if reset:
            lastworked = datetime.datetime.utcnow()
        else:
            lastworked = self.lastworked
        if lastworked >= datetime.datetime.utcnow():
            return False
        data = self.data
        data["lastworked"] = (lastworked + delta).strftime(self.strtime)
        with open(self.fpath, "w") as f:
            json.dump(data, f)
        return True

# Don't Mind this mess, its so I dont have to ship default files with the cog. AKA So the code can make the files.

# DEFAULT DRINKS FILE
DRINKS_DICT = {
    "Piano Woman":{
        "Description":"It was originally called Pretty Woman, but too many people complained there should be a Piano Woman if there was a Piano Man.",
        "Flavor":"Sweet",
        "Type":"Promo",
        "Techniques":["Mixed"],
        "Ingredients":{"Adelhyde":5,"Bronson Extract":5,"Powdered Delta":2,"Flanergide":3,"Karmotrine":3},
        "Price":"320"
        },
    "Piano Man":{
        "Description":"This drink does not represent the opinions of the Bar Pianists Union or its associates.",
        "Flavor":"Sour",
        "Type":"Promo",
        "Techniques":["Mixed","Ice"],
        "Ingredients":{"Adelhyde":2,"Bronson Extract":3,"Powdered Delta":5,"Flanergide":5,"Karmotrine":3},
        "Price":"320"
        },
    "Zen Star":{
        "Description":"You'd think something so balanced would actually taste nice... you'd be dead wrong.",
        "Flavor":"Sour",
        "Type":"Promo",
        "Techniques":["Mixed","Ice"],
        "Ingredients":{"Adelhyde":4,"Bronson Extract":4,"Powdered Delta":4,"Flanergide":4,"Karmotrine":4},
        "Price":"210"
        },
    "Bloom Light":{
        "Description":"It's so unnecessarily brown....",
        "Flavor":"Spicy",
        "Type":"Promo",
        "Techniques":["Mixed","Ice","Aged"],
        "Ingredients":{"Adelhyde":4,"Bronson Extract":4,"Powdered Delta":4,"Flanergide":4,"Karmotrine":4},
        "Price":"230"
        },
    "Grizzly Temple":{
        "Description":"This one's kinda unbearable. It's mostly for fans of the movie it was used on.",
        "Flavor":"Bitter",
        "Type":"Promo",
        "Techniques":["Blended"],
        "Ingredients":{"Adelhyde":3,"Bronson Extract":3,"Powdered Delta":3,"Flanergide":0,"Karmotrine":1},
        "Price":"220"
        },
    "Brandtini":{
        "Description":"8 out of 10 smug assholes would recommend it but they're too busy being smug assholes.",
        "Flavor":"Sour",
        "Type":"Classy",
        "Techniques":["Mixed","Aged"],
        "Ingredients":{"Adelhyde":6,"Bronson Extract":0,"Powdered Delta":3,"Flanergide":0,"Karmotrine":1},
        "Price":"250"
        },
    "Bad Touch":{
        "Description":"We're nothing but mammals after all.",
        "Flavor":"Sour",
        "Type":"Classy",
        "Techniques":["Mixed","Iced"],
        "Ingredients":{"Adelhyde":0,"Bronson Extract":2,"Powdered Delta":2,"Flanergide":2,"Karmotrine":4},
        "Price":"250"
        },
    "Cobalt Velvet":{
        "Description":"It's like champaigne served on a cup that had a bit of cola left.",
        "Flavor":"Bubbly",
        "Type":"Classy",
        "Techniques":["Mixed","Iced"],
        "Ingredients":{"Adelhyde":2,"Bronson Extract":0,"Powdered Delta":0,"Flanergide":3,"Karmotrine":5},
        "Price":"280"
        },
    "Fringe Weaver":{
        "Description":"It's like drinking ethylic alcohol with a spoonful of sugar.",
        "Flavor":"Bubbly",
        "Type":"Classy",
        "Techniques":["Mixed","Aged"],
        "Ingredients":{"Adelhyde":1,"Bronson Extract":0,"Powdered Delta":0,"Flanergide":0,"Karmotrine":9},
        "Price":"260"
        },
    "Mercuryblast":{
        "Description":"No thermometer was harmed in the creation of this drink.",
        "Flavor":"Sour",
        "Type":"Classy",
        "Techniques":["Blended","Iced"],
        "Ingredients":{"Adelhyde":1,"Bronson Extract":1,"Powdered Delta":3,"Flanergide":3,"Karmotrine":2},
        "Price":"250"
        },
    "Beer":{
        "Description":"Traditionally brewed beer has become a luxury, but this one's pretty close to the real deal...",
        "Flavor":"Bubbly",
        "Type":"Classic",
        "Techniques":["Mixed"],
        "Ingredients":{"Adelhyde":1,"Bronson Extract":2,"Powdered Delta":1,"Flanergide":2,"Karmotrine":4},
        "Price":"200"
        },
    "Bleeding Jane":{
        "Description":"Say the name of this drink three times in front of a mirror and you'll look like a fool.",
        "Flavor":"Spicy",
        "Type":"Classic",
        "Techniques":["Blended"],
        "Ingredients":{"Adelhyde":0,"Bronson Extract":1,"Powdered Delta":3,"Flanergide":3,"Karmotrine":0},
        "Price":"200"
        },
    "Frothy Water":{
        "Description":"PG-rated shows' favorite Beer ersatz since 2040.",
        "Flavor":"Bubbly",
        "Type":"Classic",
        "Techniques":["Mixed","Aged"],
        "Ingredients":{"Adelhyde":1,"Bronson Extract":1,"Powdered Delta":1,"Flanergide":1,"Karmotrine":0},
        "Price":"150"
        },
    "Moonblast":{
        "Description":"No relation to the Hadron cannon you can see on the moon for one week every month.",
        "Flavor":"Sweet",
        "Type":"Girly",
        "Techniques":["Blended","Iced"],
        "Ingredients":{"Adelhyde":6,"Bronson Extract":0,"Powdered Delta":1,"Flanergide":1,"Karmotrine":2},
        "Price":"180"
        },
    "Fluffy Dream":{
        "Description":"A couple of these will make your tongue feel velvet-y. More of them and you'll be sleeping soundly.",
        "Flavor":"Sweet",
        "Type":"Girly",
        "Techniques":["Mixed","Aged"],
        "Ingredients":{"Adelhyde":3,"Bronson Extract":0,"Powdered Delta":3,"Flanergide":0,"Karmotrine":-1},
        "Price":"170"
        },
    "Sunshine Cloud":{
        "Description":"Tastes like old chocolate milk with its good smell intact. Some say it tastes like caramel too...",
        "Flavor":"Bitter",
        "Type":"Girly",
        "Techniques":["Blended","Iced"],
        "Ingredients":{"Adelhyde":2,"Bronson Extract":2,"Powdered Delta":0,"Flanergide":0,"Karmotrine":-1},
        "Price":"150"
        },
    "Sugar Rush":{
        "Description":"Sweet, light and fruity. As girly as it gets.",
        "Flavor":"Sweet",
        "Type":"Girly",
        "Techniques":["Mixed"],
        "Ingredients":{"Adelhyde":2,"Bronson Extract":0,"Powdered Delta":1,"Flanergide":0,"Karmotrine":0},
        "Price":"150"
        },
    "Blue Fairy":{
        "Description":"One of these will make all your teeth turn blue. Hope you brushed them well.",
        "Flavor":"Sweet",
        "Type":"Girly",
        "Techniques":["Mixed","Aged"],
        "Ingredients":{"Adelhyde":4,"Bronson Extract":0,"Powdered Delta":0,"Flanergide":1,"Karmotrine":-1},
        "Price":"170"
        },
    "Sparkle Star":{
        "Description":"They used to actually sparkle, but too many complaints about skin problem made them redesign the drink without sparkling.",
        "Flavor":"Sweet",
        "Type":"Girly",
        "Techniques":["Mixed","Aged"],
        "Ingredients":{"Adelhyde":2,"Bronson Extract":0,"Powdered Delta":1,"Flanergide":0,"Karmotrine":-1},
        "Price":"150"
        },
    "Gut Punch":{
        "Description":"It's supposed to mean \"a punch made of innards\", but the name actually described what you feel while drinking it.",
        "Flavor":"Bitter",
        "Type":"Manly",
        "Techniques":["Mixed","Aged"],
        "Ingredients":{"Adelhyde":0,"Bronson Extract":5,"Powdered Delta":1,"Flanergide":1,"Karmotrine":-1},
        "Price":"80"
        },
    "Suplex":{
        "Description":"A small twist on the Piledriver, putting more emphasis on the tongue burning and less on the throat burning.",
        "Flavor":"Bitter",
        "Type":"Manly",
        "Techniques":["Mixed","Iced"],
        "Ingredients":{"Adelhyde":0,"Bronson Extract":4,"Powdered Delta":0,"Flanergide":3,"Karmotrine":3},
        "Price":"160"
        },
    "Crevice Spike":{
        "Description":"It will knock the drunkenness out of you or knock you out cold.",
        "Flavor":"Sour",
        "Type":"Manly",
        "Techniques":["Blended"],
        "Ingredients":{"Adelhyde":0,"Bronson Extract":0,"Powdered Delta":2,"Flanergide":4,"Karmotrine":-1},
        "Price":"140"
        },
    "Marsblast":{
        "Description":"One of these is enough to leave your face red like the actual planet.",
        "Flavor":"Spicy",
        "Type":"Manly",
        "Techniques":["Blended"],
        "Ingredients":{"Adelhyde":0,"Bronson Extract":6,"Powdered Delta":1,"Flanergide":4,"Karmotrine":2},
        "Price":"170"
        },
    "Pile Driver":{
        "Description":"It doesn't burn as hard on the tongue but you better not have a sore throat when drinking it...",
        "Flavor":"Bitter",
        "Type":"Manly",
        "Techniques":["Mixed"],
        "Ingredients":{"Adelhyde":0,"Bronson Extract":3,"Powdered Delta":0,"Flanergide":3,"Karmotrine":4},
        "Price":"170"
        }
}
        
#DEFAULT QUOTES FILE
QUOTES_DICT = {
    "greetings":["\"Welcome back to Va-11 Hall-A, Please enjoy your stay.\"", "*wakes up* \"Oh. Welcome to....\" *goes back to sleep*"],
    "drinks":{
        "Sweet":["Sweet, like your personallity... That was a joke."],
        "Sour":["I didn't know you liked sour drinks. Noted."],
        "General":["Made fresh I swear"]
    },
    "amount":["\"Maybe you should work for us? I bet Boss can get something for you to do. Maybe you'll clean the bathroom.\" *grins*", "\"Boss pays pretty good. Ask her for work.\""]
}

#DEFAULT WORK FILE
WORK_DICT = {
    "cleaning":{
            "desc":"Easiest, fastest, and less paying job. Good for a quick buck.",
            "minhours":"1",
            "maxhours":"2",
            "minwage":"200"
    },
    "busboy":{
            "desc":"Clean up dishes around the bar.",
            "minhours":"3",
            "maxhours":"5",
            "minwage":"230"
    },
    "sign person":{
            "desc":"Stand outside and annoy-, I mean, tell people about the store.",
            "minhours":"4",
            "maxhours":"6",
            "minwage":"250"
    },
    "labor":{
            "desc":"Do some good old manual labor.",
            "minhours":"2",
            "maxhours":"5",
            "minwage":"270"
    },
    "bartender":{
            "desc":"Jill looks like she is having fun bartending. I just hope she isn't pretending. ",
            "minhours":"5",
            "maxhours":"6",
            "minwage":"300"
    }
}

def setup(bot):
    n = bartender(bot)
    bot.add_cog(n)