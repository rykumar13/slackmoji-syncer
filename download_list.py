import json
import os
import auth
from cafe import get_emoji_list, __location__

print("running download_list script")

# gentrack slack api bot token
api_bot_token = auth.api_bot_token
auth_headers = {'Authorization': 'Bearer ' + api_bot_token}

new_json_raw = get_emoji_list(auth_headers)

with open(os.path.join(__location__, 'emoji_list_gentrack.json'), 'w') as f:
    f.write(json.dumps(new_json_raw))

# owari slack api bot token
api_bot_token = auth.api_bot_token
auth_headers = {'Authorization': 'Bearer ' + api_bot_token}

new_json_raw = get_emoji_list(auth_headers)

with open(os.path.join(__location__, 'emoji_list_owari.json'), 'w') as f:
    f.write(json.dumps(new_json_raw))

# load owari emojis
with open('emoji_list_owari.json', 'r') as a:
    owari_emojis = json.load(a)['emoji']

# load gentrack emojis
with open('emoji_list_gentrack.json', 'r') as b:
    gentrack_emojis = json.load(b)['emoji']

# compare the two
new_item = {emoji_key: gentrack_emojis[emoji_key] for emoji_key in gentrack_emojis if emoji_key not in owari_emojis}

# removed excluded emojis
with open('exclude_list.json', 'r') as x:
    exclude_list = json.load(x)['emoji']

# compare diff with exclude list
final_list = {emoji_key: new_item[emoji_key] for emoji_key in new_item if emoji_key not in exclude_list}

# write delta to file
with open('diff_emoji_list.json', 'w') as c:
    json.dump(final_list, c)

# download emojis
os.system('./download.sh diff_emoji_list.json')

# remove unwanted ; from name
directory = "output/"
for count, filename in enumerate(os.listdir(directory)):
    split = filename.split(":")

    if len(split) == 2:
        dst = split[0] + split[1]
        src = directory + filename
        dst = directory + dst
        os.rename(src, dst)
    else:
        print(filename)