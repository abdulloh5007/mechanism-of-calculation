function toggleTheme() {
    document.body.classList.toggle('light');
}

function markDone() {
    const used = [];

    document.querySelectorAll("tbody tr").forEach((row) => {
        const index = parseInt(row.dataset.index);
        const count = parseInt(row.children[2].innerText);

        if (count > 0) {
            used.push({ index, count });
        }
    });

    fetch("/done", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ used }),
    })
        .then(res => res.json())
        .then(() => {
            alert("Товары обновлены!");
            document.querySelector("input[name='target']").value = '';
            document.querySelector("input[name='max_per_type']").value = '';
            document.getElementById("target-display").innerText = '';
        });
}

// 🎯 Форматирование чисел над полем input (не внутри него)
function updateFormattedDisplay(input, displayEl) {
    input.addEventListener("input", function () {
        const raw = input.value.replace(/\s/g, "");
        if (!raw || isNaN(raw)) {
            displayEl.innerText = '';
            return;
        }

        const number = parseFloat(raw);
        if (!isNaN(number)) {
            const formatted = number.toLocaleString("ru-RU");
            displayEl.innerText = formatted;
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const targetInput = document.querySelector("input[name='target']");
    const targetDisplay = document.getElementById("target-display");

    if (targetInput && targetDisplay) {
        updateFormattedDisplay(targetInput, targetDisplay);
        // при загрузке тоже обновить
        targetInput.dispatchEvent(new Event('input'));
    }
});
