// Öffentliche Teamdaten; keine Tokens im Browser.
(async function(){
  const root=document.getElementById('discord-team-roster');if(!root)return;
  function node(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;}
  function group(title,role,people,icon){
    const panel=node('section','team-group team-rank-group');
    const head=node('h3','team-group-title');
    head.append(node('span','',`${icon||'🛡️'} ${title}`),node('span','team-count',String(people.length)));
    panel.append(head);
    const list=node('div','team-people');
    if(!people.length)panel.append(node('p','team-empty','Aktuell keine Mitglieder.'));
    for(const person of people){
      const card=node('div','team-person');
      if(typeof person.avatar==='string' && /^https:\/\/cdn\.discordapp\.com\//.test(person.avatar)){
        const img=node('img');img.alt='';img.loading='lazy';img.referrerPolicy='no-referrer';img.src=person.avatar;card.append(img);
      }else card.append(node('span','team-fallback',(person.name||'?').slice(0,1).toUpperCase()));
      const meta=node('div');meta.append(node('div','team-person-name',person.name||'Discord-Mitglied'),node('div','team-person-role',role));card.append(meta);list.append(card);
    }
    panel.append(list);return panel;
  }
  try{
    let response;
    try{response=await fetch('https://raw.githubusercontent.com/thecrazylifeserver/tcl-community/main/team.json?ts='+Date.now(),{cache:'no-store'});if(!response.ok)throw Error('remote failed');}
    catch(_){response=await fetch('team.json?ts='+Date.now(),{cache:'no-store'});}
    if(!response.ok)throw Error('no data');
    const data=await response.json();const blocks=[];
    if(Array.isArray(data.ranks)){
      for(const rank of data.ranks){const people=Array.isArray(rank.members)?rank.members:[];if(people.length)blocks.push(group(rank.name||'Team',rank.name||'Team',people,rank.icon||'🛡️'));}
    }
    const team=Array.isArray(data.team)?data.team:[],helpers=Array.isArray(data.helpers)?data.helpers:[];
    if(team.length)blocks.push(group('Weitere Teammitglieder','Team',team,'🛡️'));
    if(helpers.length)blocks.push(group('Helfer','Helfer',helpers,'🤝'));
    // Älteres JSON-Format bleibt kompatibel.
    if(!blocks.length)blocks.push(node('p','team-empty','Aktuell keine Einträge.'));
    root.replaceChildren(...blocks);
  }catch(e){root.replaceChildren(node('p','team-empty','Die Teamübersicht ist vorübergehend nicht verfügbar.'));}
})();
