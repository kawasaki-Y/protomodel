// ログイン処理
document.addEventListener('DOMContentLoaded', function() {
    // ログインフォームの処理
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(loginForm);
            
            // デバッグ：送信するデータを確認
            console.log('送信データ:', Object.fromEntries(formData));
            
            fetch('/auth/login', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('ステータスコード:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('レスポンスデータ:', data);
                
                if (data.success) {
                    // 成功時はリダイレクト
                    console.log('ログイン成功、リダイレクト先:', data.redirect);
                    window.location.href = data.redirect || '/dashboard';
                } else {
                    // エラーメッセージを表示
                    const errorElement = document.getElementById('login-error');
                    if (errorElement) {
                        errorElement.textContent = data.message || 'ログインに失敗しました。';
                        errorElement.style.display = 'block';
                    } else {
                        console.error('エラー表示要素が見つかりません');
                        alert(data.message || 'ログインに失敗しました。');
                    }
                }
            })
            .catch(error => {
                console.error('ログインエラー:', error);
                alert('サーバーとの通信に失敗しました。もう一度お試しください。');
            });
        });
    } else {
        console.warn('ログインフォームが見つかりません');
    }
    
    // サインアップフォームの処理（新規追加）
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(signupForm);
            
            console.log('サインアップデータ送信:', Object.fromEntries(formData));
            
            fetch('/auth/signup', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('サインアップレスポンスステータス:', response.status);
                if (!response.ok) {
                    throw new Error('サーバーエラー: ' + response.status);
                }
                return response.json().catch(() => response.text());
            })
            .then(data => {
                console.log('サインアップレスポンス:', data);
                
                // JSONオブジェクトでない場合（HTML等を受け取った場合）
                if (typeof data === 'string') {
                    // リダイレクトが含まれているかチェック
                    if (data.includes('window.location.href') || data.includes('Redirecting')) {
                        window.location.href = '/dashboard';
                        return;
                    }
                }
                
                // JSONオブジェクトの場合
                if (data && data.success) {
                    window.location.href = data.redirect || '/dashboard';
                } else if (data && data.message) {
                    // エラーメッセージがある場合
                    showSignupError(data.message);
                } else {
                    // 成功だがJSONでない場合はダッシュボードに遷移
                    window.location.href = '/dashboard';
                }
            })
            .catch(error => {
                console.error('サインアップエラー:', error);
                showSignupError('登録処理中にエラーが発生しました。もう一度お試しください。');
            });
        });
    }
    
    // 新規登録フォームの処理
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(registerForm);
            
            // パスワード一致確認
            const password = formData.get('password');
            const confirmPassword = formData.get('confirm_password');
            
            if (password !== confirmPassword) {
                const errorElement = document.getElementById('register-error');
                if (errorElement) {
                    errorElement.textContent = 'パスワードが一致しません。';
                    errorElement.style.display = 'block';
                }
                return;
            }
            
            fetch('/auth/register', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 成功時はリダイレクト
                    window.location.href = data.redirect || '/dashboard';
                } else {
                    // エラーメッセージを表示
                    const errorElement = document.getElementById('register-error');
                    if (errorElement) {
                        errorElement.textContent = data.message || '登録に失敗しました。';
                        errorElement.style.display = 'block';
                    }
                    // 詳細なエラー情報をコンソールに出力（デバッグ用）
                    if (data.details) {
                        console.error('登録エラー詳細:', data.details);
                    }
                }
            })
            .catch(error => {
                console.error('登録エラー:', error);
                const errorElement = document.getElementById('register-error');
                if (errorElement) {
                    errorElement.textContent = 'サーバーとの通信に失敗しました。';
                    errorElement.style.display = 'block';
                }
            });
        });
    }
    
    // サインアップエラー表示ヘルパー関数
    function showSignupError(message) {
        const errorElement = document.getElementById('signup-error');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        } else {
            alert(message);
        }
    }
}); 