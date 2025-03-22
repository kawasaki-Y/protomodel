// 事業設定ページのJavaScript
document.addEventListener('DOMContentLoaded', function() {
    // 事業一覧の取得と表示
    function loadBusinesses() {
        fetch('/api/business/businesses')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayBusinesses(data.businesses);
                } else {
                    console.error('事業データの取得に失敗しました:', data.message);
                }
            })
            .catch(error => {
                console.error('APIリクエストエラー:', error);
            });
    }
    
    // 事業一覧の表示
    function displayBusinesses(businesses) {
        const businessList = document.getElementById('business-list');
        if (!businessList) return;
        
        if (businesses.length === 0) {
            businessList.innerHTML = '<p class="text-gray-500">登録された事業がありません。</p>';
            return;
        }
        
        const listItems = businesses.map(business => {
            return `
                <div class="bg-gray-50 p-4 rounded border border-gray-200">
                    <h4 class="font-bold">${business.name}</h4>
                    <p class="text-sm text-gray-600">${business.description || '説明なし'}</p>
                </div>
            `;
        });
        
        businessList.innerHTML = listItems.join('');
    }
    
    // 事業登録フォームのハンドリング
    const businessForm = document.getElementById('business-form');
    if (businessForm) {
        businessForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(businessForm);
            
            fetch('/api/business/businesses', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    businessForm.reset();
                    loadBusinesses();  // 事業一覧を再読込
                } else {
                    alert(data.message || '事業の登録に失敗しました');
                }
            })
            .catch(error => {
                console.error('APIリクエストエラー:', error);
                alert('サーバーとの通信に失敗しました');
            });
        });
    }
    
    // 初期表示時に事業一覧を読み込む
    loadBusinesses();
});

function editBusiness(businessId) {
    const row = document.getElementById(`business-row-${businessId}`);
    const nameSpan = row.querySelector('.business-name');
    const nameInput = row.querySelector('.business-edit-input');
    const editBtn = row.querySelector('.edit-btn');
    const saveBtn = row.querySelector('.save-btn');

    nameSpan.classList.add('hidden');
    nameInput.classList.remove('hidden');
    editBtn.classList.add('hidden');
    saveBtn.classList.remove('hidden');
}

async function saveBusiness(businessId) {
    const row = document.getElementById(`business-row-${businessId}`);
    const nameInput = row.querySelector('.business-edit-input');
    const newName = nameInput.value.trim();

    if (!newName) {
        alert('事業名を入力してください。');
        return;
    }

    try {
        const response = await fetch(`/api/business/${businessId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: newName })
        });

        if (response.ok) {
            const nameSpan = row.querySelector('.business-name');
            const editBtn = row.querySelector('.edit-btn');
            const saveBtn = row.querySelector('.save-btn');

            nameSpan.textContent = newName;
            nameSpan.classList.remove('hidden');
            nameInput.classList.add('hidden');
            editBtn.classList.remove('hidden');
            saveBtn.classList.add('hidden');
        } else {
            alert('事業名の更新に失敗しました。');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('事業名の更新中にエラーが発生しました。');
    }
}

async function deleteBusiness(businessId) {
    if (!confirm('この事業を削除してもよろしいですか？')) {
        return;
    }

    try {
        const response = await fetch(`/api/business/${businessId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const row = document.getElementById(`business-row-${businessId}`);
            row.remove();
        } else {
            alert('事業の削除に失敗しました。');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('事業の削除中にエラーが発生しました。');
    }
} 