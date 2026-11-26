"use strict";
const $ = (id) => document.getElementById(id),
  fmt = (n) =>
    n == null
      ? "—"
      : Number(n).toLocaleString("vi-VN", { maximumFractionDigits: 2 }),
  pct = (n) => (n == null ? "—" : fmt(n * 100) + "%"),
  tau = (n) => (n == null ? "—" : Number(n).toFixed(6));
const esc = (x) =>
  String(x ?? "—").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const labels = {
  overview: [
    "Tổng quan tối ưu hóa",
    "Giảm chi phí kiểm tra hệ thống khí nén xe tải dưới giới hạn công suất bảo trì.",
  ],
  baseline: [
    "So sánh Baseline",
    "Cùng tập Validation và hàm chi phí benchmark.",
  ],
  optimization: [
    "Tối ưu hóa Optuna TPE",
    "Lịch sử tìm kiếm siêu tham số và nghiệm khả thi tốt nhất quan sát được.",
  ],
  threshold: [
    "Phân tích ngưỡng quyết định",
    "Tương tác với 101 điểm độ nhạy đã lưu trên Validation.",
  ],
  test: [
    "Đánh giá Official Test",
    "Kết quả kiểm thử độc lập của chính sách đã đóng băng.",
  ],
  live: [
    "Dự đoán và quyết định bảo trì",
    "Dùng checkpoint Trial 16 để chấm một lô CSV và kiểm tra giới hạn công suất.",
  ],
  integrity: [
    "Kiểm chứng thực nghiệm",
    "Đọc lại artifact và kiểm tra mã băm SHA-256 cùng tính nhất quán toán học.",
  ],
};
let evidence = null,
  active = "overview";
function kpis(id, rows) {
  $(id).innerHTML = rows
    .map(
      ([label, val, sub]) =>
        `<div class="kpi"><small>${esc(label)}</small><strong>${esc(val)}</strong><span>${esc(sub)}</span></div>`,
    )
    .join("");
}
function kv(id, rows) {
  $(id).innerHTML = rows
    .map(
      ([k, v]) =>
        `<div class="kv"><span>${esc(k)}</span><strong>${esc(v)}</strong></div>`,
    )
    .join("");
}
function table(id, headers, rows, highlight = -1) {
  $(id).innerHTML =
    `<table><thead><tr>${headers.map((x) => `<th scope="col">${esc(x)}</th>`).join("")}</tr></thead><tbody>${rows.map((r, i) => `<tr${i === highlight ? ' class="highlight"' : ""}>${r.map((x) => `<td>${esc(x)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}
function chart(
  id,
  xs,
  series,
  {
    limit = null,
    marker = null,
    xlabel = "Ngưỡng τ",
    yMin = null,
    yMax = null,
  } = {},
) {
  const W = 680,
    H = 278,
    L = 67,
    R = 20,
    T = 18,
    B = 44;
  const all = series
    .flatMap((s) => s.vals)
    .concat(limit === null ? [] : [limit]);
  let lo = yMin ?? Math.min(...all),
    hi = yMax ?? Math.max(...all);
  if (hi === lo) hi = lo + 1;
  if (yMax === null) hi += 0.06 * (hi - lo);
  if (yMin === null) lo = Math.max(0, lo - 0.06 * (hi - lo));
  const X = (i) => L + (W - L - R) * (i / (xs.length - 1 || 1)),
    Y = (v) => T + ((H - T - B) * (hi - v)) / (hi - lo);
  let out = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc($(id).closest("article").querySelector("h2").textContent)}">`;
  for (let j = 0; j <= 4; j++) {
    let v = lo + ((hi - lo) * j) / 4,
      y = Y(v);
    out += `<line class="grid" x1="${L}" x2="${W - R}" y1="${y}" y2="${y}"/><text x="${L - 8}" y="${y + 4}" text-anchor="end">${esc(fmt(Math.round(v)))}</text>`;
  }
  for (let j = 0; j <= 5; j++) {
    let i = Math.round(((xs.length - 1) * j) / 5),
      x = X(i);
    out += `<text x="${x}" y="${H - B + 19}" text-anchor="middle">${esc(xs[i])}</text>`;
  }
  out += `<line class="axis" x1="${L}" x2="${W - R}" y1="${H - B}" y2="${H - B}"/><text x="${(L + W - R) / 2}" y="${H - 6}" text-anchor="middle">${esc(xlabel)}</text>`;
  if (limit !== null)
    out += `<line x1="${L}" x2="${W - R}" y1="${Y(limit)}" y2="${Y(limit)}" stroke="#b56819" stroke-width="2" stroke-dasharray="5 4"/><text x="${W - R - 3}" y="${Y(limit) - 7}" text-anchor="end">K = ${fmt(limit)}</text>`;
  for (const s of series) {
    out += `<polyline fill="none" stroke="${s.color}" stroke-width="${s.width ?? 2.5}" stroke-linejoin="round" points="${s.vals.map((v, i) => `${X(i)},${Y(v)}`).join(" ")}"/>`;
  }
  if (marker !== null) {
    let x = X(marker),
      y = Y(series[0].vals[marker]);
    out += `<line x1="${x}" x2="${x}" y1="${T}" y2="${H - B}" stroke="#172a3a" stroke-dasharray="4 4"/><circle cx="${x}" cy="${y}" r="5" fill="#0c766e" stroke="white" stroke-width="2"/>`;
  }
  $(id).innerHTML = out + "</svg>";
}
function show(tab) {
  active = tab;
  document.querySelectorAll(".page").forEach((p) => (p.hidden = p.id !== tab));
  document.querySelectorAll("nav button").forEach((b) => {
    b.classList.toggle("active", b.dataset.tab === tab);
    b.setAttribute("aria-current", b.dataset.tab === tab ? "page" : "false");
  });
  $("page-title").textContent = labels[tab][0];
  $("page-sub").textContent = labels[tab][1];
}
document
  .querySelectorAll("nav button")
  .forEach((b) => b.addEventListener("click", () => show(b.dataset.tab)));
function threshold() {
  if (!evidence) return;
  const { validation, thresholds } = evidence;
  const slider = $("tau");
  const index = Number(slider.value);
  const point = thresholds[index];
  const formattedThreshold = point.threshold.toFixed(2);
  $("tau-value").textContent = formattedThreshold;
  slider.setAttribute("aria-valuetext", formattedThreshold);
  kpis("threshold-kpis", [
    ["Chi phí", fmt(point.cost), "đơn vị benchmark"],
    ["Công suất", fmt(point.M) + " / " + fmt(validation.K), "lượt kiểm tra"],
    ["Recall", pct(point.TP / validation.P), "tỷ lệ phát hiện lỗi APS"],
  ]);
  table(
    "threshold-counts",
    [
      "TP · Phát hiện đúng",
      "FP · Kiểm tra thừa",
      "FN · Bỏ sót",
      "TN · Loại đúng",
    ],
    [[point.TP, point.FP, point.FN, point.TN].map(fmt)],
  );
  const feasibility = $("feasibility");
  feasibility.className = "note " + (point.feasible ? "good" : "bad");
  feasibility.textContent = point.feasible
    ? "Khả thi · Còn " + fmt(validation.K - point.M) + " lượt kiểm tra."
    : "Không khả thi · Vượt " + fmt(point.M - validation.K) + " lượt kiểm tra.";
  const xs = thresholds.map((q) => q.threshold.toFixed(2));
  chart(
    "cost-chart",
    xs,
    [{ vals: thresholds.map((q) => q.cost), color: "#0c766e" }],
    { marker: index, yMin: 0 },
  );
  chart(
    "capacity-chart",
    xs,
    [{ vals: thresholds.map((q) => q.M), color: "#365d83" }],
    { marker: index, limit: validation.K, yMin: 0 },
  );
}
$("tau").addEventListener("input", threshold);
function render(d) {
  evidence = d;
  const v = d.validation,
    t = d.test,
    c = d.config,
    p = d.selected,
    tr = d.trials;
  const f = (n) => fmt(n);
  kpis("overview-kpis", [
    [
      "Chi phí Validation · Trial 16",
      f(v.total_cost),
      "thấp nhất trong 20 trial Optuna",
    ],
    ["Giảm chi phí Test", f(t.saving_pct) + "%", "so với không can thiệp"],
    ["Recall Test", pct(t.recall), "tỷ lệ phát hiện lỗi APS"],
    ["Công suất Test", f(t.M) + " / " + f(t.K), "thỏa ràng buộc"],
  ]);
  $("formula").textContent =
    `min C(θ, τ) = ${c.objective.cost_fp} × FP + ${c.objective.cost_fn} × FN`;
  $("constraint").textContent =
    `M = TP + FP ≤ K = ⌊N × ${c.constraint.capacity_fraction}⌋`;
  $("pipeline").innerHTML = [
    ["Train", c.data.train_samples],
    ["Validation", c.data.validation_samples],
    ["Tìm kiếm TPE", tr.length + " trials"],
    ["Official Test", t.N],
  ]
    .map(
      ([k, n]) =>
        `<div><span>${esc(k)}</span><strong>${esc(typeof n === "number" ? f(n) : n)}</strong></div>`,
    )
    .join("");
  kv("decision", [
    ["Trial được chọn", p.selected_trial],
    ["Ngưỡng đóng băng", tau(p.frozen_threshold)],
    ["Chi phí Validation", f(v.total_cost)],
    ["Chi phí Official Test", f(t.total_cost)],
    ["Seed", c.optimizer.sampler_seed],
  ]);
  const bas = d.baselines.map((b) => ({
    ...b,
    label:
      b.baseline_id +
      (b.policy_id
        ? ""
        : b.threshold == null
          ? " · Tham chiếu"
          : " · τ = " + tau(b.threshold)),
  }));
  bas.push({ ...v, label: "RF + Optuna · Trial 16" });
  const lowest = bas.reduce(
    (best, row, index) =>
      row.M <= row.K && (best < 0 || row.total_cost < bas[best].total_cost)
        ? index
        : best,
    -1,
  );
  const mx = Math.max(...bas.map((b) => b.total_cost));
  $("baseline-bars").innerHTML = bas
    .map(
      (b, i) =>
        `<div class="bar-row"><span>${esc(b.label)}</span><div class="bar-track"><svg viewBox="0 0 100 16" preserveAspectRatio="none"><rect width="${(100 * b.total_cost) / mx}" height="16" fill="${i === lowest ? "#0c766e" : "#7794ad"}"/></svg></div><strong class="bar-number">${f(b.total_cost)}</strong></div>`,
    )
    .join("");
  table(
    "baseline-table",
    ["Chính sách", "Ngưỡng", "Chi phí", "FP", "FN", "Recall", "M / K"],
    bas.map((b) => [
      b.label,
      tau(b.threshold),
      f(b.total_cost),
      f(b.FP),
      f(b.FN),
      pct(b.recall),
      f(b.M) + " / " + f(b.K),
    ]),
    lowest,
  );
  const rf = bas.find((b) => b.policy_id === "default_optimized_threshold");
  const saving = v.total_cost - rf.total_cost;
  $("baseline-comparison").textContent =
    `${rf.label} có chi phí thấp nhất trong các chính sách đã đánh giá trên Validation: ${f(rf.total_cost)}, thấp hơn Trial 16 ${f(saving)} đơn vị (${pct(saving / v.total_cost)}). ` +
    `RF mặc định có ${f(rf.FP)} FP, ${f(rf.FN)} FN, Recall ${pct(rf.recall)} và M=${f(rf.M)}. Trial 16 có ${f(v.FP)} FP, ${f(v.FN)} FN, Recall ${pct(v.recall)} và M=${f(v.M)}. ` +
    "Hai cấu hình khác siêu tham số và class_weight (None và balanced). Trial 16 là chính sách đã chốt trước G10.";
  kpis("opt-kpis", [
    ["Trials hoàn thành", tr.length, "ngân sách " + c.budget.max_trials],
    ["Trial tốt nhất", p.selected_trial, "đánh số từ 0"],
    ["Chi phí thấp nhất của Optuna", f(v.total_cost), "Validation · 20 trial"],
    ["Ngưỡng nghiệm", tau(v.threshold), "giá trị làm tròn"],
  ]);
  chart(
    "convergence-chart",
    tr.map((x) => x.trial_number),
    [
      { vals: tr.map((x) => x.objective_value), color: "#91a7ba", width: 1.5 },
      { vals: tr.map((x) => x.best_so_far), color: "#0c766e", width: 3 },
    ],
    { xlabel: "Trial" },
  );
  kv("parameters", [
    ...Object.entries(p.hyperparameters),
    ["Ngưỡng τ đóng băng", p.frozen_threshold],
  ]);
  kv(
    "search-space",
    Object.entries(c.search_space).map(([k, x]) => [
      k,
      `${x.low} – ${x.high}${x.step ? " (bước " + x.step + ")" : ""}`,
    ]),
  );
  table(
    "trial-table",
    [
      "Trial",
      "Chi phí",
      "Best-so-far",
      "Ngưỡng",
      "M",
      "TP",
      "FP",
      "FN",
      "TN",
      "Fit (s)",
    ],
    tr.map((x) => [
      x.trial_number,
      f(x.objective_value),
      f(x.best_so_far),
      tau(x.threshold),
      f(x.M),
      f(x.TP),
      f(x.FP),
      f(x.FN),
      f(x.TN),
      f(x.fit_seconds),
    ]),
    p.selected_trial,
  );
  $("exact-policy").textContent =
    `Trial ${p.selected_trial}: τ = ${p.frozen_threshold}; chi phí ${f(v.total_cost)}, M = ${f(v.M)} / ${f(v.K)}. Thanh trượt không thay đổi nghiệm này.`;
  threshold();
  kpis("test-kpis", [
    ["Chi phí Test", f(t.total_cost), "benchmark"],
    ["Giảm chi phí", f(t.saving_pct) + "%", "so với B0"],
    ["Recall", pct(t.recall), "Official Test"],
    ["Công suất", f(t.M) + " / " + f(t.K), "khả thi"],
  ]);
  table(
    "matrix",
    ["Thực tế / Dự đoán", "Không kiểm tra", "Kiểm tra"],
    [
      ["Không lỗi APS (neg)", f(t.TN) + " · TN", f(t.FP) + " · FP"],
      ["Lỗi APS (pos)", f(t.FN) + " · FN", f(t.TP) + " · TP"],
    ],
  );
  kv("test-metrics", [
    ["Precision", pct(t.precision)],
    ["Recall", pct(t.recall)],
    ["Specificity", pct(t.specificity)],
    ["F1", pct(t.f1)],
    ["ROC-AUC", Number(t.roc_auc).toFixed(4)],
    ["PR-AUC", Number(t.pr_auc).toFixed(4)],
    ["Số mẫu", f(t.N)],
  ]);
  $("test-policy").textContent =
    `Ngưỡng đóng băng τ = ${t.threshold}. Không can thiệp: ${f(t.reference_cost)}; chính sách đã chọn: ${f(t.total_cost)} đơn vị chi phí.`;
  kv(
    "integrity-groups",
    d.integrity.map((g) => [g.run, g.checked + " / " + g.checked + " PASS"]),
  );
  kv("sources", Object.entries(d.source));
  $("status").textContent =
    d.integrity.reduce((n, g) => n + g.checked, 0) +
    " / 32 artifact đã xác minh";
  $("content").hidden = false;
  $("error").hidden = true;
  show(active);
}
async function refresh() {
  const buttons = [$("recheck"), $("retry")];
  buttons.forEach((button) => {
    button.disabled = true;
  });
  try {
    $("status").textContent = "Đang kiểm tra…";
    const r = await fetch("/api/evidence", { cache: "no-store" }),
      d = await r.json();
    if (!r.ok) throw new Error(d.error || "Không thể đọc bằng chứng");
    render(d);
    $("check-result").textContent =
      "Kiểm chứng thành công: " +
      d.integrity.reduce((n, g) => n + g.checked, 0) +
      " artifact; " +
      d.trials.length +
      " trials; " +
      d.thresholds.length +
      " điểm ngưỡng.";
  } catch (e) {
    $("content").hidden = true;
    $("error").hidden = false;
    $("error-message").textContent = "Kiểm chứng thất bại. " + e.message;
    $("status").textContent = "Lỗi kiểm chứng";
  } finally {
    buttons.forEach((button) => {
      button.disabled = false;
    });
  }
}
$("recheck").addEventListener("click", refresh);
$("retry").addEventListener("click", refresh);
refresh();
