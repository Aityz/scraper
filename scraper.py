import json
import urllib.request
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Discord Scraper')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
    userAgent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 '
                 'Safari/537.36 OPR/102.0.0.0')
    parser.add_argument('--useragent', type=str, default=userAgent,
                        help='User Agent to use for requests.')
    parser.add_argument('--token', type=str, help='Discord Token to use for requests.', default=None)
    parser.add_argument('--channel', type=int, help='Channel ID to scrape.', default=None)
    parser.add_argument('--savefile', type=str, help='File to save data to.', default=None)
    args = parser.parse_args()
    if args.token is None:
        token = input('Enter Discord Token: ')
    else:
        token = args.token
    if args.channel is None:
        scrapeType = input('Enter 1 for DMs, 2 for Group DMs, 3 for Guild Channels: ')
        if scrapeType == '1':
            request = urllib.request.Request('https://discord.com/api/v9/users/@me/channels',
                                             headers={'Authorization': token, 'User-Agent': args.useragent})
            with urllib.request.urlopen(request) as response:
                channels = json.loads(response.read().decode('utf-8'))

            dms = []

            for c in channels:
                if c['type'] == 1:
                    dms.append(c)

            for i in range(len(dms)):
                print(f'{i + 1}: Direct Message with {dms[i]["recipients"][0]["username"]} ({dms[i]["id"]})')
            channel = int(input('Enter Channel Number: '))
            channel = dms[channel - 1]['id']
        elif scrapeType == '2':
            request = urllib.request.Request('https://discord.com/api/v9/users/@me/channels',
                                             headers={'Authorization': token, 'User-Agent': args.useragent})

            with urllib.request.urlopen(request) as response:
                channels = json.loads(response.read().decode('utf-8'))

            dms = []

            for c in channels:
                if c['type'] == 3:
                    dms.append(c)

            for i in range(len(dms)):
                if dms[i]['name'] is None:
                    members = ''

                    for m in dms[i]['recipients']:
                        members += f'{m["username"]}#{m["discriminator"]}, '

                    print(f'{i + 1}: GDM with {members} ({dms[i]["id"]})')
                else:
                    print(f'{i + 1}: {dms[i]["name"]} ({dms[i]["id"]})')
            channel = int(input('Enter Channel Number: '))

            channel = dms[channel - 1]['id']
        elif scrapeType == '3':
            request = urllib.request.Request('https://discord.com/api/v9/users/@me/guilds',
                                             headers={'Authorization': token, 'User-Agent': args.useragent})

            with urllib.request.urlopen(request) as response:
                guilds = json.loads(response.read().decode('utf-8'))

            for i in range(len(guilds)):
                print(f'{i + 1}: {guilds[i]["name"]} ({guilds[i]["id"]})')

            guild = int(input('Enter Guild Number: '))

            guild = guilds[guild - 1]['id']

            request = urllib.request.Request(f'https://discord.com/api/v9/guilds/{guild}/channels',
                                             headers={'Authorization': token, 'User-Agent': args.useragent})

            with urllib.request.urlopen(request) as response:
                channels = json.loads(response.read().decode('utf-8'))

            for i in range(len(channels)):
                print(f'{i + 1}: {channels[i]["name"]} ({channels[i]["id"]})')
            channel = int(input('Enter Channel Number: '))

            channel = channels[channel - 1]['id']
    else:
        channel = args.channel

    if args.debug is True:
        print('INFO: Channel ID has been selected.')

    batch = 1

    if args.debug is True:
        print('INFO: Fetching Batch 1 of data...')

    request = urllib.request.Request(f'https://discord.com/api/v9/channels/{channel}/messages?limit=50',
                                     headers={'Authorization': token, 'User-Agent': args.useragent})

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode('utf-8'))

    if args.debug is True:
        print('INFO: Batch 1 of data has been fetched.')

    dataArrays = []

    for msg in data:
        dataArrays.append(msg)

    last = data[-1]['id']

    while True:
        original = last
        if args.debug is True:
            print(f'INFO: Fetching Batch {batch + 1} of data...')
        batch += 1
        request = urllib.request.Request(f'https://discord.com/api/v9/channels/{channel}/messages?limit=50&before={last}',
                                         headers={'Authorization': token, 'User-Agent': args.useragent})
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode('utf-8'))
        if args.debug is True:
            print(f'INFO: Batch {batch + 1} of data has been fetched.')

        if len(data) == 0:
            break

        last = data[-1]['id']

        if original == last:
            break

        for msg in data:
            dataArrays.append(msg)

    if args.debug is True:
        print('INFO: Data has been fetched.')

    if args.savefile is None:
        savefile = input('Enter location to save data: ')
    else:
        savefile = args.savefile

    json.dump(dataArrays, open(savefile, 'w'), indent=4)

    if args.debug is True:
        print('INFO: Data has been saved.')
