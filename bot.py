import json
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler


#Initialize root directory
data = {}
current_dir = 'C:/'
data[current_dir] = []

board_id = -1 # Initialized By sending the /start command
CHANNEL_ID = -100 # Shows the channel ID (https://bit.ly/2NbJAHD)
sent_messages_id = [] # Holds the ID of the messages sent by the bot


def create_board(info=""):
    """ Generates main page to display files and directories
    Args:
        info(str): you can choose a string to display in the information section (default is empty)
    """
    global current_dir
    borad_text = "💠 {0} \n\n".format(current_dir)
    for item in data[current_dir]:
        if item['type'] == 'dir':
            dir_name = item['name'].rsplit('/', 1)[1]
            borad_text += "📂 {0} \n".format(dir_name)
        else:
            borad_text += "🗄 {0}-{1}\n".format(item['id'],item['name'])

    return borad_text+"\n\n 💢 {0}".format(info)
    

def get_inline_keyboard():
    """Returns Inline Keyboard"""
    button_list = [
    InlineKeyboardButton("🗑 Clear History", callback_data='clear_history')]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    return reply_markup


def start(update: Update, context: CallbackContext) -> None:
    """Sends an empty board when the command /start is issued"""
    global board_id
    chat_id = update.message.chat_id
    clear_history(update, update.message.chat_id, update.message.message_id)
    board_id = update.message.bot.send_message(chat_id = chat_id, text =create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard()).message_id
    

def list_items(update: Update, context: CallbackContext) -> None:
    """Lists items in current directory when the command /ls is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    clear_history(update, update.message.chat_id, update.message.message_id)
    update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def remove_file(update: Update, context: CallbackContext) -> None:
    """Removes specific file in the current directory when the command /rm is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    file_name = update.message.text.split(' ')[1]

    clear_history(update, update.message.chat_id, update.message.message_id)
    for i in range(len(data[current_dir])):
            if data[current_dir][i]['type'] == 'file' and data[current_dir][i]['id'] == file_name:
                    del data[current_dir][i]
                    break
    update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def remove_dir(update: Update, context: CallbackContext) -> None:
    """Removes specific directory in the current directory when the command /rmdir is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    dir_name = str(current_dir+'/'+update.message.text.split(' ')[1])

    clear_history(update, update.message.chat_id, update.message.message_id)
    if dir_name in data:
            del data[dir_name]
            for i in range(len(data[current_dir])):
                    if data[current_dir][i]['name'] == dir_name:
                            del data[current_dir][i]
                            break
    update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def create_directory(update: Update, context: CallbackContext) -> None:
    """Creates a new directory in the current directory when the command /rm is issued"""
    global current_dir
    global board_id
    chat_id = update.message.chat_id
    new_dir_name = update.message.text.split(' ')[1]
    dir_name = str(current_dir+'/'+new_dir_name)
    
    clear_history(update, update.message.chat_id, update.message.message_id)
    if dir_name in data:
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())
    else:
            data[dir_name] = []
            data[current_dir].append({
                                    'name': dir_name,
                                    'type' : 'dir'})
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board() ,parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def change_directory(update: Update, context: CallbackContext) -> None:
    """Changes directory when the command /cd is issued"""
    global current_dir
    global board_id
    chat_id = update.message.chat_id
    destination_dir = update.message.text.split(' ')[1]
    previous_dir = current_dir.rsplit('/', 1)[0]
    
    clear_history(update, update.message.chat_id, update.message.message_id)
    if destination_dir == '.':
            current_dir = previous_dir
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())

    elif current_dir+'/'+destination_dir in data:
            current_dir = current_dir+'/'+destination_dir
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())
    else:
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())

    

def add_file(update: Update, context: CallbackContext) -> None:
    """Saves the received file"""
    global current_dir
    global CHANNEL_ID
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    file_id = update.message.bot.forward_message(CHANNEL_ID, from_chat_id=chat_id, message_id=message_id).message_id
    clear_history(update, update.message.chat_id, update.message.message_id)

    if update.message.audio:
        file_name = update.message.audio.file_name
    if update.message.document:
        file_name = update.message.document.file_name
    if update.message.video:
        file_name = update.message.video.file_name
    if update.message.voice:
        file_name = update.message.voice.file_unique_id

      
    data[current_dir].append({
                            'id'   : str(file_id),
                            'name' : file_name,
                            'type' : 'file'
                            })
    update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())
 

def get_files(update: Update, context: CallbackContext) -> None:
    """Sends specific file in the current directory when the command /get is issued"""
    global current_dir
    global CHANNEL_ID
    chat_id = update.message.chat_id
    file_name = update.message.text.split(' ')[1]
    clear_history(update, update.message.chat_id, update.message.message_id)

    for e in data[current_dir]:
        if e['type'] == 'file' and e['id'] == file_name:
            message_id = update.message.bot.forward_message(chat_id, from_chat_id=CHANNEL_ID, message_id=e['id']).message_id
            sent_messages_id.append(message_id)
  

def clear_history(update, chat_id,message_id):
    """Clears received messages in chat"""
    update.message.bot.delete_message(chat_id=chat_id,message_id=message_id)
     

def clear_illegal_commands(update: Update, context: CallbackContext) -> None:
    """Clears illegal messages and commands in chat"""
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    update.message.bot.delete_message(chat_id=chat_id,message_id=message_id)


def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    """Arranges buttons in the Inline keyboard"""
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def Inline_buttons(update: Update, context: CallbackContext) -> None:
    """Responses to buttons clicked in the inline keyboard"""
    query = update.callback_query
    chat_id = query.message.chat_id
    if query.data == 'clear_history':
        if len(sent_messages_id)>0:
            for mid in sent_messages_id:
                clear_history(query,chat_id, mid)
            sent_messages_id.clear()
            query.answer(text = 'Items removed!',show_alert = True)
        else:
            query.answer(text = 'There is no item to remove!',show_alert = True)


def main():
    """Starts the bot"""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("mkdir", create_directory))
    dispatcher.add_handler(CommandHandler("cd", change_directory))
    dispatcher.add_handler(CommandHandler("rm", remove_file))
    dispatcher.add_handler(CommandHandler("rmdir", remove_dir))
    dispatcher.add_handler(CommandHandler("ls", list_items))
    dispatcher.add_handler(CommandHandler("get", get_files))
  

    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command & ~Filters.text ,add_file))
    dispatcher.add_handler(MessageHandler(Filters.text | Filters.command ,clear_illegal_commands))
    dispatcher.add_handler(CallbackQueryHandler(Inline_buttons))
    

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()