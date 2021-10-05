import asyncio

from bot import bot, HU_APP
from pyromod import listen
from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)


API_TEXT = """Galo Kamu, {}.
Selamat Datang !
Saya Adalah String Session Generator Bot
Saya Bisa Membantumu Mendapatkan String Dengan Mudah Dan Cepat !

Cukup Tekan /help untuk Info Lebih Lanjut !

⚠️ Disclaimer - Bot ini 100% aman. But Please Make Sure that You Properly Know What a String Session is & How it Works !
Bot Support - @RioGroupSupport

Sekarang Kirim `API_ID` Atau `APP_ID` Untuk Memulai Generating Session.
"""



HASH_TEXT = "Sekarang Kirim `API_HASH`.\n\nTekan /cancel Untuk Membatalkan."
PHONE_NUMBER_TEXT = (
    "Sekarang kirim nomor akun telegram mu. \n"
    "Untuk mendapatkan kode. Contoh: **+6280000029**\n\n"
    "Tekan /cancel Untuk Cancel Task."
)

@bot.on_message(filters.private & filters.command("start"))
async def genStr(_, msg: Message):
    chat = msg.chat
    api = await bot.ask(
        chat.id, API_TEXT.format(msg.from_user.mention)
    )
    if await is_cancel(msg, api.text):
        return
    try:
        check_api = int(api.text)
    except Exception:
        await msg.reply("`API_ID` Tidak Benar.\nTekan /start untuk Memulai lagi.")
        return
    api_id = api.text
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    if not len(hash.text) >= 30:
        await msg.reply("`API_HASH` Tidak Benar.\nTekan /start untuk Memulai lagi.")
        return
    api_hash = hash.text
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            return
        phone = number.text
        confirm = await bot.ask(chat.id, f'`Is "{phone}" Apakah Sudah Benar? (y/n):` \n\nKirim: `y` (Jika Ya)\nKirim: `n` (Jika Tidak)')
        if await is_cancel(msg, confirm.text):
            return
        if "y" in confirm.text:
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nTekan /start Untu Mulai Ulang.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"Anda Terkena Floodwait  {e.x} Detik")
        return
    except ApiIdInvalid:
        await msg.reply("API ID dan API Hash Tidak Benar.\n\nPress /start to Start again.")
        return
    except PhoneNumberInvalid:
        await msg.reply("Your Phone Number Tidak Benar.\n\nPress /start to Start again.")
        return
    try:
        otp = await bot.ask(
            chat.id, ("An OTP is sent to your phone number, "
                      "Please enter OTP in `1 2 3 4 5` format. __(Space between each numbers!)__ \n\n"
                      "If Bot not sending OTP then try /restart and Start Task again with /start command to Bot.\n"
                      "Press /cancel to Cancel."), timeout=300)

    except TimeoutError:
        await msg.reply("Time limit reached of 5 min.\nPress /start to Start again.")
        return
    if await is_cancel(msg, otp.text):
        return
    otp_code = otp.text
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await msg.reply("Invalid Code.\n\nPress /start to Start again.")
        return
    except PhoneCodeExpired:
        await msg.reply("Code is Expired.\n\nPress /start to Start again.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id, 
                "Your account have Two-Step Verification.\nPlease enter your Password.\n\nPress /cancel to Cancel.",
                timeout=300
            )
        except TimeoutError:
            await msg.reply("`Time limit reached of 5 min.\n\nPress /start to Start again.`")
            return
        if await is_cancel(msg, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"#PYROGRAM #STRING_SESSION\n\n```{session_string}``` \n\nBy [@String_Session_Gen_Bot](tg://openmessage?user_id=1816235885) \nA Bot By @fckualot")
        await client.disconnect()
        text = "✅ Selamat!  pyrogram string session untuk Telegram account mu berhasil dibuat.  Kau bisa mencari string sessionmu didalam saved messages atau pesan tersimpan di telegram accountmu. Terimakasih telah menggunakan saya! 🤖."
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="🔥 Support Group 🔥", url=f"https://t.me/riogroupsupport")]]
        )
        await bot.send_message(chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return


@bot.on_message(filters.private & filters.command("restart"))
async def restart(_, msg: Message):
    await msg.reply("Restarted Bot!")
    HU_APP.restart()


@bot.on_message(filters.private & filters.command("help"))
async def restart(_, msg: Message):
    out = f"""
Hi, {msg.from_user.mention}. This is Pyrogram Session String Generator Bot. \
I will give you `STRING_SESSION` for your UserBot.
It needs `API_ID`, `API_HASH`, Phone Number and One Time Verification Code. \
Which will be sent to your Phone Number.
You have to put **OTP** in `1 2 3 4 5` this format. __(Space between each numbers!)__
**NOTE:** If bot not Sending OTP to your Phone Number than send /restart Command and again send /start to Start your Process. 
Must Join Channel for Bot Updates !!
"""
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('𝘽𝙤𝙩𝙨 𝙎𝙪𝙥𝙥𝙤𝙧𝙩', url='https://t.me/riogroupsupport'),
                InlineKeyboardButton('𝘿𝙚𝙫𝙚𝙡𝙤𝙥𝙚𝙧', url='https://t.me/fckualot')
            ],
            [
                InlineKeyboardButton('🔥 𝗨𝗽𝗱𝗮𝘁𝗲𝘀 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 🔥 ', url='https://t.me/riobotsupport'),
            ]
        ]
    )
    await msg.reply(out, reply_markup=reply_markup)


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("Process Cancelled.")
        return True
    return False

if __name__ == "__main__":
    bot.run()
