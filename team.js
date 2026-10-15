// Öffentliche Daten aus team.json. Keine Discord-Tokens oder geheimen IDs im Browser.
(async function(){
  const root=document.getElementById('discord-team-roster');if(!root)return;
  function node(tag,className,text){const el=document.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el}
  function group(title,role,people){const panel=node('section','team-group');const head=node('h3','team-group-title');head.append(node('span','',title),node('span','team-count',String(people.length)));panel.append(head);const list=node('div','team-people');
    if(!people.length)panel.append(node('p','team-empty','Aktuell keine Einträge.'));
    for(const person of people){const card=node('div','team-person');if(typeof person.avatar==='string' && /^https:\/\/cdn\.discordapp\.com\//.test(person.avatar)){const img=node('img');img.alt='';img.loading='lazy';img.referrerPolicy='no-referrer';img.src=person.avatar;card.append(img)}else card.append(node('span','team-fallback',(person.name||'?').slice(0,1).toUpperCase()));const meta=node('div');meta.append(node('div','team-person-name',person.name||'Discord-Mitglied'),node('div','team-person-role',role));card.append(meta);list.append(card)}panel.append(list);return panel;
  }
  try{let response;try{response=await fetch('https://raw.githubusercontent.com/thecrazylifeserver/tcl-community/main/team.json?ts='+Date.now(),{cache:'no-store'});if(!response.ok)throw Error('remote failed')}catch(_){response=await fetch('team.json?ts='+Date.now(),{cache:'no-store'})}if(!response.ok)throw Error('no data');const data=await response.json();root.replaceChildren(group('🛡️ Team','Team',Array.isArray(data.team)?data.team:[]),group('🤝 Helfer','Helfer',Array.isArray(data.helpers)?data.helpers:[]));}catch(e){root.append(node('p','team-empty','Die Teamübersicht ist vorübergehend nicht verfügbar.'));}
})();
