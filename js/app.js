// ==================== 主程序入口 ====================
// 负责初始化和协调各模块

// 初始化
function init() {
    // 加载本地数据
    loadHistory();

    // 加载收藏
    const savedFav = localStorage.getItem('lotteryFavorites');
    if (savedFav) {
        try {
            favorites = JSON.parse(savedFav);
        } catch (e) {
            favorites = [];
        }
    }

    // 初始化遗漏值网格
    const missGrid = document.getElementById('missGrid');
    missGrid.innerHTML = Array.from({length: 10}, (_, i) => `
        <div class="miss-item">
            <div class="num">${i}</div>
            <div class="miss">-</div>
        </div>
    `).join('');

    // 从服务器加载完整历史数据
    loadServerData().then(hasNewData => {
        if (hasNewData) {
            const result = doPrediction(currentType);
            updatePredictionUI(result, currentType);
            updateTrendCharts();
        } else {
            // 如果服务器没有数据，使用本地数据初始化
            const result = doPrediction(currentType);
            if (result) {
                updatePredictionUI(result, currentType);
            }
        }
    });

    // 初始化标签页点击事件
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchTab(btn.dataset.tab);
        });
    });

    // 初始化搜索历史
    renderHistoryTable();

    // 更新时间显示
    const timestamp = new Date().toLocaleString('zh-CN');
    lastUpdateTime = timestamp;
    document.getElementById('updateTime').textContent = '🕐 更新时间: ' + timestamp;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);