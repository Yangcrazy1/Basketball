(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('./data.json'), require('./engine.js'), require('./portraits.json'), require('./cards-art.json'));
  } else {
    root.NBAGame = factory(root.NBA_DATA, root.ShenrenEngine, root.NBA_PORTRAITS, root.NBA_CARD_ART);
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function (data, engine, portraitData, cardData) {
  'use strict';
  if (!data || !engine) throw new Error('整活NBA内容尚未载入');
  var clone = function (value) { return JSON.parse(JSON.stringify(value)); };
  var people = engine.enabledPeople(data, 'basket');
  var cards = engine.enabledCards(data, 'basket');
  var portraits = portraitData.portraits || portraitData;
  var cardArt = cardData.cards || cardData;
  var theme = data.themes.filter(function (t) { return t.id === 'basket'; })[0];

  function start(count, previousFirst) {
    return engine.draw(data, 'basket', Number(count), previousFirst || null);
  }
  function question(session) {
    if (!engine.valid(session, data)) throw new Error('答题进度已失效，请重新开始');
    var q = clone(engine.questionAt(session, data));
    q.options = session.deck[session.index].order.map(function (id) {
      return q.options.filter(function (o) { return o.id === id; })[0];
    });
    return q;
  }
  function answer(session, questionId, optionId) {
    return engine.recordAnswer(session, data, questionId, Number(optionId));
  }
  function previous(session) {
    if (!engine.valid(session, data)) throw new Error('答题进度已失效');
    var next = clone(session);
    next.index = Math.max(0, next.index - 1);
    next.phase = 'quiz';
    return next;
  }
  function result(session) {
    var r = engine.analyze(session, data);
    r.teamName = engine.makeSquadName('basket', r.team);
    return r;
  }
  function rerollName(r) {
    return engine.makeSquadName('basket', r.team, r.teamName ? r.teamName.title : '');
  }
  function person(id) { return engine.resolvePerson(data, id); }
  function customTeam(r, ids) {
    var issue = engine.squadError(ids, 'basket', data, true);
    if (issue) throw new Error(issue);
    var next = clone(r);
    next.team = engine.customSquad(ids, 'basket', data, r.vector, r.identity, r.augment, true);
    next.customTeam = true;
    next.hasDIY = false;
    return next;
  }
  function text(value, label, max, fallback) {
    var s = String(value === undefined || value === null ? (fallback || '') : value).trim();
    s = s.replace(/[\u0000-\u001f\u007f]/g, ' ');
    if (!s || Array.from(s).length > max) throw new Error(label + '请填写1—' + max + '个字');
    return s;
  }
  function diyDefaults() {
    return { name: '野球场隐藏巨星', number: '00', line: '数据可以没有，节目必须管够。',
      signature: { name: '篮筐欠我一个', effect: '每次打铁，都被你解释成给队友的篮板助攻。' },
      vector: [50, 50, 50, 50, 50, 50], avatarColor: '#9d7cff' };
  }
  function makeDIY(form) {
    form = form || {};
    var defaults = diyDefaults();
    var signature = typeof form.signature === 'object' && form.signature ? form.signature : {};
    var number = String(form.number === undefined ? '00' : form.number).trim();
    if (!/^\d{1,2}$/.test(number)) throw new Error('球衣号码请填写0—99');
    var vector = form.vector === undefined ? defaults.vector : form.vector;
    if (!Array.isArray(vector) || vector.length !== 6 || vector.some(function (v) {
      return !Number.isInteger(Number(v)) || Number(v) < 0 || Number(v) > 100;
    })) throw new Error('六项能力需为0—100的整数');
    var name = text(form.name, '名字', 12, defaults.name);
    var line = text(form.line === undefined ? form.tagline : form.line, '口头禅', 40, defaults.line);
    var hexName = text(form.hexName === undefined ? signature.name : form.hexName, '专属海克斯名', 12, defaults.signature.name);
    var hexEffect = text(form.hexEffect === undefined ? signature.effect : form.hexEffect, '海克斯效果', 60, defaults.signature.effect);
    var color = /^#[0-9a-f]{6}$/i.test(form.avatarColor || '') ? form.avatarColor : defaults.avatarColor;
    return { id: 'basket-diy-me', personId: 'diy-me', theme: 'basket', name: name, nickname: name,
      number: number, line: line, sub: '你亲手捏出的整活球星', tags: ['DIY自选球星'],
      signature: { name: hexName, effect: hexEffect }, hexName: hexName, hexEffect: hexEffect,
      vector: vector.map(Number), roles: [0, 1, 2, 3, 4], avatarColor: color, custom: true,
      isYou: false, enabled: true };
  }
  function withDIY(r, diy) {
    var star = makeDIY(diy);
    var next = clone(r);
    if (!Array.isArray(next.team) || next.team.length !== 5) throw new Error('请先组好五人阵容');
    var slot = next.team.findIndex(function (p) { return p.personId === 'diy-me'; });
    if (slot < 0) {
      for (var i = 4; i >= 0; i--) {
        if (!next.team[i].isYou && next.team[i].personId !== next.identity.personId) { slot = i; break; }
      }
    }
    if (slot < 0) throw new Error('没有可替换的队友位置');
    star.slot = slot;
    star.teamLine = 'DIY自选队友 · ' + star.line;
    next.team[slot] = star;
    next.hasDIY = true;
    next.customTeam = true;
    return next;
  }
  function storyStart(pid, seedIds) {
    return engine.storyStart(pid, data, seedIds || [], 'nba-preview:' + pid);
  }
  return { data: data, people: people, cards: cards, dims: theme.dims, roles: theme.roles,
    portraits: portraits, cardArt: cardArt, start: start, question: question, answer: answer,
    previous: previous, result: result, rerollName: rerollName, person: person,
    customTeam: customTeam, makeDIY: makeDIY, diyDefaults: diyDefaults, withDIY: withDIY,
    valid: function (s, complete) { return engine.valid(s, data, !!complete); },
    storyStart: storyStart,
    storyView: function (s) { return engine.storyView(s, data); },
    storyNext: function (s) { return engine.storyAdvance(s, data); },
    storyChoice: function (s, node, choice) { return engine.storyChoose(s, node, choice, data); },
    storyBack: function (s) { return engine.storyBack(s, data); }
  };
});
