export async function fetchDashboard() {
  const response = await fetch("/api/dashboard", { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`加载仪表盘失败：${response.status}`);
  return response.json();
}

export async function approveDeepRead(paper, note = "") {
  const response = await fetch("/api/approvals", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      paper_key: paper.paper_key,
      title: paper.title,
      note,
      suggested_deep_read_focus: paper.quick_read_json?.suggested_deep_read_focus || [],
    }),
  });
  if (!response.ok) throw new Error(`审批失败：${response.status}`);
  return response.json();
}

export async function updatePaperState(paperKey, status, note = "") {
  const response = await fetch("/api/paper-state", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ paper_key: paperKey, status, note }),
  });
  if (!response.ok) throw new Error(`状态同步失败：${response.status} ${await response.text()}`);
  return response.json();
}

export async function sendCoreadingMessage({ themeId, paperKey, body }) {
  const response = await fetch("/api/coreading/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ theme_id: themeId, paper_key: paperKey, body }),
  });
  if (!response.ok) throw new Error(`消息转发失败：${response.status}`);
  return response.json();
}

export async function triggerDailyArchive(date = "") {
  const response = await fetch("/api/daily/run", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(date ? { date } : {}),
  });
  if (!response.ok) throw new Error(`生成当日归档失败：${response.status}`);
  return response.json();
}

export async function saveMarkdown({ path, paperKey, docType, content }) {
  const response = await fetch("/api/markdown", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, paper_key: paperKey, doc_type: docType, content }),
  });
  if (!response.ok) throw new Error(`保存 Markdown 失败：${response.status} ${await response.text()}`);
  return response.json();
}

export async function saveMindMap({ targetType, targetId, data }) {
  const response = await fetch("/api/mindmap", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ target_type: targetType, target_id: targetId, data }),
  });
  if (!response.ok) throw new Error(`保存思路图失败：${response.status} ${await response.text()}`);
  return response.json();
}
