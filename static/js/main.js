document.addEventListener("DOMContentLoaded", () => {
  // Reload the mark page when the date changes
  const dateInput = document.querySelector("input[data-autosubmit]");
  if (dateInput) {
    dateInput.addEventListener("change", () => {
      if (dateInput.value) dateInput.form.submit();
    });
  }

  // "Set all to Present" shortcut
  const allPresent = document.getElementById("all-present");
  if (allPresent) {
    allPresent.addEventListener("click", () => {
      document
        .querySelectorAll('#mark-form input[type="radio"][value="Present"]')
        .forEach((radio) => (radio.checked = true));
    });
  }

  // Confirm before saving, because saved records are permanent
  const markForm = document.getElementById("mark-form");
  if (markForm && markForm.dataset.pending !== "0") {
    markForm.addEventListener("submit", (event) => {
      const chosen = markForm.querySelectorAll('input[type="radio"]:checked').length;
      if (chosen === 0) {
        event.preventDefault();
        alert("Pick Present or Absent for at least one student.");
        return;
      }
      const ok = confirm(
        `Save attendance for ${chosen} student(s)? Saved records can't be changed later.`
      );
      if (!ok) event.preventDefault();
    });
  }

  // Live filter for the daily log
  const search = document.getElementById("log-search");
  const rows = document.querySelectorAll("#log-table tbody tr");
  if (search) {
    search.addEventListener("input", () => {
      const q = search.value.trim().toLowerCase();
      rows.forEach((row) => {
        row.hidden = q !== "" && !row.textContent.toLowerCase().includes(q);
      });
    });
  }
});
