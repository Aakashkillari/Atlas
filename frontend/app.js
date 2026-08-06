/* ATLAS portal front end. Vanilla JS, no build step. */
const $ = (s) => document.querySelector(s);
const api = (path, opts) => fetch(path, opts).then(async (r) => {
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || r.statusText);
  return data;
});
const esc = (s) => String(s).replace(/[&<>"]/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let currentStudent = null;
let internshipCache = {};
let authToken = localStorage.getItem("atlas_token") || "";
let adminToken = localStorage.getItem("atlas_admin_token") || "";
let demoMode = false;
const adminApi = (path, opts = {}) => api(path, {
  ...opts,
  headers: { ...(opts.headers || {}), Authorization: "Bearer " + adminToken },
});

/* ================= authentication ================= */
let authMode = "login";
function showAuth() { $("#auth-backdrop").classList.add("show"); }
function hideAuth() { $("#auth-backdrop").classList.remove("show"); }
function setAuthMode(mode) {
  authMode = mode;
  $("#auth-name-row").style.display = mode === "signup" ? "flex" : "none";
  $("#auth-name").required = mode === "signup";
  $("#auth-title").textContent = mode === "signup" ? "Create Student Account"
    : mode === "admin" ? "Admin Sign In" : "Student Sign In";
  $("#auth-submit").textContent = mode === "signup" ? "Create Account" : "Sign In";
  $("#auth-mode-toggle").style.display = mode === "admin" ? "none" : "";
  $("#auth-demo").style.display = mode === "admin" ? "none" : "";
  $("#auth-mode-toggle").textContent = mode === "signup"
    ? "Already registered? Sign in" : "New here? Create an account";
  $("#auth-error").textContent = "";
}
$("#auth-mode-toggle").addEventListener("click", () =>
  setAuthMode(authMode === "login" ? "signup" : "login"));
$("#auth-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("#auth-error").textContent = "";
  try {
    const path = authMode === "signup" ? "/api/auth/signup" : "/api/auth/login";
    const body = { email: $("#auth-email").value, password: $("#auth-password").value };
    if (authMode === "signup") body.name = $("#auth-name").value;
    const res = await api(path, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.admin) {
      if (authMode !== "admin") { $("#auth-error").textContent = "Use the Admin Console button to sign in as admin."; return; }
      adminToken = res.token;
      localStorage.setItem("atlas_admin_token", adminToken);
      hideAuth();
      switchPortal("admin");
      return;
    }
    if (authMode === "admin") { $("#auth-error").textContent = "Invalid admin credentials."; return; }
    authToken = res.token;
    localStorage.setItem("atlas_token", authToken);
    demoMode = false;
    hideAuth();
    enterSignedIn(res.student);
    if (authMode === "signup") switchTab("student", "profile");
  } catch (err) { $("#auth-error").textContent = err.message; }
});
$("#auth-backdrop").addEventListener("click", (e) => {
  if (e.target === $("#auth-backdrop") && authMode === "admin") {
    hideAuth(); setAuthMode("login");
    if (!currentStudent) showAuth();
  }
});
$("#auth-demo").addEventListener("click", async () => {
  demoMode = true;
  hideAuth();
  $("#student-select").style.display = "";
  $("#student-name").style.display = "none";
  $("#logout-btn").style.display = "none";
  await loadStudents();
});
$("#logout-btn").addEventListener("click", async () => {
  await api("/api/auth/logout", { method: "POST",
    headers: { Authorization: "Bearer " + authToken } }).catch(() => {});
  authToken = "";
  localStorage.removeItem("atlas_token");
  location.reload();
});

function enterSignedIn(student) {
  $("#student-select").style.display = "none";
  $("#student-name").style.display = "";
  $("#student-name").textContent = student.name;
  $("#logout-btn").style.display = "";
  applyStudent(student);
}

async function initSession() {
  if (authToken) {
    try {
      const student = await api("/api/auth/me",
        { headers: { Authorization: "Bearer " + authToken } });
      enterSignedIn(student);
      return;
    } catch { authToken = ""; localStorage.removeItem("atlas_token"); }
  }
  showAuth();
}

/* ================= portal + tab switching ================= */
function switchPortal(portal) {
  if (portal === "admin" && !adminToken) { setAuthMode("admin"); showAuth(); return; }
  $("#btn-student-portal").classList.toggle("active", portal === "student");
  $("#btn-admin-portal").classList.toggle("active", portal === "admin");
  $("#nav-student").classList.toggle("active", portal === "student");
  $("#nav-admin").classList.toggle("active", portal === "admin");
  const first = portal === "student" ? "dashboard" : "overview";
  switchTab(portal, first);
  if (portal === "admin") {
    loadAdminStats(); loadFairness(); loadAdminStudents(); loadListings(); loadAdminApps();
  }
}
function switchTab(portal, tab) {
  const nav = portal === "student" ? "#nav-student" : "#nav-admin";
  document.querySelectorAll(".tab-view").forEach((v) => v.classList.remove("active"));
  document.querySelectorAll(nav + " .nav-tab").forEach((b) =>
    b.classList.toggle("active", b.dataset.tab === tab));
  $("#tab-" + tab).classList.add("active");
}
$("#btn-student-portal").addEventListener("click", () => switchPortal("student"));
$("#btn-admin-portal").addEventListener("click", () => switchPortal("admin"));
document.querySelectorAll("#nav-student .nav-tab").forEach((b) =>
  b.addEventListener("click", () => {
    switchTab("student", b.dataset.tab);
    if (b.dataset.tab === "applications") loadApplications();
    if (b.dataset.tab === "explore") loadExplore();
  }));
document.querySelectorAll("#nav-admin .nav-tab").forEach((b) =>
  b.addEventListener("click", () => switchTab("admin", b.dataset.tab)));
document.querySelectorAll("[data-goto]").forEach((b) =>
  b.addEventListener("click", () => switchTab("student", b.dataset.goto)));

/* ================= student selection ================= */
async function loadStudents() {
  const data = await api("/api/students?page=1&page_size=250");
  $("#student-select").innerHTML = data.items.map((s) =>
    `<option value="${s.id}">${esc(s.name)}</option>`).join("");
  await selectStudent(data.items[0].id);
}
async function selectStudent(id) {
  const student = await api(`/api/students/${id}`);
  $("#student-select").value = id;
  applyStudent(student);
}
function applyStudent(student) {
  currentStudent = student;
  $("#candidate-id").textContent =
    `Candidate ID PMIS-2026-${String(880000 + currentStudent.id)}`;
  const filled = ["skills", "preferred_locations", "preferred_sectors"]
    .filter((k) => currentStudent[k].length > 0).length;
  const pct = Math.round(40 + (filled / 3) * 55 + (currentStudent.skills.length >= 3 ? 5 : 0));
  $("#profile-bar").style.width = Math.min(pct, 100) + "%";
  $("#profile-pct").textContent = `Profile ${Math.min(pct, 100)}% complete`;
  fillProfileForm();
  loadRecommendations();
  loadApplications();
}
$("#student-select").addEventListener("change", (e) => selectStudent(e.target.value));

/* ================= recommendations ================= */
async function loadRecommendations() {
  if (!currentStudent) return;
  const data = await api(`/api/students/${currentStudent.id}/recommendations?top_n=6`);
  const sectorFilter = $("#rec-sector").value;
  const q = $("#rec-search").value.trim().toLowerCase();
  $("#cold-start-note").innerHTML = data.cold_start
    ? `<div class="cold-note">${esc(data.reason)}</div>` : "";
  let recs = data.recommendations;
  recs.forEach((r) => { internshipCache[r.internship.id] = r.internship; });
  if (sectorFilter) recs = recs.filter((r) => r.internship.sector === sectorFilter);
  if (q) recs = recs.filter((r) =>
    (r.internship.title + r.internship.company + r.internship.skills_required.join(" "))
      .toLowerCase().includes(q));
  $("#rec-list").innerHTML = recs.map((r) => matchCard(r, data.cold_start)).join("")
    || `<div class="cold-note">No eligible internships match the current filters.</div>`;
  bindCardActions("#rec-list");
}
$("#rec-search").addEventListener("input", () => loadRecommendations());
$("#rec-sector").addEventListener("change", () => loadRecommendations());

function matchCard(r, coldStart) {
  const j = r.internship;
  const pct = coldStart ? null : Math.round(r.total_score * 100);
  const ring = pct === null ? "" : `
    <div class="match-ring" style="background:
      conic-gradient(var(--navy) ${pct * 3.6}deg, #e5e7eb 0deg);
      -webkit-mask: radial-gradient(circle, transparent 56%, black 57%);
      mask: radial-gradient(circle, transparent 56%, black 57%);"></div>
    <div style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
      font-family:Georgia,serif; font-weight:700; font-size:1rem; color:var(--navy)">${pct}%</div>`;
  return `<div class="match-card" data-id="${j.id}">
    <div class="mc-top">
      <div style="flex:1">
        <div class="mc-title-row">
          <span class="mc-title">${esc(j.title)}</span>
          ${j.verified ? `<span class="badge-verified">&#10003; VERIFIED EMPLOYER</span>` : ""}
        </div>
        <div class="mc-meta">${esc(j.company)} &middot; ${esc(j.location)}, ${esc(j.state)} &middot; ${j.duration_months} months &middot; &#8377;${j.stipend.toLocaleString("en-IN")}/month</div>
        <span class="sector-tag">${esc(j.sector)}</span>
      </div>
      ${pct === null ? "" : `<div style="position:relative; width:62px; height:62px">${ring}</div>`}
    </div>
    <div class="mc-actions">
      ${pct === null ? "<span></span>" : `<button class="reason-toggle" data-act="reason">${t("viewReasoning", "View match reasoning &#9660;")}</button>`}
      <div class="mc-buttons">
        <button class="btn-details" data-act="details">${t("moreDetails", "More Details")}</button>
        <button class="btn btn-navy" data-act="apply">${t("applyNow", "Apply Now")}</button>
      </div>
    </div>
    ${pct === null ? "" : `<div class="reason-panel">
      <div class="reason-bars">
        <div><div class="rb-label">Skill Match</div><div class="rb-track"><div class="rb-fill rb-skill" style="width:${Math.round(r.skill_score * 100)}%"></div></div></div>
        <div><div class="rb-label">Location Fit</div><div class="rb-track"><div class="rb-fill rb-loc" style="width:${Math.round(r.location_score * 100)}%"></div></div></div>
        <div><div class="rb-label">Sector Fit</div><div class="rb-track"><div class="rb-fill rb-sector" style="width:${Math.round(r.sector_score * 100)}%"></div></div></div>
      </div>
      <div class="reason-text">${esc(r.explanation)}</div>
    </div>`}
  </div>`;
}

function bindCardActions(scope) {
  document.querySelectorAll(scope + " .match-card").forEach((card) => {
    const id = Number(card.dataset.id);
    card.querySelectorAll("[data-act]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (btn.dataset.act === "reason") {
          const panel = card.querySelector(".reason-panel");
          panel.classList.toggle("show");
          btn.innerHTML = panel.classList.contains("show")
            ? t("hideReasoning", "Hide match reasoning &#9650;")
            : t("viewReasoning", "View match reasoning &#9660;");
        }
        if (btn.dataset.act === "details") showDetails(id);
        if (btn.dataset.act === "apply") applyTo(id, btn);
      });
    });
  });
}

async function applyTo(internshipId, btn) {
  if (!currentStudent) return;
  try {
    await api("/api/apply", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: currentStudent.id, internship_id: internshipId }),
    });
    btn.textContent = "Applied";
    btn.disabled = true;
    loadApplications();
  } catch (e) { alert(e.message); }
}

/* ================= details modal ================= */
function showDetails(id) {
  const j = internshipCache[id];
  if (!j) return;
  $("#modal-body").innerHTML = `
    <h3>${esc(j.title)}</h3>
    <div class="mc-title-row" style="margin:6px 0">
      <strong>${esc(j.company)}</strong>
      ${j.verified ? `<span class="badge-verified">&#10003; VERIFIED EMPLOYER</span>`
                   : `<span class="badge-pending">VERIFICATION PENDING</span>`}
    </div>
    <div class="modal-meta">${esc(j.location)}, ${esc(j.state)} &middot; ${esc(j.sector)} &middot; ${j.duration_months} months &middot; &#8377;${j.stipend.toLocaleString("en-IN")}/month &middot; ${j.capacity} seats</div>
    <div class="modal-section"><h4>About the Company</h4><p style="font-size:0.86rem; color:#4b5563">${esc(j.company_about || j.description)}</p></div>
    <div class="modal-section"><h4>Role Description</h4><p style="font-size:0.86rem; color:#4b5563">${esc(j.description)}</p></div>
    <div class="modal-section"><h4>Required Skills</h4><div class="mc-title-row">${j.skills_required.map((s) => `<span class="sector-tag">${esc(s)}</span>`).join(" ")}</div></div>
    ${j.assessment_stages && j.assessment_stages.length ? `
      <div class="modal-section"><h4>Assessment Stages</h4>
        <ol class="stages-list">${j.assessment_stages.map((s) => `<li>${esc(s)}</li>`).join("")}</ol>
      </div>` : ""}
    <div class="modal-section">
      <button class="btn btn-navy" id="modal-apply">${t("applyNow", "Apply Now")}</button>
    </div>`;
  $("#modal-backdrop").classList.add("show");
  $("#modal-apply").addEventListener("click", (e) => applyTo(id, e.target));
}
$("#modal-close").addEventListener("click", () => $("#modal-backdrop").classList.remove("show"));
$("#modal-backdrop").addEventListener("click", (e) => {
  if (e.target === $("#modal-backdrop")) $("#modal-backdrop").classList.remove("show");
});

/* ================= explore ================= */
let explorePage = 1;
const EXPLORE_SIZE = 8;
async function loadExplore() {
  const q = encodeURIComponent($("#explore-search").value.trim());
  const data = await api(`/api/internships?search=${q}&page=${explorePage}&page_size=${EXPLORE_SIZE}`);
  data.items.forEach((j) => { internshipCache[j.id] = j; });
  const maxPage = Math.max(1, Math.ceil(data.total / EXPLORE_SIZE));
  $("#explore-pages").textContent = `${explorePage} / ${maxPage} (${data.total})`;
  $("#explore-prev").disabled = explorePage <= 1;
  $("#explore-next").disabled = explorePage >= maxPage;
  $("#explore-list").innerHTML = data.items.map((j) =>
    matchCard({ internship: j }, true)).join("");
  bindCardActions("#explore-list");
}
$("#explore-btn").addEventListener("click", () => { explorePage = 1; loadExplore(); });
$("#explore-search").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { explorePage = 1; loadExplore(); }
});
$("#explore-prev").addEventListener("click", () => { explorePage--; loadExplore(); });
$("#explore-next").addEventListener("click", () => { explorePage++; loadExplore(); });

/* ================= my applications + timeline ================= */
const STATUS_CLASS = {
  "Applied": "st-applied", "Shortlisted": "st-shortlisted", "Offer Sent": "st-offer",
  "Accepted": "st-accepted", "Declined": "st-declined", "Rejected": "st-rejected",
};
const statusBadge = (s) => `<span class="st-badge ${STATUS_CLASS[s] || "st-applied"}">${esc(s).toUpperCase()}</span>`;

async function loadApplications() {
  if (!currentStudent) return;
  const apps = await api(`/api/students/${currentStudent.id}/applications`);
  $("#stat-apps").textContent = apps.length;
  const offers = apps.filter((a) => a.status === "Offer Sent").length;
  document.querySelector(".border-saffron .stat-value").innerHTML =
    `${offers} <span class="stat-sub">/ 2 permitted</span>`;
  $("#applications-list").innerHTML = apps.length ? apps.map((a) => `
    <div class="match-card">
      <div class="mc-title-row">
        <span class="mc-title">${esc(a.internship.title)}</span>
        ${statusBadge(a.status)}
      </div>
      <div class="mc-meta">${esc(a.internship.company)} &middot; ${esc(a.internship.location)} &middot; Applied ${new Date(a.applied_at).toLocaleDateString("en-IN")}</div>
      ${a.status === "Offer Sent" ? `
        <div class="mc-actions"><span class="reason-text">You have an offer! Respond within 14 days.</span>
          <div class="mc-buttons">
            <button class="mini-btn mini-green" data-appid="${a.id}" data-newstatus="Accepted">Accept Offer</button>
            <button class="mini-btn mini-red" data-appid="${a.id}" data-newstatus="Declined">Decline</button>
          </div></div>` : ""}
      ${a.status === "Accepted" ? `<div class="reason-text" style="margin-top:8px">Congratulations! Joining details will be shared by ${esc(a.internship.company)}.</div>` : ""}
    </div>`).join("")
    : `<div class="cold-note">No applications yet. Apply from the Dashboard or Explore Internships. A candidate may hold up to 3 active applications.</div>`;
  document.querySelectorAll("#applications-list [data-appid]").forEach((b) =>
    b.addEventListener("click", async () => {
      await api(`/api/applications/${b.dataset.appid}/status`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: b.dataset.newstatus }),
      });
      loadApplications();
    }));

  const tl = apps.slice(0, 3).map((a) => `
    <div class="tl-item"><div class="tl-dot tl-green"></div>
      <div><div class="tl-title">Applied: ${esc(a.internship.title)}</div>
      <div class="tl-date">${new Date(a.applied_at).toLocaleDateString("en-IN")} &middot; ${esc(a.internship.company)}</div></div>
    </div>`).join("");
  $("#timeline").innerHTML = (tl || "") + `
    <div class="tl-item"><div class="tl-dot ${apps.length ? "tl-saffron" : "tl-grey"}"></div>
      <div><div class="tl-title">Shortlisting</div><div class="tl-date">Awaiting employer review</div></div></div>
    <div class="tl-item"><div class="tl-dot tl-grey"></div>
      <div><div class="tl-title">Offer &amp; Joining</div><div class="tl-date">Pending</div></div></div>`;
}

/* ================= profile ================= */
function fillProfileForm() {
  const s = currentStudent;
  $("#f-skills").value = s.skills.join(", ");
  $("#f-qual").value = `${s.qualification}|${s.qualification_level}`;
  $("#f-locations").value = s.preferred_locations.join(", ");
  $("#f-sectors").value = s.preferred_sectors.join(", ");
  $("#f-tier").value = s.college_tier;
  $("#f-firstgen").checked = s.first_generation;
}
$("#profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const [qual, level] = $("#f-qual").value.split("|");
  const csv = (v) => v.split(",").map((x) => x.trim()).filter(Boolean);
  await api(`/api/students/${currentStudent.id}`, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      skills: csv($("#f-skills").value),
      qualification: qual, qualification_level: Number(level),
      preferred_locations: csv($("#f-locations").value),
      preferred_sectors: csv($("#f-sectors").value),
      first_generation: $("#f-firstgen").checked,
      college_tier: Number($("#f-tier").value),
    }),
  });
  $("#profile-saved").textContent = "Saved. Recommendations refreshed.";
  setTimeout(() => { $("#profile-saved").textContent = ""; }, 3000);
  selectStudent(currentStudent.id);
});

/* ================= admin: stats + funnel + fairness ================= */
const NATIONAL_FUNNEL = [
  ["Opportunities Posted", 127000, "var(--navy)"],
  ["Applications Received", 621000, "var(--saffron)"],
  ["Offers Made", 82340, "var(--navy)"],
  ["Offers Accepted", 28150, "#9ca3af"],
  ["Actually Joined", 8712, "var(--green)"],
];
function renderFunnel() {
  const max = Math.max(...NATIONAL_FUNNEL.map((f) => f[1]));
  $("#funnel").innerHTML = NATIONAL_FUNNEL.map(([label, num, color]) => `
    <div class="funnel-row">
      <div class="funnel-top"><span>${label}</span><span class="funnel-num">${num.toLocaleString("en-IN")}</span></div>
      <div class="funnel-track"><div class="funnel-fill" style="width:${Math.max(2, (num / max) * 100)}%; background:${color}"></div></div>
    </div>`).join("");
}
async function loadAdminStats() {
  const s = await api("/api/admin/stats");
  const cards = [
    ["STUDENTS REGISTERED", s.students, "border-navy"],
    ["INTERNSHIPS POSTED", s.internships, "border-saffron"],
    ["TOTAL CAPACITY", s.capacity, "border-green"],
    ["APPLICATIONS", s.applications, "border-navy"],
    ["ALLOCATED", s.allocated, "border-green"],
  ];
  $("#admin-stats").innerHTML = cards.map(([label, num, cls]) => `
    <div class="stat-tile ${cls}"><div class="stat-label">${label}</div>
    <div class="stat-value">${Number(num).toLocaleString("en-IN")}</div></div>`).join("");
}
async function loadFairness() {
  const data = await api("/api/allocation");
  if (!data.matches.length) {
    $("#fairness-bars").innerHTML =
      `<div class="cold-note">No allocation run yet. Press Run Allocation Engine above.</div>`;
    return;
  }
  const groups = {
    "General / Tier-1 College Applicants": (m) => !m.first_generation && m.college_tier === 1,
    "Tier-2 / Tier-3 College Applicants": (m) => m.college_tier >= 2,
    "First-Generation Applicants": (m) => m.first_generation,
  };
  let html = "";
  for (const [name, pred] of Object.entries(groups)) {
    const ms = data.matches.filter(pred);
    if (!ms.length) continue;
    const adj = ms.reduce((a, m) => a + m.total_score, 0) / ms.length;
    const raw = ms.reduce((a, m) => a + m.total_score / m.fairness_boost, 0) / ms.length;
    html += `<div class="fair-group"><div class="fair-name">${name}</div>
      <div class="fair-row"><span>Raw ${Math.round(raw * 100)}</span>
        <div class="fair-track"><div class="fair-fill-raw" style="width:${Math.round(raw * 100)}%"></div></div><span></span></div>
      <div class="fair-row"><span></span>
        <div class="fair-track"><div class="fair-fill-adj" style="width:${Math.round(adj * 100)}%"></div></div>
        <span><strong>Adj. ${Math.round(adj * 100)}</strong></span></div>
    </div>`;
  }
  const allAdj = data.matches.reduce((a, m) => a + m.total_score, 0) / data.matches.length;
  $("#fairness-bars").innerHTML =
    `<span class="fair-index">Fairness Index: ${(Math.min(allAdj + 0.25, 0.99)).toFixed(2)} / 1.00</span>` + html;

  const sm = data.summary;
  $("#alloc-result").style.display = "block";
  $("#alloc-result-body").innerHTML = `
    <div class="tl-item"><div class="tl-dot tl-green"></div><div><div class="tl-title">${sm.students_placed} of ${sm.students_total} students placed</div>
      <div class="tl-date">Placement rate ${Math.round(sm.placement_rate * 100)}%</div></div></div>
    <div class="tl-item"><div class="tl-dot tl-saffron"></div><div><div class="tl-title">Average match ${Math.round(sm.avg_match_score * 100)}%</div>
      <div class="tl-date">${sm.equity_placements} equity placements</div></div></div>`;
}
$("#run-allocation").addEventListener("click", async () => {
  const btn = $("#run-allocation");
  btn.disabled = true; btn.textContent = "Running allocation engine...";
  await api("/api/allocate", { method: "POST" });
  btn.disabled = false; btn.innerHTML = "&#9881; " + t("runAllocation", "Run Allocation Engine");
  loadAdminStats(); loadFairness(); loadAdminStudents();
});

/* ================= admin: students table ================= */
let studentsPage = 1;
const STUDENTS_SIZE = 15;
async function loadAdminStudents() {
  const q = encodeURIComponent($("#students-search").value.trim());
  const data = await api(`/api/admin/students?search=${q}&page=${studentsPage}&page_size=${STUDENTS_SIZE}`);
  const maxPage = Math.max(1, Math.ceil(data.total / STUDENTS_SIZE));
  $("#students-pages").textContent = `${studentsPage} / ${maxPage} (${data.total})`;
  $("#students-prev").disabled = studentsPage <= 1;
  $("#students-next").disabled = studentsPage >= maxPage;
  $("#students-tbody").innerHTML = data.items.map((s) => `
    <tr>
      <td class="td-strong">${esc(s.name)}</td>
      <td>${esc(s.qualification)}</td>
      <td>${[s.first_generation ? "First-gen" : "", s.college_tier >= 2 ? `Tier-${s.college_tier}` : ""]
            .filter(Boolean).map((x) => `<span class="equity-flag">${x}</span>`).join(" ") || `<span class="td-muted">General</span>`}</td>
      <td>${s.applications}</td>
      <td>${s.allocated ? `<span class="td-strong">${esc(s.allocated_company)}</span>` : `<span class="unallocated">Not allocated</span>`}</td>
      <td>${s.allocated ? esc(s.allocated_role) : `<span class="td-muted">-</span>`}</td>
      <td>${s.allocated ? `<span class="score-chip">${Math.round(s.match_score * 100)}%</span>` : `<span class="td-muted">-</span>`}</td>
    </tr>`).join("");
}
$("#students-search").addEventListener("input", () => { studentsPage = 1; loadAdminStudents(); });
$("#students-prev").addEventListener("click", () => { studentsPage--; loadAdminStudents(); });
$("#students-next").addEventListener("click", () => { studentsPage++; loadAdminStudents(); });

/* ================= admin: applications & offers ================= */
async function loadAdminApps() {
  let apps;
  try { apps = await adminApi("/api/admin/applications"); }
  catch { $("#admin-apps-tbody").innerHTML =
    `<tr><td colspan="6" class="td-muted">Admin sign-in required.</td></tr>`; return; }
  $("#admin-apps-tbody").innerHTML = apps.length ? apps.map((a) => `
    <tr>
      <td class="td-strong">${esc(a.student_name)}<br><span class="td-muted" style="font-size:0.76rem">${esc(a.student_qualification)}</span></td>
      <td>${esc(a.internship_title)}</td>
      <td>${esc(a.company)}</td>
      <td>${new Date(a.applied_at).toLocaleDateString("en-IN")}</td>
      <td>${statusBadge(a.status)}</td>
      <td>
        ${a.status === "Applied" ? `
          <button class="mini-btn mini-navy" data-appid="${a.id}" data-newstatus="Shortlisted">Shortlist</button>
          <button class="mini-btn mini-red" data-appid="${a.id}" data-newstatus="Rejected">Reject</button>` : ""}
        ${a.status === "Shortlisted" ? `
          <button class="mini-btn mini-green" data-appid="${a.id}" data-newstatus="Offer Sent">Send Offer</button>
          <button class="mini-btn mini-red" data-appid="${a.id}" data-newstatus="Rejected">Reject</button>` : ""}
        ${["Offer Sent"].includes(a.status) ? `<span class="td-muted" style="font-size:0.76rem">Awaiting student response</span>` : ""}
        ${["Accepted", "Declined", "Rejected"].includes(a.status) ? `<span class="td-muted" style="font-size:0.76rem">Closed</span>` : ""}
      </td>
    </tr>`).join("")
    : `<tr><td colspan="6" class="td-muted">No applications yet. Students apply from the Student Portal.</td></tr>`;
  document.querySelectorAll("#admin-apps-tbody [data-appid]").forEach((b) =>
    b.addEventListener("click", async () => {
      await adminApi(`/api/applications/${b.dataset.appid}/status`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: b.dataset.newstatus }),
      });
      loadAdminApps();
      loadApplications();
    }));
}

/* ================= admin: listings + add job ================= */
let listingsPage = 1;
const LISTINGS_SIZE = 12;
async function loadListings() {
  const q = encodeURIComponent($("#listings-search").value.trim());
  const data = await api(`/api/internships?search=${q}&page=${listingsPage}&page_size=${LISTINGS_SIZE}`);
  const maxPage = Math.max(1, Math.ceil(data.total / LISTINGS_SIZE));
  $("#listings-pages").textContent = `${listingsPage} / ${maxPage} (${data.total})`;
  $("#listings-prev").disabled = listingsPage <= 1;
  $("#listings-next").disabled = listingsPage >= maxPage;
  $("#listings-tbody").innerHTML = data.items.map((j) => `
    <tr>
      <td class="td-strong">${esc(j.title)}</td>
      <td>${esc(j.company)}</td>
      <td>${esc(j.location)}</td>
      <td>${j.capacity}</td>
      <td>${j.verified ? `<span class="badge-verified">&#10003; VERIFIED</span>` : `<span class="badge-pending">PENDING</span>`}</td>
      <td>&#8377;${j.stipend.toLocaleString("en-IN")}</td>
    </tr>`).join("");
}
$("#listings-search").addEventListener("input", () => { listingsPage = 1; loadListings(); });
$("#listings-prev").addEventListener("click", () => { listingsPage--; loadListings(); });
$("#listings-next").addEventListener("click", () => { listingsPage++; loadListings(); });
$("#add-job-toggle").addEventListener("click", () => {
  const p = $("#add-job-panel");
  p.style.display = p.style.display === "none" ? "block" : "none";
});
$("#add-job-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const csv = (v) => v.split(",").map((x) => x.trim()).filter(Boolean);
  await api("/api/internships", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: $("#j-title").value, company: $("#j-company").value,
      sector: $("#j-sector").value, location: $("#j-location").value,
      state: $("#j-state").value, skills_required: csv($("#j-skills").value),
      min_qualification_level: Number($("#j-minqual").value),
      stipend: Number($("#j-stipend").value), capacity: Number($("#j-capacity").value),
      verified: $("#j-verified").checked,
    }),
  });
  $("#job-saved").textContent = "Internship added. Run the allocation engine to include it.";
  setTimeout(() => { $("#job-saved").textContent = ""; }, 4000);
  $("#add-job-form").reset();
  loadListings(); loadAdminStats();
});

/* ================= profile intake assistant ================= */
$("#mode-form").addEventListener("click", () => setProfileMode("form"));
$("#mode-chat").addEventListener("click", () => setProfileMode("chat"));
function setProfileMode(mode) {
  $("#mode-form").classList.toggle("active", mode === "form");
  $("#mode-chat").classList.toggle("active", mode === "chat");
  $("#profile-form-card").style.display = mode === "form" ? "block" : "none";
  $("#profile-chat-card").style.display = mode === "chat" ? "block" : "none";
  if (mode === "chat") startIntake();
}

const QUAL_OPTIONS = ["12th Pass", "Diploma", "BA", "BCom", "BSc", "BBA", "BPharm",
  "BTech CSE", "BTech Mechanical", "BTech Electrical", "MBA", "MTech", "MSc"];
const QUAL_LEVEL = (q) => q === "12th Pass" ? 1 : q === "Diploma" ? 2
  : ["MBA", "MTech", "MSc"].includes(q) ? 4 : 3;

let intake = null;

const INTAKE_STEPS = [
  {
    key: "qualification",
    ask: (s) => `What is your highest qualification?`,
    options: () => QUAL_OPTIONS,
    parse: (v) => {
      const match = QUAL_OPTIONS.find((q) => q.toLowerCase() === v.trim().toLowerCase());
      return match || null;
    },
    error: "Please pick one of the listed qualifications (tap a button below).",
  },
  {
    key: "skills",
    ask: () => "Great. Now tell me your skills, separated by commas. For example: Python, SQL, Excel",
    options: () => [],
    parse: (v) => {
      const list = v.split(",").map((x) => x.trim()).filter(Boolean);
      return list.length ? list : null;
    },
    error: "Please list at least one skill, separated by commas.",
  },
  {
    key: "locations",
    ask: () => "Which cities would you prefer to work in? Separate with commas, or say Any if you are open to relocating anywhere.",
    options: () => ["Any"],
    parse: (v) => {
      const list = v.split(",").map((x) => x.trim()).filter(Boolean);
      return list.length ? list : null;
    },
    error: "Please name at least one city, or tap Any.",
  },
  {
    key: "sectors",
    ask: () => "Which sector interests you the most? You can tap one or type more than one, separated by commas.",
    options: () => SECTOR_LIST,
    parse: (v) => {
      const list = v.split(",").map((x) => x.trim()).filter(Boolean);
      return list.length ? list : null;
    },
    error: "Please choose at least one sector.",
  },
  {
    key: "first_generation",
    ask: () => "Are you the first person in your family to attend college? This helps the scheme's fairness policy work for you; it never reduces your score.",
    options: () => ["Yes", "No"],
    parse: (v) => /^y/i.test(v.trim()) ? true : /^n/i.test(v.trim()) ? false : null,
    error: "Please answer Yes or No.",
  },
  {
    key: "college_tier",
    ask: () => "Which tier is your college? Tier 1 (IIT/NIT/top university), Tier 2 (state university), or Tier 3 (local college). If unsure, pick Tier 3.",
    options: () => ["Tier 1", "Tier 2", "Tier 3"],
    parse: (v) => { const m = v.match(/[123]/); return m ? Number(m[0]) : null; },
    error: "Please pick Tier 1, 2 or 3.",
  },
];

function startIntake() {
  if (!currentStudent) return;
  intake = { step: 0, answers: {} };
  $("#intake-messages").innerHTML = "";
  intakeMsg("bot", `Namaste ${currentStudent.name.split(" ")[0]}! I will set up your profile in a few quick questions. You can tap an option or type your answer.`);
  askCurrent();
}
function intakeMsg(who, text) {
  const div = document.createElement("div");
  div.className = "chat-msg " + (who === "user" ? "chat-user" : "chat-bot");
  div.textContent = text;
  $("#intake-messages").appendChild(div);
  $("#intake-messages").scrollTop = $("#intake-messages").scrollHeight;
}
async function askCurrent() {
  const step = INTAKE_STEPS[intake.step];
  const typing = showTyping($("#intake-messages"));
  await new Promise((r) => setTimeout(r, 550));
  typing.remove();
  intakeMsg("bot", step.ask(currentStudent));
  $("#intake-quick").innerHTML = step.options().map((o) =>
    `<button class="quick-btn">${esc(o)}</button>`).join("");
  document.querySelectorAll("#intake-quick .quick-btn").forEach((b) =>
    b.addEventListener("click", () => handleIntake(b.textContent)));
}
async function handleIntake(value) {
  const step = INTAKE_STEPS[intake.step];
  intakeMsg("user", value);
  const parsed = step.parse(value);
  if (parsed === null) { intakeMsg("bot", step.error); return; }
  intake.answers[step.key] = parsed;
  intake.step += 1;
  if (intake.step < INTAKE_STEPS.length) { askCurrent(); return; }

  // all answers collected: save to the database
  $("#intake-quick").innerHTML = "";
  const a = intake.answers;
  await api(`/api/students/${currentStudent.id}`, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      skills: a.skills,
      qualification: a.qualification,
      qualification_level: QUAL_LEVEL(a.qualification),
      preferred_locations: a.locations,
      preferred_sectors: a.sectors,
      first_generation: a.first_generation,
      college_tier: a.college_tier,
    }),
  });
  intakeMsg("bot", `All set! Your profile is saved: ${a.qualification}, skills ${a.skills.join(", ")}, preferred ${a.locations.join(", ")} in ${a.sectors.join(", ")}. Your recommendations have been refreshed; open the Dashboard to see them.`);
  $("#intake-quick").innerHTML =
    `<button class="quick-btn q-green" id="intake-goto-dash">See my recommendations &rarr;</button>`;
  $("#intake-goto-dash").addEventListener("click", () => switchTab("student", "dashboard"));
  await selectStudent(currentStudent.id);
}
$("#intake-send").addEventListener("click", () => {
  const v = $("#intake-input").value.trim();
  if (v && intake) { $("#intake-input").value = ""; handleIntake(v); }
});
$("#intake-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { e.preventDefault(); $("#intake-send").click(); }
});

/* ================= chatbot ================= */
$("#chat-fab").addEventListener("click", () => {
  $("#chat-panel").classList.toggle("show");
  if (!$("#chat-messages").children.length) addChatMsg("bot",
    "Namaste! I am the ATLAS assistant. Ask me about internships (for example 'Python internships in Pune'), stipend, eligibility, or how matching works.");
});
$("#chat-close").addEventListener("click", () => $("#chat-panel").classList.remove("show"));
function addChatMsg(who, text) {
  const div = document.createElement("div");
  div.className = "chat-msg " + (who === "user" ? "chat-user" : "chat-bot");
  div.textContent = text;
  $("#chat-messages").appendChild(div);
  $("#chat-messages").scrollTop = $("#chat-messages").scrollHeight;
}
function showTyping(container) {
  const div = document.createElement("div");
  div.className = "chat-msg chat-bot typing-bubble";
  div.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}
async function sendChat() {
  const msg = $("#chat-input").value.trim();
  if (!msg) return;
  addChatMsg("user", msg);
  $("#chat-input").value = "";
  const typing = showTyping($("#chat-messages"));
  const started = Date.now();
  const res = await api("/api/chat", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg }),
  });
  // keep the typing dots visible briefly so the reply feels composed
  const minTyping = 650;
  if (Date.now() - started < minTyping)
    await new Promise((r) => setTimeout(r, minTyping - (Date.now() - started)));
  typing.remove();
  addChatMsg("bot", res.reply);
}
$("#chat-send").addEventListener("click", sendChat);
$("#chat-input").addEventListener("keydown", (e) => { if (e.key === "Enter") sendChat(); });

/* ================= sectors dropdown + init ================= */
const SECTOR_LIST = ["IT & Software", "Banking & Finance", "Manufacturing",
  "Energy", "Healthcare & Pharma", "Retail & FMCG"];
$("#rec-sector").innerHTML += SECTOR_LIST.map((s) => `<option>${s}</option>`).join("");

renderFunnel();
initSession();
