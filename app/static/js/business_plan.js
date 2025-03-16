/**
 * 事業計画管理用JavaScript
 * 項目の追加、編集、削除および月次データの入力機能を提供
 */

// DOMが読み込まれたら実行
document.addEventListener('DOMContentLoaded', function() {
    // 各ボタンの参照を取得
    const saveChangesBtn = document.getElementById('saveChangesBtn');
    const addItemBtn = document.getElementById('addItemBtn');
    
    // 変更を保存ボタンのイベントリスナー
    if (saveChangesBtn) {
        saveChangesBtn.addEventListener('click', saveAllChanges);
    }
    
    // 項目追加ボタンのイベントリスナー
    if (addItemBtn) {
        addItemBtn.addEventListener('click', showAddItemModal);
    }
    
    // 編集可能なセルにイベントリスナーを設定
    setupEditableCells();
    
    // 削除ボタンにイベントリスナーを設定
    setupDeleteButtons();
    
    // 事業計画を取得して表示
    fetchCurrentPlan();
});

/**
 * 編集可能なセルにクリックイベントリスナーを設定
 */
function setupEditableCells() {
    const editableCells = document.querySelectorAll('.editable-cell');
    
    editableCells.forEach(cell => {
        cell.addEventListener('click', function() {
            const currentValue = this.textContent.trim();
            const itemId = this.closest('tr').dataset.itemId;
            const month = this.dataset.month;
            
            // 編集用の入力フィールドを作成
            const input = document.createElement('input');
            input.type = 'number';
            input.value = currentValue.replace(/[¥,]/g, ''); // 通貨記号と桁区切りを削除
            input.className = 'w-full border-none focus:ring-2 focus:ring-blue-500';
            
            // 元の内容を入力フィールドで置き換え
            this.textContent = '';
            this.appendChild(input);
            
            // 入力フィールドにフォーカス
            input.focus();
            
            // 入力完了時の処理
            input.addEventListener('blur', function() {
                const newValue = this.value;
                // 数値としての検証
                const numericValue = parseInt(newValue) || 0;
                
                // セルを更新
                const formattedValue = new Intl.NumberFormat('ja-JP', { 
                    style: 'currency', 
                    currency: 'JPY' 
                }).format(numericValue);
                
                cell.textContent = formattedValue;
                
                // データを一時保存（あとでまとめて送信）
                cell.dataset.pendingValue = numericValue;
            });
            
            // Enterキーのハンドリング
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    this.blur();
                }
            });
        });
    });
}

/**
 * 削除ボタンにイベントリスナーを設定
 */
function setupDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-item-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (!confirm('この項目を削除してもよろしいですか？子項目も全て削除されます。')) {
                return;
            }
            
            const itemId = this.closest('tr').dataset.itemId;
            
            // 項目削除APIを呼び出し
            fetch(`/business-plan/item/${itemId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 成功時は行を削除
                    this.closest('tr').remove();
                    // 子項目も削除
                    const childRows = document.querySelectorAll(`tr[data-parent-id="${itemId}"]`);
                    childRows.forEach(row => row.remove());
                } else {
                    alert('削除に失敗しました');
                }
            })
            .catch(error => {
                console.error('エラー:', error);
                alert('削除処理中にエラーが発生しました');
            });
        });
    });
}

/**
 * 全ての変更をサーバーに保存
 */
function saveAllChanges() {
    const editableCells = document.querySelectorAll('.editable-cell[data-pending-value]');
    const updatePromises = [];
    
    // 変更されたセルごとにAPIを呼び出し
    editableCells.forEach(cell => {
        const itemId = cell.closest('tr').dataset.itemId;
        const month = cell.dataset.month;
        const newValue = cell.dataset.pendingValue;
        
        // 月別金額のみの更新データを作成
        const updateData = {
            monthly_amounts: {}
        };
        updateData.monthly_amounts[month] = parseInt(newValue);
        
        // 更新APIの呼び出し
        const updatePromise = fetch(`/business-plan/item/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 保留データをクリア
                delete cell.dataset.pendingValue;
                return true;
            } else {
                return false;
            }
        })
        .catch(error => {
            console.error('エラー:', error);
            return false;
        });
        
        updatePromises.push(updatePromise);
    });
    
    // 全ての更新が完了したら通知
    Promise.all(updatePromises)
        .then(results => {
            const successCount = results.filter(result => result).length;
            if (successCount === updatePromises.length) {
                alert('全ての変更が保存されました');
            } else {
                alert(`${successCount}/${updatePromises.length}の変更が保存されました`);
            }
        });
}

/**
 * 項目追加モーダルを表示
 */
function showAddItemModal() {
    // モーダル要素を取得または作成
    let modal = document.getElementById('addItemModal');
    
    if (!modal) {
        // モーダルがなければ作成
        modal = document.createElement('div');
        modal.id = 'addItemModal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
                <h3 class="text-lg font-bold mb-4">新規項目の追加</h3>
                
                <form id="addItemForm" class="space-y-4">
                    <div>
                        <label for="parentId" class="block text-sm font-medium text-gray-700">親項目</label>
                        <select id="parentId" name="parentId" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                            <option value="">-- ルート項目として追加 --</option>
                            ${generateParentOptions()}
                        </select>
                    </div>
                    
                    <div>
                        <label for="category" class="block text-sm font-medium text-gray-700">カテゴリ</label>
                        <select id="category" name="category" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                            <option value="売上">売上</option>
                            <option value="原価">原価</option>
                            <option value="販管費">販管費</option>
                            <option value="営業外収益">営業外収益</option>
                            <option value="営業外費用">営業外費用</option>
                        </select>
                    </div>
                    
                    <div>
                        <label for="item_type" class="block text-sm font-medium text-gray-700">項目タイプ</label>
                        <select id="item_type" name="item_type" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                            <option value="header">見出し</option>
                            <option value="detail" selected>詳細</option>
                        </select>
                    </div>
                    
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700">項目名</label>
                        <input type="text" id="name" name="name" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    </div>
                    
                    <div>
                        <label for="description" class="block text-sm font-medium text-gray-700">説明</label>
                        <textarea id="description" name="description" rows="2" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"></textarea>
                    </div>
                    
                    <div id="detailFields" class="space-y-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label for="quantity" class="block text-sm font-medium text-gray-700">数量</label>
                                <input type="number" id="quantity" name="quantity" step="0.01" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                            </div>
                            
                            <div>
                                <label for="unit" class="block text-sm font-medium text-gray-700">単位</label>
                                <input type="text" id="unit" name="unit" placeholder="個, 時間等" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                            </div>
                        </div>
                        
                        <div>
                            <label for="unit_price" class="block text-sm font-medium text-gray-700">単価</label>
                            <input type="number" id="unit_price" name="unit_price" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                        </div>
                    </div>
                    
                    <div class="flex justify-end space-x-3 pt-4 border-t">
                        <button type="button" id="cancelAddItem" class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md">
                            キャンセル
                        </button>
                        <button type="submit" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md">
                            追加する
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 項目タイプの変更でフィールド表示切替
        const itemTypeSelect = modal.querySelector('#item_type');
        const detailFields = modal.querySelector('#detailFields');
        
        itemTypeSelect.addEventListener('change', function() {
            if (this.value === 'header') {
                detailFields.style.display = 'none';
            } else {
                detailFields.style.display = 'block';
            }
        });
        
        // キャンセルボタンの処理
        modal.querySelector('#cancelAddItem').addEventListener('click', function() {
            modal.remove();
        });
        
        // フォーム送信の処理
        modal.querySelector('#addItemForm').addEventListener('submit', function(e) {
            e.preventDefault();
            addNewItem(this);
        });
    } else {
        // 既存のモーダルを表示
        modal.style.display = 'flex';
    }
}

/**
 * 親項目のオプションを生成
 */
function generateParentOptions() {
    let options = '';
    const rootItems = document.querySelectorAll('tr[data-level="0"]');
    
    rootItems.forEach(item => {
        const itemId = item.dataset.itemId;
        const itemName = item.querySelector('.item-name').textContent.trim();
        options += `<option value="${itemId}">${itemName}</option>`;
    });
    
    return options;
}

/**
 * 新規項目をAPIに送信して追加
 */
function addNewItem(form) {
    // 事業計画IDを取得
    const businessPlanId = document.getElementById('business_plan_id').value;
    
    // フォームデータを収集
    const formData = {
        business_plan_id: parseInt(businessPlanId),
        parent_id: form.parentId.value ? parseInt(form.parentId.value) : null,
        category: form.category.value,
        item_type: form.item_type.value,
        name: form.name.value,
        description: form.description.value,
        quantity: form.quantity.value ? parseFloat(form.quantity.value) : null,
        unit_price: form.unit_price.value ? parseInt(form.unit_price.value) : null,
        unit: form.unit.value
    };
    
    // APIを呼び出し
    fetch('/business-plan/item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 成功時はページをリロード
            alert('項目が追加されました');
            location.reload();
        } else {
            alert('項目の追加に失敗しました');
        }
    })
    .catch(error => {
        console.error('エラー:', error);
        alert('処理中にエラーが発生しました');
    });
}

// 事業計画の項目を取得する関数
function fetchPlanItems() {
    fetch('/business-plan/api/plan-items')
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                // 月別ヘッダーを生成
                generateMonthHeaders(data.months);
                // 事業計画項目を表示
                renderPLStatementTable(data.items, data.months);
                // 売上・利益の合計を計算して表示
                calculateTotals(data.items);
                // グラフを描画
                renderCharts(data.months, data.items);
            } else {
                // データがない場合はサンプルデータで表示
                renderSamplePLTable();
            }
        })
        .catch(error => {
            console.error('事業計画項目の取得に失敗しました:', error);
            // エラー時もサンプルデータで表示
            renderSamplePLTable();
        });
}

// 月別ヘッダーを生成する関数
function generateMonthHeaders(months) {
    const headerRow = document.getElementById('monthHeaderRow');
    
    // 既存のヘッダーをクリア（科目と年間合計は残す）
    while (headerRow.children.length > 2) {
        headerRow.removeChild(headerRow.lastChild);
    }
    
    // 月別ヘッダーを追加
    months.forEach(month => {
        const th = document.createElement('th');
        // 月表示を「YYYY-MM」から「MM月」形式に変更
        const monthPart = month.split('-')[1];
        th.textContent = monthPart + '月';
        headerRow.appendChild(th);
    });
}

// 損益計算書テーブルのレンダリング関数
function renderPLStatementTable(items, months) {
    const tableBody = document.getElementById('planItemsBody');
    tableBody.innerHTML = '';
    
    // 1. 売上高（収益事業別の合計値）
    renderPLSection(tableBody, '売上高', 'revenue', items, months, 'blue');
    
    // 2. 売上原価（勘定科目の合計値）
    renderPLSection(tableBody, '売上原価', 'cost', items, months, 'red');
    
    // 3. 売上総利益（売上-売上原価）
    renderPLCalculatedRow(tableBody, '売上総利益', 'gross_profit', 'revenue', 'cost', items, months, 'green');
    
    // 4. 販売費及び一般管理費（勘定科目の合計値）
    renderPLSection(tableBody, '販売費及び一般管理費', 'sga', items, months, 'red');
    
    // 5. 営業利益（売上総利益-販売費及び一般管理費）
    renderPLCalculatedRow(tableBody, '営業利益', 'operating_profit', 'gross_profit', 'sga', items, months, 'green');
    
    // 6. 営業外収益（勘定科目の合計値）
    renderPLSection(tableBody, '営業外収益', 'non_operating_income', items, months, 'blue');
    
    // 7. 営業外費用（勘定科目の合計値）
    renderPLSection(tableBody, '営業外費用', 'non_operating_expense', items, months, 'red');
    
    // 8. 経常利益（営業利益＋営業外収益-営業外費用）
    renderPLComplexCalculatedRow(tableBody, '経常利益', 'ordinary_income', 
        [
            { key: 'operating_profit', sign: 1 },
            { key: 'non_operating_income', sign: 1 },
            { key: 'non_operating_expense', sign: -1 }
        ], 
        items, months, 'green');
    
    // 9. 特別利益（勘定科目の合計値）
    renderPLSection(tableBody, '特別利益', 'extraordinary_income', items, months, 'blue');
    
    // 10. 特別損失（勘定科目の合計値）
    renderPLSection(tableBody, '特別損失', 'extraordinary_loss', items, months, 'red');
    
    // 11. 税引前当期純利益（経常利益＋特別利益-特別損失）
    renderPLComplexCalculatedRow(tableBody, '税引前当期純利益', 'income_before_tax', 
        [
            { key: 'ordinary_income', sign: 1 },
            { key: 'extraordinary_income', sign: 1 },
            { key: 'extraordinary_loss', sign: -1 }
        ], 
        items, months, 'green');
    
    // 12. 法人税等支払額（税引前当期純利益✖️法人税率）
    renderPLTaxRow(tableBody, '法人税等支払額', 'tax', 'income_before_tax', 0.3, items, months, 'red');
    
    // 13. 税引後当期純利益（税引前当期純利益-法人税等支払額）
    renderPLCalculatedRow(tableBody, '税引後当期純利益', 'net_income', 'income_before_tax', 'tax', items, months, 'green');
}

// 損益計算書セクション（親項目とその子項目）を表示する関数
function renderPLSection(tableBody, sectionTitle, sectionKey, items, months, colorClass) {
    // サンプルデータ（APIから実際のデータに置き換える予定）
    const sectionData = {
        total: getRandomTotal(),
        monthly: months.map(() => getRandomTotal() / 12)
    };
    
    const childItems = [
        { name: sectionTitle + ' 項目1', total: sectionData.total * 0.6, monthly: sectionData.monthly.map(m => m * 0.6) },
        { name: sectionTitle + ' 項目2', total: sectionData.total * 0.4, monthly: sectionData.monthly.map(m => m * 0.4) }
    ];
    
    // 親項目行
    const parentRow = document.createElement('tr');
    parentRow.classList.add('table-secondary');
    
    const parentNameCell = document.createElement('td');
    parentNameCell.textContent = sectionTitle;
    parentNameCell.style.fontWeight = 'bold';
    parentRow.appendChild(parentNameCell);
    
    const parentTotalCell = document.createElement('td');
    parentTotalCell.textContent = formatCurrency(sectionData.total);
    parentTotalCell.style.textAlign = 'right';
    parentTotalCell.style.fontWeight = 'bold';
    if (colorClass === 'blue') parentTotalCell.classList.add('text-primary');
    if (colorClass === 'red') parentTotalCell.classList.add('text-danger');
    if (colorClass === 'green') parentTotalCell.classList.add('text-success');
    parentRow.appendChild(parentTotalCell);
    
    // 月別の金額
    sectionData.monthly.forEach(monthAmount => {
        const monthCell = document.createElement('td');
        monthCell.textContent = formatCurrency(monthAmount);
        monthCell.style.textAlign = 'right';
        monthCell.style.fontWeight = 'bold';
        if (colorClass === 'blue') monthCell.classList.add('text-primary');
        if (colorClass === 'red') monthCell.classList.add('text-danger');
        if (colorClass === 'green') monthCell.classList.add('text-success');
        parentRow.appendChild(monthCell);
    });
    
    tableBody.appendChild(parentRow);
    
    // 子項目行
    childItems.forEach(item => {
        const childRow = document.createElement('tr');
        
        const childNameCell = document.createElement('td');
        childNameCell.textContent = '　' + item.name;
        childRow.appendChild(childNameCell);
        
        const childTotalCell = document.createElement('td');
        childTotalCell.textContent = formatCurrency(item.total);
        childTotalCell.style.textAlign = 'right';
        childRow.appendChild(childTotalCell);
        
        // 月別の項目金額
        item.monthly.forEach(monthAmount => {
            const monthCell = document.createElement('td');
            monthCell.textContent = formatCurrency(monthAmount);
            monthCell.style.textAlign = 'right';
            childRow.appendChild(monthCell);
        });
        
        tableBody.appendChild(childRow);
    });
    
    // セクションの合計をグローバル変数に保存（計算用）
    if (!window.plTotals) window.plTotals = {};
    window.plTotals[sectionKey] = {
        total: sectionData.total,
        monthly: sectionData.monthly
    };
}

// 損益計算書の計算行（2つの項目の計算結果）を表示する関数
function renderPLCalculatedRow(tableBody, rowTitle, resultKey, sourceKey1, sourceKey2, items, months, colorClass) {
    if (!window.plTotals) return;
    
    const source1 = window.plTotals[sourceKey1] || { total: 0, monthly: months.map(() => 0) };
    const source2 = window.plTotals[sourceKey2] || { total: 0, monthly: months.map(() => 0) };
    
    // 計算
    const resultTotal = source1.total - source2.total;
    const resultMonthly = source1.monthly.map((val, idx) => val - source2.monthly[idx]);
    
    // 結果行
    const resultRow = document.createElement('tr');
    resultRow.classList.add('table-secondary');
    
    const resultNameCell = document.createElement('td');
    resultNameCell.textContent = rowTitle;
    resultNameCell.style.fontWeight = 'bold';
    resultRow.appendChild(resultNameCell);
    
    const resultTotalCell = document.createElement('td');
    resultTotalCell.textContent = formatCurrency(resultTotal);
    resultTotalCell.style.textAlign = 'right';
    resultTotalCell.style.fontWeight = 'bold';
    if (colorClass === 'blue') resultTotalCell.classList.add('text-primary');
    if (colorClass === 'red') resultTotalCell.classList.add('text-danger');
    if (colorClass === 'green') resultTotalCell.classList.add('text-success');
    resultRow.appendChild(resultTotalCell);
    
    // 月別の計算結果
    resultMonthly.forEach(monthAmount => {
        const monthCell = document.createElement('td');
        monthCell.textContent = formatCurrency(monthAmount);
        monthCell.style.textAlign = 'right';
        monthCell.style.fontWeight = 'bold';
        if (colorClass === 'blue') monthCell.classList.add('text-primary');
        if (colorClass === 'red') monthCell.classList.add('text-danger');
        if (colorClass === 'green') monthCell.classList.add('text-success');
        resultRow.appendChild(monthCell);
    });
    
    tableBody.appendChild(resultRow);
    
    // 計算結果をグローバル変数に保存（さらなる計算用）
    window.plTotals[resultKey] = {
        total: resultTotal,
        monthly: resultMonthly
    };
}

// 複数項目の複雑な計算結果を表示する関数
function renderPLComplexCalculatedRow(tableBody, rowTitle, resultKey, sources, items, months, colorClass) {
    if (!window.plTotals) return;
    
    // 初期値
    let resultTotal = 0;
    let resultMonthly = months.map(() => 0);
    
    // 各ソース項目を計算
    sources.forEach(source => {
        const sourceData = window.plTotals[source.key] || { total: 0, monthly: months.map(() => 0) };
        resultTotal += sourceData.total * source.sign;
        resultMonthly = resultMonthly.map((val, idx) => val + (sourceData.monthly[idx] * source.sign));
    });
    
    // 結果行
    const resultRow = document.createElement('tr');
    resultRow.classList.add('table-secondary');
    
    const resultNameCell = document.createElement('td');
    resultNameCell.textContent = rowTitle;
    resultNameCell.style.fontWeight = 'bold';
    resultRow.appendChild(resultNameCell);
    
    const resultTotalCell = document.createElement('td');
    resultTotalCell.textContent = formatCurrency(resultTotal);
    resultTotalCell.style.textAlign = 'right';
    resultTotalCell.style.fontWeight = 'bold';
    if (colorClass === 'blue') resultTotalCell.classList.add('text-primary');
    if (colorClass === 'red') resultTotalCell.classList.add('text-danger');
    if (colorClass === 'green') resultTotalCell.classList.add('text-success');
    resultRow.appendChild(resultTotalCell);
    
    // 月別の計算結果
    resultMonthly.forEach(monthAmount => {
        const monthCell = document.createElement('td');
        monthCell.textContent = formatCurrency(monthAmount);
        monthCell.style.textAlign = 'right';
        monthCell.style.fontWeight = 'bold';
        if (colorClass === 'blue') monthCell.classList.add('text-primary');
        if (colorClass === 'red') monthCell.classList.add('text-danger');
        if (colorClass === 'green') monthCell.classList.add('text-success');
        resultRow.appendChild(monthCell);
    });
    
    tableBody.appendChild(resultRow);
    
    // 計算結果をグローバル変数に保存
    window.plTotals[resultKey] = {
        total: resultTotal,
        monthly: resultMonthly
    };
}

// 法人税等の計算行を表示する関数
function renderPLTaxRow(tableBody, rowTitle, resultKey, sourceKey, taxRate, items, months, colorClass) {
    if (!window.plTotals) return;
    
    const source = window.plTotals[sourceKey] || { total: 0, monthly: months.map(() => 0) };
    
    // 計算
    const resultTotal = source.total * taxRate;
    const resultMonthly = source.monthly.map(val => val * taxRate);
    
    // 結果行
    const resultRow = document.createElement('tr');
    resultRow.classList.add('table-secondary');
    
    const resultNameCell = document.createElement('td');
    resultNameCell.textContent = rowTitle;
    resultNameCell.style.fontWeight = 'bold';
    resultRow.appendChild(resultNameCell);
    
    const resultTotalCell = document.createElement('td');
    resultTotalCell.textContent = formatCurrency(resultTotal);
    resultTotalCell.style.textAlign = 'right';
    resultTotalCell.style.fontWeight = 'bold';
    if (colorClass === 'blue') resultTotalCell.classList.add('text-primary');
    if (colorClass === 'red') resultTotalCell.classList.add('text-danger');
    if (colorClass === 'green') resultTotalCell.classList.add('text-success');
    resultRow.appendChild(resultTotalCell);
    
    // 月別の計算結果
    resultMonthly.forEach(monthAmount => {
        const monthCell = document.createElement('td');
        monthCell.textContent = formatCurrency(monthAmount);
        monthCell.style.textAlign = 'right';
        monthCell.style.fontWeight = 'bold';
        if (colorClass === 'blue') monthCell.classList.add('text-primary');
        if (colorClass === 'red') monthCell.classList.add('text-danger');
        if (colorClass === 'green') monthCell.classList.add('text-success');
        resultRow.appendChild(monthCell);
    });
    
    tableBody.appendChild(resultRow);
    
    // 計算結果をグローバル変数に保存
    window.plTotals[resultKey] = {
        total: resultTotal,
        monthly: resultMonthly
    };
}

// 通貨フォーマット関数
function formatCurrency(value) {
    return new Intl.NumberFormat('ja-JP').format(value);
}

// 現在の事業計画を取得する関数
function fetchCurrentPlan() {
    fetch('/business-plan/api/current-plan')
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                // 事業計画が存在する場合の処理
                document.getElementById('no-plan-message').classList.add('d-none');
                document.getElementById('plan-content').classList.remove('d-none');
                
                // 事業計画の基本情報を表示
                document.getElementById('business-year').textContent = data.year + '年度';
                document.getElementById('business-period').textContent = 
                    data.start_month + ' 〜 ' + data.end_month;
                
                // 事業計画項目のデータを取得して表示
                fetchPlanItems();
            } else {
                // 事業計画がない場合の処理
                document.getElementById('no-plan-message').classList.remove('d-none');
                document.getElementById('plan-content').classList.add('d-none');
            }
        })
        .catch(error => {
            console.error('事業計画データの取得に失敗しました:', error);
            // エラーメッセージを表示
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger';
            alertDiv.textContent = 'データの取得中にエラーが発生しました。ページを再読み込みしてください。';
            document.querySelector('.container').prepend(alertDiv);
        });
}

// ランダムな合計値を生成（サンプル用）
function getRandomTotal() {
    return Math.floor(Math.random() * 10000000) + 1000000;
}

// 売上・利益の合計を計算する関数
function calculateTotals(items) {
    if (!window.plTotals) return;
    
    // 売上と利益の合計を取得
    const totalRevenue = window.plTotals.revenue ? window.plTotals.revenue.total : 0;
    const netIncome = window.plTotals.net_income ? window.plTotals.net_income.total : 0;
    
    // ビジネスプラン概要の売上・利益を更新
    const revenueTotalElement = document.getElementById('revenue-total');
    const profitTotalElement = document.getElementById('profit-total');
    
    if (revenueTotalElement) {
        revenueTotalElement.textContent = formatCurrency(totalRevenue) + '円';
    }
    
    if (profitTotalElement) {
        const profitRatio = totalRevenue > 0 ? (netIncome / totalRevenue * 100) : 0;
        profitTotalElement.textContent = formatCurrency(netIncome) + '円 (' + profitRatio.toFixed(1) + '%)';
    }
}

// グラフの描画用関数
function renderCharts(months, items) {
    if (!window.plTotals) return;
    
    // 月表示を短縮形式に変換（YYYY-MM -> MM月）
    const displayMonths = months.map(month => month.split('-')[1] + '月');
    
    // 1. 収益指標グラフ（売上高と各利益の推移）
    renderRevenueChart(displayMonths);
    
    // 2. カテゴリー別売上比率グラフ
    renderCategoryChart();
    
    // 3. 利益率推移グラフ
    renderProfitRatioChart(displayMonths);
}

// 収益指標グラフの描画（売上高、営業利益、経常利益、当期純利益の推移）
function renderRevenueChart(months) {
    const revenueCanvas = document.getElementById('revenue-chart');
    if (!revenueCanvas) return;
    
    // 既存のチャートがあれば破棄
    if (window.revenueChart) {
        window.revenueChart.destroy();
    }
    
    // グラフデータの作成
    const data = {
        labels: months,
        datasets: [
            {
                label: '売上高',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 2,
                data: window.plTotals.revenue ? window.plTotals.revenue.monthly : [],
                tension: 0.1
            },
            {
                label: '営業利益',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 2,
                data: window.plTotals.operating_profit ? window.plTotals.operating_profit.monthly : [],
                tension: 0.1
            },
            {
                label: '経常利益',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgb(153, 102, 255)',
                borderWidth: 2,
                data: window.plTotals.ordinary_income ? window.plTotals.ordinary_income.monthly : [],
                tension: 0.1
            },
            {
                label: '当期純利益',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderColor: 'rgb(255, 159, 64)',
                borderWidth: 2,
                data: window.plTotals.net_income ? window.plTotals.net_income.monthly : [],
                tension: 0.1
            }
        ]
    };
    
    // グラフの設定
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '主要収益指標の推移'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.raw) + '円';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000000) {
                                return (value / 1000000).toFixed(0) + 'M';
                            } else if (value >= 1000) {
                                return (value / 1000).toFixed(0) + 'K';
                            }
                            return value;
                        }
                    }
                }
            }
        }
    };
    
    // グラフの描画
    window.revenueChart = new Chart(revenueCanvas, config);
}

// カテゴリー別売上比率グラフの描画
function renderCategoryChart() {
    const categoryCanvas = document.getElementById('category-chart');
    if (!categoryCanvas) return;
    
    // 既存のチャートがあれば破棄
    if (window.categoryChart) {
        window.categoryChart.destroy();
    }
    
    // ダミーデータを生成（実際にはAPIから取得したデータを使用）
    // この部分は実際のAPIデータ構造に合わせて修正が必要
    const revenueCategories = [
        { name: '事業1', value: getRandomTotal() * 0.4 },
        { name: '事業2', value: getRandomTotal() * 0.3 },
        { name: '事業3', value: getRandomTotal() * 0.2 },
        { name: 'その他', value: getRandomTotal() * 0.1 }
    ];
    
    // グラフデータの作成
    const data = {
        labels: revenueCategories.map(cat => cat.name),
        datasets: [{
            label: '売上比率',
            data: revenueCategories.map(cat => cat.value),
            backgroundColor: [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)'
            ],
            borderColor: [
                'rgb(255, 99, 132)',
                'rgb(54, 162, 235)',
                'rgb(255, 206, 86)',
                'rgb(75, 192, 192)',
                'rgb(153, 102, 255)'
            ],
            borderWidth: 1
        }]
    };
    
    // グラフの設定
    const config = {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '事業別売上比率'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return context.label + ': ' + formatCurrency(value) + '円 (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    };
    
    // グラフの描画
    window.categoryChart = new Chart(categoryCanvas, config);
}

// 利益率推移グラフの描画
function renderProfitRatioChart(months) {
    const profitRatioCanvas = document.getElementById('profit-ratio-chart');
    if (!profitRatioCanvas) return;
    
    // 既存のチャートがあれば破棄
    if (window.profitRatioChart) {
        window.profitRatioChart.destroy();
    }
    
    // 利益率データの計算
    const grossProfitRatio = [];
    const operatingProfitRatio = [];
    const netIncomeRatio = [];
    
    // 各月の利益率を計算
    for (let i = 0; i < months.length; i++) {
        const revenue = window.plTotals.revenue && window.plTotals.revenue.monthly[i] || 0;
        if (revenue > 0) {
            const grossProfit = window.plTotals.gross_profit && window.plTotals.gross_profit.monthly[i] || 0;
            const operatingProfit = window.plTotals.operating_profit && window.plTotals.operating_profit.monthly[i] || 0;
            const netIncome = window.plTotals.net_income && window.plTotals.net_income.monthly[i] || 0;
            
            grossProfitRatio.push((grossProfit / revenue) * 100);
            operatingProfitRatio.push((operatingProfit / revenue) * 100);
            netIncomeRatio.push((netIncome / revenue) * 100);
        } else {
            grossProfitRatio.push(0);
            operatingProfitRatio.push(0);
            netIncomeRatio.push(0);
        }
    }
    
    // グラフデータの作成
    const data = {
        labels: months,
        datasets: [
            {
                label: '売上総利益率',
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
                borderColor: 'rgb(255, 206, 86)',
                borderWidth: 2,
                data: grossProfitRatio,
                tension: 0.1
            },
            {
                label: '営業利益率',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 2,
                data: operatingProfitRatio,
                tension: 0.1
            },
            {
                label: '純利益率',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgb(153, 102, 255)',
                borderWidth: 2,
                data: netIncomeRatio,
                tension: 0.1
            }
        ]
    };
    
    // グラフの設定
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '利益率の推移'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toFixed(1) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    };
    
    // グラフの描画
    window.profitRatioChart = new Chart(profitRatioCanvas, config);
}

// サンプルの損益計算書テーブルを表示する関数
function renderSamplePLTable() {
    // サンプルの月データ（1月から12月）
    const sampleMonths = [];
    for (let i = 1; i <= 12; i++) {
        sampleMonths.push(`2023-${i.toString().padStart(2, '0')}`);
    }
    
    // 月別ヘッダーを生成
    generateMonthHeaders(sampleMonths);
    
    // サンプルデータでテーブルをレンダリング
    const tableBody = document.getElementById('planItemsBody');
    tableBody.innerHTML = '';
    
    // 損益計算書の項目と構造を定義
    const plStructure = [
        // 1. 売上高
        { type: 'parent', name: '売上高', colorClass: 'blue', children: [
            { name: '収益事業A', value: 5000000 },
            { name: '収益事業B', value: 3000000 },
            { name: '収益事業C', value: 2000000 }
        ]},
        
        // 2. 売上原価
        { type: 'parent', name: '売上原価', colorClass: 'red', children: [
            { name: '仕入費', value: 2500000 },
            { name: '外注費', value: 1500000 },
            { name: '材料費', value: 800000 }
        ]},
        
        // 3. 売上総利益（計算項目）
        { type: 'calculation', name: '売上総利益', colorClass: 'green' },
        
        // 4. 販売費及び一般管理費
        { type: 'parent', name: '販売費及び一般管理費', colorClass: 'red', children: [
            { name: '人件費', value: 3000000 },
            { name: '家賃', value: 600000 },
            { name: '広告宣伝費', value: 400000 },
            { name: '通信費', value: 200000 },
            { name: '消耗品費', value: 150000 },
            { name: '水道光熱費', value: 180000 },
            { name: '保険料', value: 120000 },
            { name: '交通費', value: 250000 },
            { name: '接待交際費', value: 300000 },
            { name: '減価償却費', value: 350000 },
            { name: 'その他経費', value: 500000 }
        ]},
        
        // 5. 営業利益（計算項目）
        { type: 'calculation', name: '営業利益', colorClass: 'green' },
        
        // 6. 営業外収益
        { type: 'parent', name: '営業外収益', colorClass: 'blue', children: [
            { name: '受取利息', value: 50000 },
            { name: '受取配当金', value: 30000 },
            { name: '助成金収入', value: 200000 }
        ]},
        
        // 7. 営業外費用
        { type: 'parent', name: '営業外費用', colorClass: 'red', children: [
            { name: '支払利息', value: 120000 },
            { name: '為替差損', value: 80000 }
        ]},
        
        // 8. 経常利益（計算項目）
        { type: 'calculation', name: '経常利益', colorClass: 'green' },
        
        // 9. 特別利益
        { type: 'parent', name: '特別利益', colorClass: 'blue', children: [
            { name: '固定資産売却益', value: 300000 }
        ]},
        
        // 10. 特別損失
        { type: 'parent', name: '特別損失', colorClass: 'red', children: [
            { name: '固定資産除却損', value: 150000 }
        ]},
        
        // 11. 税引前当期純利益（計算項目）
        { type: 'calculation', name: '税引前当期純利益', colorClass: 'green' },
        
        // 12. 法人税等
        { type: 'parent', name: '法人税等', colorClass: 'red', children: [
            { name: '法人税・住民税等', value: 800000 }
        ]},
        
        // 13. 当期純利益（計算項目）
        { type: 'calculation', name: '税引後当期純利益', colorClass: 'green' }
    ];
    
    // 累計計算用の変数
    let totalSales = 0;
    let totalCost = 0;
    let totalSGA = 0;
    let totalOperatingIncome = 0;
    let totalNonOperatingIncome = 0;
    let totalNonOperatingExpense = 0;
    let totalOrdinaryIncome = 0;
    let totalExtraordinaryIncome = 0;
    let totalExtraordinaryLoss = 0;
    let totalIncomeBeforeTax = 0;
    let totalTax = 0;
    let totalNetIncome = 0;
    
    // 項目ごとにレンダリング
    plStructure.forEach(item => {
        if (item.type === 'parent') {
            // 親項目の合計値を計算
            const totalValue = item.children.reduce((sum, child) => sum + child.value, 0);
            
            // 親項目行の作成
            const parentRow = document.createElement('tr');
            parentRow.classList.add('table-secondary');
            
            const parentNameCell = document.createElement('td');
            parentNameCell.textContent = item.name;
            parentNameCell.style.fontWeight = 'bold';
            parentRow.appendChild(parentNameCell);
            
            const parentTotalCell = document.createElement('td');
            parentTotalCell.textContent = formatCurrency(totalValue);
            parentTotalCell.style.textAlign = 'right';
            parentTotalCell.style.fontWeight = 'bold';
            if (item.colorClass === 'blue') parentTotalCell.classList.add('text-primary');
            if (item.colorClass === 'red') parentTotalCell.classList.add('text-danger');
            if (item.colorClass === 'green') parentTotalCell.classList.add('text-success');
            parentRow.appendChild(parentTotalCell);
            
            // 月別の金額（年間合計を12等分）
            for (let i = 0; i < 12; i++) {
                const monthValue = Math.round(totalValue / 12);
                const monthCell = document.createElement('td');
                monthCell.textContent = formatCurrency(monthValue);
                monthCell.style.textAlign = 'right';
                monthCell.style.fontWeight = 'bold';
                if (item.colorClass === 'blue') monthCell.classList.add('text-primary');
                if (item.colorClass === 'red') monthCell.classList.add('text-danger');
                if (item.colorClass === 'green') monthCell.classList.add('text-success');
                parentRow.appendChild(monthCell);
            }
            
            tableBody.appendChild(parentRow);
            
            // 累計値の更新
            if (item.name === '売上高') {
                totalSales = totalValue;
            } else if (item.name === '売上原価') {
                totalCost = totalValue;
            } else if (item.name === '販売費及び一般管理費') {
                totalSGA = totalValue;
            } else if (item.name === '営業外収益') {
                totalNonOperatingIncome = totalValue;
            } else if (item.name === '営業外費用') {
                totalNonOperatingExpense = totalValue;
            } else if (item.name === '特別利益') {
                totalExtraordinaryIncome = totalValue;
            } else if (item.name === '特別損失') {
                totalExtraordinaryLoss = totalValue;
            } else if (item.name === '法人税等') {
                totalTax = totalValue;
            }
            
            // 子項目行を作成
            item.children.forEach(child => {
                const childRow = document.createElement('tr');
                
                const childNameCell = document.createElement('td');
                childNameCell.textContent = '　' + child.name;
                childRow.appendChild(childNameCell);
                
                const childTotalCell = document.createElement('td');
                childTotalCell.textContent = formatCurrency(child.value);
                childTotalCell.style.textAlign = 'right';
                childRow.appendChild(childTotalCell);
                
                // 月別の金額（年間合計を12等分）
                for (let i = 0; i < 12; i++) {
                    const monthValue = Math.round(child.value / 12);
                    const monthCell = document.createElement('td');
                    monthCell.textContent = formatCurrency(monthValue);
                    monthCell.style.textAlign = 'right';
                    childRow.appendChild(monthCell);
                }
                
                tableBody.appendChild(childRow);
            });
        } else if (item.type === 'calculation') {
            // 計算項目の値を算出
            let calculatedValue = 0;
            
            if (item.name === '売上総利益') {
                calculatedValue = totalSales - totalCost;
            } else if (item.name === '営業利益') {
                totalOperatingIncome = totalSales - totalCost - totalSGA;
                calculatedValue = totalOperatingIncome;
            } else if (item.name === '経常利益') {
                totalOrdinaryIncome = totalOperatingIncome + totalNonOperatingIncome - totalNonOperatingExpense;
                calculatedValue = totalOrdinaryIncome;
            } else if (item.name === '税引前当期純利益') {
                totalIncomeBeforeTax = totalOrdinaryIncome + totalExtraordinaryIncome - totalExtraordinaryLoss;
                calculatedValue = totalIncomeBeforeTax;
            } else if (item.name === '税引後当期純利益') {
                totalNetIncome = totalIncomeBeforeTax - totalTax;
                calculatedValue = totalNetIncome;
            }
            
            // 計算結果行を作成
            const calcRow = document.createElement('tr');
            calcRow.classList.add('table-secondary');
            
            const calcNameCell = document.createElement('td');
            calcNameCell.textContent = item.name;
            calcNameCell.style.fontWeight = 'bold';
            calcRow.appendChild(calcNameCell);
            
            const calcTotalCell = document.createElement('td');
            calcTotalCell.textContent = formatCurrency(calculatedValue);
            calcTotalCell.style.textAlign = 'right';
            calcTotalCell.style.fontWeight = 'bold';
            calcTotalCell.classList.add('text-success');
            calcRow.appendChild(calcTotalCell);
            
            // 月別の金額（年間合計を12等分）
            for (let i = 0; i < 12; i++) {
                const monthValue = Math.round(calculatedValue / 12);
                const monthCell = document.createElement('td');
                monthCell.textContent = formatCurrency(monthValue);
                monthCell.style.textAlign = 'right';
                monthCell.style.fontWeight = 'bold';
                monthCell.classList.add('text-success');
                calcRow.appendChild(monthCell);
            }
            
            tableBody.appendChild(calcRow);
        }
    });
    
    // プランの概要表示を更新
    document.getElementById('business-year').textContent = '2023年度';
    document.getElementById('business-period').textContent = '2023-01 〜 2023-12';
    document.getElementById('revenue-total').textContent = formatCurrency(totalSales) + '円';
    document.getElementById('profit-total').textContent = formatCurrency(totalNetIncome) + '円 (' + 
        (totalSales > 0 ? (totalNetIncome / totalSales * 100).toFixed(1) : 0) + '%)';
    
    // サンプルグラフの描画
    renderSampleCharts(sampleMonths);
}

// サンプルグラフの描画
function renderSampleCharts(months) {
    // 月表示を短縮形式に変換（YYYY-MM -> MM月）
    const displayMonths = months.map(month => month.split('-')[1] + '月');
    
    // サンプルデータ
    const salesData = Array(12).fill(0).map(() => Math.floor(Math.random() * 500000) + 500000);
    const operatingIncomeData = salesData.map(sale => Math.floor(sale * 0.15));
    const ordinaryIncomeData = operatingIncomeData.map(income => Math.floor(income * 1.1));
    const netIncomeData = ordinaryIncomeData.map(income => Math.floor(income * 0.7));
    
    // 収益指標グラフ
    const revenueCanvas = document.getElementById('revenue-chart');
    if (revenueCanvas) {
        if (window.revenueChart) {
            window.revenueChart.destroy();
        }
        
        window.revenueChart = new Chart(revenueCanvas, {
            type: 'line',
            data: {
                labels: displayMonths,
                datasets: [
                    {
                        label: '売上高',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 2,
                        data: salesData,
                        tension: 0.1
                    },
                    {
                        label: '営業利益',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgb(75, 192, 192)',
                        borderWidth: 2,
                        data: operatingIncomeData,
                        tension: 0.1
                    },
                    {
                        label: '経常利益',
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderColor: 'rgb(153, 102, 255)',
                        borderWidth: 2,
                        data: ordinaryIncomeData,
                        tension: 0.1
                    },
                    {
                        label: '当期純利益',
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        borderColor: 'rgb(255, 159, 64)',
                        borderWidth: 2,
                        data: netIncomeData,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '主要収益指標の推移'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + formatCurrency(context.raw) + '円';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                if (value >= 1000000) {
                                    return (value / 1000000).toFixed(0) + 'M';
                                } else if (value >= 1000) {
                                    return (value / 1000).toFixed(0) + 'K';
                                }
                                return value;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // カテゴリグラフ
    const categoryCanvas = document.getElementById('category-chart');
    if (categoryCanvas) {
        if (window.categoryChart) {
            window.categoryChart.destroy();
        }
        
        window.categoryChart = new Chart(categoryCanvas, {
            type: 'doughnut',
            data: {
                labels: ['収益事業A', '収益事業B', '収益事業C'],
                datasets: [{
                    label: '売上比率',
                    data: [5000000, 3000000, 2000000],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)'
                    ],
                    borderColor: [
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 206, 86)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '事業別売上比率'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return context.label + ': ' + formatCurrency(value) + '円 (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // 利益率グラフ
    const profitRatioCanvas = document.getElementById('profit-ratio-chart');
    if (profitRatioCanvas) {
        if (window.profitRatioChart) {
            window.profitRatioChart.destroy();
        }
        
        // 利益率データの計算
        const grossProfitRatio = salesData.map(sale => 45 + Math.random() * 5);
        const operatingProfitRatio = salesData.map(sale => 15 + Math.random() * 3);
        const netIncomeRatio = salesData.map(sale => 8 + Math.random() * 2);
        
        window.profitRatioChart = new Chart(profitRatioCanvas, {
            type: 'line',
            data: {
                labels: displayMonths,
                datasets: [
                    {
                        label: '売上総利益率',
                        backgroundColor: 'rgba(255, 206, 86, 0.2)',
                        borderColor: 'rgb(255, 206, 86)',
                        borderWidth: 2,
                        data: grossProfitRatio,
                        tension: 0.1
                    },
                    {
                        label: '営業利益率',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgb(75, 192, 192)',
                        borderWidth: 2,
                        data: operatingProfitRatio,
                        tension: 0.1
                    },
                    {
                        label: '純利益率',
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderColor: 'rgb(153, 102, 255)',
                        borderWidth: 2,
                        data: netIncomeRatio,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '利益率の推移'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.raw.toFixed(1) + '%';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
} 