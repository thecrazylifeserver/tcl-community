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

team=[];helpers=[]
for m in members:
    roles=set(m.get('roles') or [])
    entry=public_member(m)
    if not entry:continue
    if team_role in roles:team.append(entry)
    elif helper_role in roles:helpers.append(entry) # Team hat Vorrang bei beiden Rollen
for li in (team,helpers):li.sort(key=lambda x:x['name'].casefold())
payload={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'team':team,'helpers':helpers}
Path('team.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Erfolgreich: {len(team)} Team-Mitglieder und {len(helpers)} Helfer')
