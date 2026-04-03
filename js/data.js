// ==================== 数据存储模块 ====================
// 负责数据加载、存储和管理

let LotteryData = {
    pl3: [],  // 排列三历史
    '3d': []  // 3D历史
};
let favorites = [];
let currentType = 'pl3';
let lastUpdateTime = null;

// 加载历史数据
function loadHistory() {
    const saved = localStorage.getItem('lotteryData');
    if (saved) {
        try {
            LotteryData = JSON.parse(saved);
        } catch (e) {
            console.log('数据加载失败');
        }
    }
}

// 保存数据到localStorage
function saveHistory() {
    localStorage.setItem('lotteryData', JSON.stringify(LotteryData));
}

// 从服务器加载完整历史数据
function loadServerData() {
    return fetch('data/all_history.json')
        .then(r => r.json())
        .then(data => {
            if (data.length > 0) {
                data.forEach(item => {
                    const num = item.number || '';
                    const record = {
                        period: item.period,
                        num1: num[0] || '0',
                        num2: num[1] || '0',
                        num3: num[2] || '0',
                        type: item.type,
                        sum: parseInt(num[0] || 0) + parseInt(num[1] || 0) + parseInt(num[2] || 0),
                        date: item.date || ''
                    };
                    if (item.type === 'pl3' || item.type === '排列三') {
                        if (!LotteryData.pl3.some(p => p.period === record.period)) {
                            LotteryData.pl3.push(record);
                        }
                    } else {
                        if (!LotteryData['3d'].some(p => p.period === record.period)) {
                            LotteryData['3d'].push(record);
                        }
                    }
                });
                // 按期号排序
                LotteryData.pl3.sort((a, b) => b.period.localeCompare(a.period));
                LotteryData['3d'].sort((a, b) => b.period.localeCompare(a.period));
                // 保存到localStorage
                saveHistory();
                return true;
            }
            return false;
        })
        .catch(() => {
            console.log('服务器数据加载失败，使用本地数据');
            return false;
        });
}

// 刷新数据
function refreshData() {
    const timestamp = new Date().toLocaleString('zh-CN');
    lastUpdateTime = timestamp;
    document.getElementById('updateTime').textContent = '🕐 更新时间: ' + timestamp;

    return loadServerData().then(hasNewData => {
        if (hasNewData) {
            const result = doPrediction(currentType);
            updatePredictionUI(result, currentType);
            updateTrendCharts();
        }
    });
}

// 获取当前类型的历史数据
function getHistory(type) {
    return LotteryData[type] || [];
}

// 导出模块
window.LotteryData = LotteryData;
window.loadHistory = loadHistory;
window.saveHistory = saveHistory;
window.loadServerData = loadServerData;
window.refreshData = refreshData;
window.getHistory = getHistory;
window.favorites = favorites;
window.currentType = currentType;
window.lastUpdateTime = lastUpdateTime;