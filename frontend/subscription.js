const API_BASE = "http://localhost:8000/admin/requests";

async function loadSubscriptions() {
  try {
    const res = await fetch(API_BASE + "/");
    if (!res.ok) {
      throw new Error(`Ошибка запроса: ${res.status}`);
    }

    const data = await res.json();

    const tbody = document.querySelector("#subsTable tbody");
    tbody.innerHTML = "";

    const approved = data.filter(item => item.status === "Одобрена");

    if (approved.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7">Активных подписок нет</td></tr>`;
      return;
    }

    approved.forEach(item => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${item.id}</td>
        <td>${item.user_id}</td>
        <td>${item.tariff_code}</td>
        <td>${item.duration_months} мес.</td>
        <td>${item.status}</td>
        <td>${new Date(item.created_at).toLocaleDateString()}</td>
        <td>${new Date(item.created_at).toLocaleDateString()}</td>
      `;

      tbody.appendChild(row);
    });

  } catch (err) {
    console.error("Ошибка при загрузке подписок:", err);
    const tbody = document.querySelector("#subsTable tbody");
    tbody.innerHTML = `<tr><td colspan="7">Ошибка при загрузке подписок</td></tr>`;
  }
}

// Загружаем подписки при открытии страницы
loadSubscriptions();
