// ==================== UI更新模块 ====================
// 包含：所有UI更新函数

// ==================== 标签页切换 ====================
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    if (tabName === 'history') {
        renderHistoryTable();
    } else if (tabName === 'trend') {
        updateTrendCharts();
    }
}

// ==================== 彩票类型切换 ====================
function switchType(type) {
    currentType = type;
    document.querySelectorAll('.lottery-btn').forEach(el => el.classList.remove('active'));
    document.querySelector(`[data-type="${type}"]`).classList.add('active');

    const result = doPrediction(type);
    updatePredictionUI(result, type);
    updateTrendCharts();
}

// ==================== 预测结果UI更新 ====================
function updatePredictionUI(result, type) {
    if (!result) {
        document.getElementById('predictionResult').innerHTML = `
            <div class="empty-state">
                <div class="icon">📊</div>
                <p>暂无${type === 'pl3' ? '排列三' : '3D'}历史数据</p>
                <p style="font-size:0.9rem;margin-top:8px;">请先导入历史数据</p>
            </div>
        `;
        return;
    }

    const container = document.getElementById('predictionResult');
    container.innerHTML = `
        <div class="result-row">
            <div class="result-label">金胆</div>
            <div class="result-value">
                <div class="num-ball gold">${result.gold}</div>
            </div>
        </div>
        <div class="result-row">
            <div class="result-label">银胆</div>
            <div class="result-value">
                <div class="num-ball silver">${result.silver}</div>
            </div>
        </div>
        <div class="result-row">
            <div class="result-label">五码</div>
            <div class="result-value">
                ${result.top5.map(n => `<div class="num-ball">${n}</div>`).join('')}
            </div>
        </div>
        <div class="result-row">
            <div class="result-label">位置码</div>
            <div class="result-value" style="flex-direction:column;gap:8px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="width:40px;color:var(--text-muted);">位1</span>
                    ${result.wuxiao.pos1.map(n => `<div class="num-ball">${n}</div>`).join('')}
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="width:40px;color:var(--text-muted);">位2</span>
                    ${result.wuxiao.pos2.map(n => `<div class="num-ball">${n}</div>`).join('')}
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="width:40px;color:var(--text-muted);">位3</span>
                    ${result.wuxiao.pos3.map(n => `<div class="num-ball">${n}</div>`).join('')}
                </div>
            </div>
        </div>
        <div class="result-row">
            <div class="result-label">四注</div>
            <div class="result-value" style="flex-direction:column;gap:8px;">
                ${result.bets.map((b, i) => `
                    <div class="bet-number">
                        <span style="color:var(--text-muted);margin-right:8px;">注${i+1}</span>
                        ${b.split('').join(' ')}
                    </div>
                `).join('')}
            </div>
        </div>
        <div class="result-row">
            <div class="result-label">和值</div>
            <div class="result-value">
                ${result.sums.map(s => `<div class="sum-box">${s}</div>`).join('')}
            </div>
        </div>
        <p style="text-align:center;color:var(--text-muted);font-size:0.85rem;margin-top:16px;">
            基于最近 ${result.historyCount} 期数据分析
        </p>
    `;

    // 更新遗漏值
    updateMissGrid(result.miss);

    // 更新334断组
    updateDuanVisual(result.duan);

    // 更新对码法
    const duimaHistory = LotteryData[type];
    const duima = analyzeDuima(duimaHistory);
    const duimaStability = checkStability(duimaHistory, 'duima');
    updateDuimaVisual(duima, duimaStability);

    // 更新和值尾分解
    const sumtail = analyzeSumTail(duimaHistory);
    const sumtailStability = checkStability(duimaHistory, 'sumtail');
    updateSumTailVisual(sumtail, sumtailStability);

    // 更新组合分解
    updateCombinedVisual(duimaHistory);
}

// ==================== 334断组UI更新 ====================
function updateDuanVisual(duan) {
    document.getElementById('duan-group4').textContent = duan ? duan.g4 : '-';
    document.getElementById('duan-group3a').textContent = duan ? duan.g3a : '-';
    document.getElementById('duan-group3b').textContent = duan ? duan.g3b : '-';
    document.getElementById('duan-method').textContent = duan ? duan.method : '-';

    const stabilityEl = document.getElementById('duan-stability');
    if (duan && duan.rate > 0) {
        if (duan.stable) {
            stabilityEl.innerHTML = `<span style="color:var(--success);">[OK] 30期 ${duan.rate}%</span>`;
        } else {
            stabilityEl.innerHTML = `<span style="color:var(--warning);">[WARN] 30期 ${duan.rate}%</span>`;
        }
    } else {
        stabilityEl.textContent = '';
    }
}

// ==================== 分解式UI更新 ====================
function updateDuimaVisual(duima, stability) {
    document.getElementById('duima-group-a').textContent = duima ? duima.duimaGroup : '-';
    document.getElementById('duima-group-b').textContent = duima ? duima.remainingGroup : '-';

    const stabilityEl = document.getElementById('duima-stability');
    if (stability && stability.total > 0) {
        if (stability.stable) {
            stabilityEl.innerHTML = `<span style="color:var(--success);">[OK] 30期 ${stability.rate}%</span>`;
        } else {
            stabilityEl.innerHTML = `<span style="color:var(--warning);">[WARN] 30期 ${stability.rate}%</span>`;
        }
    } else {
        stabilityEl.textContent = '';
    }
}

function updateSumTailVisual(sumtail, stability) {
    document.getElementById('sumtail-group-a').textContent = sumtail ? sumtail.group4 : '-';
    document.getElementById('sumtail-group-b').textContent = sumtail ? sumtail.group6 : '-';
    document.getElementById('sumtail-sum').textContent = sumtail ? `和尾: ${sumtail.sumTail}` : '和尾: -';

    const stabilityEl = document.getElementById('sumtail-stability');
    if (stability && stability.total > 0) {
        if (stability.stable) {
            stabilityEl.innerHTML = `<span style="color:var(--success);">[OK] 30期 ${stability.rate}%</span>`;
        } else {
            stabilityEl.innerHTML = `<span style="color:var(--warning);">[WARN] 30期 ${stability.rate}%</span>`;
        }
    } else {
        stabilityEl.textContent = '';
    }
}

function updateCombinedVisual(history) {
    if (history.length < 2) {
        document.getElementById('combined-intersection').textContent = '-';
        document.getElementById('combined-remaining').textContent = '-';
        return;
    }

    const lastNum = history[0].num1 + history[0].num2 + history[0].num3;
    const { duimaGroup } = getDuimaGroup(lastNum);
    const { group4, group6 } = getSumTailGroup(lastNum);

    // 交集
    const intersection = Array.from(new Set(duimaGroup.split('').filter(d => group4.includes(d)))).sort().join('');
    document.getElementById('combined-intersection').textContent = intersection || '无';

    // 稳定度检查
    const duimaStability = checkStability(history, 'duima');
    const sumtailStability = checkStability(history, 'sumtail');
    const combinedStability = checkStability(history, 'combined');

    // 确定推荐方法
    let recommendedMethod = 'combined';
    let recommendedGroup = intersection;
    let recommendDesc = '';

    if (!duimaStability.stable && !sumtailStability.stable) {
        if (duimaStability.rate > sumtailStability.rate) {
            recommendedMethod = 'duima';
            recommendedGroup = duimaGroup;
            recommendDesc = `[WARN] 两种方法都不稳定，对码法正确率更高(${duimaStability.rate}%)，仅供参考`;
        } else {
            recommendedMethod = 'sumtail';
            recommendedGroup = group4;
            recommendDesc = `[WARN] 两种方法都不稳定，和值尾分解正确率更高(${sumtailStability.rate}%)，仅供参考`;
        }
    } else if (!duimaStability.stable) {
        recommendedMethod = 'sumtail';
        recommendedGroup = group4;
        recommendDesc = `[WARN] 对码法不稳定(${duimaStability.rate}%)，使用和值尾分解(${sumtailStability.rate}%)`;
    } else if (!sumtailStability.stable) {
        recommendedMethod = 'duima';
        recommendedGroup = duimaGroup;
        recommendDesc = `[WARN] 和值尾分解不稳定(${sumtailStability.rate}%)，使用对码法(${duimaStability.rate}%)`;
    } else {
        recommendDesc = `两种方法都稳定，使用交集进行推荐`;
    }

    // 剩余
    const remaining = Array.from(new Set('0123456789'.split('').filter(d => !recommendedGroup.includes(d)))).sort().join('');
    document.getElementById('combined-remaining').textContent = remaining;
    document.getElementById('combined-desc').textContent = recommendDesc;

    // 稳定度显示
    const stabilityEl = document.getElementById('combined-stability');
    const displayRate = recommendedMethod === 'combined' ? combinedStability.rate :
                        recommendedMethod === 'duima' ? duimaStability.rate : sumtailStability.rate;
    const isStable = recommendedMethod === 'combined' ? combinedStability.stable :
                    recommendedMethod === 'duima' ? duimaStability.stable : sumtailStability.stable;

    if (combinedStability.total > 0) {
        if (isStable) {
            stabilityEl.innerHTML = `<span style="color:var(--success);">[OK] 30期 ${displayRate}%</span>`;
        } else {
            stabilityEl.innerHTML = `<span style="color:var(--warning);">[WARN] 30期 ${displayRate}%</span>`;
        }
    } else {
        stabilityEl.textContent = '';
    }
}

// ==================== 遗漏值UI更新 ====================
function updateMissGrid(miss) {
    const container = document.getElementById('missGrid');
    const avgMiss = Object.values(miss).reduce((a, b) => a + b, 0) / 10;

    container.innerHTML = Object.entries(miss).map(([num, m]) => {
        let className = 'miss-item';
        if (m === 0) className += ' hot';
        else if (m > avgMiss * 1.5) className += ' warning';
        else if (m < avgMiss * 0.5) className += ' cold';

        return `
            <div class="${className}">
                <div class="num">${num}</div>
                <div class="miss">遗漏 ${m}</div>
            </div>
        `;
    }).join('');
}

// ==================== 历史表格 ====================
function renderHistoryTable(filter = '', typeFilter = 'all') {
    const tbody = document.getElementById('historyTableBody');
    let history = [...LotteryData.pl3, ...LotteryData['3d']];

    if (typeFilter !== 'all') {
        history = history.filter(h => h.type === typeFilter);
    }

    if (filter) {
        history = history.filter(h => h.period.includes(filter));
    }

    history.sort((a, b) => b.period.localeCompare(a.period));
    history = history.slice(0, 100);

    tbody.innerHTML = history.map(item => `
        <tr>
            <td>${item.period}</td>
            <td>${item.type === 'pl3' ? '排列三' : '3D'}</td>
            <td style="color:var(--accent-1);font-weight:bold;">${item.num1} ${item.num2} ${item.num3}</td>
            <td>${item.sum}</td>
            <td>${item.date}</td>
            <td><button class="btn-outline" onclick="addToFavorite('${item.period}')">⭐</button></td>
        </tr>
    `).join('');
}

function searchHistory() {
    const filter = document.getElementById('searchInput').value;
    const typeFilter = document.getElementById('historyTypeFilter').value;
    renderHistoryTable(filter, typeFilter);
}

// ==================== 走势图表 ====================
function updateTrendCharts() {
    const history = LotteryData[currentType];
    if (history.length === 0) return;

    // 更新统计
    document.getElementById('stat-total').textContent = history.length;

    let oddCount = 0, bigCount = 0;
    for (let item of history.slice(0, 50)) {
        const nums = [parseInt(item.num1), parseInt(item.num2), parseInt(item.num3)];
        for (let n of nums) {
            if (n % 2 === 1) oddCount++;
            if (n >= 5) bigCount++;
        }
    }

    const total = Math.min(50, history.length) * 3;
    document.getElementById('stat-odd').textContent = (oddCount / total * 100).toFixed(1) + '%';
    document.getElementById('stat-big').textContent = (bigCount / total * 100).toFixed(1) + '%';

    // 和值分布
    const sumFreq = {};
    for (let item of history.slice(0, 50)) {
        sumFreq[item.sum] = (sumFreq[item.sum] || 0) + 1;
    }

    const maxFreq = Math.max(...Object.values(sumFreq));
    const chartContainer = document.getElementById('trendChart');
    chartContainer.innerHTML = Object.entries(sumFreq)
        .sort((a, b) => a[0] - b[0])
        .map(([sum, freq]) => {
            const height = (freq / maxFreq * 180) + 10;
            const left = (parseInt(sum) / 27 * 100) + '%';
            return `<div class="chart-bar" style="left:${left};height:${height}px;" title="和值${sum}: ${freq}次"></div>`;
        }).join('');
}

// ==================== 工具函数 ====================
function showCompareTool() {
    const tool = document.getElementById('compareTool');
    tool.style.display = tool.style.display === 'none' ? 'block' : 'none';
}

function compareNumbers() {
    const num1 = document.getElementById('compareInput1').value.trim();
    const num2 = document.getElementById('compareInput2').value.trim();

    if (num1.length !== 3 || num2.length !== 3) {
        document.getElementById('compareResult').innerHTML = '<p style="color:var(--danger);">请输入3位号码</p>';
        return;
    }

    const n1 = num1.split('').map(Number);
    const n2 = num2.split('').map(Number);

    let same = 0;
    for (let i = 0; i < 3; i++) {
        if (n1[i] === n2[i]) same++;
    }

    document.getElementById('compareResult').innerHTML = `
        <p>号码1: ${num1}</p>
        <p>号码2: ${num2}</p>
        <p style="margin-top:12px;">相同位置: ${same}个</p>
        <p>匹配率: ${(same / 3 * 100).toFixed(0)}%</p>
    `;
}

function showMissAnalysis() {
    alert('遗漏分析功能开发中...');
}

function showSumDistribution() {
    alert('和值分布功能开发中...');
}

// ==================== 数据导入 ====================
function handleFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const content = e.target.result;
            parseAndImport(content, file.name);
        } catch (err) {
            alert('文件解析失败');
        }
    };
    reader.readAsText(file);
}

function parseAndImport(content, filename) {
    let imported = 0;

    try {
        // 尝试JSON格式
        if (filename.endsWith('.json')) {
            const data = JSON.parse(content);
            if (Array.isArray(data)) {
                data.forEach(item => {
                    if (item.period && item.number && item.type) {
                        const num = item.number;
                        const record = {
                            period: item.period,
                            num1: num[0], num2: num[1], num3: num[2],
                            type: item.type,
                            sum: parseInt(num[0]) + parseInt(num[1]) + parseInt(num[2]),
                            date: item.date || ''
                        };
                        if (!LotteryData[record.type === 'pl3' ? 'pl3' : '3d'].some(p => p.period === record.period)) {
                            LotteryData[record.type === 'pl3' ? 'pl3' : '3d'].push(record);
                            imported++;
                        }
                    }
                });
            }
        } else {
            // 文本格式
            const lines = content.split('\n');
            lines.forEach(line => {
                line = line.trim();
                if (!line) return;

                const parts = line.split(/[,\s]+/);
                if (parts.length >= 3) {
                    const record = {
                        period: parts[0],
                        num1: parts[1][0] || '0',
                        num2: parts[1][1] || '0',
                        num3: parts[1][2] || '0',
                        type: parts[2] || 'pl3',
                        sum: parseInt(parts[1][0] || 0) + parseInt(parts[1][1] || 0) + parseInt(parts[1][2] || 0),
                        date: parts[3] || ''
                    };
                    const typeKey = record.type === 'pl3' ? 'pl3' : '3d';
                    if (!LotteryData[typeKey].some(p => p.period === record.period)) {
                        LotteryData[typeKey].push(record);
                        imported++;
                    }
                }
            });
        }

        saveHistory();
        alert(`成功导入 ${imported} 条数据`);

        // 更新UI
        const result = doPrediction(currentType);
        updatePredictionUI(result, currentType);

    } catch (err) {
        alert('导入失败: ' + err.message);
    }
}

function importManualData() {
    const content = document.getElementById('manualInput').value;
    if (!content.trim()) {
        alert('请输入数据');
        return;
    }

    parseAndImport(content, 'manual.txt');
}

function addToFavorite(period) {
    if (!favorites.includes(period)) {
        favorites.push(period);
        localStorage.setItem('lotteryFavorites', JSON.stringify(favorites));
        alert('已添加到收藏');
    }
}

// 导出UI模块
window.switchTab = switchTab;
window.switchType = switchType;
window.updatePredictionUI = updatePredictionUI;
window.updateDuanVisual = updateDuanVisual;
window.updateDuimaVisual = updateDuimaVisual;
window.updateSumTailVisual = updateSumTailVisual;
window.updateCombinedVisual = updateCombinedVisual;
window.updateMissGrid = updateMissGrid;
window.renderHistoryTable = renderHistoryTable;
window.searchHistory = searchHistory;
window.updateTrendCharts = updateTrendCharts;
window.showCompareTool = showCompareTool;
window.compareNumbers = compareNumbers;
window.showMissAnalysis = showMissAnalysis;
window.showSumDistribution = showSumDistribution;
window.handleFileImport = handleFileImport;
window.parseAndImport = parseAndImport;
window.importManualData = importManualData;
window.addToFavorite = addToFavorite;