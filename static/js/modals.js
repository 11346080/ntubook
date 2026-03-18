// 確認刪除
function confirmDelete() {
    console.log('書籍已下架');
    alert('書籍已成功下架！');
    // 這裡可以連接後端 API
    const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
    deleteModal.hide();
}

// 移除收藏
function removeFavorite() {
    console.log('已從收藏移除');
    alert('已從收藏移除！');
    // 這裡可以連接後端 API
    const favModal = bootstrap.Modal.getInstance(document.getElementById('removeFromFavoritesModal'));
    favModal.hide();
}

// 預約表單提交
document.addEventListener('DOMContentLoaded', function() {
    const reserveForm = document.getElementById('reserveForm');
    if (reserveForm) {
        reserveForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('預約請求已送出');
            alert('預約請求已成功送出！賣家會盡快與你聯絡。');
            const reserveModal = bootstrap.Modal.getInstance(document.getElementById('reserveModal'));
            reserveModal.hide();
        });
    }

    // 檢舉表單提交
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('檢舉已提交');
            alert('感謝你的檢舉！我們會認真審視相關內容。');
            const reportModal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
            reportModal.hide();
        });
    }

    // 拒絕預約表單提交
    const rejectForm = document.getElementById('rejectForm');
    if (rejectForm) {
        rejectForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('預約已拒絕');
            alert('已拒絕預約請求！');
            const rejectModal = bootstrap.Modal.getInstance(document.getElementById('rejectModal'));
            rejectModal.hide();
        });
    }
});
