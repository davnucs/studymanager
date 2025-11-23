function showAddBoardPopup() {
  document.getElementById("addBoardPopup").style.display = "flex";
}

function closePopup() {
  document.getElementById("addBoardPopup").style.display = "none";
}

<script>
  document.getElementById('reminderLink').addEventListener('click', function() {
    const popup = document.getElementById('reminderPopup');
    popup.style.display = 'flex';

    // Fetch reminders dynamically
    fetch('/reminders_data')  // You'll create this route in backend
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('reminderContent');
        if (data.reminders.length === 0) {
          container.innerHTML = '<p>No upcoming reminders.</p>';
        } else {
          container.innerHTML = '';
          data.reminders.forEach(reminder => {
            container.innerHTML += `
              <div class="reminder-item">
                <strong>${reminder.board_name}</strong> - ${reminder.title} (Due: ${reminder.due_date})
              </div>
            `;
          });
        }
      }).catch(() => {
        document.getElementById('reminderContent').innerHTML = '<p>Error loading reminders.</p>';
      });
  });

  function closeReminderPopup(event) {
    if (!event || event.target.id === 'reminderPopup') {
      document.getElementById('reminderPopup').style.display = 'none';
    }
  }
</script>
