/* Deterministic entertainment scoring. No browser or platform APIs. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.ParallelEngine = factory();
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const SECONDARY_WEIGHT = 0.3;
  function getMode(data, id = 'standard') {
    const mode = data.modes.find(m => m.id === id);
    if (!mode) throw new Error('不支持的题量');
    return mode;
  }
  function getQuestions(data, id = 'standard') { return data.questions.slice(0, getMode(data, id).count); }
  function inferMode(answers, data, id) {
    return id ? data.modes.find(m => m.id === id) : data.modes.find(m => m.count === answers?.length);
  }
  function validAnswers(answers, data, complete = true, modeId = null) {
    const mode = inferMode(answers, data, modeId);
    return Boolean(mode && Array.isArray(answers) && answers.length === mode.count &&
      Array.from(answers).every(v => (!complete && v === null) || (Number.isInteger(v) && v >= 1 && v <= 4)));
  }
  function normalized(values) {
    if (!values.length) throw new Error('没有足够的题目');
    return Math.round((values.reduce((sum, v) => sum + v, 0) / values.length - 1) / 3 * 100);
  }
  function rawPoint(q, answer) { return q.values ? q.values[answer - 1] : answer; }
  function questionPoint(q, answer) {
    const raw = rawPoint(q, answer);
    return q.reverse ? 5 - raw : raw;
  }
  function contributions(answers, questions, dim) {
    const values = [];
    questions.forEach((q, i) => {
      if (q.dim === dim) values.push({ value: questionPoint(q, answers[i]), weight: 1 });
      if (q.secondary?.dim === dim) values.push({ value: q.secondary.values[answers[i] - 1], weight: SECONDARY_WEIGHT });
    });
    return values;
  }
  function dimensionScore(answers, questions, dim) {
    const values = contributions(answers, questions, dim);
    const weight = values.reduce((sum, item) => sum + item.weight, 0);
    if (!weight) throw new Error('没有足够的题目');
    const mean = values.reduce((sum, item) => sum + item.value * item.weight, 0) / weight;
    return Math.round((mean - 1) / 3 * 100);
  }
  function score(answers, data, modeId = null) {
    if (!validAnswers(answers, data, true, modeId)) throw new Error('请完成对应题量的所有题目');
    const questions = data.questions.slice(0, answers.length);
    return data.dimensions.map(dim => dimensionScore(answers, questions, dim.id));
  }
  function similarity(a, b) {
    if (a.length !== b.length || !a.length) throw new Error('向量维度不一致');
    return Math.round(Math.max(0, 100 * (1 - a.reduce((sum, v, i) => sum + Math.abs(v - b[i]), 0) / (a.length * 100))));
  }
  function rank(vector, profiles) {
    return profiles.map(p => ({ ...p, similarity: similarity(vector, p.vector), distance: vector.reduce((s, v, i) => s + Math.abs(v - p.vector[i]), 0) }))
      .sort((a, b) => a.distance - b.distance || a.id.localeCompare(b.id));
  }
  function explain(vector, target, dimensions) {
    const diffs = dimensions.map((d, i) => ({ ...d, gap: Math.abs(vector[i] - target.vector[i]), value: vector[i], target: target.vector[i] }))
      .sort((a, b) => a.gap - b.gap || a.id.localeCompare(b.id));
    return { close: diffs.slice(0, 2), contrast: diffs[diffs.length - 1] };
  }
  function makeEvidence(answers, questions, dimensions, vector) {
    const ordered = dimensions.map((d, i) => ({ ...d, coordinate: vector[i], index: i }))
      .sort((a, b) => Math.abs(b.coordinate - 50) - Math.abs(a.coordinate - 50) || a.index - b.index);
    const evidence = [];
    for (const dim of ordered) {
      const choices = questions.flatMap((q, i) => q.dim === dim.id ? [{ q, i, value: questionPoint(q, answers[i]) }] : []);
      const high = dim.coordinate >= 50;
      choices.sort((a, b) => {
        const aAligned = (a.value >= 2.5) === high ? 1 : 0;
        const bAligned = (b.value >= 2.5) === high ? 1 : 0;
        return bAligned - aAligned || Math.abs(b.value - 2.5) - Math.abs(a.value - 2.5) || a.i - b.i;
      });
      const selected = choices[0];
      if (!selected) continue;
      const { q, i, value } = selected;
      evidence.push({
        questionId: q.id, title: q.title, scene: q.scene, option: q.options[answers[i] - 1],
        dimension: dim.name, dimensionId: dim.id, direction: value >= 2.5 ? 'high' : 'low', value,
        preference: value >= 2.5 ? dim.high : dim.low,
        ...(q.secondary ? { secondary: { dimensionId: q.secondary.dim, value: q.secondary.values[answers[i] - 1], weight: SECONDARY_WEIGHT } } : {})
      });
      if (evidence.length === 4) break;
    }
    return evidence;
  }
  function makeVariation(answers, questions, dimensions) {
    return dimensions.flatMap(dim => {
      const choices = questions.flatMap((q, i) => q.dim === dim.id ? [{ q, value: questionPoint(q, answers[i]) }] : [])
        .sort((a, b) => a.value - b.value || a.q.id.localeCompare(b.q.id));
      if (choices.length < 2) return [];
      const low = choices[0], high = choices[choices.length - 1], spread = high.value - low.value;
      if (spread < 3) return [];
      return [{ dimension: dim.name, dimensionId: dim.id, spread, lowQuestionId: low.q.id, highQuestionId: high.q.id,
        description: `你在「${high.q.scene.replace(/^\d+\s*·\s*/, '')}」偏向${dim.high}，在「${low.q.scene.replace(/^\d+\s*·\s*/, '')}」更接近${dim.low}；不同场景会带出你的不同侧面。` }];
    }).sort((a, b) => b.spread - a.spread || a.dimensionId.localeCompare(b.dimensionId)).slice(0, 3);
  }
  function analyze(answers, data, modeId = null) {
    const vector = score(answers, data, modeId), mode = inferMode(answers, data, modeId);
    const questions = data.questions.slice(0, mode.count);
    const getCoordinate = dim => vector[data.dimensions.findIndex(d => d.id === dim)];
    // Longer modes revise the estimate using all actual responses, not only the first eight.
    const coreScores = ['social', 'explore', 'empathy'].map(getCoordinate);
    const familyCode = coreScores.map(v => v >= 50 ? '1' : '0').join('');
    const family = data.profiles.find(p => p.id === data.familyCodes[familyCode]);
    let subtype = null, branch = null, subCode = '', branchCode = '', facets = null;
    if (mode.count >= 16) {
      subCode = ['action', 'order'].map(dim => getCoordinate(dim) >= 50 ? '1' : '0').join('');
      subtype = data.subtypes[subCode];
    }
    if (mode.count === 24) {
      const last = data.questions.slice(16, 24);
      facets = Object.fromEntries(['spotlight', 'boundary'].map(facet => [facet, normalized(last.flatMap((q, i) => {
        if (q.facet !== facet) return [];
        const raw = rawPoint(q, answers[i + 16]);
        return [q.facetReverse ? 5 - raw : raw];
      }))]));
      branchCode = ['spotlight', 'boundary'].map(f => facets[f] >= 50 ? '1' : '0').join('');
      branch = data.branches[branchCode];
    }
    return { mode, vector, familyCode, coreScores, profile: { ...family, similarity: similarity(vector, family.vector) },
      rankings: rank(vector, data.profiles), subtype, branch, facets,
      code: familyCode + (subCode ? '-' + subCode : '') + (branchCode ? '-' + branchCode : ''),
      coverage: data.dimensions.map(d => questions.filter(q => q.dim === d.id).length),
      weightedCoverage: data.dimensions.map(d => contributions(answers, questions, d.id).reduce((sum, item) => sum + item.weight, 0)),
      evidence: makeEvidence(answers, questions, data.dimensions, vector),
      boundaryDimensions: data.dimensions.flatMap((d, i) => vector[i] >= 40 && vector[i] <= 60 ? [{ id: d.id, name: d.name, value: vector[i], low: d.low, high: d.high }] : []),
      variation: makeVariation(answers, questions, data.dimensions),
      featured: rank(vector, data.characters.filter(p => data.featured.includes(p.id))),
      categories: Object.fromEntries(data.categories.map(c => [c.id, rank(vector, data.characters.filter(p => p.category === c.id))])) };
  }
  return { getMode, getQuestions, validAnswers, score, similarity, rank, explain, analyze };
});
