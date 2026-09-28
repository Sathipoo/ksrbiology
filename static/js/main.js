// KSR Biology Portal Interactive Logic

document.addEventListener("DOMContentLoaded", () => {
  // 1. Client-Side Instant Filtering on Homepage
  const searchInput = document.getElementById("search-materials");
  const gradePills = document.querySelectorAll(".grade-pill");
  const categoryPills = document.querySelectorAll(".category-pill");
  const materialCards = document.querySelectorAll(".material-card");
  const emptyState = document.getElementById("empty-state");
  const resultsCount = document.getElementById("results-count");

  let currentGrade = "All";
  let currentCategory = "All";
  let currentSearch = "";

  function filterMaterials() {
    let visibleCount = 0;

    materialCards.forEach((card) => {
      const cardGrade = card.getAttribute("data-grade") || "";
      const cardCategory = card.getAttribute("data-category") || "";
      const cardText = (card.textContent || "").toLowerCase();

      const matchesGrade = (currentGrade === "All" || cardGrade === currentGrade);
      const matchesCategory = (currentCategory === "All" || cardCategory === currentCategory);
      const matchesSearch = (!currentSearch || cardText.includes(currentSearch));

      if (matchesGrade && matchesCategory && matchesSearch) {
        card.style.display = "flex";
        visibleCount++;
      } else {
        card.style.display = "none";
      }
    });

    if (resultsCount) {
      resultsCount.textContent = `${visibleCount} Material${visibleCount === 1 ? '' : 's'}`;
    }

    if (emptyState) {
      emptyState.style.display = (visibleCount === 0) ? "block" : "none";
    }
  }

  // Grade filter click
  gradePills.forEach((pill) => {
    pill.addEventListener("click", () => {
      gradePills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      currentGrade = pill.getAttribute("data-value") || "All";
      filterMaterials();
    });
  });

  // Category filter click
  categoryPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      categoryPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      currentCategory = pill.getAttribute("data-value") || "All";
      filterMaterials();
    });
  });

  // Realtime search input
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      currentSearch = e.target.value.trim().toLowerCase();
      filterMaterials();
    });
  }

  // 2. Auto-dismiss Flash alerts after 5 seconds
  setTimeout(() => {
    document.querySelectorAll(".flash-alert").forEach((alert) => {
      alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      alert.style.opacity = "0";
      alert.style.transform = "translateY(-10px)";
      setTimeout(() => alert.remove(), 500);
    });
  }, 5000);

  // 3. File Dropzone drag-and-drop enhancements
  const fileDropzones = document.querySelectorAll(".file-dropzone");
  fileDropzones.forEach((dropzone) => {
    const input = dropzone.querySelector("input[type='file']");
    const label = dropzone.querySelector(".file-name-label");

    if (input) {
      input.addEventListener("change", () => {
        if (input.files.length > 0) {
          if (label) {
            label.textContent = `Selected: ${input.files[0].name} (${(input.files[0].size / (1024 * 1024)).toFixed(2)} MB)`;
            label.style.color = "#047857";
            label.style.fontWeight = "bold";
          }
        }
      });
    }
  });
});

// Modal Helpers
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("active");
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("active");
  }
}

// Edit Material Modal Population Helper
function openEditModal(id, title, grade, chapter, category, description, isPinned) {
  const form = document.getElementById("edit-material-form");
  if (form) {
    form.action = `/admin/material/${id}/edit`;
    document.getElementById("edit-title").value = title;
    document.getElementById("edit-grade").value = grade;
    document.getElementById("edit-chapter").value = chapter;
    document.getElementById("edit-category").value = category;
    document.getElementById("edit-description").value = description;
    document.getElementById("edit-pinned").checked = (isPinned === "True" || isPinned === true);
    openModal("editModal");
  }
}
