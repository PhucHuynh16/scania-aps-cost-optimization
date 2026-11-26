"use strict";

(() => {
  const el = (id) => document.getElementById(id);
  const upload = el("live-upload"),
    sample = el("live-sample"),
    download = el("live-export");
  const file = el("live-file"),
    threshold = el("live-threshold"),
    capacity = el("live-capacity");
  const mode = el("live-mode"),
    prioritize = el("live-prioritize"),
    result = el("live-result");
  const status = el("live-status"),
    decisionError = el("live-decision-error");
  const whole = new Intl.NumberFormat("vi-VN");
  const decimal = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 2 });
  const percent = (value) =>
    value === null ? "—" : decimal.format(value * 100) + "%";
  const sampleUrl = "/validation-sample.csv";
  let batch = null;
  let current = null;

  function addRow(target, values, header = false) {
    const row = target.insertRow();
    for (const value of values) {
      const cell = document.createElement(header ? "th" : "td");
      if (header) cell.scope = "col";
      cell.textContent = value;
      row.append(cell);
    }
  }

  function fillStats(target, pairs) {
    target.replaceChildren();
    for (const [label, value] of pairs) {
      const row = document.createElement("div");
      row.className = "kv";
      const name = document.createElement("span");
      const body = document.createElement("strong");
      name.textContent = label;
      body.textContent = value;
      row.append(name, body);
      target.append(row);
    }
  }

  function getCapacity(count) {
    const input = capacity.value;
    if (mode.value === "count") {
      const k = Number(input);
      return /^[0-9]+$/.test(input) && k <= count ? k : null;
    }
    if (!/^[0-9]+(?:\.[0-9]{1,2})?$/.test(input) || Number(input) > 100)
      return null;
    const [integer, fraction = ""] = input.split(".");
    const units = Number(integer) * 100 + Number(fraction.padEnd(2, "0"));
    return Math.floor((count * units) / 10_000);
  }

  function evaluate(labels, decisions) {
    let tp = 0,
      fp = 0,
      fn = 0,
      tn = 0;
    labels.forEach((label, index) => {
      if (label === 1) {
        if (decisions[index]) tp++;
        else fn++;
      } else if (decisions[index]) {
        fp++;
      } else {
        tn++;
      }
    });
    return {
      tp,
      fp,
      fn,
      tn,
      cost: 10 * fp + 500 * fn,
      precision: tp + fp ? tp / (tp + fp) : null,
      recall: tp + fn ? tp / (tp + fn) : null,
      f1: 2 * tp + fp + fn ? (2 * tp) / (2 * tp + fp + fn) : null,
    };
  }

  function drawEvaluation(labels, decisions, capped, adjusted) {
    const message = el("live-label-info"),
      metrics = el("live-metrics"),
      matrix = el("live-matrix");
    metrics.replaceChildren();
    matrix.replaceChildren();
    message.textContent =
      labels === null
        ? "Lô chưa có nhãn class. Chi phí, FP, FN và các chỉ số đánh giá cần nhãn thực tế."
        : "Chỉ số bên dưới tính từ nhãn của lô CSV hiện tại.";
    if (labels === null) return;
    addRow(
      metrics.createTHead(),
      [
        "Chính sách",
        "Chi phí",
        "TP",
        "FP",
        "FN",
        "TN",
        "Precision",
        "Recall",
        "F1",
      ],
      true,
    );
    const body = metrics.createTBody();
    const policies = [["Theo ngưỡng", evaluate(labels, decisions)]];
    if (adjusted) policies.push(["Sau ưu tiên", evaluate(labels, capped)]);
    for (const [name, row] of policies) {
      addRow(body, [
        name,
        row.cost,
        row.tp,
        row.fp,
        row.fn,
        row.tn,
        percent(row.precision),
        percent(row.recall),
        percent(row.f1),
      ]);
    }
    const [name, applied] = policies.at(-1);
    addRow(
      matrix.createTHead(),
      ["Ma trận · " + name, "Không đề xuất", "Đề xuất"],
      true,
    );
    const rows = matrix.createTBody();
    addRow(rows, ["Thực tế neg", applied.tn + " · TN", applied.fp + " · FP"]);
    addRow(rows, ["Thực tế pos", applied.fn + " · FN", applied.tp + " · TP"]);
  }

  function recalculate() {
    if (batch === null) return;
    const tau = Number(threshold.value);
    const n = batch.scores.length;
    const k = getCapacity(n);
    const valid =
      threshold.value !== "" &&
      Number.isFinite(tau) &&
      0 <= tau &&
      tau <= 1 &&
      k !== null;
    decisionError.hidden = valid;
    result.hidden = !valid;
    download.disabled = !valid;
    if (!valid) {
      current = null;
      decisionError.textContent =
        "Nhập ngưỡng từ 0 đến 1. Công suất là phần trăm từ 0 đến 100 (tối đa hai chữ số thập phân) hoặc số nguyên từ 0 đến N.";
      return;
    }
    const decisions = batch.scores.map((score) => score >= tau);
    const chosen = decisions.flatMap((flag, index) => (flag ? [index] : []));
    const m = chosen.length;
    const adjusted = prioritize.checked && m > k;
    let capped = decisions;
    if (adjusted) {
      chosen.sort((a, b) => batch.scores[b] - batch.scores[a] || a - b);
      const best = new Set(chosen.slice(0, k));
      capped = decisions.map((_, index) => best.has(index));
    }
    current = { tau, k, decisions, capped, adjusted };
    fillStats(el("live-stats"), [
      ["Tổng số dòng N", whole.format(n)],
      ["Ngưỡng τ", String(tau)],
      ["Công suất K", whole.format(k)],
      ["Đề xuất theo ngưỡng M", whole.format(m)],
      ["Không đề xuất theo ngưỡng", whole.format(n - m)],
      ["M / K", k === 0 ? "— (K = 0)" : percent(m / k)],
      ["Công suất còn lại", whole.format(Math.max(k - m, 0))],
      ...(adjusted ? [["Đề xuất sau ưu tiên", whole.format(k)]] : []),
    ]);
    const feasible = el("live-feasible");
    feasible.className = m <= k ? "note good" : "note bad";
    feasible.textContent =
      m <= k
        ? "Khả thi: M ≤ K."
        : "Không khả thi theo ngưỡng: vượt " +
          whole.format(m - k) +
          " lượt." +
          (adjusted ? " Chính sách ưu tiên đưa số đề xuất về K." : "");
    const rows = el("live-rows").tBodies[0];
    rows.replaceChildren();
    for (const [index, score] of batch.scores.entries()) {
      addRow(rows, [
        index + 1,
        score.toFixed(8),
        decisions[index] ? "Kiểm tra" : "Không đề xuất",
        adjusted ? (capped[index] ? "Kiểm tra" : "Không đề xuất") : "—",
      ]);
    }
    drawEvaluation(batch.labels, decisions, capped, adjusted);
  }

  async function requestPrediction(getBody) {
    batch = current = null;
    result.hidden = true;
    download.disabled = upload.disabled = sample.disabled = true;
    decisionError.hidden = true;
    status.className = "note";
    status.textContent = "Đang kiểm tra CSV và chạy checkpoint…";
    try {
      const body = await getBody();
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "text/csv" },
        body,
      });
      const data = await response.json();
      if (!response.ok)
        throw new Error(data.error || "Dự đoán chưa thành công.");
      batch = data;
      threshold.value = data.threshold;
      mode.value = "percent";
      capacity.value = "10";
      capacity.max = "100";
      capacity.step = "0.01";
      prioritize.checked = false;
      status.className = "note good";
      status.textContent =
        "Đã dự đoán " +
        whole.format(data.scores.length) +
        " dòng · " +
        data.model_version;
      recalculate();
    } catch (error) {
      status.className = "note bad";
      status.textContent = error.message;
    } finally {
      upload.disabled = sample.disabled = false;
    }
  }

  upload.addEventListener("click", () => {
    const selected = file.files[0];
    if (!selected || selected.size > 4 * 1024 * 1024) {
      status.className = "note bad";
      status.textContent = selected
        ? "Tệp CSV vượt giới hạn 4 MiB."
        : "Chọn một tệp CSV hoặc dùng CSV mẫu Validation.";
      return;
    }
    requestPrediction(() => selected.arrayBuffer());
  });

  sample.addEventListener("click", () =>
    requestPrediction(async () => {
      const response = await fetch(sampleUrl);
      if (!response.ok) throw new Error("Thiếu CSV mẫu Validation.");
      return response.arrayBuffer();
    }),
  );

  for (const control of [threshold, capacity, prioritize])
    control.addEventListener("input", recalculate);
  mode.addEventListener("change", () => {
    const asCount = mode.value === "count";
    capacity.value = asCount
      ? Math.floor((batch?.scores.length || 0) / 10)
      : "10";
    capacity.max = asCount ? batch?.scores.length || 0 : 100;
    capacity.step = asCount ? "1" : "0.01";
    recalculate();
  });

  download.addEventListener("click", () => {
    if (!batch || !current) return;
    const { tau, k, decisions, capped, adjusted } = current;
    const data =
      [
        "row,aps_positive_score,threshold,threshold_action,capacity_action,capacity_limit,model_version,policy",
        ...batch.scores.map((score, index) =>
          [
            index + 1,
            score,
            tau,
            Number(decisions[index]),
            adjusted ? Number(capped[index]) : "",
            k,
            batch.model_version,
            adjusted ? "threshold_then_top_k" : "threshold",
          ].join(","),
        ),
      ].join("\r\n") + "\r\n";
    const objectUrl = URL.createObjectURL(
      new Blob([data], { type: "text/csv;charset=utf-8" }),
    );
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = "scania_aps_predictions.csv";
    link.click();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
  });
})();
