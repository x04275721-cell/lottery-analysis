// ==================== 334断组模块 ====================
// 包含：三种334断组方法

// 和跨合尾查表334断组表
const HEKUA_334_TABLE = {
    '0': ['237', '014569', '238'],
    '1': ['238', '012567', '349'],
    '2': ['239', '013568', '047'],
    '3': ['012', '134568', '079'],
    '4': ['123', '014569', '068'],
    '5': ['234', '015679', '018'],
    '6': ['345', '012678', '129'],
    '7': ['456', '123789', '023'],
    '8': ['567', '023489', '016'],
    '9': ['678', '123459', '037']
};

// 方法一：对码断组法
function make334Duima(lastNum) {
    const duimaSet = new Set();
    for (const d of lastNum) {
        duimaSet.add(d);
        duimaSet.add(DUIMA_PAIRS[d]);
    }
    const merged = Array.from(duimaSet).sort();

    let g4, g3a, g3b;

    if (merged.length === 4) {
        // 刚好4个，作为第一组
        g4 = merged.join('');
        // 剩余6个用自然升序分两组
        const remainingSet = new Set('0123456789'.split(''));
        merged.forEach(d => remainingSet.delete(d));
        const remaining = Array.from(remainingSet).sort();
        g3a = remaining.slice(0, 3).join('');
        g3b = remaining.slice(3).join('');
    } else if (merged.length === 6) {
        // 6个，选含奖号多的4个作为g4
        // 剩余2个与另外4个组成g3a和g3b
        const remainingSet = new Set('0123456789'.split(''));
        merged.forEach(d => remainingSet.delete(d));
        const remainingFromOther = Array.from(remainingSet).sort();

        // g4取前4个（含奖号多的优先）
        g4 = merged.slice(0, 4).join('');
        // 剩余2个 + 另外4个 = 6个，分两组
        const mergedRemaining = merged.slice(4);
        const combinedRemaining = [...mergedRemaining, ...remainingFromOther].sort();
        g3a = combinedRemaining.slice(0, 3).join('');
        g3b = combinedRemaining.slice(3).join('');
    } else {
        // 处理特殊情况：奖号全相同（豹子如000）或只有2个不同数字（组三如001）
        // 用奖号去重后补对码，再补其他数字凑够4个
        const uniqueDigits = [...new Set(lastNum.split(''))].sort();
        const supplemented = [...new Set([...uniqueDigits, ...uniqueDigits.map(d => DUIMA_PAIRS[d])])].sort();
        // 补其他数字凑够4个
        for (let i = 0; i <= 9 && supplemented.length < 4; i++) {
            if (!supplemented.includes(String(i))) {
                supplemented.push(String(i));
            }
        }
        g4 = supplemented.slice(0, 4).join('');

        // 重新计算剩余
        const g4Set = new Set(g4.split(''));
        const stillRemaining = '0123456789'.split('').filter(d => !g4Set.has(d)).sort();
        g3a = stillRemaining.slice(0, 3).join('');
        g3b = stillRemaining.slice(3).join('');
    }
    return { g4, g3a, g3b, method: '对码断组法' };
}

// 方法二：和跨合尾查表法
function make334Hekua(lastNum) {
    // 计算和值
    const sum = parseInt(lastNum[0]) + parseInt(lastNum[1]) + parseInt(lastNum[2]);
    // 计算跨度
    const nums = lastNum.split('').map(Number).sort((a, b) => a - b);
    const kuadu = nums[2] - nums[0];
    // 和跨尾
    const tail = String((sum + kuadu) % 10);
    const groups = HEKUA_334_TABLE[tail];
    return { g4: groups[1], g3a: groups[0], g3b: groups[2], method: '和跨查表法' };
}

// 计算均衡度（奇偶+大小）
function calcBalanceScore(g4, g3a, g3b) {
    const allGroups = [g4.split(''), g3a.split(''), g3b.split('')];
    let score = 0;

    for (const group of allGroups) {
        const odd = group.filter(d => parseInt(d) % 2 === 1).length;
        const even = group.length - odd;
        // 奇偶均衡：2:1或1:2得1分，3:0或0:3得0分
        if ((odd === 2 && even === 1) || (odd === 1 && even === 2)) score++;
        else if (odd === 3 || even === 3) score += 0;

        // 大小均衡：0-4为小，5-9为大
        const small = group.filter(d => parseInt(d) <= 4).length;
        const big = group.length - small;
        if ((small === 2 && big === 1) || (small === 1 && big === 2)) score++;
        else if (small === 3 || big === 3) score += 0;
    }
    return score;
}

// 方法三：奖号邻号法（追热法）
function make334Linhao(lastNum) {
    const nums = lastNum.split('').map(Number);

    // 生成全部+1和全部-1的邻号
    const plus1 = nums.map(n => (n + 1) % 10);
    const minus1 = nums.map(n => (n + 9) % 10);

    // 去重并取前3个（不足3个则用其他数字补充）
    const plus1Unique = [...new Set(plus1)].sort();
    const minus1Unique = [...new Set(minus1)].sort();

    // 如果邻号去重后不足3个，从剩余数字补充
    const remainingAll = '0123456789'.split('').map(Number);
    const numsSet = new Set(nums);
    const supplementPool = remainingAll.filter(n => !numsSet.has(n) && !plus1Unique.includes(n));

    // 确保 g3a 有3个数字
    while (plus1Unique.length < 3 && supplementPool.length > 0) {
        plus1Unique.push(supplementPool.shift());
    }
    while (minus1Unique.length < 3 && supplementPool.length > 0) {
        minus1Unique.push(supplementPool.shift());
    }

    const g3a_plus = plus1Unique.slice(0, 3).sort().join('');
    const g3a_minus = minus1Unique.slice(0, 3).sort().join('');

    // 计算均衡度选择更好的方案
    const remainingSet = new Set('0123456789'.split('').map(Number));
    nums.forEach(n => remainingSet.delete(n));

    // 方案A：+1邻号
    const remainingA = Array.from(remainingSet).sort();
    const g3bA = remainingA.slice(0, 3).join('');
    const g4A = remainingA.slice(3).join('');
    const scoreA = calcBalanceScore(lastNum, g3a_plus, g3bA);

    // 方案B：-1邻号
    const remainingB = Array.from(remainingSet).sort();
    const g3bB = remainingB.slice(0, 3).join('');
    const g4B = remainingB.slice(3).join('');
    const scoreB = calcBalanceScore(lastNum, g3a_minus, g3bB);

    if (scoreA >= scoreB) {
        return { g4: g4A, g3a: g3a_plus, g3b: g3bA, method: '邻号法(+1)' };
    } else {
        return { g4: g4B, g3a: g3a_minus, g3b: g3bB, method: '邻号法(-1)' };
    }
}

// 检查334断组是否正确（不是1-1-1分布即为正确）
function check334Correct(resultNum, g4, g3a, g3b) {
    const uniqueDigits = new Set(resultNum);
    let in4 = 0, in3a = 0, in3b = 0;

    for (const d of uniqueDigits) {
        if (g4.includes(d)) in4++;
        if (g3a.includes(d)) in3a++;
        if (g3b.includes(d)) in3b++;
    }

    // 1-1-1分布 = 失败
    return !(in4 === 1 && in3a === 1 && in3b === 1);
}

// 334断组分析（返回推荐结果）
function analyze334(history) {
    if (history.length < 2) {
        return { g4: '-', g3a: '-', g3b: '-', method: '-', rate: 0, stable: false };
    }

    const lastNum = history[0].num1 + history[0].num2 + history[0].num3;

    // 生成三种断组
    const duima = make334Duima(lastNum);
    const hekua = make334Hekua(lastNum);
    const linhao = make334Linhao(lastNum);

    // 回测正确率
    const duimaStats = backtest334Method(history.slice(), make334Duima);
    const hekuaStats = backtest334Method(history.slice(), make334Hekua);
    const linhaoStats = backtest334Method(history.slice(), make334Linhao);

    // 选正确率最高的
    const methods = [
        { name: '对码断组法', ...duima, ...duimaStats },
        { name: '和跨查表法', ...hekua, ...hekuaStats },
        { name: '邻号法', ...linhao, ...linhaoStats }
    ];

    methods.sort((a, b) => b.rate - a.rate);
    const best = methods[0];

    return {
        g4: best.g4,
        g3a: best.g3a,
        g3b: best.g3b,
        method: best.name + ' (30期' + best.rate + '%)',
        rate: best.rate,
        stable: best.stable,
        allMethods: methods
    };
}

// 导出模块
window.HEKUA_334_TABLE = HEKUA_334_TABLE;
window.make334Duima = make334Duima;
window.make334Hekua = make334Hekua;
window.calcBalanceScore = calcBalanceScore;
window.make334Linhao = make334Linhao;
window.check334Correct = check334Correct;
window.analyze334 = analyze334;