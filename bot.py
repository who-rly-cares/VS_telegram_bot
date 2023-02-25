import telebot
import time

api_key = "6132881671:AAH7zzcAF2tP5iTeufxIAgxs0ubCcaz60hU"
command_starter = "#"
help_argument = "-h"
Updaters=[]
Handlers=[]

muted_list = []
admins_list = ["Who_Knows_Anyway"]

def IsAdmin(msg):
    return msg.from_user.username in admins_list

class MuteData():
    def __init__(self, tid, duration, date_started):
        self.tid = tid
        self.duration = int(duration)
        self.date_started = date_started

    def duration_ended(self):
        return self.date_started+self.duration <= time.time()

    def __str__(self):
        return f"{self.tid}->muted for \n{self.duration}seconds \nfrom unix:{self.date_started}"


def IsMuted(tid):
    for i1 in muted_list:
        if i1.tid == tid:
            return i1.duration_ended() == False
    return False

def FindMutedData_ByTid(tid):
    for i1 in muted_list:
        if i1.tid == tid:
            return i1
    return None

def RemoveMutedData_ByTid(tid):
    n = FindMutedData_ByTid(tid)
    muted_list.remove(n)
    del n

def AddMutedData(n:MuteData):
    muted_list.append(n)

def is_int(n:str):
    try:
        int(n)
        return True
    except:
        return False

def can_be_a_telegram_id(n:str):
    return n[0] == "@"

def IsCommand(msg, command_keyword):
    return msg.text[0] == command_starter and msg.text.split()[0].strip()[1:] == command_keyword

def IsHelpCommand(msg, command_keyword):
    cnd1 = msg.text[0] == command_starter
    cnd2 = msg.text.split()[0].strip()[1:] == command_keyword
    if msg.text.split().__len__() != 2:
        return False
    cnd3 = msg.text.split()[1] == help_argument

    return cnd1 and cnd2 and cnd3

class Command:
    instances = []
    def __init__(self, KeyWord, MainFunction, HelpFunction, TriggerFunction, UpdateFunction, ParseCommand):
        self.KeyWord = KeyWord
        self.MainFunction=MainFunction
        self.HelpFunction=HelpFunction
        self.TriggerFunction=TriggerFunction
        self.UpdateFunction=UpdateFunction
        self.ParseCommand=ParseCommand
        self.__class__.instances.append(self)

    def add_handler(self, bot):
        trigger_function = lambda msg : self.TriggerFunction(msg, bot) and IsCommand(msg, self.KeyWord)
        def output(msg):
            print(IsCommand(msg, self.KeyWord))
            if trigger_function(msg) == False:
                return False
            if IsHelpCommand(msg, self.KeyWord):
                self.HelpFunction(msg, bot)
                return True
            else:
                parsed_args = self.ParseCommand(msg, bot)
                self.MainFunction(msg, parsed_args, bot)
                return True

        Updaters.append(self.UpdateFunction)
        Handlers.append(output)
        globals()[self.KeyWord+"_Handler"] = output


    @classmethod
    def AddHandlers(cls, bot):
        for i1 in cls.instances:
            i1.add_handler(bot)






def CommandDeco(command_class_data)->None:
    output = Command(
    command_class_data.KeyWord,
    command_class_data.MainFunction,
    command_class_data.HelpFunction,
    command_class_data.TriggerFunction,
    command_class_data.UpdateFunction,
    command_class_data.ParseCommand)
    globals()[command_class_data.__name__] = output






@CommandDeco
class Dalam:
    KeyWord = "dalam"
    @staticmethod
    def ParseCommand( msg, bot)->dict:
        return {"how_many_times":int(msg.text.split()[1])};

    @staticmethod
    def MainFunction(msg, parsed_args, bot):
        output = "dalam"*parsed_args["how_many_times"]
        bot.reply_to(msg, output)

    @staticmethod
    def HelpFunction(msg, bot):
        help_txt ="""
        Syntax:
            /dalam <many_times:int>

        Exmpale:
            /dalam, 5
            will give you:
            dalam dalam dalam dalam dalam


        """
        bot.reply_to(msg, help_txt)

    @staticmethod
    def TriggerFunction(msg, bot)->bool:
        return True


    @staticmethod
    def UpdateFunction(msg, bot):
        pass


@CommandDeco
class Mute:
    KeyWord = "mh"
    @staticmethod
    def ParseCommand( msg, bot)->dict:
        is_list_muteds_command = None
        is_mute_command = None
        is_un_mute_command = None

        output = {
            "who":None,
            "duration":None,
            "is_list_muteds_command":None,
            "is_mute_command":None,
            "is_un_mute_command":None,}

        time_units = "hdwsm"
        time_unit_constnats = {
        "s":1,
        "m":60,
        "h":3600,
        "d":3600*24,
        "w":3600*24*7,}

        splited = msg.text.split()
        if len(splited) == 5:
            if splited[1] == "mute" and can_be_a_telegram_id(splited[2]) and is_int(splited[3]) and splited[4] in time_units:
                #/mh mute @id duration timeunit
                output['is_mute_command'] = True
                output['who'] = splited[2].replace("@", "")
                output['duration'] = int(splited[3]) * time_unit_constnats[splited[4]]


        if len(splited) == 3:
            if splited[1] == "unmute" and can_be_a_telegram_id(splited[2]):
                #mh unmute @id
                output['is_un_mute_command'] = True
                output['who'] = splited[2].replace("@", "")

        if len(splited) == 2:
            if splited[1] == "list":
                output["is_list_muteds_command"] = True

        print(f"ParseCommand from mute -> {output}")
        return output




    @staticmethod
    def MainFunction(msg, parsed_args, bot):
        if parsed_args["is_list_muteds_command"]:
            output = ""
            for i1 in muted_list:
                output += i1.__str__() + "\n"
            if output == "":
                output = "no one is muted "
            bot.reply_to(msg, output)

        elif parsed_args["is_un_mute_command"]:
            is_muted = IsMuted(parsed_args['who'])
            if is_muted == False:
                bot.reply_to(msg, f"{parsed_args['who']} was not muted!")

            elif is_muted == True:

                f = FindMutedData_ByTid(parsed_args["who"])
                RemoveMutedData_ByTid(parsed_args["who"])
                bot.reply_to(msg, f"{parsed_args['who']} is now unmuted")


        elif parsed_args["is_mute_command"]:
            n = MuteData(parsed_args["who"], parsed_args["duration"], time.time())
            AddMutedData(n)
            bot.reply_to(msg, f"{parsed_args['who']} is now muted from unix:{time.time()} for {parsed_args['duration']}seconds")




    @staticmethod
    def HelpFunction(msg, bot):
        help_txt =f"""
        Syntax:
            #mh mute @id duration timeunit -> mutes a person
            {command_starter}mh unmute @id -> unmutes a person
            {command_starter}mh list ->lists muted people

        Exmpale:
            {command_starter}mh mute @Kmaran 12 h

            mutes kamran for 12 hours
            note : h:hours w:weeks d:days



            {command_starter}mh unmute @kamran
            unmutes kamran
        """
        bot.reply_to(msg, help_txt)

    @staticmethod
    def TriggerFunction(msg, bot)->bool:
        print("is_admin", IsAdmin(msg))
        return IsAdmin(msg)



    @staticmethod
    def UpdateFunction(msg, bot):
        if IsMuted(msg.from_user.username):
            n = FindMutedData_ByTid(msg.from_user.username)
            if n.duration_ended() == True:
                RemoveMutedData_ByTid(msg.from_user.username)
                bot.reply_to(msg, "your are now unmuted :)")
            bot.delete_message(msg.chat.id, msg.message_id)






bot = telebot.TeleBot(api_key, parse_mode=None)

Command.AddHandlers(bot)

@bot.message_handler(func=lambda msg : True)
def MessageHandler(msg):
    print("@"+msg.from_user.username,msg.text)
    for i1 in Handlers:
        n = i1(msg)
        if n == True:
            break

    for i1 in Updaters:
        i1(msg, bot)

bot.infinity_polling()
