// Tab 切換事件
document.getElementById('dashboardTabs').addEventListener('show.bs.tab', function(e) {
    console.log('切換到：', e.target.getAttribute('id'));
});
