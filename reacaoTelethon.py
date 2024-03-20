import asyncio
import json
import os
import random
from telethon.errors import PhoneNumberBannedError
from telethon.sync import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl import types

def load_config_session():
    with open('session.json', 'r') as file:
        config = json.load(file)
    return config

def load_config():
    with open('chats.json', 'r') as file:
        config = json.load(file)
    return config

async def react_to_message(client, event):
    emoji = lambda: random.choice([ "🏆", "🎉", "🔥", "👏"])
    
    await client(SendReactionRequest(
        peer=event.chat_id,
        msg_id=event.id,
        reaction=[types.ReactionEmoji(
            emoticon=emoji()
        )]
    ))

async def check_banned_number(client, session_file):
    try:
        # Verifica se o número foi banido
        await client.get_me()
    except PhoneNumberBannedError:
        print(f"O número {session_file} foi banido!")
        os.remove(session_file)
        print(f"Arquivo de sessão {session_file} removido.")
        return True
    return False

async def main(session_name, groups):
    config = load_config_session()
    api_id = config.get('api_id', [])
    api_hash = config.get('api_hash', [])

    client = TelegramClient(f'sessions/{session_name}', api_id, api_hash)
    await client.start()

    # Verifica se o número foi banido
    session_file = f'sessions/{session_name}'
    if await check_banned_number(client, session_file):
        return

    # Registre um único manipulador de evento para todas as mensagens
    @client.on(events.NewMessage(chats=groups))
    async def event_handler(event):
        await react_to_message(client, event)

    # Aguarde eventos indefinidamente
    await client.run_until_disconnected()

async def start_all_clients():
    sessions_folder = 'sessions'
    config = load_config()
    chats = config.get('chats', [])
    tasks = []

    for session_file in os.listdir(sessions_folder):
        if session_file.endswith('.session'):
            tasks.append(main(session_file, chats))

    print('BOT INICIADO')
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(start_all_clients())
