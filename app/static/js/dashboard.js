/**
 * ダッシュボード用JavaScript
 * グラフとデータの表示機能を提供
 */

// DOMが読み込まれたら実行
document.addEventListener('DOMContentLoaded', function() {
    console.log('dashboard.js loaded');
    
    // 日付と時刻の更新
    function updateDateTime() {
        const now = new Date();
        const dateOptions = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
        const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
        
        document.getElementById('current-date').textContent = now.toLocaleDateString('ja-JP', dateOptions);
        document.getElementById('current-time').textContent = now.toLocaleTimeString('ja-JP', timeOptions);
    }
    
    // 励ましのメッセージ
    const encouragementMessages = [
        "今日も一日頑張りましょう！",
        "小さな進歩も大切な一歩です",
        "チームで協力して目標達成を目指しましょう",
        "困難は成長の機会です",
        "計画を立てて着実に前進しましょう",
        "今月の目標達成まであと少しです！",
        "新しいアイデアが会社を成長させます",
        "今日の努力が明日の成果につながります"
    ];
    
    function setRandomEncouragement() {
        const randomIndex = Math.floor(Math.random() * encouragementMessages.length);
        document.getElementById('encouragement-message').textContent = encouragementMessages[randomIndex];
    }
    
    // 初期更新と定期更新の設定
    updateDateTime();
    setRandomEncouragement();
    setInterval(updateDateTime, 1000);
    setInterval(setRandomEncouragement, 3600000); // 1時間ごとに更新

    // グラフデータを取得して描画
    loadAndRenderCharts();
    
    // PDF出力ボタンのイベントリスナー
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', exportPdf);
    }
    
    // PPT出力ボタンのイベントリスナー
    const exportPptBtn = document.getElementById('exportPptBtn');
    if (exportPptBtn) {
        exportPptBtn.addEventListener('click', exportPpt);
    }
    
    // サイドバーメニューの状態を初期化
    initializeSidebar();
});

/**
 * グラフデータを取得して描画
 */
function loadAndRenderCharts() {
    fetch('/api/dashboard/chart-data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('APIエラー:', data.error);
                return;
            }
            
            // 月次推移グラフの描画
            renderMonthlyChart(data);
            
            // 指標カードの更新 (実績がある場合)
            updateMetricCards(data);
        })
        .catch(error => {
            console.error('データ取得エラー:', error);
        });
}

/**
 * 月次推移グラフを描画
 */
function renderMonthlyChart(data) {
    const ctx = document.getElementById('revenueChart').getContext('2d');
    
    // グラフが既に存在する場合は破棄
    if (window.revenueChart) {
        window.revenueChart.destroy();
    }
    
    // Chart.jsでグラフ作成
    window.revenueChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '売上・利益・資金残高の推移',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 15,
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    padding: 10,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('ja-JP', { 
                                    style: 'currency', 
                                    currency: 'JPY' 
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '月',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10
                        }
                    },
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '金額（円）',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        padding: {
                            bottom: 10
                        }
                    },
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('ja-JP', { 
                                style: 'currency', 
                                currency: 'JPY',
                                notation: 'compact',
                                compactDisplay: 'short'
                            }).format(value);
                        }
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.3 // 線を少し滑らかに
                },
                point: {
                    radius: 4,
                    hoverRadius: 6
                }
            }
        }
    });
}

/**
 * 指標カードの更新
 */
function updateMetricCards(data) {
    // データセットから合計値を計算
    if (data.datasets && data.datasets.length > 0) {
        // 売上高
        const salesData = data.datasets.find(d => d.label === '売上');
        if (salesData && salesData.data) {
            const totalSales = salesData.data.reduce((sum, val) => sum + val, 0);
            updateMetricCard('salesCard', totalSales);
        }
        
        // 営業利益
        const profitData = data.datasets.find(d => d.label === '利益');
        if (profitData && profitData.data) {
            const totalProfit = profitData.data.reduce((sum, val) => sum + val, 0);
            updateMetricCard('profitCard', totalProfit);
        }
        
        // 資金残高（最終月の値）
        const cashData = data.datasets.find(d => d.label === '資金残高');
        if (cashData && cashData.data && cashData.data.length > 0) {
            const endCash = cashData.data[cashData.data.length - 1];
            updateMetricCard('cashCard', endCash);
        }
    }
}

/**
 * 指標カードの内容を更新
 */
function updateMetricCard(cardId, value) {
    const card = document.getElementById(cardId);
    if (!card) return;
    
    const valueElement = card.querySelector('.metric-value');
    if (valueElement) {
        valueElement.textContent = new Intl.NumberFormat('ja-JP', { 
            style: 'currency', 
            currency: 'JPY' 
        }).format(value);
    }
}

/**
 * PDFファイルのエクスポート
 */
function exportPdf() {
    // 対象の事業計画IDを取得（現在表示中のID、または最新のもの）
    const planId = document.getElementById('current_plan_id')?.value || null;
    
    // API呼び出し
    fetch('/api/export/pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            plan_id: planId,
            include_cash_flow: true
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('PDF生成に失敗しました');
        }
    })
    .then(blob => {
        // ダウンロードリンクを生成
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '事業計画_レポート.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('エラー:', error);
        alert('PDF出力中にエラーが発生しました');
    });
}

/**
 * PowerPointファイルのエクスポート
 */
function exportPpt() {
    // 対象の事業計画IDを取得（現在表示中のID、または最新のもの）
    const planId = document.getElementById('current_plan_id')?.value || null;
    
    // API呼び出し
    fetch('/api/export/ppt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            plan_id: planId,
            include_chart: true
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('PowerPoint生成に失敗しました');
        }
    })
    .then(blob => {
        // ダウンロードリンクを生成
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '事業計画_プレゼン.pptx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('エラー:', error);
        alert('PowerPoint出力中にエラーが発生しました');
    });
}

// サイドバーメニューの状態を初期化
function initializeSidebar() {
    // サイドバーメニューのトグル
    document.querySelectorAll('.sidebar-dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const menu = this.nextElementSibling;
            if (menu) {
                menu.classList.toggle('hidden');
            }
        });
    });
    
    // サブメニューのトグル
    document.querySelectorAll('.sidebar-submenu-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const submenu = this.nextElementSibling;
            if (submenu) {
                submenu.classList.toggle('hidden');
            }
        });
    });
} 