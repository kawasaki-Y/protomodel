// 共通のJavaScript機能
document.addEventListener('DOMContentLoaded', function() {
    console.log('main.js loaded successfully');
    
    // サイドバーメニューの状態がURLに基づいて自動的に展開されるようにする
    function setupSidebar() {
        // 現在のパスを取得
        const currentPath = window.location.pathname;
        
        // 収益計画関連ページかどうか確認
        const isRevenuePage = [
            '/business-setting',
            '/service-setting',
            '/customer-setting',
            '/revenue-plan'
        ].some(path => currentPath.includes(path));
        
        // 収益計画関連ページの場合、関連するメニューを開く
        if (isRevenuePage) {
            // 計画作成メニューを展開
            const planningMenu = document.querySelector('[data-submenu="planning"]');
            if (planningMenu) {
                planningMenu.classList.add('active');
                const planningSubmenu = document.getElementById('planning-submenu');
                if (planningSubmenu) {
                    planningSubmenu.classList.remove('hidden');
                    planningSubmenu.classList.add('active');
                }
            }
            
            // 収益計画サブメニューを展開
            const revenueMenu = document.querySelector('[data-submenu="revenue"]');
            if (revenueMenu) {
                revenueMenu.classList.add('active');
                const revenueSubmenu = document.getElementById('revenue-submenu');
                if (revenueSubmenu) {
                    revenueSubmenu.classList.remove('hidden');
                    revenueSubmenu.classList.add('active');
                }
            }
        }
    }
    
    // サイドバーメニューの展開設定を実行
    setupSidebar();
    
    // サイドバーのドロップダウン機能
    const menuLinks = document.querySelectorAll('.has-submenu');
    if (menuLinks && menuLinks.length > 0) {
        menuLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                // サブメニューのID取得
                const submenuId = this.getAttribute('data-submenu') + '-submenu';
                const submenu = document.getElementById(submenuId);
                
                // 開閉状態の切り替え
                if (submenu) {
                    submenu.classList.toggle('hidden');
                    submenu.classList.toggle('active');
                    this.classList.toggle('active');
                }
            });
        });
    }
    
    // フラッシュメッセージの自動非表示
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages && flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.style.display = 'none';
                }, 300);
            }, 5000);
        });
    }

    // サイドバーのドロップダウントグル
    const toggleButtons = document.querySelectorAll('.sidebar-dropdown-toggle');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dropdownMenu = this.nextElementSibling;
            dropdownMenu.classList.toggle('hidden');
        });
    });

    // サブメニューのドロップダウントグル
    const subToggleButtons = document.querySelectorAll('.sidebar-submenu-toggle');
    subToggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const submenu = this.nextElementSibling;
            submenu.classList.toggle('hidden');
        });
    });
}); 