// ==================== 回测模块 ====================
// 包含：334断组回测、分解式回测、稳定度检查

// 回测334断组方法
function backtest334Method(history, makeMethod) {
    let correct = 0;
    const total = Math.min(30, history.length - 1);

    for (let i = 0; i < total; i++) {
        const lastNum = history[i].num1 + history[i].num2 + history[i].num3;
        const resultNum = history[i + 1].num1 + history[i + 1].num2 + history[i + 1].num3;

        const { g4, g3a, g3b } = makeMethod(lastNum);
        if (check334Correct(resultNum, g4, g3a, g3b)) {
            correct++;
        }
    }

    const rate = Math.round((correct / total) * 100);
    const stable = rate >= 85;

    return { correct, total, rate, stable };
}

// 回测分解式方法
function backtestFenjiMethod(history, getGroupFn) {
    let correct = 0;
    const total = Math.min(30, history.length - 1);

    for (let i = 0; i < total; i++) {
        const lastNum = history[i].num1 + history[i].num2 + history[i].num3;
        const resultNum = history[i + 1].num1 + history[i + 1].num2 + history[i + 1].num3;

        const groups = getGroupFn(lastNum);
        if (checkResult(resultNum, groups.groupA, groups.groupB)) {
            correct++;
        }
    }

    const rate = Math.round((correct / total) * 100);
    const stable = rate >= 85;

    return { correct, total, rate, stable };
}

// 检查分解式稳定度
function checkStability(history, method) {
    let correct = 0;
    const total = Math.min(30, history.length - 1);

    for (let i = 0; i < total; i++) {
        const lastNum = history[i].num1 + history[i].num2 + history[i].num3;
        const resultNum = history[i + 1].num1 + history[i + 1].num2 + history[i + 1].num3;

        let isCorrect = false;

        if (method === 'duima') {
            const { duimaGroup, remainingGroup } = getDuimaGroup(lastNum);
            isCorrect = checkResult(resultNum, duimaGroup, remainingGroup);
        } else if (method === 'sumtail') {
            const { group4, group6 } = getSumTailGroup(lastNum);
            isCorrect = checkResult(resultNum, group4, group6);
        } else if (method === 'combined') {
            const { duimaGroup, remainingGroup } = getDuimaGroup(lastNum);
            const { group4, group6 } = getSumTailGroup(lastNum);
            const intersection = Array.from(new Set(duimaGroup.split('').filter(d => group4.includes(d)))).sort().join('');
            isCorrect = intersection.length >= 1 && intersection.length <= 2;
        }

        if (isCorrect) correct++;
    }

    const rate = Math.round((correct / total) * 100);
    const stable = rate >= 85;

    return { correct, total, rate, stable };
}

// 导出模块
window.backtest334Method = backtest334Method;
window.backtestFenjiMethod = backtestFenjiMethod;
window.checkStability = checkStability;