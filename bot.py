import nest_asyncio
import asyncio
import logging
import re
import pathlib
from telegram import Update, MessageEntity
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

logging.basicConfig(level=logging.INFO)

TOKEN = "7676730172:AAFi2nwDQpCGAU6jH0TLewGsezxofoB4PsQ"
GROUP_CHAT_ID = -1001890799008

BASE_DIR = pathlib.Path(__file__).parent.resolve()
SECOND_AD_IMAGE_PATH = BASE_DIR / "second_ad_banner.jpg"
FOURTH_AD_IMAGE_PATH = BASE_DIR / "fourth_ad_banner.jpg"
FIFTH_AD_IMAGE_PATH = BASE_DIR / "fifth_ad_banner.jpg"  # 🆕 добавлено

CUSTOM_EMOJI_IDS = ["5206607081334906820", "5355012477883004708"]
PREMIUM_ADMINS = [6589844779]

bot_id = None

first_law_text = (
    "🔔 Ուշադրություն 🔔  \n"
    "‼️ Խմբի կանոնները ‼️ \n\n"
    "1️⃣ Գրեք հայերեն կամ լատինատառ  \n"
    "2️⃣ Չտարածել ուրիշ խմբեր\n"
    "3️⃣ Հարգել խմբի բոլոր անդամներին\n"
    "4️⃣ Քաղաքականություն չքննարկել\n"
    "5️⃣ Կրիմինալ պոստերը արգելվում է\n"
    "6️⃣ Ցանկացած գոծունեության գովազդը, որից եկամուտ եք ակնկալում, բացի Ձեր անձնական իրերի վաճառքից կամ վարձակալության հանձնելուց վճարովի է, գովազդի համար կապնվեք @losangelosadmin"
)

SECOND_AD_TEXT = """Բարև Ձեզ   
🚘 Եթե ունեցել եք ավտովթար համեցեք իմ Body Shop :
✅  Արտաքին դեֆորմացիա (Body Work)
✅  Ներկում (Paint)
✅ Փոլիշ (Polish)
✅  Ընթացքային մասերի վերանորոգում (Suspension)
✅  Իրավաբանական օգնություն
📞 7475995550, 7473085876
📱 https://www.instagram.com/_carprof_
"""

FOURTH_AD_TEXT = (
    "❇️Մեր  ակադեմիան առաջարկում է Օնլայն  Ամերիկյան Անգլերենի դասեր ձեր ցանկացած վայրից և ցանկացած ժամի❇️\n"
    "✔️Սովորեք նորագույն մեթոդներով և արագ \n"
    "✔️Խոսակցական Ամերիկյան Անգլերեն\n"
    "✔️Հնարավոր և անհնար մեթոդներ արագ արդյունք ունենալու համար\n"
    "Հարցերի դեպքում կապնվեք @elevate_academy1"
)

FIFTH_AD_TEXT = (  # 🆕 добавлено
    "Բարև Ձեզ👋\n"
    "‼️Մենք տրամադրում ենք երաշխավորված Շենգենյան վիզաներ 1-5 տարի ժամկետով՝ առանց մերժման, "
    "բոլոր ՀՀ քաղաքացիներին, ովքեր ունեն կանաչ քարտ կամ ժամանակավորապես բնակվում են Կալիֆոռնիա նահանգում։ "
    "Հարցերի դեպքում՝\n"
    "Telegram @SCHENGEN_G\n"
    "WhatsApp +1 424 278 89 41‼️"
)


def build_premium_ad(is_premium=False):
    text = (
        "📺 First Stream TV\n"
        "✅  16,000+ ալիքներ\n"
        "✅  Ֆիլմեր • Սերիալներ • Սպորտ\n"
        "✅  Հասանելի է բոլոր սարքերում\n"
        "💸 Շատ մատչելի գին\n\n"
        "✅ Netflix\n✅ Match TV\n✅ Fast Sports TV\n✅ Discovery\n✅ National Geographic\n"
        "📲 Կապ՝ @vahekarapetyan10"
    )
    entities = []
    if is_premium:
        idx = 0
        emoji_index = 0
        while True:
            pos = text.find("☑", idx)
            if pos == -1:
                break
            custom_id = CUSTOM_EMOJI_IDS[emoji_index % len(CUSTOM_EMOJI_IDS)]
            entities.append(MessageEntity(type="custom_emoji", offset=pos, length=1, custom_emoji_id=custom_id))
            idx = pos + 1
            emoji_index += 1
    return text, entities


async def is_user_admin_or_owner(update: Update, user_id: int) -> bool:
    if user_id in PREMIUM_ADMINS:
        return True
    try:
        member = await update.effective_chat.get_member(user_id)
        return member.status in ["administrator", "creator"]
    except Exception as e:
        logging.error(f"Ошибка проверки прав пользователя: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Բարև! Ես Լոս Անջելես Հայեր խմբի բոտն եմ 😊")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Հրամաններ:\n"
        "/premiumtest — պրեմիում գովազդի փորձ\n"
        "/getemojiid — ստանալ emoji ID\n"
        "/debugad — ստուգել գովազդի նկարը\n"
        "/testlaw — փորձել կանոնները\n"
        "/sendsecondad — ուղարկել 2-րդ գովազդ\n"
        "/sendfourthad — ուղարկել 4-րդ գովազդ (Անգլերեն դասեր)\n"
        "/sendfifthad — ուղարկել 5-րդ գովազդ (Շենգենյան վիզաներ)\n"
        "/del — ջնջել այն հաղորդագրությունը, որի պատասխանին դուք գրում եք այս հրամանը"
    )


async def premiumtest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_premium = user_id in PREMIUM_ADMINS or (update.effective_user.is_premium or False)
    text, entities = build_premium_ad(is_premium=is_premium)
    await update.message.reply_text(text=text)


async def getemojiid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ids = [e.custom_emoji_id for e in update.message.entities if e.type == "custom_emoji"] if update.message.entities else []
    await update.message.reply_text("ID-ներ:\n" + "\n".join(ids) if ids else "Չգտա custom emoji.")


async def debugad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Նկարի ստուգում: (Առաջին գովազդը ջնջված է)")


async def testlaw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_first_law(context.application)
    await update.message.reply_text("✅ Կանոնները ուղարկվեցին")


async def publish_second_ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_second_ad(context.application)
    await update.message.reply_text("✅ Երկրորդ գովազդը ուղարկվեց")


async def publish_fourth_ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_fourth_ad(context.application)
    await update.message.reply_text("✅ Չորրորդ գովազդը (Անգլերեն դասեր) ուղարկվեց")


async def publish_fifth_ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_fifth_ad(context.application)
    await update.message.reply_text("✅ Հինգերորդ գովազդը (Շենգենյան վիզաներ) ուղարկվեց")


async def delete_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_id
    user_id = update.effective_user.id

    if user_id != bot_id and not await is_user_admin_or_owner(update, user_id):
        await update.message.reply_text("⚠️ Только администраторы, владелец и бот могут использовать эту команду.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Խնդրում եմ պատասխանեք այն հաղորդագրությանը, որը ցանկանում եք ջնջել, "
            "և նորից գրեք այս հրամանը։"
        )
        return

    chat_id = update.effective_chat.id
    msg_to_delete_id = update.message.reply_to_message.message_id
    cmd_msg_id = update.message.message_id

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_to_delete_id)
        await context.bot.delete_message(chat_id=chat_id, message_id=cmd_msg_id)
        logging.info(f"Message {msg_to_delete_id} deleted by user {user_id}")
    except Exception as e:
        logging.error(f"Failed to delete message {msg_to_delete_id} by user {user_id}: {e}")


async def publish_first_law(application):
    await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=first_law_text)


async def publish_second_ad(application):
    if SECOND_AD_IMAGE_PATH.is_file():
        with SECOND_AD_IMAGE_PATH.open("rb") as f:
            await application.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=f, caption=SECOND_AD_TEXT)
    else:
        await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=SECOND_AD_TEXT)


async def publish_fourth_ad(application):
    if FOURTH_AD_IMAGE_PATH.is_file():
        with FOURTH_AD_IMAGE_PATH.open("rb") as f:
            await application.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=f, caption=FOURTH_AD_TEXT)
    else:
        await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=FOURTH_AD_TEXT)


async def publish_fifth_ad(application):
    if FIFTH_AD_IMAGE_PATH.is_file():
        with FIFTH_AD_IMAGE_PATH.open("rb") as f:
            await application.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=f, caption=FIFTH_AD_TEXT)
    else:
        await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=FIFTH_AD_TEXT)


async def publish_both_ads(application):
    await publish_second_ad(application)


link_pattern = re.compile(r"((https?:\/\/)?(t\.me|telegram\.me|telegram\.dog)\/\S+)|(tg:\/\/\S+)", re.IGNORECASE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = (update.message.text or "") + " " + (update.message.caption or "")

    if link_pattern.search(text):
        try:
            await update.message.delete()
            logging.info(f"Deleted message {update.message.message_id} from {update.effective_user.id} containing telegram or https link.")
        except Exception as e:
            logging.error(f"Failed to delete message {update.message.message_id}: {e}")


async def main():
    global bot_id
    application = ApplicationBuilder().token(TOKEN).build()

    me = await application.bot.get_me()
    bot_id = me.id

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("premiumtest", premiumtest))
    application.add_handler(CommandHandler("getemojiid", getemojiid))
    application.add_handler(CommandHandler("debugad", debugad))
    application.add_handler(CommandHandler("testlaw", testlaw))
    application.add_handler(CommandHandler("sendsecondad", publish_second_ad_cmd))
    application.add_handler(CommandHandler("sendfourthad", publish_fourth_ad_cmd))
    application.add_handler(CommandHandler("sendfifthad", publish_fifth_ad_cmd))
    application.add_handler(CommandHandler("del", delete_message_handler))

    application.add_handler(MessageHandler(filters.ALL & (~filters.StatusUpdate.ALL), handle_message))

    arm_timezone = timezone("Asia/Yerevan")
    scheduler = AsyncIOScheduler(timezone=arm_timezone)
    scheduler.add_job(publish_first_law, "cron", hour=9, minute=0, args=[application])
    scheduler.add_job(publish_both_ads, "cron", hour=11, minute=0, args=[application])
    scheduler.add_job(publish_fourth_ad, "cron", hour=12, minute=0, args=[application])
    scheduler.add_job(publish_fifth_ad, "cron", hour=14, minute=0, args=[application])  # 🕑 14:00 по Еревану
    scheduler.add_job(publish_fifth_ad, "cron", hour=22, minute=0, args=[application])  # 🌙 22:00 по Еревану
    scheduler.start()

    await application.run_polling()


if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
