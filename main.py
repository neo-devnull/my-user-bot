import logging
from telethon.sync import TelegramClient, events
from config import api_id, api_hash
import asyncio

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.ERROR)


async def get_participants(client, chat):
    members = await client.get_participants(chat,
                                            aggressive=True,
                                            search="Deleted Account")
    return members


async def kick_user(client, chat, user):
    print(f"Kicking {user} from {chat}")
    try:
        msg = await client.kick_participant(
            chat,
            user
        )
        await msg.delete()
    except Exception:
        # Shiet, idk what happened.
        pass


async def parse(message):
    return message.split(' ')[1:]


with TelegramClient('acc', api_id, api_hash) as client:
    @client.on(events.NewMessage(pattern='^.member', outgoing=True))
    async def member_handler(message):
        await message.delete()
        parsed = await parse(message.text)

        if not len(parsed):
            return -1

        members = await get_participants(client, message.chat_id)
        deleted = [member for member in members if member.deleted]

        if parsed[0] == "ls":
            text = f"Member count: {len(members)}\nDeleted: {len(deleted)}"
            await client.send_message(
                message.chat_id,
                message=text
            )

        if parsed[0] == "rm":
            loop = asyncio.get_event_loop()
            for member in deleted:
                loop.create_task(kick_user(client, message.chat_id, member.id))

    @client.on(events.NewMessage(pattern='^.chat', outgoing=True))
    async def chat_id(message):
        await message.delete()
        parsed = await parse(message.text)
        if not len(parsed):
            return -1

        if parsed[0] == "id":
            await client.send_message(
                message.chat_id,
                message=f"{message.chat_id} is the chat id"
            )

    client.run_until_disconnected()