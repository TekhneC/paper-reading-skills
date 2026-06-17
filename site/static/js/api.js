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
  if (!response.ok) throw new Error(`审批失败：${response.status} ${await response.text()}`);
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

export async function deletePaper(paperKey) {
  const response = await fetch("/api/papers/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ paper_key: paperKey }),
  });
  if (!response.ok) throw new Error(`删除文献失败：${response.status} ${await response.text()}`);
  return response.json();
}

export async function sendCoreadingMessage({ themeId, paperKey, body, intent = "open_question", sourceView = "coreading_chat" }) {
  const response = await fetch("/api/coreading/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ theme_id: themeId, paper_key: paperKey, body, intent, source_view: sourceView }),
  });
  if (!response.ok) throw new Error(`共读消息发送失败：${response.status} ${await response.text()}`);
  return response.json();
}

export async function sendDeepReadInteractionMessage({
  paperKey,
  body,
  interactionMode = "follow_up",
  sourceView = "deep_read_panel",
}) {
  const response = await fetch("/api/deep-read-interactions/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      paper_key: paperKey,
      body,
      interaction_mode: interactionMode,
      source_view: sourceView,
    }),
  });
  if (!response.ok) throw new Error(`精读交互消息写入失败：${response.status} ${await response.text()}`);
  return response.json();
}

export async function deleteDeepReadInteractionMessage({ paperKey, messageId }) {
  const response = await fetch("/api/deep-read-interactions/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ paper_key: paperKey, message_id: messageId }),
  });
  if (!response.ok) throw new Error(`删除精读交互消息失败：${response.status} ${await response.text()}`);
  return response.json();
}

export async function clearDeepReadInteractions({ paperKey }) {
  const response = await fetch("/api/deep-read-interactions/clear", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ paper_key: paperKey }),
  });
  if (!response.ok) throw new Error(`清空精读交互历史失败：${response.status} ${await response.text()}`);
  return response.json();
}

export async function triggerDailyArchive(date = "", options = {}) {
  const response = await fetch("/api/daily/run", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ ...(date ? { date } : {}), ...options }),
  });
  if (!response.ok) throw new Error(`生成当日归档失败：${response.status} ${await response.text()}`);
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
