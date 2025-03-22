// 収益計画関連の JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('business.js loaded');
    
    // サイドバーメニューの展開状態を確認する
    const planningMenuItem = document.querySelector('.sidebar-dropdown-toggle');
    const planningSubMenu = document.querySelector('.sidebar-dropdown-menu');
    const revenuePlanMenuItem = document.querySelector('.sidebar-submenu-toggle');
    const revenuePlanSubMenu = document.querySelector('.sidebar-submenu');
    
    // メニュー展開を確認するデバッグ用コード
    console.log('計画作成メニュー:', planningMenuItem);
    console.log('計画作成サブメニュー:', planningSubMenu);
    console.log('収益計画を作成メニュー:', revenuePlanMenuItem);
    console.log('収益計画サブメニュー:', revenuePlanSubMenu);
    
    // URLパスからアクティブなメニューを特定
    const currentPath = window.location.pathname;
    
    // 収益計画関連ページの場合はメニューを自動的に展開
    if (currentPath.includes('/business-setting') || 
        currentPath.includes('/service-setting') || 
        currentPath.includes('/customer-setting') || 
        currentPath.includes('/revenue-plan')) {
        
        // 計画作成メニューを展開
        if (planningSubMenu) {
            planningSubMenu.classList.remove('hidden');
        }
        
        // 収益計画サブメニューを展開
        if (revenuePlanSubMenu) {
            revenuePlanSubMenu.classList.remove('hidden');
        }
        
        console.log('収益計画関連ページを検出、メニューを展開しました');
    }
}); 