// TCL Discord-Teamübersicht. Kein Bot-Token im Browser!
(async function () {
  const root = document.getElementById('discord-team-roster');
  if (!root) return;
  const make = (tag, className, value) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (value !== undefined) el.textContent = value;
    return el;
  };
  function section(label, people, icon) {
    const group = make('section', 'team-group team-rank-group');
    const head = make('h3', 'team-group-title');
    head.append(make('span', '', `${icon || '🛡️'} ${label}`), make('span', 'team-count', String(people.length)));
    group.append(head);
    const list = make('div', 'team-people');
    for (const person of people) {
      const item = make('div', 'team-person');
      if (typeof person.avatar === 'string' && /^https:\/\/cdn\.discordapp\.com\//.test(person.avatar)) {
        const img = make('img');
        img.src = person.avatar; img.alt = ''; img.loading = 'lazy'; img.referrerPolicy = 'no-referrer';
        item.append(img);
      } else {
        item.append(make('span', 'team-fallback', String(person.name || '?').slice(0, 1).toUpperCase()));
      }
      const meta = make('div');
      meta.append(make('div', 'team-person-name', person.name || 'Discord-Mitglied'), make('div', 'team-person-role', label));
      item.append(meta); list.append(item);
    }
    group.append(list);
    return group;
  }
  try {
    const response = await fetch('./team.json?version=' + Date.now(), {cache: 'no-store'});
    if (!response.ok) throw Error('HTTP ' + response.status);
    const data = await response.json();
    const blocks = [];
    if (Array.isArray(data.ranks)) {
      for (const rank of data.ranks) {
        const members = Array.isArray(rank.members) ? rank.members : [];
        if (members.length) blocks.push(section(rank.name || 'Team', members, rank.icon));
      }
    }
    const team = Array.isArray(data.team) ? data.team : [];
    const helpers = Array.isArray(data.helpers) ? data.helpers : [];
    if (team.length) blocks.push(section('Weitere Teammitglieder', team, '🛡️'));
    if (helpers.length) blocks.push(section('Helfer', helpers, '🤝'));
    root.replaceChildren(...(blocks.length ? blocks : [make('p', 'team-empty', 'Derzeit sind keine Teammitglieder eingetragen.') ]));
  } catch (error) {
    console.warn('TCL-Teamübersicht:', error);
    root.replaceChildren(make('p', 'team-empty', 'Teamdaten können gerade nicht geladen werden.'));
  }
})();
