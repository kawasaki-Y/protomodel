let currentBusinessId = null;
let customers = [];
let planData = {};

// 事業切り替え
function switchBusiness(businessId) {
    currentBusinessId = businessId;
    loadRevenuePlan(businessId);
    
    // タブのスタイル更新
    document.querySelectorAll('.business-tab').forEach(tab => {
        tab.classList.remove('border-blue-500', 'text-blue-600');
        tab.classList.add('border-transparent', 'text-gray-500');
        if (parseInt(tab.dataset.businessId) === businessId) {
            tab.classList.add('border-blue-500', 'text-blue-600');
            tab.classList.remove('border-transparent', 'text-gray-500');
        }
    });
}

// 収益計画データの読み込み
async function loadRevenuePlan(businessId) {
    try {
        const response = await fetch(`/api/revenue-plan/${businessId}`);
        const data = await response.json();
        
        customers = data.customers;
        planData = data.values || {};
        renderRevenuePlan();
    } catch (error) {
        console.error('収益計画の読み込みに失敗:', error);
        alert('データの読み込みに失敗しました。');
    }
}

// 収益計画テーブルの描画
function renderRevenuePlan() {
    const tbody = document.getElementById('revenue-plan-body');
    tbody.innerHTML = '';

    // 既存のデータ行の描画
    Object.entries(planData).forEach(([customerId, data]) => {
        const row = createPlanRow(customerId, data);
        tbody.appendChild(row);
    });

    updateTotals();
}

// 新規行の追加（修正）
function addNewRow() {
    console.log('Adding new row...'); // デバッグログ
    const tbody = document.getElementById('revenue-plan-body');
    if (!tbody) {
        console.error('Table body not found!');
        return;
    }

    const row = createPlanRow();
    row.classList.add('fade-in');
    tbody.appendChild(row);

    // 新規行は編集可能な状態で開始
    row.querySelectorAll('input, select').forEach(input => {
        input.disabled = false;
    });
    row.classList.add('editing');

    // 編集ボタンのアイコンを保存に変更
    const editBtn = row.querySelector('.edit-btn');
    if (editBtn) {
        editBtn.innerHTML = '<i class="fas fa-save"></i>';
    }

    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// 行の作成（修正）
function createPlanRow(customerId = null, data = null) {
    const row = document.createElement('tr');
    row.className = 'plan-row';
    
    // 顧客選択セル
    const customerCell = document.createElement('td');
    customerCell.className = 'px-6 py-4 whitespace-nowrap';
    const customerSelect = document.createElement('select');
    customerSelect.className = 'customer-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500';
    customerSelect.innerHTML = `
        <option value="">顧客を選択</option>
        ${customers.map(customer => `
            <option value="${customer.id}" ${customerId === customer.id ? 'selected' : ''}>
                ${customer.name}
            </option>
        `).join('')}
    `;
    customerCell.appendChild(customerSelect);
    row.appendChild(customerCell);

    // 単価入力セル
    const priceCell = document.createElement('td');
    priceCell.className = 'px-6 py-4 whitespace-nowrap';
    const priceInput = document.createElement('input');
    priceInput.type = 'number';
    priceInput.className = 'unit-price mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500';
    priceInput.value = data?.unit_price || '';
    priceInput.onchange = () => updateRowCalculations(row);
    priceCell.appendChild(priceInput);
    row.appendChild(priceCell);

    // 月別入力セル
    for (let month = 1; month <= 12; month++) {
        const monthCell = document.createElement('td');
        monthCell.className = 'px-6 py-4 whitespace-nowrap';
        
        // 予想販売数入力
        const quantityInput = document.createElement('input');
        quantityInput.type = 'number';
        quantityInput.className = 'quantity-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500';
        quantityInput.dataset.month = month;
        quantityInput.value = data?.quantities?.[month] || '';
        quantityInput.onchange = () => updateRowCalculations(row);
        
        // 売上表示
        const amountDiv = document.createElement('div');
        amountDiv.className = 'amount-display text-sm text-gray-500 mt-1';
        amountDiv.textContent = '¥0';
        
        monthCell.appendChild(quantityInput);
        monthCell.appendChild(amountDiv);
        row.appendChild(monthCell);
    }

    // 年間合計セル
    const totalCell = document.createElement('td');
    totalCell.className = 'px-6 py-4 whitespace-nowrap font-bold row-total';
    totalCell.textContent = '¥0';
    row.appendChild(totalCell);

    // 操作セルの修正
    const actionCell = document.createElement('td');
    actionCell.className = 'px-6 py-4 whitespace-nowrap';
    const actionDiv = document.createElement('div');
    actionDiv.className = 'flex space-x-2';

    // 編集ボタン
    const editButton = document.createElement('button');
    editButton.className = 'edit-btn text-blue-600 hover:text-blue-900';
    editButton.innerHTML = '<i class="fas fa-edit"></i>';
    editButton.addEventListener('click', function() {
        editRow(this);
    });

    // 削除ボタン
    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-btn text-red-600 hover:text-red-900';
    deleteButton.innerHTML = '<i class="fas fa-trash"></i>';
    deleteButton.addEventListener('click', function() {
        deleteRow(this);
    });

    actionDiv.appendChild(editButton);
    actionDiv.appendChild(deleteButton);
    actionCell.appendChild(actionDiv);
    row.appendChild(actionCell);

    // 初期状態では入力フィールドを無効化
    row.querySelectorAll('input, select').forEach(input => {
        input.disabled = true;
    });

    return row;
}

// 行の計算更新
function updateRowCalculations(row) {
    const unitPrice = parseFloat(row.querySelector('.unit-price').value) || 0;
    let rowTotal = 0;

    // 各月の売上計算
    row.querySelectorAll('.quantity-input').forEach(input => {
        const quantity = parseFloat(input.value) || 0;
        const amount = unitPrice * quantity;
        const amountDisplay = input.nextElementSibling;
        amountDisplay.textContent = formatNumber(amount);
        rowTotal += amount;
    });

    // 行合計の更新
    row.querySelector('.row-total').textContent = formatNumber(rowTotal);
    updateTotals();
    
    // 自動保存を実行
    debounce(saveAllData, 1000)();
}

// 合計の更新
function updateTotals() {
    const rows = document.querySelectorAll('.plan-row');
    let yearTotal = 0;

    // 月別合計の初期化
    const monthTotals = Array(12).fill(0);

    // 各行の集計
    rows.forEach(row => {
        row.querySelectorAll('.amount-display').forEach((display, index) => {
            const amount = parseAmountDisplay(display.textContent);
            monthTotals[index] += amount;
        });
    });

    // 月別合計の表示更新
    monthTotals.forEach((total, index) => {
        const monthTotalCell = document.querySelector(`.month-total[data-month="${index + 1}"]`);
        monthTotalCell.textContent = formatNumber(total);
        yearTotal += total;
    });

    // 年間合計の更新
    document.querySelector('.year-total').textContent = formatNumber(yearTotal);
}

// 行の削除（修正）
function deleteRow(button) {
    console.log('Deleting row...'); // デバッグログ
    if (confirm('この行を削除してもよろしいですか？')) {
        const row = button.closest('tr');
        row.classList.add('fade-out');
        
        setTimeout(() => {
            row.remove();
            updateTotals();
        }, 300);
    }
}

// 数値のフォーマット
function formatNumber(number) {
    return new Intl.NumberFormat('ja-JP').format(number);
}

// 金額表示からの数値変換
function parseAmountDisplay(text) {
    return parseFloat(text.replace(/,/g, '')) || 0;
}

// 行の編集モード切り替え（修正）
function editRow(button) {
    console.log('Editing row...'); // デバッグログ
    const row = button.closest('tr');
    const inputs = row.querySelectorAll('input, select');
    const isEditing = row.classList.contains('editing');

    if (isEditing) {
        // 編集モードを終了
        row.classList.remove('editing');
        inputs.forEach(input => {
            input.disabled = true;
        });
        button.innerHTML = '<i class="fas fa-edit"></i>';
        updateRowCalculations(row);
    } else {
        // 編集モードを開始
        row.classList.add('editing');
        inputs.forEach(input => {
            input.disabled = false;
        });
        button.innerHTML = '<i class="fas fa-save"></i>';
    }
}

// 自動保存のためのdebounce関数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// データの保存
async function saveAllData() {
    try {
        const rows = document.querySelectorAll('.plan-row');
        const saveData = {
            business_id: currentBusinessId,
            values: {}
        };

        rows.forEach(row => {
            const customerId = row.querySelector('.customer-select').value;
            if (!customerId) return;

            const unitPrice = parseFloat(row.querySelector('.unit-price').value) || 0;
            const quantities = {};

            row.querySelectorAll('.quantity-input').forEach(input => {
                const month = input.dataset.month;
                quantities[month] = parseFloat(input.value) || 0;
            });

            saveData.values[customerId] = {
                unit_price: unitPrice,
                quantities: quantities
            };
        });

        const response = await fetch('/api/revenue-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(saveData)
        });

        if (response.ok) {
            // 保存成功時の通知
            const saveBtn = document.querySelector('.save-btn');
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<i class="fas fa-check mr-2"></i>保存完了';
            setTimeout(() => {
                saveBtn.innerHTML = originalText;
            }, 2000);
        } else {
            throw new Error('保存に失敗しました');
        }
    } catch (error) {
        console.error('保存エラー:', error);
        alert('データの保存に失敗しました。');
    }
}

// データ保存処理の関数
async function saveRevenuePlan() {
    try {
        const rows = document.querySelectorAll('.plan-row');
        const saveData = {
            business_id: currentBusinessId,
            values: {}
        };

        // 各行のデータを収集
        rows.forEach(row => {
            const customerId = row.querySelector('.customer-select').value;
            if (!customerId) return;

            const quantities = {};
            let hasChanges = false;

            // 各月のデータを収集
            row.querySelectorAll('.quantity-input').forEach(input => {
                const month = input.dataset.month;
                const quantity = parseInt(input.value) || 0;
                
                // 変更があった場合のみ保存対象に含める
                if (quantity !== (input.dataset.originalValue || 0)) {
                    quantities[month] = quantity;
                    hasChanges = true;
                }
            });

            // 変更があったデータのみを保存対象に含める
            if (hasChanges) {
                saveData.values[customerId] = {
                    quantities: quantities
                };
            }
        });

        // データを保存
        const response = await fetch('/api/revenue-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(saveData)
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || '保存に失敗しました');
        }

        // 保存成功時の処理
        showSuccessMessage('収益計画を保存しました');
        
        // 保存したデータを現在の値として設定
        rows.forEach(row => {
            row.querySelectorAll('.quantity-input').forEach(input => {
                input.dataset.originalValue = input.value;
            });
        });

    } catch (error) {
        console.error('保存エラー:', error);
        showErrorMessage('データの保存に失敗しました');
    }
}

// 成功メッセージを表示する関数
function showSuccessMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg';
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
}

// エラーメッセージを表示する関数
function showErrorMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded shadow-lg';
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
}

// DOMContentLoadedイベントリスナーの修正
document.addEventListener('DOMContentLoaded', () => {
    const firstTab = document.querySelector('.business-tab');
    if (firstTab) {
        const businessId = parseInt(firstTab.dataset.businessId);
        switchBusiness(businessId);
    }

    // 行追加ボタンのイベントリスナーを修正
    const addButton = document.querySelector('.add-row-btn');
    if (addButton) {
        addButton.addEventListener('click', addNewRow);
        console.log('Add button listener attached');
    } else {
        console.error('Add button not found!');
    }
});

// スタイルの追加（修正）
const style = document.createElement('style');
style.textContent = `
    .fade-in {
        opacity: 0;
        animation: fadeIn 0.3s ease-in forwards;
    }
    
    .fade-out {
        opacity: 1;
        animation: fadeOut 0.3s ease-out forwards;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(10px); }
    }
    
    .edit-btn, .delete-btn {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .edit-btn:hover, .delete-btn:hover {
        transform: translateY(-1px);
    }

    .editing input, .editing select {
        background-color: #f8fafc;
        border-color: #3b82f6;
    }
`;
document.head.appendChild(style); 