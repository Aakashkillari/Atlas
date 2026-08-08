/* ATLAS portal front end: student, company, and admin roles. */
const $ = (s) => document.querySelector(s);
const api = (path, opts = {}) => {
  const headers = { ...(opts.headers || {}) };
  if (authToken) headers.Authorization = "Bearer " + authToken;
  return fetch(path, { ...opts, headers }).then(async (r) => {
    const data = await r.json().catch(() => ({}));
    if (!r.ok) {
      const err = new Error(typeof data.detail === "string" ? data.detail : r.statusText);
      err.status = r.status;
      throw err;
    }
    return data;
  });
};
const esc = (s) => String(s).replace(/[&<>"]/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// which portal this URL is for: /student, /company, /admin
const PATH_ROLE = ["student", "company", "admin"].includes(location.pathname.replace(/\//g, ""))
  ? location.pathname.replace(/\//g, "") : "student";
// one persistent session PER PORTAL, so student/company/admin can all stay
// signed in at the same time (three tabs work independently)
const TOKEN_KEY = "atlas_token_" + PATH_ROLE;
let authToken = localStorage.getItem(TOKEN_KEY) || "";
let currentRole = null;      // 'student' | 'company' | 'admin'
let currentStudent = null;
let currentCompany = null;
let internshipCache = {};

/* ================= navigation ================= */
const STUDENT_TABS = ["dashboard", "profile", "explore", "applications",
  "messages", "documents", "skills", "help", "coming"];
const COMPANY_TABS = ["c-dash", "c-post", "c-applicants", "messages"];
const ADMIN_TABS = ["overview", "admin-students", "admin-companies",
  "admin-apps", "listings", "admin-complaints"];

function switchTab(tab) {
  document.querySelectorAll(".tab-view").forEach((v) => v.classList.remove("active"));
  document.querySelectorAll(".nav-tab").forEach((b) =>
    b.classList.toggle("active", b.dataset.tab === tab));
  const view = $("#tab-" + tab);
  if (!view) return;
  view.classList.add("active");
  if (ADMIN_TABS.includes(tab)) view.prepend($("#nav-admin"));
  // per-tab loaders
  if (tab === "explore") loadExplore();
  if (tab === "applications") loadApplications();
  if (tab === "messages") loadMessages(true);
  if (tab === "documents") loadDocuments();
  if (tab === "skills") loadSkillAnalytics();
  if (tab === "help") renderFaq();
  if (tab === "c-dash") loadCompanyDash();
  if (tab === "c-applicants") loadCompanyApplicants();
  if (tab === "live") { loadInsights(); loadLivePmis(); }
  if (tab === "overview") { loadAdminStats(); loadFairness(); }
  if (tab === "admin-students") loadAdminStudents();
  if (tab === "admin-companies") loadAdminCompanies();
  if (tab === "admin-apps") loadAdminApps();
  if (tab === "listings") loadListings();
  if (tab === "admin-complaints") loadAdminComplaints();
}
document.querySelectorAll(".nav-tab").forEach((b) =>
  b.addEventListener("click", () => switchTab(b.dataset.tab)));
document.querySelectorAll("[data-goto]").forEach((b) =>
  b.addEventListener("click", () => switchTab(b.dataset.goto)));

function showPortal(role) {
  currentRole = role;
  $("#nav-student").style.display = role === "student" ? "" : "none";
  $("#nav-company").style.display = role === "company" ? "" : "none";
  $("#user-role-label").textContent =
    role === "admin" ? "Administrator" : role === "company" ? "Company" : "Student";
  if (role === "student") switchTab("dashboard");
  if (role === "company") switchTab("c-dash");
  if (role === "admin") { $("#nav-student").style.display = "none"; switchTab("overview"); }
}

/* ================= auth ================= */
let authMode = "login";      // 'login' | 'signup'
let authRole = PATH_ROLE === "company" ? "company" : "student";

function showAuth() { $("#auth-backdrop").classList.add("show"); }
function hideAuth() { $("#auth-backdrop").classList.remove("show"); }

function renderAuth() {
  const signupStudent = authMode === "signup" && authRole === "student";
  $("#auth-mobile-row").style.display = signupStudent ? "flex" : "none";
  $("#auth-mobile").required = signupStudent;
  if (PATH_ROLE === "admin") {
    // admin URL: fixed-credential sign-in only
    $("#auth-role-student").parentElement.style.display = "none";
    $("#auth-mode-toggle").style.display = "none";
    $("#auth-name-row").style.display = "none";
    $("#auth-company-row").style.display = "none";
    $("#auth-sector-row").style.display = "none";
    $("#auth-title").textContent = "Administrator Sign In";
    $("#auth-submit").textContent = "Sign In";
    $("#auth-error").textContent = "";
    return;
  }
  const signup = authMode === "signup";
  $("#auth-name-row").style.display = signup && authRole === "student" ? "flex" : "none";
  $("#auth-company-row").style.display = signup && authRole === "company" ? "flex" : "none";
  $("#auth-sector-row").style.display = signup && authRole === "company" ? "flex" : "none";
  $("#auth-name").required = signup && authRole === "student";
  $("#auth-company").required = signup && authRole === "company";
  $("#auth-title").textContent =
    (authRole === "company" ? "Company " : "Student ") + (signup ? "Registration" : "Sign In");
  $("#auth-submit").textContent = signup ? "Create Account" : "Sign In";
  $("#auth-mode-toggle").textContent = signup
    ? "Already registered? Sign in" : "New here? Create an account";
  $("#auth-role-student").classList.toggle("active", authRole === "student");
  $("#auth-role-company").classList.toggle("active", authRole === "company");
  $("#auth-error").textContent = "";
}
$("#auth-role-student").addEventListener("click", () => { authRole = "student"; renderAuth(); });
$("#auth-role-company").addEventListener("click", () => { authRole = "company"; renderAuth(); });
$("#auth-mode-toggle").addEventListener("click", () => {
  authMode = authMode === "login" ? "signup" : "login"; renderAuth();
});

$("#auth-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("#auth-error").textContent = "";
  try {
    let res;
    if (authMode === "signup" && authRole === "company") {
      res = await api("/api/auth/company/signup", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: $("#auth-company").value, sector: $("#auth-sector").value,
          email: $("#auth-email").value, password: $("#auth-password").value }),
      });
    } else if (authMode === "signup") {
      res = await api("/api/auth/signup", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: $("#auth-name").value,
          email: $("#auth-email").value, password: $("#auth-password").value,
          mobile: $("#auth-mobile").value }),
      });
    } else {
      res = await api("/api/auth/login", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: $("#auth-email").value,
          password: $("#auth-password").value }),
      });
    }
    // store the session under the portal that matches its role
    localStorage.setItem("atlas_token_" + res.role, res.token);
    if (res.role !== PATH_ROLE) {
      // signed in as a different role than this URL: go to the right portal
      // (already signed in there; no second login needed)
      location.href = "/" + res.role;
      return;
    }
    authToken = res.token;
    hideAuth();
    enterSession(res);
    if (authMode === "signup" && res.role === "student") switchTab("profile");
  } catch (err) { $("#auth-error").textContent = err.message; }
});

$("#logout-btn").addEventListener("click", async () => {
  await api("/api/auth/logout", { method: "POST" }).catch(() => {});
  authToken = "";
  localStorage.removeItem(TOKEN_KEY);
  location.reload();
});

function enterSession(p) {
  currentStudent = p.student || null;
  currentCompany = p.company || null;
  const name = p.role === "admin" ? "Administrator"
    : p.role === "company" ? currentCompany.name : currentStudent.name;
  $("#student-name").textContent = name;
  $("#avatar-circle").textContent = name[0].toUpperCase();
  $("#logout-btn").style.display = "";
  showPortal(p.role);
  if (p.role === "student") applyStudent(currentStudent);
  if (p.role === "company") $("#c-hero-name").textContent = currentCompany.name;
  loadMessages(false);
  setInterval(() => loadMessages(false), 30000);
}

async function initSession() {
  // migrate a session stored under the old single-token key
  const legacy = localStorage.getItem("atlas_token");
  if (!authToken && legacy) { authToken = legacy; localStorage.removeItem("atlas_token"); }
  // retry on server hiccups (cold starts, restarts); only a real 401 signs out
  for (let attempt = 0; authToken; attempt++) {
    try {
      const p = await api("/api/auth/me");
      if (p.role !== PATH_ROLE) {
        // this session belongs to another portal: move it there and stay signed in
        localStorage.setItem("atlas_token_" + p.role, authToken);
        localStorage.removeItem(TOKEN_KEY);
        location.href = "/" + p.role;
        return;
      }
      localStorage.setItem(TOKEN_KEY, authToken);
      enterSession(p);
      return;
    } catch (err) {
      if (err.status === 401) {
        authToken = "";
        localStorage.removeItem(TOKEN_KEY);
        break;
      }
      if (attempt >= 15) break;  // ~45s: give up but KEEP the token for next visit
      $("#student-name").textContent = "Reconnecting...";
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
  renderAuth();
  showAuth();
}
$("#btn-admin-portal").addEventListener("click", () => {
  if (currentRole === "admin") { switchTab("overview"); return; }
  location.href = "/admin";
});
$("#btn-student-portal").addEventListener("click", () => {});

/* ================= student dashboard ================= */
function applyStudent(student) {
  currentStudent = student;
  const first = student.name.split(" ")[0];
  $("#hero-name").textContent = first;
  $("#candidate-id").textContent =
    `Candidate ID PMIS-2026-${String(880000 + student.id)}`;
  const filled = ["skills", "preferred_locations", "preferred_sectors"]
    .filter((k) => student[k].length > 0).length;
  const pct = Math.min(Math.round(40 + (filled / 3) * 55 +
    (student.skills.length >= 3 ? 5 : 0)), 100);
  $("#profile-bar").style.width = pct + "%";
  $("#profile-pct-num").textContent = pct;
  $("#profile-pct").textContent = pct >= 90 ? "Looking great!" : "Almost there";
  fillProfileForm();
  loadRecommendations();
  loadApplications();
}

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

  if (!data.cold_start && data.recommendations.length) {
    const top = data.recommendations[0];
    const pct = Math.round(top.total_score * 100);
    $("#stat-match").textContent = pct;
    $("#stat-match-sub").textContent =
      pct >= 75 ? "Excellent match" : pct >= 50 ? "Good match" : "Improve your profile";
    $("#overall-match").textContent = pct + "%";
    renderRadar(top);
  } else {
    $("#stat-match").textContent = "--";
    $("#stat-match-sub").textContent = "Complete your profile";
    $("#overall-match").textContent = "--%";
    $("#radar-wrap").innerHTML =
      `<p class="sub-line" style="text-align:center; padding:20px 0">Add skills to your profile to see your match breakdown.</p>`;
  }
}
$("#rec-search").addEventListener("input", () => loadRecommendations());
$("#rec-sector").addEventListener("change", () => loadRecommendations());

function renderRadar(r) {
  const axes = [
    ["Skills Match", r.skill_score],
    ["Location Fit", r.location_score],
    ["Sector Fit", r.sector_score],
    ["Preference Fit", (r.location_score + r.sector_score) / 2],
    ["Overall", r.total_score],
  ];
  const cx = 130, cy = 115, R = 82, n = axes.length;
  const pt = (i, v) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    return [cx + Math.cos(a) * R * v, cy + Math.sin(a) * R * v];
  };
  const ring = (v) => axes.map((_, i) => pt(i, v).map((x) => x.toFixed(1)).join(",")).join(" ");
  const dataPoly = axes.map(([, v], i) => pt(i, Math.max(v, 0.08)).map((x) => x.toFixed(1)).join(",")).join(" ");
  const labels = axes.map(([name, v], i) => {
    const [x, y] = pt(i, 1.26);
    return `<text x="${x.toFixed(0)}" y="${y.toFixed(0)}" text-anchor="middle"
      font-size="9" font-weight="700" fill="#7a8194">${name}</text>
      <text x="${x.toFixed(0)}" y="${(y + 11).toFixed(0)}" text-anchor="middle"
      font-size="9" font-weight="800" fill="#1f2430">${Math.round(v * 100)}%</text>`;
  }).join("");
  const spokes = axes.map((_, i) => {
    const [x, y] = pt(i, 1);
    return `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#e9ecf2"/>`;
  }).join("");
  $("#radar-wrap").innerHTML = `
    <svg viewBox="0 0 260 240" width="260" height="240" role="img" aria-label="Match breakdown radar chart">
      ${[0.33, 0.66, 1].map((v) => `<polygon points="${ring(v)}" fill="none" stroke="#e9ecf2"/>`).join("")}
      ${spokes}
      <polygon points="${dataPoly}" fill="rgba(255,122,26,0.18)" stroke="#FF7A1A" stroke-width="2"/>
      ${labels}
    </svg>`;
}

function matchCard(r, coldStart) {
  const j = r.internship;
  const pct = coldStart ? null : Math.round(r.total_score * 100);
  return `<div class="match-card" data-id="${j.id}">
    <div class="mc-top">
      <div style="flex:1">
        <div class="mc-title-row">
          <span class="mc-title">${esc(j.title)}</span>
          ${j.verified ? `<span class="badge-verified">VERIFIED EMPLOYER</span>` : ""}
        </div>
        <div class="mc-meta">${esc(j.company)} &middot; ${esc(j.location)}, ${esc(j.state)} &middot; ${j.duration_months} months &middot; &#8377;${j.stipend.toLocaleString("en-IN")}/month</div>
        <span class="sector-tag">${esc(j.sector)}</span>
        ${j.skills_required.slice(0, 3).map((s) => `<span class="sector-tag">${esc(s)}</span>`).join("")}
      </div>
      ${pct === null ? "" : `<div class="score-pill-wrap"><span class="score-pill">${pct}% Match</span></div>`}
    </div>
    <div class="mc-actions">
      ${pct === null ? "<span></span>" : `<button class="reason-toggle" data-act="reason">View match reasoning</button>`}
      <div class="mc-buttons">
        <button class="btn-details" data-act="details">More Details</button>
        ${currentRole === "student" ? `<button class="btn btn-navy" data-act="apply">Apply Now</button>` : ""}
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
          btn.textContent = panel.classList.contains("show")
            ? "Hide match reasoning" : "View match reasoning";
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

function showDetails(id) {
  const j = internshipCache[id];
  if (!j) return;
  $("#modal-body").innerHTML = `
    <h3>${esc(j.title)}</h3>
    <div class="mc-title-row" style="margin:6px 0">
      <strong>${esc(j.company)}</strong>
      ${j.verified ? `<span class="badge-verified">VERIFIED EMPLOYER</span>`
                   : `<span class="badge-pending">VERIFICATION PENDING</span>`}
    </div>
    <div class="modal-meta">${esc(j.location)}, ${esc(j.state)} &middot; ${esc(j.sector)} &middot; ${j.duration_months} months &middot; &#8377;${j.stipend.toLocaleString("en-IN")}/month &middot; ${j.capacity} seats</div>
    <div class="modal-section"><h4>About the Company</h4><p style="font-size:0.86rem; color:#4a5265">${esc(j.company_about || j.description)}</p></div>
    <div class="modal-section"><h4>Role Description</h4><p style="font-size:0.86rem; color:#4a5265">${esc(j.description)}</p></div>
    <div class="modal-section"><h4>Required Skills</h4><div class="mc-title-row">${j.skills_required.map((s) => `<span class="sector-tag">${esc(s)}</span>`).join(" ")}</div></div>
    ${j.assessment_stages && j.assessment_stages.length ? `
      <div class="modal-section"><h4>Assessment Stages</h4>
        <ol class="stages-list">${j.assessment_stages.map((s) => `<li>${esc(s)}</li>`).join("")}</ol>
      </div>` : ""}
    ${currentRole === "student" ? `<div class="modal-section">
      <button class="btn btn-navy" id="modal-apply">Apply Now</button></div>` : ""}`;
  $("#modal-backdrop").classList.add("show");
  const b = $("#modal-apply");
  if (b) b.addEventListener("click", (e) => applyTo(id, e.target));
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

/* ================= applications ================= */
const STATUS_CLASS = {
  "Applied": "st-applied", "Shortlisted": "st-shortlisted", "Offer Sent": "st-offer",
  "Accepted": "st-accepted", "Declined": "st-declined", "Rejected": "st-rejected",
};
const statusBadge = (s) => `<span class="st-badge ${STATUS_CLASS[s] || "st-applied"}">${esc(s).toUpperCase()}</span>`;

async function loadApplications() {
  if (!currentStudent) return;
  const apps = await api(`/api/students/${currentStudent.id}/applications`);
  $("#stat-apps").textContent = apps.length;
  $("#stat-apps-active").textContent =
    apps.filter((a) => ["Applied", "Shortlisted", "Offer Sent"].includes(a.status)).length;
  $("#stat-shortlisted").textContent =
    apps.filter((a) => ["Shortlisted", "Offer Sent", "Accepted"].includes(a.status)).length;
  $("#applications-mini").innerHTML = apps.length ? `
    <div class="table-wrap"><table class="data-table">
      <thead><tr><th>Company</th><th>Role</th><th>Status</th><th>Applied On</th></tr></thead>
      <tbody>${apps.slice(0, 4).map((a) => `<tr>
        <td class="td-strong">${esc(a.internship.company)}</td>
        <td>${esc(a.internship.title)}</td>
        <td>${statusBadge(a.status)}</td>
        <td class="td-muted">${new Date(a.applied_at).toLocaleDateString("en-IN")}</td>
      </tr>`).join("")}</tbody></table></div>`
    : `<p class="sub-line">No applications yet. Apply from the recommendations above.</p>`;

  $("#applications-list").innerHTML = apps.length ? apps.map((a) => `
    <div class="match-card">
      <div class="mc-title-row">
        <span class="mc-title">${esc(a.internship.title)}</span>
        ${statusBadge(a.status)}
      </div>
      <div class="mc-meta">${esc(a.internship.company)} &middot; ${esc(a.internship.location)} &middot; Applied ${new Date(a.applied_at).toLocaleDateString("en-IN")}</div>
      ${a.status === "Offer Sent" ? `
        <div class="mc-actions"><span class="reason-text">You have an offer. Respond within 14 days.</span>
          <div class="mc-buttons">
            <button class="mini-btn mini-green" data-appid="${a.id}" data-newstatus="Accepted">Accept Offer</button>
            <button class="mini-btn mini-red" data-appid="${a.id}" data-newstatus="Declined">Decline</button>
          </div></div>` : ""}
      ${a.status === "Accepted" ? `<div class="reason-text" style="margin-top:8px">Congratulations! Joining details will be shared by ${esc(a.internship.company)}.</div>` : ""}
    </div>`).join("")
    : `<div class="cold-note">No applications yet. There is no cap: apply to every internship that fits you.</div>`;
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
  $("#f-mobile").value = s.mobile || "";
}
// every profile PUT must carry all fields; helper keeps mobile from being wiped
function profilePayload(overrides) {
  const s = currentStudent;
  return JSON.stringify({
    skills: s.skills, qualification: s.qualification,
    qualification_level: s.qualification_level,
    preferred_locations: s.preferred_locations,
    preferred_sectors: s.preferred_sectors,
    first_generation: s.first_generation, college_tier: s.college_tier,
    mobile: s.mobile || "", ...overrides,
  });
}
$("#profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const [qual, level] = $("#f-qual").value.split("|");
  const csv = (v) => v.split(",").map((x) => x.trim()).filter(Boolean);
  const updated = await api(`/api/students/${currentStudent.id}`, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: profilePayload({
      skills: csv($("#f-skills").value),
      qualification: qual, qualification_level: Number(level),
      preferred_locations: csv($("#f-locations").value),
      preferred_sectors: csv($("#f-sectors").value),
      first_generation: $("#f-firstgen").checked,
      college_tier: Number($("#f-tier").value),
      mobile: $("#f-mobile").value.trim(),
    }),
  }).catch((e) => { $("#profile-saved").textContent = e.message; return null; });
  if (!updated) return;
  $("#profile-saved").textContent = "Saved. Recommendations refreshed.";
  setTimeout(() => { $("#profile-saved").textContent = ""; }, 3000);
  applyStudent(updated);
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
  { key: "qualification",
    ask: () => "What is your highest qualification?",
    options: () => QUAL_OPTIONS,
    parse: (v) => QUAL_OPTIONS.find((q) => q.toLowerCase() === v.trim().toLowerCase()) || null,
    error: "Please pick one of the listed qualifications (tap a button below)." },
  { key: "skills",
    ask: () => "Now tell me your skills, separated by commas. For example: Python, SQL, Excel",
    options: () => [],
    parse: (v) => { const l = v.split(",").map((x) => x.trim()).filter(Boolean); return l.length ? l : null; },
    error: "Please list at least one skill, separated by commas." },
  { key: "locations",
    ask: () => "Which cities would you prefer to work in? Separate with commas, or say Any.",
    options: () => ["Any"],
    parse: (v) => { const l = v.split(",").map((x) => x.trim()).filter(Boolean); return l.length ? l : null; },
    error: "Please name at least one city, or tap Any." },
  { key: "sectors",
    ask: () => "Which sector interests you most? Tap one or type several, separated by commas.",
    options: () => SECTOR_LIST,
    parse: (v) => { const l = v.split(",").map((x) => x.trim()).filter(Boolean); return l.length ? l : null; },
    error: "Please choose at least one sector." },
  { key: "first_generation",
    ask: () => "Are you the first person in your family to attend college? This helps the scheme's fairness policy work for you; it never reduces your score.",
    options: () => ["Yes", "No"],
    parse: (v) => /^y/i.test(v.trim()) ? true : /^n/i.test(v.trim()) ? false : null,
    error: "Please answer Yes or No." },
  { key: "college_tier",
    ask: () => "Which tier is your college? Tier 1 (IIT/NIT/top university), Tier 2 (state university), or Tier 3 (local college).",
    options: () => ["Tier 1", "Tier 2", "Tier 3"],
    parse: (v) => { const m = v.match(/[123]/); return m ? Number(m[0]) : null; },
    error: "Please pick Tier 1, 2 or 3." },
  { key: "mobile",
    ask: () => "Finally, your mobile number (required). Companies use it to contact you about offers.",
    options: () => [],
    parse: (v) => {
      const digits = v.replace(/[^\d+]/g, "");
      return /^(\+91)?[6-9]\d{9}$/.test(digits) ? digits : null;
    },
    error: "That does not look like a valid 10-digit Indian mobile number. Please try again." },
];

function startIntake() {
  if (!currentStudent) return;
  intake = { step: 0, answers: {} };
  $("#intake-messages").innerHTML = "";
  intakeMsg("bot", `Namaste ${currentStudent.name.split(" ")[0]}! I will set up your profile in a few quick questions. Tap an option or type your answer.`);
  askCurrent();
}
function intakeMsg(who, text) {
  const div = document.createElement("div");
  div.className = "chat-msg " + (who === "user" ? "chat-user" : "chat-bot");
  div.textContent = text;
  $("#intake-messages").appendChild(div);
  $("#intake-messages").scrollTop = $("#intake-messages").scrollHeight;
}
function showTyping(container) {
  const div = document.createElement("div");
  div.className = "chat-msg chat-bot typing-bubble";
  div.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}
async function askCurrent() {
  const step = INTAKE_STEPS[intake.step];
  const typing = showTyping($("#intake-messages"));
  await new Promise((r) => setTimeout(r, 550));
  typing.remove();
  intakeMsg("bot", step.ask());
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
  $("#intake-quick").innerHTML = "";
  const a = intake.answers;
  const updated = await api(`/api/students/${currentStudent.id}`, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: profilePayload({
      skills: a.skills, qualification: a.qualification,
      qualification_level: QUAL_LEVEL(a.qualification),
      preferred_locations: a.locations, preferred_sectors: a.sectors,
      first_generation: a.first_generation, college_tier: a.college_tier,
      mobile: a.mobile,
    }),
  });
  intakeMsg("bot", `All set! Your profile is saved: ${a.qualification}, skills ${a.skills.join(", ")}. Your recommendations are ready on the Dashboard.`);
  $("#intake-quick").innerHTML =
    `<button class="quick-btn q-green" id="intake-goto-dash">See my recommendations</button>`;
  $("#intake-goto-dash").addEventListener("click", () => switchTab("dashboard"));
  applyStudent(updated);
}
$("#intake-send").addEventListener("click", () => {
  const v = $("#intake-input").value.trim();
  if (v && intake) { $("#intake-input").value = ""; handleIntake(v); }
});
$("#intake-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { e.preventDefault(); $("#intake-send").click(); }
});

/* ================= messages / notifications ================= */
async function loadMessages(markRead) {
  if (!authToken || currentRole === "admin") {
    const dot = document.querySelector(".bell-dot");
    if (dot) dot.style.display = "none";
    return;
  }
  const data = await api("/api/notifications").catch(() => ({ unread: 0, items: [] }));
  const badge = currentRole === "company" ? $("#msg-badge-c") : $("#msg-badge");
  const dot = document.querySelector(".bell-dot");
  [badge, dot].forEach((el) => {
    if (!el) return;
    el.textContent = data.unread;
    el.style.display = data.unread ? "" : "none";
  });
  $("#notif-list").innerHTML = data.items.length ? data.items.map((n) => `
    <div class="ann-item ${n.read ? "" : "notif-unread"}">
      <span class="ann-ico ${n.read ? "ico-blue" : "ico-saffron"}"><svg class="ico"><use href="#i-bell"/></svg></span>
      <div><p style="color:var(--ink); font-size:0.84rem">${esc(n.text)}</p></div>
      <span class="ann-time">${new Date(n.created_at).toLocaleDateString("en-IN")}</span>
    </div>`).join("")
    : `<p class="sub-line">No messages yet. Updates about your applications and offers appear here.</p>`;
  if (markRead && data.unread) {
    await api("/api/notifications/read", { method: "POST" });
    setTimeout(() => loadMessages(false), 400);
  }
}
$("#mark-read").addEventListener("click", async () => {
  await api("/api/notifications/read", { method: "POST" });
  loadMessages(false);
});
$("#side-bell").addEventListener("click", () => switchTab("messages"));

/* ================= documents ================= */
$("#resume-upload").addEventListener("click", async () => {
  const f = $("#resume-file").files[0];
  if (!f) { $("#upload-note").textContent = "Choose a PDF first."; return; }
  const fd = new FormData();
  fd.append("file", f);
  $("#upload-note").textContent = "Uploading...";
  try {
    const res = await api("/api/documents", { method: "POST", body: fd });
    $("#upload-note").textContent = "Uploaded.";
    if (res.parsed_skills.length) {
      const box = $("#parsed-skills-box");
      box.style.display = "block";
      box.innerHTML = `We found these skills in your resume: <strong>${res.parsed_skills.map(esc).join(", ")}</strong>.
        <button class="mini-btn mini-green" id="adopt-skills" style="margin-left:8px">Add to my profile</button>`;
      $("#adopt-skills").addEventListener("click", async () => {
        const merged = [...new Set([...currentStudent.skills, ...res.parsed_skills])];
        const updated = await api(`/api/students/${currentStudent.id}`, {
          method: "PUT", headers: { "Content-Type": "application/json" },
          body: profilePayload({ skills: merged }),
        });
        box.innerHTML = "Skills added to your profile. Recommendations refreshed.";
        applyStudent(updated);
      });
    }
    loadDocuments();
  } catch (e) { $("#upload-note").textContent = e.message; }
});

async function loadDocuments() {
  if (currentRole !== "student") return;
  const docs = await api("/api/documents").catch(() => []);
  $("#docs-list").innerHTML = docs.length ? `
    <div class="table-wrap"><table class="data-table">
      <thead><tr><th>File</th><th>Uploaded</th><th>Skills Detected</th><th></th></tr></thead>
      <tbody>${docs.map((d) => `<tr>
        <td class="td-strong">${esc(d.filename)}</td>
        <td class="td-muted">${new Date(d.uploaded_at).toLocaleDateString("en-IN")}</td>
        <td>${d.parsed_skills.map((s) => `<span class="sector-tag">${esc(s)}</span>`).join(" ") || `<span class="td-muted">-</span>`}</td>
        <td><a class="link-btn" href="/api/documents/${d.id}/download?token=${authToken}" target="_blank">View</a></td>
      </tr>`).join("")}</tbody></table></div>`
    : `<p class="sub-line" style="margin-top:14px">No documents uploaded yet.</p>`;
}

/* ================= skill analytics ================= */
async function loadSkillAnalytics() {
  if (!currentStudent) return;
  const d = await api(`/api/students/${currentStudent.id}/skill-analytics`);
  const maxCount = Math.max(...d.top_demand.map((x) => x.count), 1);
  $("#skills-body").innerHTML = `
    <div class="overall-row"><span>Your skills match</span>
      <span class="overall-pill">${d.coverage_pct}% of ${d.total_internships} listings</span></div>
    ${d.top_missing.length ? `<div class="cold-note">Most valuable skills to learn next:
      <strong>${d.top_missing.map((m) => esc(m.skill)).join(", ")}</strong></div>` : ""}
    <h4 style="margin:14px 0 10px; font-size:0.85rem">Demand across all listings</h4>
    ${d.top_demand.map((x) => `
      <div class="fair-row" style="grid-template-columns: 150px 1fr 90px; margin-bottom:7px">
        <span style="font-weight:700; color:${x.have ? "var(--green)" : "var(--ink)"}">${esc(x.skill)}${x.have ? " &#10003;" : ""}</span>
        <div class="fair-track"><div class="${x.have ? "fair-fill-adj" : "fair-fill-raw"}" style="width:${Math.round(x.count / maxCount * 100)}%"></div></div>
        <span>${x.count} listings</span>
      </div>`).join("")}`;
}

/* ================= help & support ================= */
const FAQS = [
  ["What is the stipend?", "Interns receive Rs 5,000 per month as assistance, plus a one-time grant of Rs 6,000 on joining."],
  ["Who is eligible?", "Youth aged 21-24 who are not in full-time employment or full-time education. Qualification requirements vary per internship and ATLAS checks them automatically."],
  ["How many internships can I apply to?", "There is no cap in ATLAS. Apply to every internship that fits you; the allocation engine optimises across all applications."],
  ["How does matching work?", "Hard eligibility rules run first, then semantic skill matching, fairness weighting per the scheme's affirmative-action policy, and a global optimisation so allocations are fair across all candidates."],
  ["What does the Verified badge mean?", "The scheme administrator has reviewed the listing. Prefer verified listings."],
  ["How long is the internship?", "12 months, with mentorship and on-the-job training at a partner company."],
];
function renderFaq() {
  if ($("#faq-list").children.length) return;
  $("#faq-list").innerHTML = FAQS.map(([q, a], i) => `
    <details class="faq-item"><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join("");
}
$("#help-chat").addEventListener("click", () => openAssistant());
$("#complaint-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/api/complaints", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject: $("#cmp-subject").value, details: $("#cmp-details").value }),
  });
  $("#cmp-note").textContent = "Submitted. The administrator will review it.";
  $("#complaint-form").reset();
  setTimeout(() => { $("#cmp-note").textContent = ""; }, 4000);
});

/* ================= company portal ================= */
async function loadCompanyDash() {
  const data = await api("/api/company/me");
  const c = data.company;
  currentCompany = c;
  const verified = data.listings.filter((j) => j.status === "Verified").length;
  const banner = c.status === "Pending"
    ? `<div class="cold-note" style="margin-top:16px">Your company account is awaiting approval by the scheme administrator. You will be notified here once approved; posting is enabled after that.</div>`
    : c.status === "Suspended"
    ? `<div class="cold-note" style="margin-top:16px">Your company account is suspended. Contact the scheme administrator.</div>` : "";
  document.querySelectorAll("#tab-c-dash .cold-note").forEach((el) => el.remove());
  if (banner) $("#c-stats").insertAdjacentHTML("beforebegin", banner);
  $("#c-stats").innerHTML = `
    <div class="scard"><div class="scard-top"><div class="scard-ico ico-blue"><svg class="ico"><use href="#i-briefcase"/></svg></div>
      <span class="scard-label">Listings</span></div><div class="scard-value">${data.listings.length}</div></div>
    <div class="scard"><div class="scard-top"><div class="scard-ico ico-green"><svg class="ico"><use href="#i-shield"/></svg></div>
      <span class="scard-label">Verified</span></div><div class="scard-value">${verified}</div></div>
    <div class="scard"><div class="scard-top"><div class="scard-ico ico-saffron"><svg class="ico"><use href="#i-clipboard"/></svg></div>
      <span class="scard-label">Applications</span></div><div class="scard-value">${data.applications}</div></div>
    <div class="scard"><div class="scard-top"><div class="scard-ico ico-purple"><svg class="ico"><use href="#i-building"/></svg></div>
      <span class="scard-label">Status</span></div><div class="scard-value" style="font-size:1.1rem">${esc(c.status)}</div></div>`;
  $("#c-listings-tbody").innerHTML = data.listings.map((j) => `
    <tr><td class="td-strong">${esc(j.title)}</td><td>${esc(j.location)}</td>
    <td>${j.capacity}</td><td>${j.status === "Verified"
      ? `<span class="badge-verified">VERIFIED</span>`
      : `<span class="badge-pending">${esc(j.status).toUpperCase()}</span>`}</td></tr>`).join("")
    || `<tr><td colspan="4" class="td-muted">No listings yet. Use Post Internship.</td></tr>`;
}

$("#c-post-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const csv = (v) => v.split(",").map((x) => x.trim()).filter(Boolean);
  await api("/api/company/internships", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: $("#cp-title").value, location: $("#cp-location").value,
      state: $("#cp-state").value, skills_required: csv($("#cp-skills").value),
      min_qualification_level: Number($("#cp-minqual").value),
      capacity: Number($("#cp-capacity").value),
      stipend: Number($("#cp-stipend").value) || 5000,
    }),
  });
  $("#cp-note").textContent = "Published. Awaiting admin verification.";
  $("#c-post-form").reset();
  setTimeout(() => { $("#cp-note").textContent = ""; }, 4000);
});

async function loadCompanyApplicants() {
  const apps = await api("/api/company/applicants");
  $("#c-apps-tbody").innerHTML = apps.length ? apps.map((a) => `
    <tr>
      <td class="td-strong">${esc(a.student.name)}<br>
        <span class="td-muted" style="font-size:0.74rem">${esc(a.student.qualification)}${a.student.mobile ? " &middot; " + esc(a.student.mobile) : ""}</span></td>
      <td>${esc(a.internship_title)}</td>
      <td>${a.student.skills.slice(0, 3).map((s) => `<span class="sector-tag">${esc(s)}</span>`).join(" ")}</td>
      <td><span class="score-chip">${a.match_pct}%</span></td>
      <td>${a.documents.length
        ? a.documents.map((d) => `<a class="link-btn" href="/api/documents/${d.id}/download?token=${authToken}" target="_blank">Resume</a>`).join(" ")
        : `<span class="td-muted">None</span>`}</td>
      <td>${statusBadge(a.status)}</td>
      <td>
        ${a.status === "Applied" ? `
          <button class="mini-btn mini-navy" data-appid="${a.id}" data-newstatus="Shortlisted">Shortlist</button>
          <button class="mini-btn mini-red" data-appid="${a.id}" data-newstatus="Rejected">Reject</button>` : ""}
        ${a.status === "Shortlisted" ? `
          <button class="mini-btn mini-green" data-appid="${a.id}" data-newstatus="Offer Sent">Send Offer</button>
          <button class="mini-btn mini-red" data-appid="${a.id}" data-newstatus="Rejected">Reject</button>` : ""}
        ${["Offer Sent", "Accepted", "Declined", "Rejected"].includes(a.status)
          ? `<span class="td-muted" style="font-size:0.74rem">${a.status === "Offer Sent" ? "Awaiting response" : "Closed"}</span>` : ""}
      </td>
    </tr>`).join("")
    : `<tr><td colspan="7" class="td-muted">No applications yet.</td></tr>`;
  document.querySelectorAll("#c-apps-tbody [data-appid]").forEach((b) =>
    b.addEventListener("click", async () => {
      await api(`/api/applications/${b.dataset.appid}/status`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: b.dataset.newstatus }),
      });
      loadCompanyApplicants();
    }));
}

/* ================= admin ================= */
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
    ["Students", s.students, "ico-blue", "i-user"],
    ["Companies", s.companies, "ico-saffron", "i-building"],
    ["Internships", s.internships, "ico-green", "i-briefcase"],
    ["Applications", s.applications, "ico-purple", "i-clipboard"],
    ["Allocated", s.allocated, "ico-green", "i-shield"],
  ];
  $("#admin-stats").innerHTML = cards.map(([label, num, cls, ico]) => `
    <div class="scard"><div class="scard-top"><div class="scard-ico ${cls}"><svg class="ico"><use href="#${ico}"/></svg></div>
    <span class="scard-label">${label}</span></div>
    <div class="scard-value">${Number(num).toLocaleString("en-IN")}</div></div>`).join("");
}

async function loadInsights() {
  try {
    const d = await api("/api/live/insights");
    $("#insights-badge").style.display = d.live === false ? "none" : "";
    const t = d.totals;
    const top = d.states.slice(0, 8);
    $("#insights-body").innerHTML = `
      <div class="stat-cards" style="grid-template-columns:repeat(4,1fr); margin:12px 0">
        ${[["Profiles", t.profiles], ["Opportunities", t.opportunities],
           ["Offers", t.offers], ["Accepted", t.accepted]].map(([l, v]) => `
          <div class="scard" style="padding:12px 14px"><span class="scard-label">${l}</span>
          <div class="scard-value" style="font-size:1.2rem">${Number(v).toLocaleString("en-IN")}</div></div>`).join("")}
      </div>
      <div class="table-wrap"><table class="data-table">
        <thead><tr><th>State</th><th>Profiles</th><th>Opportunities</th><th>Offers</th><th>Accepted</th></tr></thead>
        <tbody>${top.map((s) => `<tr>
          <td class="td-strong">${esc(s.state)}</td>
          <td>${(s.profiles || 0).toLocaleString("en-IN")}</td>
          <td>${(s.opportunities || 0).toLocaleString("en-IN")}</td>
          <td>${(s.offers || 0).toLocaleString("en-IN")}</td>
          <td class="score-chip">${(s.accepted || 0).toLocaleString("en-IN")}</td>
        </tr>`).join("")}</tbody></table></div>`;
  } catch {
    $("#insights-body").innerHTML = `<p class="sub-line">Live government data unavailable right now.</p>`;
  }
}

async function loadLivePmis() {
  try {
    const d = await api("/api/live/pmis");
    $("#live-badge").style.display = "";
    const top = d.records.slice(0, 10);
    const max = Math.max(...top.map((r) => r.accepted), 1);
    $("#live-pmis").innerHTML = `
      <p class="sub-line" style="margin:8px 0">${esc(d.title)} &middot; Total accepted: <strong>${d.total_accepted.toLocaleString("en-IN")}</strong></p>
      ${top.map((r) => `
        <div class="fair-row" style="grid-template-columns:170px 1fr 70px; margin-bottom:6px">
          <span style="font-weight:700">${esc(r.state)}</span>
          <div class="fair-track"><div class="fair-fill-adj" style="width:${Math.round(r.accepted / max * 100)}%"></div></div>
          <span>${r.accepted.toLocaleString("en-IN")}</span>
        </div>`).join("")}`;
  } catch {
    $("#live-pmis").innerHTML = `<p class="sub-line">Live government data unavailable right now.</p>`;
  }
}

async function loadFairness() {
  const data = await api("/api/allocation");
  if (!data.matches.length) {
    $("#fairness-bars").innerHTML =
      `<div class="cold-note">No allocation run yet. Press Run Allocation Engine above.</div>`;
    $("#alloc-result").style.display = "none";
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
  $("#fairness-bars").innerHTML = html || `<p class="sub-line">Waiting for allocations.</p>`;
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
  try { await api("/api/allocate", { method: "POST" }); } catch (e) { alert(e.message); }
  btn.disabled = false; btn.textContent = "Run Allocation Engine";
  loadAdminStats(); loadFairness(); loadAdminStudents();
});

let studentsPage = 1;
const STUDENTS_SIZE = 15;
async function loadAdminStudents() {
  const q = encodeURIComponent($("#students-search").value.trim());
  const data = await api(`/api/admin/students?search=${q}&page=${studentsPage}&page_size=${STUDENTS_SIZE}`);
  const maxPage = Math.max(1, Math.ceil(data.total / STUDENTS_SIZE));
  $("#students-pages").textContent = `${studentsPage} / ${maxPage} (${data.total})`;
  $("#students-prev").disabled = studentsPage <= 1;
  $("#students-next").disabled = studentsPage >= maxPage;
  $("#students-tbody").innerHTML = data.items.length ? data.items.map((s) => `
    <tr>
      <td class="td-strong">${esc(s.name)}</td>
      <td>${esc(s.qualification)}</td>
      <td>${[s.first_generation ? "First-gen" : "", s.college_tier >= 2 ? `Tier-${s.college_tier}` : ""]
            .filter(Boolean).map((x) => `<span class="equity-flag">${x}</span>`).join(" ") || `<span class="td-muted">General</span>`}</td>
      <td>${s.applications}</td>
      <td>${s.allocated ? `<span class="td-strong">${esc(s.allocated_company)}</span>` : `<span class="unallocated">Not allocated</span>`}</td>
      <td>${s.allocated ? esc(s.allocated_role) : `<span class="td-muted">-</span>`}</td>
      <td>${s.allocated ? `<span class="score-chip">${Math.round(s.match_score * 100)}%</span>` : `<span class="td-muted">-</span>`}</td>
    </tr>`).join("")
    : `<tr><td colspan="7" class="td-muted">No students registered yet.</td></tr>`;
}
$("#students-search").addEventListener("input", () => { studentsPage = 1; loadAdminStudents(); });
$("#students-prev").addEventListener("click", () => { studentsPage--; loadAdminStudents(); });
$("#students-next").addEventListener("click", () => { studentsPage++; loadAdminStudents(); });

async function loadAdminCompanies() {
  const companies = await api("/api/admin/companies");
  $("#admin-companies-tbody").innerHTML = companies.map((c) => `
    <tr>
      <td class="td-strong">${esc(c.name)}</td>
      <td>${esc(c.sector)}</td>
      <td>${c.listings}</td>
      <td>${c.status === "Active" ? `<span class="badge-verified">ACTIVE</span>`
          : c.status === "Pending" ? `<span class="st-badge st-shortlisted">PENDING APPROVAL</span>`
          : `<span class="st-badge st-rejected">SUSPENDED</span>`}</td>
      <td>
        ${c.status === "Pending" ? `
          <button class="mini-btn mini-green" data-cid="${c.id}" data-newstatus="Active">Approve</button>
          <button class="mini-btn mini-red" data-cid="${c.id}" data-newstatus="Suspended">Reject</button>` : ""}
        ${c.status === "Active" ? `
          <button class="mini-btn mini-red" data-cid="${c.id}" data-newstatus="Suspended">Suspend</button>` : ""}
        ${c.status === "Suspended" ? `
          <button class="mini-btn mini-green" data-cid="${c.id}" data-newstatus="Active">Activate</button>` : ""}
      </td>
    </tr>`).join("");
  document.querySelectorAll("#admin-companies-tbody [data-cid]").forEach((b) =>
    b.addEventListener("click", async () => {
      await api(`/api/admin/companies/${b.dataset.cid}/status`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: b.dataset.newstatus }),
      });
      loadAdminCompanies();
    }));
}

async function loadAdminApps() {
  let apps;
  try { apps = await api("/api/admin/applications"); }
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
        ${["Offer Sent", "Accepted", "Declined", "Rejected"].includes(a.status)
          ? `<span class="td-muted" style="font-size:0.74rem">${a.status === "Offer Sent" ? "Awaiting student" : "Closed"}</span>` : ""}
      </td>
    </tr>`).join("")
    : `<tr><td colspan="6" class="td-muted">No applications yet.</td></tr>`;
  document.querySelectorAll("#admin-apps-tbody [data-appid]").forEach((b) =>
    b.addEventListener("click", async () => {
      await api(`/api/applications/${b.dataset.appid}/status`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: b.dataset.newstatus }),
      });
      loadAdminApps();
    }));
}

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
      <td>${j.status === "Verified" ? `<span class="badge-verified">VERIFIED</span>` : `<span class="badge-pending">${esc(j.status || "PENDING").toUpperCase()}</span>`}</td>
      <td>
        ${j.status !== "Verified" ? `<button class="mini-btn mini-green" data-iid="${j.id}" data-newstatus="Verified">Verify</button>` : ""}
        ${j.status !== "Suspended" ? `<button class="mini-btn mini-red" data-iid="${j.id}" data-newstatus="Suspended">Suspend</button>`
          : `<button class="mini-btn mini-navy" data-iid="${j.id}" data-newstatus="Pending">Restore</button>`}
      </td>
    </tr>`).join("");
  document.querySelectorAll("#listings-tbody [data-iid]").forEach((b) =>
    b.addEventListener("click", async () => {
      await api(`/api/admin/internships/${b.dataset.iid}/status`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: b.dataset.newstatus }),
      });
      loadListings();
    }));
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
  $("#job-saved").textContent = "Internship added.";
  setTimeout(() => { $("#job-saved").textContent = ""; }, 4000);
  $("#add-job-form").reset();
  loadListings(); loadAdminStats();
});

async function loadAdminComplaints() {
  const rows = await api("/api/admin/complaints");
  $("#admin-complaints-tbody").innerHTML = rows.length ? rows.map((c) => `
    <tr>
      <td class="td-strong">${esc(c.student_name)}</td>
      <td>${esc(c.subject)}</td>
      <td class="td-muted" style="max-width:280px">${esc(c.details)}</td>
      <td>${c.status === "Open" ? `<span class="st-badge st-shortlisted">OPEN</span>` : `<span class="badge-verified">RESOLVED</span>`}</td>
      <td>${c.status === "Open" ? `<button class="mini-btn mini-green" data-cmpid="${c.id}">Resolve</button>` : ""}</td>
    </tr>`).join("")
    : `<tr><td colspan="5" class="td-muted">No grievances submitted.</td></tr>`;
  document.querySelectorAll("#admin-complaints-tbody [data-cmpid]").forEach((b) =>
    b.addEventListener("click", async () => {
      await api(`/api/admin/complaints/${b.dataset.cmpid}`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "Resolved" }),
      });
      loadAdminComplaints();
    }));
}

/* ================= chatbot ================= */
function addChatMsg(who, text) {
  const div = document.createElement("div");
  div.className = "chat-msg " + (who === "user" ? "chat-user" : "chat-bot");
  div.textContent = text;
  $("#chat-messages").appendChild(div);
  $("#chat-messages").scrollTop = $("#chat-messages").scrollHeight;
}
function openAssistant() {
  $("#chat-panel").classList.add("show");
  if (!$("#chat-messages").children.length) addChatMsg("bot",
    "Namaste! I am the ATLAS assistant. Try 'recommend jobs for me', 'my application status', or ask about stipend and eligibility.");
}
$("#chat-fab").addEventListener("click", openAssistant);
$("#side-assistant").addEventListener("click", openAssistant);
$("#qa-assistant").addEventListener("click", openAssistant);
$("#chat-close").addEventListener("click", () => $("#chat-panel").classList.remove("show"));
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
  const minTyping = 650;
  if (Date.now() - started < minTyping)
    await new Promise((r) => setTimeout(r, minTyping - (Date.now() - started)));
  typing.remove();
  addChatMsg("bot", res.reply);
}
$("#chat-send").addEventListener("click", sendChat);
$("#chat-input").addEventListener("keydown", (e) => { if (e.key === "Enter") sendChat(); });

/* ================= topbar ================= */
$("#hamburger").addEventListener("click", () =>
  document.querySelector(".app-shell").classList.toggle("collapsed"));
$("#top-search").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && currentRole === "student") {
    $("#explore-search").value = e.target.value;
    switchTab("explore");
    explorePage = 1;
    loadExplore();
  }
});

/* Live Data dashboard entry points */
$("#live-data-btn").addEventListener("click", () => switchTab("live"));
$("#impact-live-btn").addEventListener("click", () => switchTab("live"));
$("#live-refresh").addEventListener("click", () => { loadInsights(); loadLivePmis(); });

/* ================= init ================= */
const SECTOR_LIST = ["IT & Software", "Banking & Finance", "Manufacturing",
  "Energy", "Healthcare & Pharma", "Retail & FMCG"];
$("#rec-sector").innerHTML += SECTOR_LIST.map((s) => `<option>${s}</option>`).join("");

renderFunnel();
initSession();
