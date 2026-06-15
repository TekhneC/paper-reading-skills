import {
  approveDeepRead,
  fetchDashboard,
  saveMarkdown,
  saveMindMap,
  sendCoreadingMessage,
  triggerDailyArchive,
  updatePaperState,
} from "./api.js";
import { escapeHtml, renderMarkdown } from "./markdown.js";
import { bindMindMapEditor, readMindMapData, renderMindMap } from "./mindmap.js";
import { currentItems, jumpTo, paperByKey, selectedItem, setDashboard, state, themeById } from "./state.js";

const appShell = document.querySelector("#appShell");
const summaryGrid = document.querySelector("#summaryGrid");
const itemList = document.querySelector("#itemList");
const detailHeader = document.querySelector("#detailHeader");
const contentPanel = document.querySelector("#contentPanel");
const searchInput = document.querySelector("#searchInput");
const refreshButton = document.querySelector("#refreshButton");
const sidebarToggle = document.querySelector("#sidebarToggle");
const dailyWorkflowButton = document.querySelector("#dailyWorkflowButton");
const modeButtons = [...document.querySelectorAll(".segment")];
const viewButtons = [...document.querySelectorAll(".view-tab")];

async function boot() {
  bindEvents();
  await load();
}

function bindEvents() {
  refreshButton.addEventListener("click", load);
  dailyWorkflowButton.addEventListener("click", handleDailyWorkflow);
  sidebarToggle.addEventListener("click", () => {
    state.sidebarCollapsed = !state.sidebarCollapsed;
    appShell.classList.toggle("sidebar-collapsed", state.sidebarCollapsed);
  });

  searchInput.addEventListener("input", () => {
    state.query = searchInput.value;
    state.selectedId = currentItems()[0]?.id || null;
    render();
  });

  modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      state.selectedId = null;
      state.view = "overview";
      setActiveButtons();
      state.selectedId = currentItems()[0]?.id || null;
      render();
    });
  });

  viewButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.view = button.dataset.view;
      setActiveButtons();
      renderDetail();
    });
  });
}

async function load() {
  try {
    refreshButton.disabled = true;
    setDashboard(await fetchDashboard());
    render();
    toast("数据已刷新");
  } catch (error) {
    contentPanel.innerHTML = `<div class="empty-state"><h2>加载失败</h2><p>${escapeHtml(error.message)}</p></div>`;
  } finally {
    refreshButton.disabled = false;
  }
}

function render() {
  setActiveButtons();
  renderSummary();
  renderList();
  renderDetail();
}

function setActiveButtons() {
  modeButtons.forEach((button) => button.classList.toggle("is-active", button.dataset.mode === state.mode));
  viewButtons.forEach((button) => button.classList.toggle("is-active", button.dataset.view === state.view));
}

function renderSummary() {
  const summary = state.dashboard?.summary || {};
  const metrics = [
    ["Todo", summary.todo_count || 0],
    ["文献", summary.paper_count || 0],
    ["已批", summary.approved_count || 0],
    ["精读", summary.deep_read_count || 0],
    ["归档", summary.archive_count || 0],
    ["消息", summary.message_count || 0],
  ];
  summaryGrid.innerHTML = metrics
    .map(([label, value]) => `<div class="metric"><strong>${value}</strong><span>${label}</span></div>`)
    .join("");
}

function renderList() {
  const items = currentItems();
  if (!items.length) {
    itemList.innerHTML = document.querySelector("#emptyStateTemplate").innerHTML;
    return;
  }

  itemList.innerHTML = items
    .map((item) => {
      const active = item.id === selectedItem()?.id ? " is-active" : "";
      return `<button class="list-item${active}" data-id="${escapeHtml(item.id)}">
        <span class="list-title">${escapeHtml(item.title)}</span>
        <span class="list-meta">
          <span>${escapeHtml(item.id)}</span>
          ${item.subtitle ? `<span>${escapeHtml(item.subtitle)}</span>` : ""}
          <span class="badge ${statusClass(item.status)}">${escapeHtml(item.status || "")}</span>
        </span>
      </button>`;
    })
    .join("");

  itemList.querySelectorAll(".list-item").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedId = button.dataset.id;
      render();
    });
  });
}

function renderDetail() {
  const item = selectedItem();
  if (!item) {
    detailHeader.innerHTML = "";
    contentPanel.innerHTML = document.querySelector("#emptyStateTemplate").innerHTML;
    return;
  }

  if (state.view === "source" || (item.kind !== "paper" && ["quick", "deep"].includes(state.view))) {
    state.view = "overview";
    setActiveButtons();
  }

  renderHeader(item);
  const renderers = {
    overview: renderOverview,
    quick: renderQuickRead,
    deep: renderDeepRead,
    map: renderMap,
    interact: renderInteraction,
  };
  contentPanel.innerHTML = renderers[state.view](item);
  bindDetailActions(item);
}

function renderHeader(item) {
  const raw = item.raw;
  const isPaper = item.kind === "paper";
  const approved = isPaper && raw.approval;
  const canApprove = isPaper && !approved;
  detailHeader.innerHTML = `<div class="title-row">
    <div>
      <p class="eyebrow">${escapeHtml(item.kind)}</p>
      <h2>${escapeHtml(item.title)}</h2>
      <div class="list-meta">
        <span class="badge ${statusClass(item.status)}">${escapeHtml(item.status || "")}</span>
        ${isPaper && raw.recommended_action ? `<span class="badge">${escapeHtml(raw.recommended_action)}</span>` : ""}
        ${approved ? `<span class="badge good">deep_read_approved</span>` : ""}
      </div>
    </div>
    <div class="actions">
      ${item.kind === "todo" ? `<button class="primary-button" id="handleTodoButton">${todoActionLabel(item.raw)}</button>` : ""}
      ${canApprove ? `<button class="primary-button" id="approveButton">批准精读</button>` : ""}
      ${isPaper ? renderStateSelect(raw) : ""}
      <button class="secondary-button" id="copyIdButton">复制 ID</button>
    </div>
  </div>`;
}

function renderStateSelect(paper) {
  const states = ["queued", "quick_read_done", "deep_read_candidate", "deep_read_approved", "deep_read_done"];
  return `<label class="state-picker">
    <span>状态</span>
    <select id="stateSelect">
      ${states.map((status) => `<option value="${status}" ${paper.status === status ? "selected" : ""}>${status}</option>`).join("")}
    </select>
  </label>`;
}

function todoActionLabel(todo) {
  if (todo.action === "daily_triage") return "生成当日归档";
  return "处理该事项";
}

function renderOverview(item) {
  if (item.kind === "todo") return renderTodoOverview(item.raw);
  if (item.kind === "archive" || item.kind === "archive-summary") return renderArchiveOverview(item.raw);
  if (item.kind === "theme") return renderThemeOverview(item.raw);
  if (item.kind === "message") return renderMessageOverview(item.raw);
  const paper = item.raw;
  return `<div class="meta-grid">
    ${meta("Paper key", paper.paper_key)}
    ${meta("Year", paper.year)}
    ${meta("Venue", paper.venue)}
    ${meta("Status", paper.status)}
    ${meta("Evidence", paper.evidence_status)}
    ${meta("PDF", paper.pdf?.available ? "available" : "missing")}
  </div>
  <h3>阅读资产</h3>
  <div class="meta-grid">
    ${asset("Quick read", paper.quick_read)}
    ${asset("Deep read", paper.deep_read)}
    ${asset("Approval", paper.approval ? { path: `state/approvals/${paper.paper_key}.json` } : null)}
    ${asset("Workflow state", paper.workflow_state?.updated_at ? { path: "state/workflow_state.json" } : null)}
  </div>
  <h3>机器摘要</h3>
  ${jsonBlock({
    recommended_action: paper.recommended_action,
    decision_label: paper.decision_label,
    suggested_deep_read_focus: paper.quick_read_json?.suggested_deep_read_focus,
    key_takeaway: paper.deep_read_json?.key_takeaway,
  })}`;
}

function renderTodoOverview(todo) {
  const linkedPaper = todo.paper_key ? paperByKey(todo.paper_key) : null;
  return `<div class="todo-layout">
    <section>
      <div class="meta-grid">
        ${meta("Action", todo.action)}
        ${meta("Priority", todo.priority)}
        ${meta("Status", todo.status)}
        ${meta("Paper", todo.paper_key)}
        ${meta("Theme", todo.theme_id)}
      </div>
      <h3>原因</h3>
      <p>${escapeHtml(todo.reason || "未记录。")}</p>
    </section>
    <section>
      <h3>当日阅读</h3>
      ${renderMarkdown(state.dashboard?.latest_daily?.digest?.content || "暂无当日归档。可在左侧底部点击“触发 Daily”生成。")}
    </section>
    ${linkedPaper ? `<section><h3>关联文献</h3>${renderPaperMini(linkedPaper)}</section>` : ""}
  </div>`;
}

function renderThemeOverview(theme) {
  return `<div class="meta-grid">
    ${asset("Theme state", theme.theme_state)}
    ${asset("Comparison matrix", theme.comparison_matrix)}
    ${asset("Synthesis report", theme.synthesis_report)}
  </div>
  ${renderMarkdown(theme.synthesis_report?.content || theme.theme_state?.content || "")}`;
}

function renderArchiveOverview(run) {
  return `<div class="meta-grid">
    ${meta("Date", run.date)}
    ${asset("Digest", run.digest)}
  </div>
  ${renderMarkdown(run.digest?.content || "")}`;
}

function renderMessageOverview(message) {
  return `<div class="chat-panel">
    ${renderChatMessages([message])}
  </div>`;
}

function renderQuickRead(item) {
  return renderMarkdownEditor(item.raw, "quick");
}

function renderDeepRead(item) {
  return renderMarkdownEditor(item.raw, "deep");
}

function renderMarkdownEditor(paper, docType) {
  const record = docType === "quick" ? paper.quick_read : paper.deep_read;
  const title = docType === "quick" ? "快读 Markdown" : "精读 Markdown";
  const placeholder = docType === "quick" ? "这里编辑 quick_read.md" : "这里编辑 deep_read.md";
  const content = record?.content || "";
  return `<div class="split-reader" id="splitReader">
    <section class="editor-pane">
      <div class="pane-toolbar">
        <h3>${title}</h3>
        <div class="toolbar-actions">
          <button class="secondary-button" id="toggleMarkdownSourceButton">源码</button>
          <button class="primary-button" id="saveMarkdownButton" data-doc-type="${docType}" data-path="${escapeHtml(record?.path || "")}">保存 Markdown</button>
        </div>
      </div>
      <div class="rendered-markdown-editor" id="renderedMarkdownEditor" contenteditable="true" spellcheck="false" aria-label="${title}">
        ${renderMarkdown(content)}
      </div>
      <textarea class="markdown-source-editor is-hidden" id="markdownEditor" spellcheck="false" placeholder="${placeholder}">${escapeHtml(content)}</textarea>
    </section>
    <section class="source-pane" id="sourcePane">
      <div class="pane-toolbar">
        <h3>原文对照</h3>
        <button class="secondary-button" id="toggleSourcePaneButton">收起原文</button>
      </div>
      <div class="source-body" id="sourceBody">${renderSourceFrame(paper)}</div>
    </section>
  </div>`;
}

function renderSourceFrame(paper) {
  if (!paper.pdf?.available) {
    return `<div class="empty-state"><h2>没有可打开的原文 PDF</h2><p>当 reading queue 或 source cache 包含可访问 PDF 路径后，这里会以内嵌方式显示。</p></div>`;
  }
  return `<iframe class="source-frame" src="${paper.pdf.url}" title="Original PDF"></iframe>`;
}

function renderMap(item) {
  return renderMindMap(item);
}

function renderInteraction(item) {
  const paper = item.kind === "paper" ? item.raw : item.raw.paper_key ? paperByKey(item.raw.paper_key) : null;
  const theme = item.kind === "theme" ? item.raw : themeById(item.raw.theme_id || "long_memory_multiturn");
  const themeId = theme?.theme_id || item.raw.theme_id || "long_memory_multiturn";
  const paperKey = paper?.paper_key || item.raw.paper_key || "";
  const messages = (theme?.messages?.length ? theme.messages : state.dashboard?.messages || [])
    .filter((message) => !themeId || message.theme_id === themeId)
    .slice(-20);
  return `<div class="chat-panel">
    <div class="chat-header">
      <div>
        <h3>共读聊天</h3>
        <p class="muted">消息会写入本地 outbox，供后续桥接器或 Codex 线程消费。</p>
      </div>
      <span class="badge">${escapeHtml(themeId)}</span>
    </div>
    <div class="chat-log" id="chatLog">${renderChatMessages(messages)}</div>
    <div class="chat-composer">
      <input id="messageTheme" value="${escapeHtml(themeId)}" aria-label="Theme ID" />
      <input id="messagePaper" value="${escapeHtml(paperKey)}" aria-label="Paper key" placeholder="paper key" />
      <textarea id="messageBody" rows="3" placeholder="输入要转发给共读流程的问题、判断或下一步请求。"></textarea>
      <button class="primary-button" id="sendMessageButton">发送</button>
    </div>
  </div>`;
}

function renderChatMessages(messages) {
  if (!messages.length) return `<div class="empty-state compact"><p>暂无共读消息。</p></div>`;
  return messages
    .map((message) => `<article class="chat-message">
      <div class="chat-meta">
        <span>${escapeHtml(message.sender || "local_site")}</span>
        <span>${escapeHtml(message.created_at || "")}</span>
      </div>
      <p>${escapeHtml(message.body || "")}</p>
      <div class="list-meta">
        <span class="badge">${escapeHtml(message.forward_status || "")}</span>
        ${message.paper_key ? `<span>${escapeHtml(message.paper_key)}</span>` : ""}
      </div>
    </article>`)
    .join("");
}

function bindDetailActions(item) {
  document.querySelector("#copyIdButton")?.addEventListener("click", async () => {
    await navigator.clipboard.writeText(item.id);
    toast("ID 已复制");
  });

  document.querySelector("#handleTodoButton")?.addEventListener("click", () => {
    if (item.raw.action === "daily_triage") {
      handleDailyTodo();
      return;
    }
    jumpTo(item.raw.target);
    setActiveButtons();
    state.selectedId = currentItems().find((candidate) => candidate.id === state.selectedId)?.id || currentItems()[0]?.id || null;
    render();
  });

  document.querySelector("#approveButton")?.addEventListener("click", async () => {
    const note = window.prompt("审批备注（可留空）", "");
    try {
      await approveDeepRead(item.raw, note || "");
      await load();
      toast("已写入精读审批并同步 state");
    } catch (error) {
      toast(error.message);
    }
  });

  document.querySelector("#stateSelect")?.addEventListener("change", async (event) => {
    try {
      await updatePaperState(item.raw.paper_key, event.target.value, "updated from local site");
      await load();
      toast("状态已同步到本地 state");
    } catch (error) {
      toast(error.message);
      event.target.value = item.raw.status;
    }
  });

  document.querySelector("#toggleMarkdownSourceButton")?.addEventListener("click", (event) => {
    const rendered = document.querySelector("#renderedMarkdownEditor");
    const editor = document.querySelector("#markdownEditor");
    const showingSource = !editor.classList.contains("is-hidden");
    if (showingSource) {
      rendered.innerHTML = renderMarkdown(editor.value);
      rendered.classList.remove("is-hidden");
      editor.classList.add("is-hidden");
      event.currentTarget.textContent = "源码";
    } else {
      editor.value = markdownFromRendered(rendered);
      editor.classList.remove("is-hidden");
      rendered.classList.add("is-hidden");
      event.currentTarget.textContent = "渲染";
    }
  });

  document.querySelector("#saveMarkdownButton")?.addEventListener("click", async (event) => {
    const editor = document.querySelector("#markdownEditor");
    const rendered = document.querySelector("#renderedMarkdownEditor");
    const content = editor && !editor.classList.contains("is-hidden") ? editor.value : markdownFromRendered(rendered);
    const docType = event.currentTarget.dataset.docType;
    const path = event.currentTarget.dataset.path;
    try {
      await saveMarkdown({ path, paperKey: item.raw.paper_key, docType, content });
      await load();
      state.mode = "papers";
      state.selectedId = item.raw.paper_key;
      state.view = docType;
      render();
      toast("Markdown 已保存");
    } catch (error) {
      toast(error.message);
    }
  });

  document.querySelector("#saveMindMapButton")?.addEventListener("click", async () => {
    try {
      await saveMindMap({
        targetType: mindMapTargetType(item),
        targetId: mindMapTargetId(item),
        data: readMindMapData(),
      });
      await load();
      state.view = "map";
      render();
      toast("思路图已保存到本地输出");
    } catch (error) {
      toast(error.message);
    }
  });

  document.querySelector("#sendMessageButton")?.addEventListener("click", async () => {
    const body = document.querySelector("#messageBody").value.trim();
    const themeId = document.querySelector("#messageTheme").value.trim();
    const paperKey = document.querySelector("#messagePaper").value.trim();
    try {
      await sendCoreadingMessage({ themeId, paperKey, body });
      await load();
      state.mode = "themes";
      state.selectedId = themeId;
      state.view = "interact";
      render();
      toast("消息已写入本地共读队列");
    } catch (error) {
      toast(error.message);
    }
  });

  document.querySelector("#toggleSourcePaneButton")?.addEventListener("click", (event) => {
    const split = document.querySelector("#splitReader");
    split.classList.toggle("source-collapsed");
    event.currentTarget.textContent = split.classList.contains("source-collapsed") ? "展开原文" : "收起原文";
  });

  bindMindMapEditor();
}

async function handleDailyTodo() {
  await handleDailyWorkflow();
}

async function handleDailyWorkflow() {
  try {
    await triggerDailyArchive();
    await load();
    state.mode = "archives";
    state.selectedId = state.dashboard?.latest_daily?.date || currentItems()[0]?.id || null;
    state.view = "overview";
    render();
    toast("已生成当日归档并同步本地状态");
  } catch (error) {
    toast(error.message);
  }
}

function markdownFromRendered(root) {
  if (!root) return "";
  const article = root.querySelector(".markdown") || root;
  const blocks = [...article.children].map(blockToMarkdown).filter(Boolean);
  const markdown = blocks.join("\n\n").trim();
  return markdown ? `${markdown}\n` : "";
}

function blockToMarkdown(node) {
  const tag = node.tagName?.toLowerCase();
  if (!tag) return "";
  if (/^h[1-4]$/.test(tag)) return `${"#".repeat(Number(tag.slice(1)))} ${node.textContent.trim()}`;
  if (tag === "ul") {
    return [...node.querySelectorAll(":scope > li")]
      .map((li) => `- ${inlineMarkdown(li)}`)
      .join("\n");
  }
  if (tag === "pre") return `\`\`\`\n${node.textContent.trim()}\n\`\`\``;
  if (tag === "table") return tableToMarkdown(node);
  return inlineMarkdown(node);
}

function inlineMarkdown(node) {
  return node.textContent.replace(/\n{2,}/g, "\n").trim();
}

function tableToMarkdown(table) {
  const rows = [...table.querySelectorAll("tr")].map((row) =>
    [...row.children].map((cell) => cell.textContent.trim().replace(/\|/g, "\\|")),
  );
  if (!rows.length) return "";
  const header = `| ${rows[0].join(" | ")} |`;
  const divider = `| ${rows[0].map(() => "---").join(" | ")} |`;
  const body = rows.slice(1).map((row) => `| ${row.join(" | ")} |`);
  return [header, divider, ...body].join("\n");
}

function mindMapTargetType(item) {
  if (item.kind === "theme") return "theme";
  if (item.kind === "archive" || item.kind === "archive-summary") return "archive";
  return "paper";
}

function mindMapTargetId(item) {
  if (item.kind === "theme") return item.raw.theme_id;
  if (item.kind === "archive" || item.kind === "archive-summary") return item.raw.date;
  return item.raw.paper_key;
}

function renderPaperMini(paper) {
  return `<div class="meta-grid">
    ${meta("Title", paper.title)}
    ${meta("Status", paper.status)}
    ${meta("Recommendation", paper.recommended_action)}
    ${meta("Evidence", paper.evidence_status)}
  </div>`;
}

function meta(label, value) {
  return `<div class="meta-cell"><span>${escapeHtml(label)}</span>${escapeHtml(value ?? "未记录")}</div>`;
}

function asset(label, record) {
  const value = record?.path || "missing";
  const cls = record ? "good" : "warn";
  return `<div class="meta-cell"><span>${escapeHtml(label)}</span><span class="badge ${cls}">${escapeHtml(value)}</span></div>`;
}

function jsonBlock(value) {
  return `<pre><code>${escapeHtml(JSON.stringify(value, null, 2))}</code></pre>`;
}

function statusClass(status = "") {
  if (status.includes("done") || status.includes("approved") || status.includes("ready") || status.includes("queued_for")) return "good";
  if (status.includes("missing") || status.includes("open")) return "warn";
  return "";
}

function toast(message) {
  const existing = document.querySelector(".toast");
  existing?.remove();
  const node = document.createElement("div");
  node.className = "toast";
  node.textContent = message;
  document.body.appendChild(node);
  window.setTimeout(() => node.remove(), 2600);
}

boot();
