import os
import requests
from time import sleep
import auth

print("running emoji_upload script")

# owari api bot token
API_BOT_TOKEN = auth.api_bot_token
USER_TOKEN = auth.USER_TOKEN

# endpoints
URL_ADD = "https://owari-famiri.slack.com/api/emoji.add"
URL_CUSTOMIZE = "https://owari-famiri.slack.com/customize/emoji"
URL_LIST = "https://owari-famiri.slack.com/api/emoji.adminList"

# test folder
TEST_FOLDER = 'output/'


def main():
    session = _session()
    uploaded = 0
    for filename in os.listdir(TEST_FOLDER):
        print("Processing {}.".format(filename))
        emoji_name = os.path.splitext(os.path.basename(filename))[0].strip()
        upload_emoji(session, emoji_name, "{}{}".format(TEST_FOLDER, filename))
        print("{} upload complete.".format(filename))
        uploaded += 1
    print('\nUploaded {} emojis'.format(uploaded))


def _session():
    session = requests.session()
    session.url_customize = URL_CUSTOMIZE
    session.url_add = URL_ADD
    session.url_list = URL_LIST
    session.api_token = USER_TOKEN
    return session


def upload_emoji(session, emoji_name, filename):
    data = {
        'mode': 'data',
        'name': emoji_name,
        'token': session.api_token
    }
    while True:
        with open(filename, 'rb') as f:
            files = {'image': f}
            resp = session.post(session.url_add, data=data, files=files, allow_redirects=False)

            if resp.status_code == 429:
                wait = int(resp.headers.get('retry-after', 1))
                print("429 Too Many Requests!, sleeping for %d seconds" % wait)
                sleep(wait)
                continue

        resp.raise_for_status()

        # Slack returns 200 OK even if upload fails, so check for status.
        response_json = resp.json()
        if not response_json['ok']:
            print("Error with uploading %s: %s" % (emoji_name, response_json))

        break


if __name__ == '__main__':
    main()

