function editCustomer(customerId) {
    const row = document.getElementById(`customer-row-${customerId}`);
    const nameSpan = row.querySelector('.customer-name');
    const nameInput = row.querySelector('.customer-edit-input');
    const editBtn = row.querySelector('.edit-btn');
    const saveBtn = row.querySelector('.save-btn');

    nameSpan.classList.add('hidden');
    nameInput.classList.remove('hidden');
    editBtn.classList.add('hidden');
    saveBtn.classList.remove('hidden');
}

async function saveCustomer(customerId) {
    const row = document.getElementById(`customer-row-${customerId}`);
    const nameInput = row.querySelector('.customer-edit-input');
    const newName = nameInput.value.trim();

    if (!newName) {
        alert('顧客名を入力してください。');
        return;
    }

    try {
        const response = await fetch(`/api/customer/${customerId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: newName })
        });

        if (response.ok) {
            const nameSpan = row.querySelector('.customer-name');
            const editBtn = row.querySelector('.edit-btn');
            const saveBtn = row.querySelector('.save-btn');

            nameSpan.textContent = newName;
            nameSpan.classList.remove('hidden');
            nameInput.classList.add('hidden');
            editBtn.classList.remove('hidden');
            saveBtn.classList.add('hidden');
        } else {
            alert('顧客名の更新に失敗しました。');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('顧客名の更新中にエラーが発生しました。');
    }
}

async function deleteCustomer(customerId) {
    if (!confirm('この顧客を削除してもよろしいですか？')) {
        return;
    }

    try {
        const response = await fetch(`/api/customer/${customerId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const row = document.getElementById(`customer-row-${customerId}`);
            row.remove();
        } else {
            alert('顧客の削除に失敗しました。');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('顧客の削除中にエラーが発生しました。');
    }
} 