/* ATLAS dashboard — vanilla JS, no build step */
const $ = (sel) => document.querySelector(sel);
const api = (path, opts) => fetch(path, opts).then((r) => r.json());

/* ---------- tabs ---------- */
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    tab.classList.add("active");
    $("#view-" + tab.dataset.view).classList.add("active");
    if (tab.dataset.view === "admin") loadAllocation();
  });
});

/* ---------- internship browsing ---------- */
let page = 1;
let lastTotal = 0;
const PAGE_SIZE = 6;

async function loadInternships() {
  const q = encodeURIComponent($("#search-box").value.trim());
  const data = await api(`/api/internships?search=${q}&page=${page}&page_size=${PAGE_SIZE}`);
  lastTotal = data.total;
  const maxPage = Math.max(1, Math.ceil(data.total / PAGE_SIZE));
  $("#page-info").textContent = `Page ${page} of ${maxPage} (${data.total} internships)`;
  $("#prev-page").disabled = page <= 1;
  $("#next-page").disabled = page >= maxPage;
  $("#internship-list").innerHTML = data.items.map(jobCard).join("") ||
    `<p class="hint">No internships match that search.</p>`;
}

function jobCard(j) {
  return `<div class="job-card">
    <h3>${j.title}</h3>
    <div class="company">${j.company}
      ${j.verified ? '<span class="badge badge-verified">&#10004; Verified Employer</span>' : ""}
    </div>
    <div class="meta">&#128205; ${j.location}, ${j.state} &middot; ${j.duration_months} months &middot; &#8377;${j.stipend.toLocaleString("en-IN")}/mo &middot; ${j.capacity} seats</div>
    <span class="badge badge-sector">${j.sector}</span>
    <div class="skill-tags">${j.skills_required.map((s) => `<span class="skill-tag">${s}</span>`).join("")}</div>
  </div>`;
}

$("#search-btn").addEventListener("click", () => { page = 1; loadInternships(); });
$("#search-box").addEventListener("keydown", (e) => { if (e.key === "Enter") { page = 1; loadInternships(); } });
$("#prev-page").addEventListener("click", () => { if (page > 1) { page--; loadInternships(); } });
$("#next-page").addEventListener("click", () => { page++; loadInternships(); });

/* ---------- student recommendations ---------- */
async function loadStudentDropdown() {
  const data = await api("/api/students?page=1&page_size=250");
  $("#student-select").innerHTML = data.items
    .map((s) => `<option value="${s.id}">#${s.id} — ${s.name} (${s.qualification}${s.skills.length < 2 ? ", thin profile" : ""})</option>`)
    .join("");
}

$("#recommend-btn").addEventListener("click", async () => {
  const id = $("#student-select").value;
  const student = await api(`/api/students/${id}`);
  const chip = $("#student-profile");
  chip.classList.add("show");
  chip.innerHTML = `<strong>${student.name}</strong> &middot; ${student.qualification}
    &middot; Skills: ${student.skills.join(", ") || "<em>none listed</em>"}
    &middot; Prefers: ${student.preferred_locations.join(", ")} / ${student.preferred_sectors.join(", ")}
    ${student.first_generation ? ' &middot; <span class="equity-dot">First-generation</span>' : ""}
    &middot; Tier-${student.college_tier} college`;

  const data = await api(`/api/students/${id}/recommendations`);
  let html = "";
  if (data.cold_start) {
    html += `<div class="cold-note">&#9432; Cold-start fallback: ${data.reason}</div>`;
    html += data.recommendations.map((r) => jobCard(r.internship)).join("");
  } else {
    html = data.recommendations.map(recCard).join("");
  }
  $("#recommendations").innerHTML = html || `<p class="hint">No eligible internships found.</p>`;
});

function bar(label, cls, value) {
  return `<span>${label}</span>
    <div class="bar-track"><div class="bar-fill ${cls}" style="width:${Math.round(value * 100)}%"></div></div>
    <span>${Math.round(value * 100)}%</span>`;
}

function recCard(r) {
  const j = r.internship;
  return `<div class="rec-card">
    <div class="rec-head">
      <div>
        <h3>${j.title} &middot; ${j.company}
          ${j.verified ? '<span class="badge badge-verified">&#10004; Verified</span>' : ""}</h3>
        <div class="meta">&#128205; ${j.location} &middot; ${j.sector}</div>
      </div>
      <span class="score-pill">${Math.round(r.total_score * 100)}% match</span>
    </div>
    <div class="score-bars">
      ${bar("Skills", "bar-skill", r.skill_score)}
      ${bar("Location", "bar-loc", r.location_score)}
      ${bar("Sector", "bar-sector", r.sector_score)}
    </div>
    <div class="explanation">&#128161; ${r.explanation}</div>
  </div>`;
}

/* ---------- admin allocation ---------- */
$("#allocate-btn").addEventListener("click", async () => {
  const btn = $("#allocate-btn");
  btn.disabled = true;
  btn.textContent = "Running Hungarian allocation…";
  const data = await api("/api/allocate", { method: "POST" });
  renderAllocation(data);
  btn.disabled = false;
  btn.innerHTML = "&#9881; Run Smart Allocation";
});

async function loadAllocation() {
  renderAllocation(await api("/api/allocation"));
}

function renderAllocation(data) {
  const s = data.summary;
  if (!s) {
    $("#summary-cards").innerHTML =
      `<p class="hint">No allocation run yet — click "Run Smart Allocation".</p>`;
    $("#allocation-table tbody").innerHTML = "";
    return;
  }
  $("#summary-cards").innerHTML = `
    <div class="stat-card stat-navy"><div class="num">${s.students_total}</div><div class="label">Total Students</div></div>
    <div class="stat-card stat-green"><div class="num">${s.students_placed}</div><div class="label">Placed</div></div>
    <div class="stat-card stat-saffron"><div class="num">${Math.round(s.placement_rate * 100)}%</div><div class="label">Placement Rate</div></div>
    <div class="stat-card stat-white"><div class="num">${Math.round(s.avg_match_score * 100)}%</div><div class="label">Avg Match Score</div></div>
    <div class="stat-card stat-navy"><div class="num">${s.equity_placements}</div><div class="label">Equity Placements</div></div>`;

  $("#allocation-table tbody").innerHTML = data.matches.map((m, i) => `
    <tr data-idx="${i}">
      <td>${m.student_name}${m.first_generation ? ' <span class="equity-dot" title="First-generation">&#9679;</span>' : ""}</td>
      <td>${m.internship_title}</td>
      <td>${m.company}${m.verified ? " &#10004;" : ""}</td>
      <td>${m.location}</td>
      <td>${Math.round(m.skill_score * 100)}%</td>
      <td>${Math.round(m.location_score * 100)}%</td>
      <td>${Math.round(m.sector_score * 100)}%</td>
      <td>${m.fairness_boost > 1 ? "+" + Math.round((m.fairness_boost - 1) * 100) + "%" : "—"}</td>
      <td class="total-cell">${Math.round(m.total_score * 100)}%</td>
    </tr>`).join("");

  document.querySelectorAll("#allocation-table tbody tr").forEach((tr) => {
    tr.addEventListener("click", () => {
      document.querySelectorAll("#allocation-table tbody tr").forEach((r) => r.classList.remove("selected"));
      tr.classList.add("selected");
      const m = data.matches[Number(tr.dataset.idx)];
      const box = $("#match-detail");
      box.classList.add("show");
      box.innerHTML = `<h3>${m.student_name} &rarr; ${m.internship_title} @ ${m.company}</h3>
        <div class="explanation">&#128161; ${m.explanation}</div>`;
    });
  });
}

/* ---------- init ---------- */
loadInternships();
loadStudentDropdown();
