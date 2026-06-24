import logging
import paramiko
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ----------------- إعدادات البوت وسيرفر CentOS 6 -----------------
TOKEN = "8808737324:AAHNBs5t-eWWjpEVTQ6jPD5mPr1jZtMt-74"

CENTOS_IP = "192.168.126.128"
CENTOS_USER = "hassan"
CENTOS_PASSWORD = "44797247m"
# -----------------------------------------------------------------

def run_ssh_command(command):
    """دالة للاتصال بالسيرفر وتنفيذ الأوامر"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(CENTOS_IP, username=CENTOS_USER, password=CENTOS_PASSWORD, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        ssh.close()
        return output if output else "No output"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Full Server Status", callback_data="status_all")],
        [InlineKeyboardButton("🧠 RAM & CPU", callback_data="status_ram_cpu")],
        [InlineKeyboardButton("💾 Disk Space", callback_data="status_disk")],
        [InlineKeyboardButton("⏱️ Uptime", callback_data="status_uptime")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🐧 CentOS 6 Monitoring Bot\nSelect what you want to check:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔄 Fetching data from CentOS 6... Please wait.")
    
    choice = query.data
    response_text = ""

    if choice == "status_uptime":
        uptime = run_ssh_command("uptime")
        response_text = f"⏱️ **Server Uptime:**\n`{uptime}`"
        
    elif choice == "status_disk":
        disk = run_ssh_command("df -h /")
        response_text = f"💾 **Disk Usage (Root):**\n`{disk}`"
        
    elif choice == "status_ram_cpu":
        # أوامر متوافقة تماماً مع CentOS 6 القديم
        ram = run_ssh_command("free -m")
        cpu = run_ssh_command("top -b -n 1 | head -n 5")
        response_text = f"🧠 **Memory Status (MB):**\n`{ram}`\n\n📊 **CPU Load:**\n`{cpu}`"
        
    elif choice == "status_all":
        uptime = run_ssh_command("uptime")
        ram = run_ssh_command("free -m | grep Mem")
        disk = run_ssh_command("df -h / | tail -n 1")
        
        response_text = (
            f"📊 **CentOS 6 Quick Dashboard**\n\n"
            f"⏱️ **Uptime:** {uptime}\n\n"
            f"🧠 **RAM (Total/Used/Free):**\n`{ram}`\n\n"
            f"💾 **Disk Usage:**\n`{disk}`"
        )

    # إعادة إظهار الأزرار عشان لو عايز يضغط تاني
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh Full Status", callback_data="status_all")],
        [InlineKeyboardButton("🧠 RAM & CPU", callback_data="status_ram_cpu")],
        [InlineKeyboardButton("💾 Disk Space", callback_data="status_disk")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text, parse_mode="Markdown", reply_markup=reply_markup)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_buttons))
    
    print("Monitoring Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()