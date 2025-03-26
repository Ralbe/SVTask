function showTab(tabId) {
    // Скрыть все вкладки
    document.getElementById('applicant-tab').style.display = 'none';
    document.getElementById('employer-tab').style.display = 'none';

    // Показать выбранную вкладку
    document.getElementById(tabId + '-tab').style.display = 'block';

    // Обновить стиль кнопок
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`.tab-button[onclick="showTab('${tabId}')"]`).classList.add('active');
}

// По умолчанию показываем вкладку "Соискатель"
document.addEventListener('DOMContentLoaded', () => {
    showTab('applicant');
});
