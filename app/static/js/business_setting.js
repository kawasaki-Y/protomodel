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