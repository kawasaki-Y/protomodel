/**
 * 資金繰り計画管理用JavaScript
 * 項目の追加、編集、削除および日別データの入力機能を提供
 */

// DOMが読み込まれたら実行
document.addEventListener('DOMContentLoaded', function() {
    // 各ボタンの参照を取得
    const saveChangesBtn = document.getElementById('saveChangesBtn');
    const addItemBtn = document.getElementById('addItemBtn');
    const syncWithPlanBtn = document.getElementById('syncWithPlanBtn');
    
    // 変更を保存ボタンのイベントリスナー
    if (saveChangesBtn) {
        saveChangesBtn.addEventListener('click', saveAllChanges);
    }
    
    // 項目追加ボタンのイベントリスナー
    if (addItemBtn) {
        addItemBtn.addEventListener('click', showAddItemModal);
    }
    
    // 事業計画と同期ボタンのイベントリスナー
    if (syncWithPlanBtn) {
        syncWithPlanBtn.addEventListener('click', syncWithBusinessPlan);
    }
    
    // 編集可能なセルにイベントリスナーを設定
    setupEditableCells();
    
    // 削除ボタンにイベントリスナーを設定
    setupDeleteButtons();
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
            const monthDay = this.dataset.monthDay;
            
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
            fetch(`/cash-flow/item/${itemId}`, {
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
    const itemsToUpdate = {};
    
    // 変更されたセルを項目ごとにグループ化
    editableCells.forEach(cell => {
        const itemId = cell.closest('tr').dataset.itemId;
        const monthDay = cell.dataset.monthDay;
        const newValue = cell.dataset.pendingValue;
        
        if (!itemsToUpdate[itemId]) {
            itemsToUpdate[itemId] = {};
        }
        
        // m1_d5, m1_d10 などの形式からm1とdayTypeを抽出
        const [month, dayType] = monthDay.split('_');
        
        if (!itemsToUpdate[itemId][month]) {
            itemsToUpdate[itemId][month] = {};
        }
        
        itemsToUpdate[itemId][month][dayType] = parseInt(newValue);
    });
    
    // 項目ごとにAPIを呼び出し
    for (const itemId in itemsToUpdate) {
        const updatePromise = fetch(`/cash-flow/item/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(itemsToUpdate[itemId])
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // この項目に関連する全ての保留データをクリア
                document.querySelectorAll(`tr[data-item-id="${itemId}"] .editable-cell[data-pending-value]`)
                    .forEach(cell => {
                        delete cell.dataset.pendingValue;
                    });
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
    }
    
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
                            <option value="営業収入">営業収入</option>
                            <option value="営業支出">営業支出</option>
                            <option value="投資収入">投資収入</option>
                            <option value="投資支出">投資支出</option>
                            <option value="財務収入">財務収入</option>
                            <option value="財務支出">財務支出</option>
                            <option value="現金残高">現金残高</option>
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
                    
                    <div>
                        <label for="related_plan_item_id" class="block text-sm font-medium text-gray-700">関連事業計画項目</label>
                        <select id="related_plan_item_id" name="related_plan_item_id" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                            <option value="">-- 関連なし --</option>
                            ${generateRelatedItemOptions()}
                        </select>
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
 * 関連事業計画項目のオプションを生成
 */
function generateRelatedItemOptions() {
    let options = '';
    const planItemsData = document.getElementById('plan_items_data');
    
    if (planItemsData) {
        try {
            const planItems = JSON.parse(planItemsData.dataset.items);
            
            planItems.forEach(item => {
                options += `<option value="${item.id}">${item.name}</option>`;
            });
        } catch (e) {
            console.error('事業計画項目データの解析エラー:', e);
        }
    }
    
    return options;
}

/**
 * 新規項目をAPIに送信して追加
 */
function addNewItem(form) {
    // 資金繰り計画IDを取得
    const cashFlowPlanId = document.getElementById('cash_flow_plan_id').value;
    
    // フォームデータを収集
    const formData = {
        cash_flow_plan_id: parseInt(cashFlowPlanId),
        parent_id: form.parentId.value ? parseInt(form.parentId.value) : null,
        related_plan_item_id: form.related_plan_item_id.value ? parseInt(form.related_plan_item_id.value) : null,
        category: form.category.value,
        item_type: form.item_type.value,
        name: form.name.value,
        description: form.description.value,
    };
    
    // APIを呼び出し
    fetch('/cash-flow/item', {
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

/**
 * 事業計画と同期
 */
function syncWithBusinessPlan() {
    // 資金繰り計画IDを取得
    const cashFlowPlanId = document.getElementById('cash_flow_plan_id').value;
    
    if (!confirm('事業計画からデータを同期しますか？既存の入力データが上書きされる可能性があります。')) {
        return;
    }
    
    // 同期APIを呼び出し
    fetch(`/cash-flow/sync-with-business-plan/${cashFlowPlanId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 成功時はページをリロード
            alert('事業計画と同期しました');
            location.reload();
        } else {
            alert('同期に失敗しました');
        }
    })
    .catch(error => {
        console.error('エラー:', error);
        alert('処理中にエラーが発生しました');
    });
} 