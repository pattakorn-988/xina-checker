from discord.ext import tasks, commands
from pathlib import Path
import requests
from dotenv import load_dotenv
import os

load_dotenv()
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    polling_job.start()


@bot.command()
async def version(ctx, arg=None):
    if arg is None:
        await ctx.send('Which environment would you like to check? (aws, sit, uat)')
    elif arg == 'aws':
        r = requests.get('https://sit-cd-scb-protect.iigdata.com/api/check_version')
        await ctx.send(r.json())
    elif arg == 'sit':
        r = requests.get('https://sit-cd.scbprotect.io/api/check_version')
        await ctx.send(r.json())
    elif arg == 'uat':
        r = requests.get('https://uat-cd.scbprotect.io/api/check_version')
        await ctx.send(r.json())
    else:
        await ctx.send('I don\'t understand, -20 social credit score.')


@tasks.loop(minutes=5.0)
async def polling_job():
    await bot.wait_until_ready()
    await poll_env('aws')
    await poll_env('sit')
    await poll_env('uat')


async def poll_env(env):
    earth = '<@311142730241933324>'
    lady = '<@839317682968068116>'
    tk = '<@365513774242988042>'
    boat = '<@796929182713905174>'
    pin = '<@692036135609827358>'

    endpoint = {
        'aws': 'https://sit-cd-scb-protect.iigdata.com/api/check_version',
        'sit': 'https://sit-cd.scbprotect.io/api/check_version',
        'uat': 'https://uat-cd.scbprotect.io/api/check_version',
    }.get(env, 'https://sit-cd-scb-protect.iigdata.com/api/check_version')

    r = requests.get(endpoint)
    env_file_check = Path(f'{env}.txt')
    env_file_check.touch(exist_ok=True)

    env_read = open(env_file_check, 'r')

    env_v = r.text
    old_v = env_read.read()
    env_changed = old_v != env_v

    env_read.close()

    if env_changed:
        env_write = open(env_file_check, 'w+')
        env_write.write(env_v)
        env_write.close()
        channel = bot.get_channel(int(os.getenv('CHANNEL')))

        templates = {
            'aws': f'\n{earth} {boat} {tk}\nAWS version changed\nOld:\n\t{old_v}\n\nNew:\n\t{env_v}',
            'sit': f'\n{lady} {earth}\nSIT version changed\nOld:\n\t{old_v}\n\nNew:\n\t{env_v}',
            'uat': f'\n{pin} {earth}\nUAT version changed\nOld:\n\t{old_v}\n\nNew:\n\t{env_v}',
        }.get(env, f'\n{earth} {boat} {tk}\nAWS version changed\nOld:\n\t{old_v}\n\nNew:\n\t{env_v}')

        if old_v:
            await channel.send(templates)


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
