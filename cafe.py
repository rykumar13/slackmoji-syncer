import requests
import json
import os
import sys
import auth

# token for main slack
main_slack_token = auth.main_slack_token

# owari slack tokens
owari_slack_token = auth.owari_slack_token
api_bot_token = auth.api_bot_token

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
base_url = 'https://slack.com/api/'
auth_headers = {'Authorization': 'Bearer ' + api_bot_token}
slack_channel_id = auth.slack_channel_id
prod_channel_id = auth.prod_channel_id
test_channel_id = auth.test_channel_id


def get_emoji_list(auth_headers_ext):
    url = base_url + 'emoji.list'
    response = requests.get(url, headers=auth_headers_ext)
    json = validate_request_response(response)

    return json


def post_message_to_channel(message):
    url = base_url + 'chat.postMessage'
    params = {'channel': slack_channel_id, 'text': message, 'username': 'Emoji Chef', 'icon_emoji': ':blob_cook:'}
    response = requests.post(url, headers=auth_headers, params=params)
    validate_request_response(response)


def validate_request_response(response):
    if response.status_code != 200:
        raise RuntimeError(f'Response code {response.status_code} for emoji.list API call')
    json = response.json()
    if 'error' in json:
        raise RuntimeError(f'Received error response back from emoji.list API call: {json["error"]}')
    return json


if __name__ == "__main__":
    # a dry run will not post to slack or update the json record
    dry_run = 'dry' in sys.argv
    print('Loading old emojis from file...')
    with open(os.path.join(__location__, 'last.json'), 'r') as f:
        old_str = f.read()
        old_json = json.loads(old_str)['emoji']
    print('Loading new emojis from API...')
    new_json_raw = get_emoji_list(auth_headers)
    new_json = new_json_raw['emoji']
    all_new = [emoji_key for emoji_key in new_json if emoji_key not in old_json]
    new_emojis = [key for key in all_new if not new_json[key].startswith('alias')]
    new_aliases = [key for key in all_new if new_json[key].startswith('alias')]

    all_removed = [emoji_key for emoji_key in old_json if emoji_key not in new_json]
    emoji_count = len([1 for x in new_json if not new_json[x].startswith('alias')])
    alias_count = len(new_json) - emoji_count
    print('Success!\n')
    print(f'Emoji Count: {emoji_count}')
    print(f'Alias Count: {alias_count}')
    print(f'New Emojis:  {new_emojis}')
    print(f'New Aliases: {new_aliases}')
    print(f'All Removed: {all_removed}')
    message = f'We now have {emoji_count} varieties of emoji available, with {alias_count} aliases.\n\n'

    if len(all_new) > 0:
        message += f'*New emoji(s) fresh out the oven:*\n'
        for key in all_new:
            if key in new_emojis:
                message += f':{key}: {key}\n'
            else:
                message += f':{key}: {key} (alias for `{new_json[key][6:]}`)\n'
    else:
        message += 'We\'re fresh out of new emojis, check back tomorrow!'
    if len(all_removed) > 0:
        message += f'\n\n:rip: *The following emojis are no longer for sale:* :byedog:\n'
        message += '\n'.join([f':{key}: {old_json[key]}' for key in all_removed])
    if not dry_run:

        if 'fresh out of new emojis' not in message:
            print('Posting message to channel...')
            post_message_to_channel(message)

        # update the last.json file
        print('Updating previous emoji record...')
        with open(os.path.join(__location__, 'last.json'), 'w') as f:
            f.write(json.dumps(new_json_raw))
    else:
        print(message)
    print('Done!')
