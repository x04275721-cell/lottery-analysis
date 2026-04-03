// ==================== 预测算法模块 ====================
// 包含：金银胆、五码、位置码、四注、和值、遗漏值

// 计算和值
function getSum(num1, num2, num3) {
    return parseInt(num1) + parseInt(num2) + parseInt(num3);
}

// 计算奇偶比
function getJiOu(nums) {
    let ji = 0;
    for (let n of nums) {
        if (parseInt(n) % 2 === 1) ji++;
    }
    return { ji, ou: 3 - ji };
}

// 计算大小比
function getDaXiao(nums) {
    let da = 0;
    for (let n of nums) {
        if (parseInt(n) >= 5) da++;
    }
    return { da, xiao: 3 - da };
}

// 分析遗漏值
function analyzeMiss(history) {
    const miss = {};
    for (let i = 0; i <= 9; i++) {
        miss[i] = 0;
    }

    for (let item of history) {
        const nums = [item.num1, item.num2, item.num3];
        for (let n of nums) {
            miss[parseInt(n)] = 0;
        }
        // 增加其他数字的遗漏值
        for (let i = 0; i <= 9; i++) {
            if (!nums.includes(String(i))) {
                miss[i]++;
            }
        }
    }
    return miss;
}

// 统计数字出现频率
function getNumFrequency(history, count = 30) {
    const freq = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0};
    for (let i = 0; i < Math.min(count, history.length); i++) {
        const item = history[i];
        freq[parseInt(item.num1)]++;
        freq[parseInt(item.num2)]++;
        freq[parseInt(item.num3)]++;
    }
    return freq;
}

// 获取频率最高的N个数字
function getTopN(freq, n = 5) {
    return Object.entries(freq)
        .sort((a, b) => b[1] - a[1])
        .slice(0, n)
        .map(([k]) => parseInt(k));
}

// 获取位置频率
function getPositionFrequency(history, count = 50) {
    const pos1 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0};
    const pos2 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0};
    const pos3 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0};

    for (let i = 0; i < Math.min(count, history.length); i++) {
        const item = history[i];
        pos1[parseInt(item.num1)]++;
        pos2[parseInt(item.num2)]++;
        pos3[parseInt(item.num3)]++;
    }

    return { pos1, pos2, pos3 };
}

// 预测和值
function predictSum(history, count = 50) {
    const sumFreq = {};
    for (let i = 0; i < Math.min(count, history.length); i++) {
        const s = history[i].sum;
        sumFreq[s] = (sumFreq[s] || 0) + 1;
    }
    return Object.entries(sumFreq)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 2)
        .map(([k]) => parseInt(k));
}

// 生成四注推荐
function generateBets(wuxiao1, wuxiao2, wuxiao3, sums) {
    const bets = [];
    // 第一注：各取第一位
    bets.push([wuxiao1[0], wuxiao2[0], wuxiao3[0]].join(''));
    // 第二注：频率最高的组合
    bets.push([wuxiao1[0], wuxiao2[1], wuxiao3[1]].join(''));
    // 第三注：和值匹配
    for (let s of sums) {
        const target = s;
        for (let i = 0; i < wuxiao1.length; i++) {
            for (let j = 0; j < wuxiao2.length; j++) {
                for (let k = 0; k < wuxiao3.length; k++) {
                    if (wuxiao1[i] + wuxiao2[j] + wuxiao3[k] === target) {
                        bets.push([wuxiao1[i], wuxiao2[j], wuxiao3[k]].join(''));
                        return bets;
                    }
                }
            }
        }
    }
    // 默认第三注
    bets.push([wuxiao1[1], wuxiao2[0], wuxiao3[2]].join(''));
    return bets;
}

// 执行预测
function doPrediction(type) {
    const history = LotteryData[type];
    if (history.length === 0) {
        return null;
    }

    // 1. 金银胆
    const freq = getNumFrequency(history, 30);
    const sortedFreq = Object.entries(freq).sort((a, b) => b[1] - a[1]);
    const gold = parseInt(sortedFreq[0][0]);
    const silver = parseInt(sortedFreq[1][0]);

    // 2. 五码推荐
    const top5 = getTopN(freq, 5);
    const posFreq = getPositionFrequency(history, 50);
    const wuxiao = {
        pos1: getTopN(posFreq.pos1, 5),
        pos2: getTopN(posFreq.pos2, 5),
        pos3: getTopN(posFreq.pos3, 5)
    };

    // 3. 和值预测
    const sums = predictSum(history, 50);

    // 4. 四注推荐
    const bets = generateBets(wuxiao.pos1, wuxiao.pos2, wuxiao.pos3, sums);

    // 5. 334断组
    const duan = analyze334(history);

    // 6. 遗漏值
    const miss = analyzeMiss(history);

    return {
        gold,
        silver,
        top5,
        wuxiao,
        sums,
        bets,
        duan,
        miss,
        historyCount: history.length
    };
}

// 导出模块
window.analyzeMiss = analyzeMiss;
window.getNumFrequency = getNumFrequency;
window.getTopN = getTopN;
window.getPositionFrequency = getPositionFrequency;
window.predictSum = predictSum;
window.generateBets = generateBets;
window.doPrediction = doPrediction;