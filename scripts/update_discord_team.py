"""GitHub Actions: öffentliche Teamnamen und Avatare aus Discord synchronisieren."""
import json, os, urllib.request, urllib.error, datetime
from pathlib import Path

keys=['DISCORD_BOT_TOKEN','DISCORD_GUILD_ID','DISCORD_TEAM_ROLE_ID','DISCORD_HELPER_ROLE_ID']
missing=[k for k in keys if not os.getenv(k)]
if missing:
    raise SystemExit('Fehlende Repository Secrets/Variables: '+', '.join(missing))

token=os.environ['DISCORD_BOT_TOKEN'].strip()
guild=os.environ['DISCORD_GUILD_ID'].strip()
team_role=os.environ['DISCORD_TEAM_ROLE_ID'].strip()
helper_role=os.environ['DISCORD_HELPER_ROLE_ID'].strip()
for val in (guild,team_role,helper_role):
    if not val.isdigit():raise SystemExit('Discord-IDs müssen aus Zahlen bestehen.')

members=[];last='0'
while True:
    url=f'https://discord.com/api/v10/guilds/{guild}/members?limit=1000&after={last}'
    req=urllib.request.Request(url,headers={'Authorization':'Bot '+token,'User-Agent':'TCL-Community-Roster/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            page=json.load(r)
    except urllib.error.HTTPError as err:
        raise SystemExit(f'Discord API HTTP {err.code}; bitte Bot-Rechte, Server-ID und Server Members Intent prüfen.') from None
    if not isinstance(page,list):raise SystemExit('Unerwartete Antwort von Discord.')
    members+=page
    if len(page)<1000:break
    last=page[-1]['user']['id']
    if len(members)>100000:raise SystemExit('Zu viele Mitglieder für diesen Workflow')

def public_member(m):
    u=m.get('user') or {}
    if u.get('bot'):return None
    name=m.get('nick') or u.get('global_name') or u.get('username') or 'Mitglied'
    avatar_hash=m.get('avatar')
    if avatar_hash:
        avatar=f'https://cdn.discordapp.com/guilds/{guild}/users/{u["id"]}/avatars/{avatar_hash}.png?size=128'
    elif u.get('avatar'):
        avatar=f'https://cdn.discordapp.com/avatars/{u["id"]}/{u["avatar"]}.png?size=128'
    else:avatar=None
    return {'name':str(name)[:100],'avatar':avatar}

# Höchster Rang gewinnt; Team-/Helferrollen bleiben der Fallback.
RANKS = [{'name': 'Projektleiter', 'id': '1043272080512274554', 'icon': '👑'}, {'name': 'Developer', 'id': '1043277862104477746', 'icon': '💻'}, {'name': 'Senior Admin', 'id': '1043272335467216916', 'icon': '🛡️'}, {'name': 'Admin', 'id': '1043272317607874611', 'icon': '🛡️'}, {'name': 'Junior Admin', 'id': '1043272509774102690', 'icon': '🔰'}, {'name': 'Community Manager', 'id': '1043272585368047727', 'icon': '💬'}, {'name': 'Supportleitung', 'id': '1043273140643573940', 'icon': '🎧'}, {'name': 'Supporter', 'id': '1043273227012689980', 'icon': '🤝'}]
rank_groups = [{'name': rank['name'], 'icon': rank['icon'], 'members': []} for rank in RANKS]
team=[]; helpers=[]
for m in members:
    roles=set(m.get('roles') or [])
    entry=public_member(m)
    if not entry:continue
    matched=False
    for pos,rank in enumerate(RANKS):
        if rank['id'] in roles:
            rank_groups[pos]['members'].append(entry)
            matched=True
            break
    if not matched:
        if team_role in roles:team.append(entry)
        elif helper_role in roles:helpers.append(entry)
for group in rank_groups:
    group['members'].sort(key=lambda x:x['name'].casefold())
for li in (team,helpers):li.sort(key=lambda x:x['name'].casefold())
payload={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'ranks':rank_groups,'team':team,'helpers':helpers}
Path('team.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Erfolgreich: {sum(len(g["members"]) for g in rank_groups)} mit Rang, {len(team)} weitere Team-Mitglieder, {len(helpers)} Helfer')
