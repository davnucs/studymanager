function showAddBoardPopup() {
  document.getElementById("addBoardPopup").style.display = "flex";
}

function closePopup() {
  document.getElementById("addBoardPopup").style.display = "none";
}

function showEditCardForm(cardId) {
  const card = document.getElementById(`card-${cardId}`);
  card.querySelector(".card-display").style.display = "none";
  card.querySelector(".edit-card-form").style.display = "flex";
}

function hideEditCardForm(cardId) {
  const card = document.getElementById(`card-${cardId}`);
  card.querySelector(".edit-card-form").style.display = "none";
  card.querySelector(".card-display").style.display = "block";
}

fetch("/reminders_data")
  .then((res) => res.json())
  .then((data) => {
    const container = document.getElementById("reminderContent");
    if (data.reminders.length === 0) {
      container.innerHTML = "<p>No upcoming reminders.</p>";
    } else {
      container.innerHTML = "";
      data.reminders.forEach((reminder) => {
        const card = document.createElement("div");
        card.className = "reminder-card";
        card.innerHTML = `
          <div class="reminder-title">${reminder.board_name}</div>
          <div class="reminder-desc">${reminder.title}</div>
          <div class="reminder-due">Due: ${reminder.due_date}</div>
        `;
        container.appendChild(card);
      });
    }
  })
  .catch(() => {
    document.getElementById("reminderContent").innerHTML =
      "<p>Error loading reminders.</p>";
  });
