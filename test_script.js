
  // ━━━ SUPABASE INIT ━━━
  const supabaseUrl = 'https://jfjrzkjzfxnyhexwhoby.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpmanJ6a2p6ZnhueWhleHdob2J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0MDY4NTksImV4cCI6MjA5MDk4Mjg1OX0.hqeNEOTh5AVBwyR42JMVtm0t3dw4ghkQZPqfpmG-s48';
  const supabase = window.supabase.createClient(supabaseUrl, supabaseKey);

  // ━━━ ESTADO GLOBAL ━━━
  let STATE = {
    local: 'balneario_camboriu',
    diaIndex: 1,        // 0 = Hoje, 1 = Ontem (padrão: mostra ontem pois tem audit completa)
    tabAtual: 'auditoria',
    prazoRanking: '1_dia',
    modalLocal: 'balneario_camboriu',
    modalClima: null,
    dados: null,
    ranking: null,
    estacoes: null,
    registrosHoje: []
  };

  // ━━━ CONSTANTES ━━━
  const ICONES = { seco: '☀️', garoa: '🌦️', moderada: '🌧️', forte: '🌧️🌧️', intensa: '⛈️' };
  const CORES_CLASS = {
    seco: 'text-yellow-400', garoa: 'text-sky-300',
    moderada: 'text-blue-400', forte: 'text-indigo-400', intensa: 'text-purple-400'
  };
  const PERIODOS = ['madrugada', 'manha', 'tarde', 'noite'];
  const LABEL_PERIODO = { madrugada: 'Madrug.', manha: 'Manhã', tarde: 'Tarde', noite: 'Noite' };

  // Mapeamento de IDs do backend para nomes bonitos
  const NOMES_MODELOS = {
    'ecmwf_ifs025': 'ECMWF IFS (Windy)',
    'gfs_seamless': 'GFS (Weather.com)',
    'icon_seamless': 'ICON (DWD)',
    'best_match': 'Open-Meteo Best Match',
    'openweathermap': 'OpenWeatherMap',
    'persistencia': 'Persistência'
  };
  const APPS_MODELOS = {
    'ecmwf_ifs025': ['Windy'],
    'gfs_seamless': ['Weather.com', 'AccuWeather'],
    'icon_seamless': ['Bright Sky'],
    'best_match': ['Open-Meteo'],
    'openweathermap': ['OWM'],
    'persistencia': []
  };

  // ━━━ SCORE HELPERS ━━━
  function scoreClass(s) {
    if (s === null) return 'text-slate-500';
    if (s >= 85) return 'score-excelente';
    if (s >= 70) return 'score-bom';
    if (s >= 50) return 'score-medio';
    if (s >= 30) return 'score-ruim';
    return 'score-pessimo';
  }
  function barClass(s) {
    if (s === null) return 'bg-slate-600';
    if (s >= 85) return 'bar-excelente';
    if (s >= 70) return 'bar-bom';
    if (s >= 50) return 'bar-medio';
    if (s >= 30) return 'bar-ruim';
    return 'bar-pessimo';
  }
  function scoreEmoji(s) {
    if (s === null) return '—';
    if (s >= 85) return '✅';
    if (s >= 70) return '🟡';
    if (s >= 50) return '🟠';
    return '❌';
  }

  // ━━━ CARREGAR DADOS ━━━
  async function carregarDados() {
    try {
      const cacheBust = new Date().getTime();
      const respDados = await fetch('dados.json?v=' + cacheBust).then(x => x.json());
      const respRanking = await fetch('ranking.json?v=' + cacheBust).then(x => x.json());
      const respEstacoes = await fetch('estacoes.json?v=' + cacheBust).then(x => x.json());
      
      // Adaptar o formato do backend (Python) para o formato esperado pela UI
      let adaptado = { dias: [] };
      let hojeStr = new Date().toISOString().split('T')[0];
      let ontemTime = new Date(); ontemTime.setDate(ontemTime.getDate() - 1);
      let ontemStr = ontemTime.toISOString().split('T')[0];

      // Dia 0: Hoje
      let diaHoje = { data: hojeStr, label: 'Hoje', locais: {} };
      // Dia 1: Ontem
      let diaOntem = { data: ontemStr, label: 'Ontem', locais: {} };

      ['balneario_camboriu', 'itajai'].forEach(loc => {
        let jsonLoc = respDados.locais?.[loc] || {};
        
        let prevHj = jsonLoc.previsoes?.[hojeStr] || {};
        let modHj = {};
        for(let m in prevHj) {
           modHj[m] = { score_1d: prevHj[m].score_1d || null, nome_display: NOMES_MODELOS[m] || m, apps_relacionados: APPS_MODELOS[m] || [], periodos_score: {} };
           PERIODOS.forEach(p => { modHj[m].periodos_score[p] = { mm: prevHj[m][p] || 0, score: null, classificacao: formatClass(prevHj[m][p] || 0) } });
        }
        diaHoje.locais[loc] = { realidade: { status: 'parcial', periodos: {} }, modelos: modHj };

        let prevOnt = jsonLoc.previsoes?.[ontemStr] || {};
        let modOnt = {};
        for(let m in prevOnt) {
           modOnt[m] = { score_1d: prevOnt[m].score_1d || null, nome_display: NOMES_MODELOS[m] || m, apps_relacionados: APPS_MODELOS[m] || [], periodos_score: {} };
           PERIODOS.forEach(p => { modOnt[m].periodos_score[p] = { mm: prevOnt[m][p] || 0, score: null, classificacao: formatClass(prevOnt[m][p] || 0) } });
        }
        
        // Formatar realidade para matching de icones (sem_chuva -> seco)
        let realOntem = JSON.parse(JSON.stringify(jsonLoc.realidade || {}));
        if(realOntem.periodos) {
            Object.values(realOntem.periodos).forEach(p => { if(p.classificacao === 'sem_chuva') p.classificacao = 'seco'; });
        }
        diaOntem.locais[loc] = { realidade: realOntem, modelos: modOnt };
      });

      adaptado.dias.push(diaHoje);
      if(respDados.locais && Object.keys(respDados.locais).length > 0) adaptado.dias.push(diaOntem);

      STATE.dados = adaptado;
      STATE.ranking = respRanking;
      STATE.estacoes = respEstacoes;
      renderizar();
    } catch(err) {
      console.error(err);
      document.getElementById('card-realidade').innerHTML =
        `<div class="text-rose-400 text-sm p-2"><i class="fa-solid fa-triangle-exclamation mr-2"></i>Erro ao carregar dados.</div>`;
    }
  }

  function formatClass(mm) {
     if(mm === 0) return 'seco';
     if(mm <= 2.5) return 'garoa';
     if(mm <= 10) return 'moderada';
     if(mm <= 25) return 'forte';
     return 'intensa';
  }

  // ━━━ TABS ━━━
  function switchTab(tab) {
    STATE.tabAtual = tab;
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active', 'bg-sky-500', 'text-white');
      btn.classList.add('text-slate-400');
    });
    document.getElementById(`content-${tab}`).classList.remove('hidden');
    const btn = document.getElementById(`tab-${tab}`);
    btn.classList.add('active');
    btn.classList.remove('text-slate-400');
    renderTab(tab);
  }

  function renderTab(tab) {
    if (!STATE.dados) return;
    if (tab === 'auditoria') renderAuditoria();
    if (tab === 'ranking') renderRanking();
    if (tab === 'historico') renderHistorico();
    if (tab === 'estacoes') renderEstacoes();
  }

  // ━━━ LOCAL ━━━
  function setLocal(local) {
    STATE.local = local;
    document.querySelectorAll('.location-btn').forEach(btn => {
      btn.classList.remove('bg-sky-500', 'text-white');
      btn.classList.add('text-slate-400');
    });
    const id = local === 'balneario_camboriu' ? 'toggle-bc' : 'toggle-itajai';
    document.getElementById(id).classList.add('bg-sky-500', 'text-white');
    document.getElementById(id).classList.remove('text-slate-400');
    renderTab(STATE.tabAtual);
  }

  // ━━━ NAVEGAÇÃO DE DIAS ━━━
  function navegarDia(dir) {
    const maxIndex = (STATE.dados?.dias?.length || 1) - 1;
    STATE.diaIndex = Math.max(0, Math.min(maxIndex, STATE.diaIndex + dir));
    renderAuditoria();
  }

  // ━━━ AUDITORIA ━━━
  function renderAuditoria() {
    if (!STATE.dados) return;
    const dias = STATE.dados.dias;
    const dia = dias[STATE.diaIndex];
    if (!dia) return;

    // Navegação
    document.getElementById('dia-label').textContent = dia.label || dia.data;
    document.getElementById('dia-data').textContent = formatarData(dia.data);
    document.getElementById('btn-proximo-dia').disabled = STATE.diaIndex === 0;
    document.getElementById('btn-proximo-dia').style.opacity = STATE.diaIndex === 0 ? '0.3' : '1';

    const localData = dia.locais?.[STATE.local];
    if (!localData) {
      document.getElementById('card-realidade').innerHTML = `<p class="text-slate-500 text-sm text-center py-4">Sem dados para este local/dia.</p>`;
      document.getElementById('cards-modelos').innerHTML = '';
      return;
    }

    // Top Acertos (Ranking rápido do mês para 1 dia de antecedência)
    renderAuditoriaRankingFlash();

    // Card Realidade
    renderCardRealidade(localData.realidade, dia.data, dia.label);

    // Cards de modelos
    renderCardsModelos(localData.modelos);
  }

  function renderAuditoriaRankingFlash() {
    if (!STATE.ranking) return;
    const arrayRanking = STATE.ranking[STATE.local]?.['1_dia'] || [];
    const top3 = arrayRanking.filter(r => r.modelo !== 'persistencia').slice(0, 3);
    
    if (!top3 || top3.length === 0) {
      document.getElementById('resumo-ranking-auditoria').innerHTML = `<span class="text-slate-500 text-xs text-center w-full block">Nenhum ranking consolidado ainda...</span>`;
      return;
    }

    const html = top3.map((item, idx) => {
      let icon = idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉';
      return `<div class="flex flex-col items-center">
        <span class="text-2xl drop-shadow-md">${icon}</span>
        <span class="font-bold text-sky-400 text-[11px] mt-1 truncate max-w-[80px]" title="${item.nome}">${item.nome}</span>
        <span class="text-emerald-400 font-extrabold text-sm">${item.score.toFixed(0)}%</span>
      </div>`;
    }).join('');

    document.getElementById('resumo-ranking-auditoria').innerHTML = html;
  }

  function renderCardRealidade(realidade, data, diaLabel) {
    if (!realidade) {
      document.getElementById('card-realidade').innerHTML = `<p class="text-slate-500 text-sm text-center py-4">Dados de realidade ainda não disponíveis.</p>`;
      return;
    }

    const statusBadge = realidade.status === 'completo'
      ? `<span class="bg-emerald-500/20 text-emerald-400 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider border border-emerald-500/30">✅ Fim do Dia</span>`
      : `<span class="bg-amber-500/20 text-amber-400 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider border border-amber-500/30 animate-pulse-soft">⏳ Parcial</span>`;

    const localizeDia = diaLabel === 'Hoje' ? '(Medindo Agora)' : '(Medido em BC/Itajaí)';

    const periodsHTML = `<div class="grid grid-cols-4 divide-x divide-emerald-900/50 text-center bg-emerald-950/20 rounded-xl mt-4 overflow-hidden border border-emerald-800/50">
      ${PERIODOS.map(p => {
        const pd = realidade.periodos[p];
        if (!pd || pd.mm === null) {
          return `<div class="p-2"><p class="text-[10px] text-emerald-700 uppercase font-bold">${LABEL_PERIODO[p]}</p><p class="text-emerald-800 text-sm mt-2 font-bold">—</p></div>`;
        }
        return `<div class="p-2 flex flex-col items-center">
          <p class="text-[10px] text-emerald-400/80 uppercase font-bold">${LABEL_PERIODO[p]}</p>
          <span class="text-2xl my-2 drop-shadow-md">${ICONES[pd.classificacao] || '—'}</span>
          <p class="font-bold text-xs text-white capitalize">${pd.classificacao}</p>
          <p class="text-[10px] text-emerald-300 font-semibold mt-0.5">${pd.mm.toFixed(1)}mm</p>
        </div>`;
      }).join('')}
    </div>`;

    const totalHTML = realidade.total_dia !== undefined
      ? `<div class="mt-3 pt-3 border-t border-emerald-800 flex items-center justify-between px-1">
          <span class="text-xs text-emerald-400 font-bold uppercase tracking-wider">TOTAL ACUMULADO</span>
          <span class="text-lg font-black text-white">${realidade.total_dia.toFixed(1)} mm</span>
        </div>` : '';

    const badgeLocalStr = STATE.local === 'balneario_camboriu' ? 'BC' : 'Itajaí';

    document.getElementById('card-realidade').innerHTML = `
      <div class="bg-emerald-900/20 rounded-2xl overflow-hidden shadow-lg shadow-emerald-500/5 border-2 border-emerald-500/80 backdrop-blur-sm">
        <div class="bg-emerald-600/20 px-4 py-3 flex justify-between items-center border-b border-emerald-500/30">
            <span class="font-black text-emerald-400 text-sm tracking-wide flex items-center"><i class="fa-solid fa-check-double mr-2"></i> REALIDADE <span class="hidden sm:inline ml-1"> ${localizeDia}</span></span>
            <span class="text-[9px] font-bold text-emerald-200 bg-emerald-700/50 px-2 py-1 rounded uppercase tracking-widest border border-emerald-500/50 shadow-sm">CEMADEN ${badgeLocalStr}</span>
        </div>
        <div class="p-4">
          <div class="flex justify-between items-start">
             ${realidade.nota ? `<p class="mb-2 text-xs text-emerald-300/80 italic font-medium"><i class="fa-solid fa-circle-info mr-1"></i>${realidade.nota}</p>` : '<div></div>'}
             ${statusBadge}
          </div>
          ${periodsHTML}
          ${totalHTML}
        </div>
      </div>
    `;
  }

  function renderCardsModelos(modelos) {
    if (!modelos) { document.getElementById('cards-modelos').innerHTML = ''; return; }

    const html = Object.entries(modelos).map(([id, modelo]) => {
      const score = modelo.score_1d;
      const apps = modelo.apps_relacionados?.length
        ? `<p class="text-[10px] text-slate-400 mt-1 uppercase font-semibold tracking-wider"><i class="fa-brands fa-app-store-ios mr-1 opacity-70"></i>${modelo.apps_relacionados.join(' · ')}</p>` : '';

      const isBaseline = id === 'persistencia';

      // Detalhes por período
      let periodsHTML = '';
      if (modelo.periodos_score) {
        periodsHTML = `<div class="mt-3 grid grid-cols-4 divide-x divide-slate-700/80 text-center bg-slate-950/40 rounded-xl overflow-hidden border border-slate-700 shadow-inner">
          ${PERIODOS.map(p => {
            const pd = modelo.periodos_score[p];
            if (!pd) return `<div class="p-2"><p class="text-[10px] text-slate-500 uppercase font-bold">${LABEL_PERIODO[p]}</p><p class="text-xs text-slate-600 mt-2">—</p></div>`;
            
            let sitLabel = ''; let sitClass = ''; let bgClass = '';
            if (pd.score !== null && pd.score !== undefined) {
              if (pd.score >= 80) { sitLabel = 'ACERTOU ✅'; sitClass = 'text-emerald-400'; bgClass = 'bg-emerald-950/20'; }
              else if (pd.score >= 50) { sitLabel = 'QUASE 🟡'; sitClass = 'text-yellow-400'; bgClass = 'bg-yellow-950/10'; }
              else { sitLabel = 'ERROU ❌'; sitClass = 'text-rose-400'; bgClass = 'bg-rose-950/20'; }
            }

            return `<div class="p-2 ${bgClass} transition-colors">
              <p class="text-[10px] text-slate-400 uppercase font-bold tracking-wide">${LABEL_PERIODO[p]}</p>
              <div class="my-1 text-xl">${ICONES[pd.classificacao] || '—'}</div>
              <p class="font-bold text-[11px] text-white capitalize">${pd.classificacao || '—'}</p>
              <p class="text-[10px] text-sky-300 font-semibold mb-1">${typeof pd.mm === 'number' ? pd.mm.toFixed(1) : '0.0'}mm</p>
              ${sitLabel ? `<div class="mt-2 pt-1 border-t border-slate-700/50">
                <span class="text-[9px] font-black tracking-wider ${sitClass}">${sitLabel}</span>
              </div>` : ''}
            </div>`;
          }).join('')}
        </div>`;
      } else if (modelo.previsao_hoje) {
        periodsHTML = `<div class="mt-3 grid grid-cols-4 divide-x divide-slate-700/80 text-center bg-slate-950/40 rounded-xl overflow-hidden border border-slate-700 shadow-inner">
          ${PERIODOS.map(p => {
            const pd = modelo.previsao_hoje[p];
            if (!pd) return `<div class="p-2"><p class="text-[10px] text-slate-500 uppercase font-bold">${LABEL_PERIODO[p]}</p></div>`;
            return `<div class="p-2 flex flex-col items-center">
              <p class="text-[9px] text-slate-400 uppercase font-bold tracking-wider">${LABEL_PERIODO[p]}</p>
              <span class="text-xl my-1.5 drop-shadow-md">${ICONES[pd.classificacao] || '—'}</span>
              <p class="font-bold text-[11px] text-white capitalize">${pd.classificacao}</p>
              <p class="text-[9px] text-slate-400 font-semibold mt-1">${pd.mm}mm</p>
            </div>`;
          }).join('')}
        </div>`;
      }

      return `<div class="glass rounded-2xl overflow-hidden mb-5 border ${isBaseline ? 'border-amber-500/30 opacity-80' : 'border-slate-700/80'} shadow-md">
        <div class="bg-slate-800/60 px-4 py-2.5 border-b border-slate-700/80 flex justify-between items-center">
            <div>
               <span class="font-extrabold text-white text-[15px] tracking-tight">${modelo.nome_display || NOMES_MODELOS[id] || id}</span>
               ${apps}
            </div>
            <span class="text-[9px] font-bold text-sky-300 bg-sky-900/30 px-2 py-1 rounded uppercase tracking-widest border border-sky-700/50 shadow-sm whitespace-nowrap ml-2 text-center leading-tight">PREVISÃO<br class="sm:hidden"> 1 DIA ANTES</span>
        </div>
        <div class="p-3.5">
          ${periodsHTML}
          ${score !== null && score !== undefined ? `
            <div class="mt-4 bg-slate-900/60 p-2.5 text-center rounded-xl border border-slate-800/80 flex flex-col sm:flex-row items-center justify-center sm:gap-2">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Grau de Acerto:</span>
                <span class="text-base font-black ${scoreClass(score)}">${score.toFixed(0)}%</span>
            </div>` 
          : `
            <div class="mt-4 bg-slate-900/60 p-2.5 text-center rounded-xl border border-slate-800/80">
                <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider"><i class="fa-solid fa-clock mr-1.5"></i>Aguardando fim do dia para auditar</span>
            </div>`}
          ${isBaseline ? `<p class="mt-3 text-[10px] text-amber-500/80 text-center uppercase tracking-widest font-black"><i class="fa-solid fa-triangle-exclamation mr-1"></i>Modelo de Persistência (Linha de Corte Mínima)</p>` : ''}
        </div>
      </div>`;
    }).join('');

    document.getElementById('cards-modelos').innerHTML = html;
  }

  // ━━━ RANKING ━━━
  function setPrazo(prazo) {
    STATE.prazoRanking = prazo;
    document.querySelectorAll('.prazo-btn').forEach(b => {
      b.classList.remove('bg-sky-500', 'text-white');
      b.classList.add('text-slate-400');
    });
    document.getElementById(`prazo-${prazo}`).classList.add('bg-sky-500', 'text-white');
    document.getElementById(`prazo-${prazo}`).classList.remove('text-slate-400');
    renderRanking();
  }

  function renderRanking() {
    if (!STATE.ranking) return;
    // O backend gera: { "balneario_camboriu": { "1_dia": [...], ... }, "itajai": { ... } }
    const localRanking = STATE.ranking[STATE.local];
    const items = localRanking?.[STATE.prazoRanking] || [];
    
    if (!items || !items.length) {
      document.getElementById('lista-ranking').innerHTML = `<p class="text-slate-500 text-sm text-center py-8">Dados insuficientes para este prazo. Acumule mais dias de auditoria.</p>`;
      return;
    }

    const rankHTML = items.map((item, idx) => {
      const posicao = idx + 1;
      const medalha = posicao === 1 ? '🥇' : posicao === 2 ? '🥈' : posicao === 3 ? '🥉' : `${posicao}º`;
      const apps = APPS_MODELOS[item.modelo] || [];
      const appsHTML = apps.length ? `<p class="text-xs text-slate-500 mt-0.5">${apps.join(' · ')}</p>` : '';
      const isBaseline = item.modelo === 'persistencia';
      const nomeDisplay = item.nome || NOMES_MODELOS[item.modelo] || item.modelo;
      const scoreVal = item.score || 0;

      const isTopCard = posicao <= 3 && !isBaseline;
      const cardClass = isTopCard
        ? 'glass rounded-2xl p-4 border border-sky-500/20 shadow-lg shadow-sky-500/5'
        : isBaseline
        ? 'glass rounded-xl p-3 border border-rose-500/30 opacity-75'
        : 'glass rounded-xl p-3';

      return `
        <div class="${cardClass}">
          <div class="flex items-center gap-3">
            <div class="text-2xl w-8 text-center">${medalha}</div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-white truncate">${nomeDisplay}</p>
              ${appsHTML}
              <p class="text-xs text-slate-500 mt-0.5">${item.amostras || 0} avaliações</p>
            </div>
            <div class="text-right">
              <p class="text-2xl font-extrabold ${scoreClass(scoreVal)}">${scoreVal.toFixed(0)}</p>
              <p class="text-xs text-slate-500">pontos</p>
            </div>
          </div>
          ${isTopCard ? `<div class="mt-3 h-1.5 bg-slate-700 rounded-full overflow-hidden">
            <div class="${barClass(scoreVal)} h-full rounded-full score-bar" style="width:${scoreVal}%"></div>
          </div>` : ''}
        </div>`;
    }).join('');

    document.getElementById('lista-ranking').innerHTML = rankHTML;
  }

  // ━━━ HISTÓRICO ━━━
  function renderHistorico() {
    // Grid de 30 dias simulado
    const climas = ['seco','seco','garoa','moderada','forte','intensa','seco','garoa','seco','seco',
                    'moderada','forte','seco','garoa','garoa','seco','seco','moderada','moderada','forte',
                    'seco','seco','garoa','seco','intensa','moderada','seco','seco','garoa','seco'];
    const cells = climas.map((c, i) => {
      const d = new Date(); d.setDate(d.getDate() - (29 - i));
      return `<div class="day-cell text-center" title="${formatarData(d.toISOString().split('T')[0])} — ${c}">
        <div class="text-xl">${ICONES[c]}</div>
        <div class="text-xs text-slate-600 mt-0.5">${d.getDate()}</div>
      </div>`;
    }).join('');
    document.getElementById('historico-cells').innerHTML = cells;

    // Tabela de scores
    const modelos = [
      { nome: 'ECMWF (Windy)', scores: [88.5, 79.2, 65.0, 52.0] },
      { nome: 'ICON', scores: [85.2, 74.8, 60.3, 47.8] },
      { nome: 'GFS (Weather.com)', scores: [82.1, 71.0, 62.5, 49.5] },
      { nome: 'OpenWeatherMap', scores: [78.0, 66.5, 55.0, 43.0] },
      { nome: 'Open-Meteo Best', scores: [75.5, 64.0, 53.5, 40.5] },
      { nome: 'Persistência', scores: [48.3, 41.5, 38.0, 35.0], baseline: true },
    ];
    const rows = modelos.map(m => {
      const cols = m.scores.map(s => `<td class="text-center p-3 font-bold ${scoreClass(s)}">${s}</td>`).join('');
      return `<tr class="border-b border-slate-800 ${m.baseline ? 'opacity-60' : ''}">
        <td class="p-3 text-xs text-slate-300 font-semibold">${m.baseline ? '─ ' : ''}${m.nome}</td>
        ${cols}
      </tr>`;
    }).join('');
    document.getElementById('historico-tbody').innerHTML = rows;
  }

  // ━━━ ESTAÇÕES ━━━
  function renderEstacoes() {
    if (!STATE.estacoes) return;
    const local = STATE.estacoes.locais?.[STATE.local];
    if (!local) { document.getElementById('lista-estacoes').innerHTML = `<p class="text-slate-500 text-center py-8">Sem dados de estações para este local.</p>`; return; }

    const html = local.estacoes.map(est => {
      const online = est.status === 'operacional';
      const statusIcon = online ? '<span class="status-online"><i class="fa-solid fa-circle text-xs mr-1"></i>Operacional</span>' : '<span class="status-offline"><i class="fa-solid fa-circle text-xs mr-1"></i>Offline</span>';
      const dados = online ? (est.hoje || est.ontem) : null;
      const labelDado = est.hoje ? 'Hoje' : 'Ontem';

      let periodsHTML = '';
      if (dados) {
        periodsHTML = `<div class="grid grid-cols-4 gap-2 mt-3">
          ${PERIODOS.map(p => {
            const pd = dados[p];
            if (!pd || pd.mm === null) return `<div class="text-center bg-slate-800/40 rounded-lg p-2"><p class="text-xs text-slate-600">${LABEL_PERIODO[p]}</p><p class="text-slate-600 text-sm">—</p></div>`;
            return `<div class="text-center bg-slate-800/40 rounded-lg p-2">
              <p class="text-xs text-slate-400">${LABEL_PERIODO[p]}</p>
              <p class="text-base">${ICONES[pd.classificacao] || '—'}</p>
              <p class="text-xs font-bold text-white">${pd.mm.toFixed(1)}mm</p>
            </div>`;
          }).join('')}
        </div>`;
      }

      const total = dados?.total_dia || dados?.total_parcial;
      const alerta = (est.hoje?.alerta || est.ontem?.alerta) ? `<div class="mt-2 bg-rose-500/10 border border-rose-500/30 rounded-lg px-3 py-2 text-xs text-rose-300">${est.hoje?.alerta || est.ontem?.alerta}</div>` : '';

      return `<div class="glass rounded-2xl p-4 ${!online ? 'opacity-60' : ''}">
        <div class="flex items-start justify-between mb-2">
          <div>
            <p class="font-bold text-white text-sm">${est.nome}</p>
            <p class="text-xs text-slate-500 mt-0.5">${est.bairro}</p>
          </div>
          <div class="text-right">
            <div class="text-xs font-semibold">${statusIcon}</div>
            ${total !== undefined ? `<p class="text-xs text-slate-400 mt-1">${labelDado}: <span class="text-white font-bold">${total.toFixed(1)}mm</span></p>` : ''}
          </div>
        </div>
        ${!online && est.nota_status ? `<p class="text-xs text-rose-400/70 mb-2"><i class="fa-solid fa-triangle-exclamation mr-1"></i>${est.nota_status}</p>` : ''}
        ${periodsHTML}
        ${alerta}
      </div>`;
    }).join('');

    // Consenso
    const cons = local.consenso_ontem || local.consenso_hoje;
    const consHTML = cons ? `
      <div class="glass rounded-2xl p-4 border border-sky-500/20">
        <p class="text-xs font-bold text-sky-400 uppercase tracking-wider mb-2"><i class="fa-solid fa-calculator mr-1.5"></i>Consenso Final (${cons.metodo})</p>
        <p class="text-xs text-slate-400 mb-2">Estações usadas: ${cons.estacoes_usadas.length} • Excluídas: ${cons.estacoes_excluidas?.length || 0}</p>
        <div class="grid grid-cols-4 gap-2">
          ${PERIODOS.map(p => {
            const pd = cons.resultado[p];
            if (!pd || pd.mm === null) return `<div class="text-center bg-slate-800/40 rounded-lg p-2"><p class="text-xs text-slate-600">${LABEL_PERIODO[p]}</p><p class="text-slate-600">—</p></div>`;
            return `<div class="text-center bg-slate-800/40 rounded-lg p-2">
              <p class="text-xs text-slate-400">${LABEL_PERIODO[p]}</p>
              <p class="text-base">${ICONES[pd.classificacao]}</p>
              <p class="text-xs font-bold text-white">${pd.mm.toFixed(1)}mm</p>
            </div>`;
          }).join('')}
        </div>
      </div>
    ` : '';

    document.getElementById('lista-estacoes').innerHTML = html + consHTML;
  }

  // ━━━ MODAL ━━━
  function abrirModal() {
    STATE.modalClima = null;
    document.getElementById('modal-overlay').classList.remove('hidden');
    document.getElementById('modal-overlay').classList.add('flex');
    setModalLocal(STATE.local);
    atualizarListaRegistros();
  }
  function fecharModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
    document.getElementById('modal-overlay').classList.remove('flex');
  }
  function setModalLocal(local) {
    STATE.modalLocal = local;
    ['balneario_camboriu', 'itajai'].forEach(l => {
      const id = l === 'balneario_camboriu' ? 'modal-local-bc' : 'modal-local-itajai';
      if (l === local) {
        document.getElementById(id).classList.add('border-sky-500', 'bg-sky-500/20', 'text-sky-300');
        document.getElementById(id).classList.remove('border-slate-600', 'text-slate-400');
      } else {
        document.getElementById(id).classList.remove('border-sky-500', 'bg-sky-500/20', 'text-sky-300');
        document.getElementById(id).classList.add('border-slate-600', 'text-slate-400');
      }
    });
  }
  function setModalClima(clima) {
    STATE.modalClima = clima;
    ['seco','garoa','moderada','forte','intensa'].forEach(c => {
      const btn = document.getElementById(`btn-${c}`);
      if (c === clima) {
        btn.classList.add('border-sky-400', 'bg-sky-500/20', 'scale-105');
      } else {
        btn.classList.remove('border-sky-400', 'bg-sky-500/20', 'scale-105');
        btn.classList.add('border-slate-600');
      }
    });
  }
  async function salvarRegistro() {
    if (!STATE.modalClima) { mostrarToast('Selecione um tipo de clima!', 'amber'); return; }
    
    document.getElementById('btn-salvar-modal').disabled = true;
    document.getElementById('btn-salvar-modal').innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Salvando...';

    const agora = new Date();
    const hora = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    
    // Determinar periodo
    const horaInt = agora.getHours();
    let periodo_calc = 'madrugada';
    if (horaInt >= 6 && horaInt < 12) periodo_calc = 'manha';
    else if (horaInt >= 12 && horaInt < 18) periodo_calc = 'tarde';
    else if (horaInt >= 18) periodo_calc = 'noite';

    const dataObj = {
      hora: hora,
      local: STATE.modalLocal,
      classificacao: STATE.modalClima,
      nota: document.getElementById('modal-nota').value || null,
      timestamp: agora.toISOString(),
      periodo: periodo_calc,
      data: agora.toISOString().split('T')[0]
    };

    const { error } = await supabase.from('topclimabc_validacoes').insert([dataObj]);

    document.getElementById('btn-salvar-modal').disabled = false;
    document.getElementById('btn-salvar-modal').innerHTML = '<i class="fa-solid fa-check mr-2"></i>Registrar';

    if (error) {
      console.error(error);
      mostrarToast('Erro ao salvar no servidor.', 'rose');
      return;
    }

    document.getElementById('modal-nota').value = '';
    STATE.modalClima = null;
    setModalClima(null);
    atualizarListaRegistros(); // Atualiza via rede
    mostrarToast(`${ICONES[dataObj.classificacao]} ${dataObj.hora} — ${dataObj.classificacao} registrado!`);
  }

  async function atualizarListaRegistros() {
    const lista = document.getElementById('lista-registros');
    const div = document.getElementById('registros-hoje');
    
    div.classList.remove('hidden');
    lista.innerHTML = '<div class="text-xs text-sky-400 text-center py-2"><i class="fa-solid fa-circle-notch fa-spin"></i> Atualizando...</div>';

    const hoje = new Date().toISOString().split('T')[0];
    const { data: registros, error } = await supabase
      .from('topclimabc_validacoes')
      .select('*')
      .eq('data', hoje)
      .order('timestamp', { ascending: false })
      .limit(20);

    if (error || !registros || !registros.length) { 
      lista.innerHTML = '<div class="text-xs text-slate-500 text-center py-2">Nenhum registro hoje ainda. Seja o primeiro!</div>';
      return; 
    }

    STATE.registrosHoje = registros;

    lista.innerHTML = registros.map(r =>
      `<div class="flex items-center gap-2 text-xs bg-slate-800/80 border border-slate-700/50 rounded-lg px-2 py-2 shadow-sm animate-fade-in">
        <span class="text-lg">${ICONES[r.classificacao]}</span>
        <span class="font-bold text-white min-w-[36px]">${r.hora}</span>
        <span class="text-[10px] font-bold uppercase tracking-wider text-sky-300 bg-sky-900/30 px-1.5 py-0.5 rounded border border-sky-800/50">${r.local === 'balneario_camboriu' ? 'BC' : 'ITJ'}</span>
        ${r.nota ? `<span class="text-slate-400 text-[10px] italic truncate">${r.nota}</span>` : ''}
      </div>`
    ).join('');
  }

  // ━━━ TOAST ━━━
  function mostrarToast(msg, tipo = 'emerald') {
    const t = document.getElementById('toast');
    document.getElementById('toast-msg').textContent = msg;
    t.classList.remove('hidden');
    setTimeout(() => t.classList.add('hidden'), 3000);
  }

  // ━━━ UTILS ━━━
  function formatarData(dataStr) {
    if (!dataStr) return '';
    const [y, m, d] = dataStr.split('-');
    return `${d}/${m}/${y}`;
  }

  // ━━━ RENDERIZAÇÃO GERAL ━━━
  function renderizar() {
    renderTab(STATE.tabAtual);
    // REMOVIDO: Carregamento do localStorage antigo
  }

  // ━━━ FECHAR MODAL AO CLICAR FORA ━━━
  document.getElementById('modal-overlay').addEventListener('click', function(e) {
    if (e.target === this) fecharModal();
  });

  // ━━━ MANUAL ━━━
  function abrirManual() {
    const el = document.getElementById('manual-overlay');
    el.classList.remove('hidden');
    el.classList.add('flex');
    switchManualTab('oque'); // sempre abre na primeira aba
  }
  function fecharManual() {
    const el = document.getElementById('manual-overlay');
    el.classList.add('hidden');
    el.classList.remove('flex');
  }
  function switchManualTab(tab) {
    const tabs = ['oque', 'modelos', 'score', 'periodos', 'faq'];
    tabs.forEach(t => {
      const btn = document.getElementById('mtab-' + t);
      const content = document.getElementById('mcontent-' + t);
      if (t === tab) {
        btn.classList.remove('text-slate-400', 'border-transparent');
        btn.classList.add('text-sky-400', 'border-sky-500');
        content.classList.remove('hidden');
      } else {
        btn.classList.remove('text-sky-400', 'border-sky-500');
        btn.classList.add('text-slate-400', 'border-transparent');
        content.classList.add('hidden');
      }
    });
  }
  // Fechar manual ao clicar fora
  document.getElementById('manual-overlay').addEventListener('click', function(e) {
    if (e.target === this) fecharManual();
  });

  // ━━━ INIT ━━━
  carregarDados();
  