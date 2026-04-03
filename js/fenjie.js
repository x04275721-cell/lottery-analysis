// ==================== 分解式模块 ====================
// 包含：对码分解式、和值尾分解式

// 对码配对表
const DUIMA_PAIRS = {
    '0': '5', '1': '6', '2': '7', '3': '8', '4': '9',
    '5': '0', '6': '1', '7': '2', '8': '3', '9': '4'
};

// 和值尾分解表
const SUM_TAIL_DECOMPOSE = {
    '0': ['0126', '345789'],
    '1': ['1237', '045689'],
    '2': ['2348', '015679'],
    '3': ['3459', '012678'],
    '4': ['0456', '123789'],
    '5': ['0126', '345789'],
    '6': ['1237', '045689'],
    '7': ['2348', '015679'],
    '8': ['3459', '012678'],
    '9': ['0456', '123789']
};

// 获取对码分解组
function getDuimaGroup(lastNum) {
    const duimaSet = new Set();
    for (const d of lastNum) {
        duimaSet.add(d);
        duimaSet.add(DUIMA_PAIRS[d]);
    }
    const duimaGroup = Array.from(duimaSet).sort().join('');
    const allDigits = new Set('0123456789');
    const remainingGroup = Array.from(allDigits - duimaSet).sort().join('');
    return { duimaGroup, remainingGroup };
}

// 获取和值尾分解组
function getSumTailGroup(lastNum) {
    const sum = parseInt(lastNum[0]) + parseInt(lastNum[1]) + parseInt(lastNum[2]);
    const sumTail = String(sum % 10);
    const decompose = SUM_TAIL_DECOMPOSE[sumTail];
    return {
        group4: decompose[0],
        group6: decompose[1],
        sumTail: sumTail
    };
}

// 检查分解式是否正确（两边都有不同数字=正确）
function checkResult(resultNum, groupA, groupB) {
    const uniqueDigits = new Set(resultNum);
    let inA = 0, inB = 0;
    for (const d of uniqueDigits) {
        if (groupA.includes(d)) inA++;
        if (groupB.includes(d)) inB++;
    }
    return inA >= 1 && inB >= 1;
}

// 对码法分析
function analyzeDuima(history) {
    if (history.length < 2) return null;
    const lastNum = history[0].num1 + history[0].num2 + history[0].num3;
    const { duimaGroup, remainingGroup } = getDuimaGroup(lastNum);
    return { lastNum, duimaGroup, remainingGroup };
}

// 和值尾分解分析
function analyzeSumTail(history) {
    if (history.length < 2) return null;
    const lastNum = history[0].num1 + history[0].num2 + history[0].num3;
    const { group4, group6, sumTail } = getSumTailGroup(lastNum);
    return { lastNum, group4, group6, sumTail };
}

// 导出模块
window.DUIMA_PAIRS = DUIMA_PAIRS;
window.SUM_TAIL_DECOMPOSE = SUM_TAIL_DECOMPOSE;
window.getDuimaGroup = getDuimaGroup;
window.getSumTailGroup = getSumTailGroup;
window.checkResult = checkResult;
window.analyzeDuima = analyzeDuima;
window.analyzeSumTail = analyzeSumTail;