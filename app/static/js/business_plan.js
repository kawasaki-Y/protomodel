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