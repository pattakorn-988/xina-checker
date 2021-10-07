import pathlib

from discord.ext import tasks, commands
import requests
from dotenv import load_dotenv
import os

load_dotenv()
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    channel = bot.get_channel(int(os.getenv('CHECKIN_CHANNEL')))
    await channel.send('Checked in to work!')
    if not polling_job.is_running():
        polling_job.start()


@bot.command()
async def version(ctx, arg=None):
    if arg is None:
        await ctx.send('Which environment would you like to check? (aws, sit, uat)')
    elif arg == 'aws':
        r = requests.get(f'{os.getenv("AWS_ENDPOINT")}/api/check_version')
        await ctx.send(r.json())
    elif arg == 'sit':
        r = requests.get(f'{os.getenv("SIT_ENDPOINT")}/api/check_version')
        await ctx.send(r.json())
    elif arg == 'uat':
        r = requests.get(f'{os.getenv("UAT_ENDPOINT")}/api/check_version')
        await ctx.send(r.json())
    else:
        await ctx.send('I don\'t understand, -20 social credit score.')


@bot.command()
async def fchk(ctx, arg=None):
    if arg is None:
        await ctx.send('Force check version diff\nUsage: !fchk <env>')
    elif arg in ['aws', 'sit', 'uat']:
        result = await poll_env(arg, True)
        if result:
            await ctx.send(result)
    else:
        await ctx.send('I don\'t understand, -20 social credit score.')


@bot.command()
async def cache(ctx, arg=None):
    result = await check_cache()
    await ctx.send(result)


@tasks.loop(minutes=5.0)
async def polling_job():
    await bot.wait_until_ready()
    await poll_env('aws')
    await poll_env('sit')
    await poll_env('uat')
    await check_cache()


async def poll_env(env, force=False):
    earth = f'<@{os.getenv("EA")}>'
    lady = f'<@{os.getenv("LD")}>'
    tk = f'<@{os.getenv("TK")}>'
    boat = f'<@{os.getenv("BT")}>'
    pin = f'<@{os.getenv("PN")}>'

    endpoint = {
        'aws': f'{os.getenv("AWS_ENDPOINT")}/api/check_version',
        'sit': f'{os.getenv("SIT_ENDPOINT")}/api/check_version',
        'uat': f'{os.getenv("UAT_ENDPOINT")}/api/check_version',
    }.get(env, f'{os.getenv("AWS_ENDPOINT")}/api/check_version')
    force_res = None
    r = requests.get(endpoint)
    if r.status_code == 200:
        path = os.path.join(pathlib.Path(__file__).parent, f'{env}.txt')
        env_file_check = pathlib.Path(path)
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

            if force:
                force_res = f'Change detected in {env.upper()}, announcing...'
            if old_v:
                await channel.send(templates)
        elif not env_changed and force:
            force_res = f'No change detected in {env.upper()}'

    return force_res


async def check_cache():
    pin = f'<@{os.getenv("PN")}>'
    endpoint = os.getenv('PROD_CACHE')
    r = requests.get(endpoint)
    if r.status_code == 200:
        fetched_items = r.json()['data']['search']['results']['items']
        # fetched_items = []
        count = len(fetched_items)
        if count == 0:
            template = f'\n{pin} \nCache problem detected\n\tEndpoint: {os.getenv("PROD_CACHE")}\n\tItems: {fetched_items}'
            channel = bot.get_channel(int(os.getenv('CHANNEL')))
            await channel.send(template)
            return 'Cache problem detected, announcing...'
        else:
            return 'Query response OK.'
    else:
        return 'Some error occurred while querying data.'


if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))
