let currentBusinessId = null;
let customers = [];
let revenuePlanData = {};

// 事業切り替え
function switchBusiness(businessId) {
    // 全てのテーブルを非表示
    document.querySelectorAll('.business-table').forEach(table => {
        table.classList.add('hidden');
    });
    
    // 選択された事業のテーブルを表示
    const selectedTable = document.getElementById(`business-table-${businessId}`);
    if (selectedTable) {
        selectedTable.classList.remove('hidden');
    }
    
    // タブのスタイルを更新
    document.querySelectorAll('.business-tab').forEach(tab => {
        tab.classList.remove('border-blue-500', 'text-blue-600');
        tab.classList.add('border-transparent', 'text-gray-500');
        if (parseInt(tab.dataset.businessId) === businessId) {
            tab.classList.add('border-blue-500', 'text-blue-600');
            tab.classList.remove('border-transparent', 'text-gray-500');
        }
    });
    
    currentBusinessId = businessId;
    loadRevenuePlan(businessId);
}

// 収益計画データの読み込み
async function loadRevenuePlan(businessId) {
    try {
        const response = await fetch(`/api/revenue-plan/${businessId}`);
        const data = await response.json();
        customers = data.customers;
        revenuePlanData = data.values || {};
        renderRevenuePlan();
    } catch (error) {
        console.error('収益計画の読み込みに失敗:', error);
        alert('データの読み込みに失敗しました。');
    }
}

// 収益計画テーブルの描画
function renderRevenuePlan() {
    const tbody = document.querySelector(`#revenue-table-body-${currentBusinessId}`);
    tbody.innerHTML = '';

    customers.forEach(customer => {
        const row = document.createElement('tr');
        
        // 事業名と顧客名
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${currentBusiness.name}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${customer.name}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <input type="number" 
                       class="unit-price border-gray-300 rounded-md"
                       data-customer-id="${customer.id}"
                       value="${getUnitPrice(customer.id)}"
                       onchange="updateAmounts(${customer.id})">
            </td>
        `;

        // 月別の入力欄（4列目～15列目）
        for (let month = 1; month <= 12; month++) {
            row.innerHTML += `
                <td class="px-6 py-4 whitespace-nowrap">
                    <input type="number" 
                           class="quantity border-gray-300 rounded-md mb-1"
                           data-customer-id="${customer.id}"
                           data-month="${month}"
                           value="${getQuantity(customer.id, month)}"
                           onchange="updateAmount(${customer.id}, ${month})">
                    <div class="amount text-gray-500 text-sm">
                        ${formatAmount(calculateAmount(customer.id, month))}
                    </div>
                </td>
            `;
        }

        // 年間合計（16列目）
        row.innerHTML += `
            <td class="px-6 py-4 whitespace-nowrap font-bold customer-total" 
                data-customer-id="${customer.id}">
                ${formatAmount(calculateCustomerTotal(customer.id))}
            </td>
        `;

        tbody.appendChild(row);
    });

    updateTotals();
    renderTotalSummary();
}

// 全体集計テーブルの描画
function renderTotalSummary() {
    const tbody = document.querySelector('#total-summary-body');
    tbody.innerHTML = '';

    businesses.forEach(business => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap font-medium">${business.name}</td>
        `;

        // 月別合計
        for (let month = 1; month <= 12; month++) {
            const monthTotal = calculateBusinessMonthTotal(business.id, month);
            row.innerHTML += `
                <td class="px-6 py-4 whitespace-nowrap">
                    ${formatAmount(monthTotal)}
                </td>
            `;
        }

        // 事業年間合計
        const yearTotal = calculateBusinessYearTotal(business.id);
        row.innerHTML += `
            <td class="px-6 py-4 whitespace-nowrap font-bold">
                ${formatAmount(yearTotal)}
            </td>
        `;

        tbody.appendChild(row);
    });
}

// 単価の取得
function getUnitPrice(customerId) {
    return revenuePlanData[customerId]?.unit_price || 0;
}

// 数量の取得
function getQuantity(customerId, month) {
    return revenuePlanData[customerId]?.quantities?.[month] || 0;
}

// 金額の計算
function calculateAmount(customerId, month) {
    const unitPrice = getUnitPrice(customerId);
    const quantity = getQuantity(customerId, month);
    return unitPrice * quantity;
}

// 顧客ごとの合計計算
function calculateCustomerTotal(customerId) {
    let total = 0;
    for (let month = 1; month <= 12; month++) {
        total += calculateAmount(customerId, month);
    }
    return total;
}

// 金額のフォーマット
function formatAmount(amount) {
    return new Intl.NumberFormat('ja-JP').format(amount);
}

// 数量変更時の処理
function updateAmount(customerId, month) {
    const row = document.querySelector(`tr[data-customer-id="${customerId}"]`);
    const quantityInput = row.querySelector(`input[data-month="${month}"]`);
    const quantity = parseInt(quantityInput.value) || 0;

    if (!revenuePlanData[customerId]) {
        revenuePlanData[customerId] = { quantities: {} };
    }
    if (!revenuePlanData[customerId].quantities) {
        revenuePlanData[customerId].quantities = {};
    }
    revenuePlanData[customerId].quantities[month] = quantity;

    const amount = calculateAmount(customerId, month);
    const amountDiv = quantityInput.nextElementSibling;
    amountDiv.textContent = formatAmount(amount);

    updateCustomerTotal(customerId);
    updateTotals();
}

// 単価変更時の処理
function updateAmounts(customerId) {
    const unitPriceInput = document.querySelector(`input.unit-price[data-customer-id="${customerId}"]`);
    const unitPrice = parseInt(unitPriceInput.value) || 0;

    if (!revenuePlanData[customerId]) {
        revenuePlanData[customerId] = {};
    }
    revenuePlanData[customerId].unit_price = unitPrice;

    // 全ての月の金額を更新
    for (let month = 1; month <= 12; month++) {
        const amount = calculateAmount(customerId, month);
        const amountDiv = document.querySelector(
            `tr[data-customer-id="${customerId}"] td:nth-child(${month + 2}) .amount`
        );
        amountDiv.textContent = formatAmount(amount);
    }

    updateCustomerTotal(customerId);
    updateTotals();
}

// 顧客合計の更新
function updateCustomerTotal(customerId) {
    const total = calculateCustomerTotal(customerId);
    const totalCell = document.querySelector(`.customer-total[data-customer-id="${customerId}"]`);
    totalCell.textContent = formatAmount(total);
}

// 全体の合計更新
function updateTotals() {
    // 月別合計の更新
    for (let month = 1; month <= 12; month++) {
        let monthTotal = 0;
        customers.forEach(customer => {
            monthTotal += calculateAmount(customer.id, month);
        });
        const monthTotalCell = document.querySelector(`.month-total[data-month="${month}"]`);
        monthTotalCell.textContent = formatAmount(monthTotal);
    }

    // 総合計の更新
    let grandTotal = 0;
    customers.forEach(customer => {
        grandTotal += calculateCustomerTotal(customer.id);
    });
    document.querySelector('.grand-total').textContent = formatAmount(grandTotal);
}

// 収益計画の保存
async function saveRevenuePlan() {
    try {
        const response = await fetch('/api/revenue-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                business_id: currentBusinessId,
                values: revenuePlanData
            })
        });

        if (response.ok) {
            alert('収益計画を保存しました。');
        } else {
            throw new Error('保存に失敗しました。');
        }
    } catch (error) {
        console.error('収益計画の保存に失敗:', error);
        alert('保存に失敗しました。');
    }
}

// ページ読み込み時に最初の事業を選択
document.addEventListener('DOMContentLoaded', () => {
    const firstTab = document.querySelector('.business-tab');
    if (firstTab) {
        const businessId = parseInt(firstTab.dataset.businessId);
        switchBusiness(businessId);
    }
}); 