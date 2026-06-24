import {
  approveDeepRead,
  clearDeepReadInteractions,
  deleteDeepReadInteractionMessage,
  deletePaper,
  fetchDashboard,
  saveMarkdown,
  saveMindMap,
  sendDeepReadInteractionMessage,
  sendCoreadingMessage,
  triggerDailyArchive,
  updatePaperState,
} from "./api.js?v=20260617-workflow-bridge";
import { escapeHtml, renderMarkdown } from "./markdown.js?v=20260617-workflow-bridge";
import { bindMindMapEditor, readMindMapData, renderMindMap } from "./mindmap.js?v=20260617-workflow-bridge";
import {
  bindCoreadingWorkspace,
  renderCoreadingWorkspace,
  renderMessageOverview,
  renderThemeOverview,
} from "./coreading.js?v=20260617-workflow-bridge";
import { currentItems, jumpTo, paperByKey, selectedItem, setDashboard, state, themeById } from "./state.js";

const appShell = document.querySelector("#appShell");
const paperFilterBar = document.querySelector("#paperFilterBar");
const itemList = document.querySelector("#itemList");
const detailHeader = document.querySelector("#detailHeader");
const contentPanel = document.querySelector("#contentPanel");
const searchInput = document.querySelector("#searchInput");
const refreshButton = document.querySelector("#refreshButton");
const sidebarToggle = document.querySelector("#sidebarToggle");
const dailyWorkflowButton = document.querySelector("#dailyWorkflowButton");
const dailyRunStatus = document.querySelector("#dailyRunStatus");
const modeButtons = [...document.querySelectorAll(".segment")];
const viewButtons = [...document.querySelectorAll(".view-tab")];
let dailyStatusPoll = null;
let dailyRunStatusCollapsed = window.localStorage.getItem("dailyRunStatusCollapsed") === "true";

const MODE_TABS = [
  [
    "today",
    "待办",
    (dashboard) => (dashboard?.latest_daily ? 1 : 0) + (dashboard?.todos?.length || 0) + (dashboard?.messages?.length || 0),
  ],
  ["papers", "文献", (dashboard) => dashboard?.papers?.length || 0],
  ["themes", "共读", (dashboard) => dashboard?.themes?.length || 0],
  ["archives", "归档", (dashboard) => dashboard?.daily_runs?.length || 0],
];

const PAPER_FILTERS = [
  ["all", "全部", () => true],
  ["quick_read_done", "快读", (paper) => paper.status === "quick_read_done"],
  ["pending_approval", "待批准", (paper) => isPendingDeepReadApproval(paper)],
  ["deep_read_done", "已精读", (paper) => paper.status === "deep_read_done" || Boolean(paper.deep_read)],
  ["queued", "待快读", (paper) => !paper.status || paper.status === "queued"],
];

const KIND_LABELS = {
  paper: "文献",
  todo: "待办",
  theme: "共读主题",
  archive: "每日归档",
  "archive-summary": "当日阅读",
  message: "共读消息",
};

const STATUS_LABELS = {
  queued: "待快读",
  quick_read_done: "快读完成",
  deep_read_candidate: "精读候选",
  deep_read_approved: "已批准精读",
  deep_read_done: "精读完成",
  archived: "已归档",
  ready: "已生成",
  missing: "缺失",
  open: "待处理",
  completed: "已完成",
  failed: "失败",
  running: "运行中",
  synthesis_ready: "综述就绪",
  state_only: "仅有状态",
  digest_ready: "归档就绪",
  metadata_only: "仅有元数据",
  queued_for_deep_read: "已进入精读队列",
};

const ACTION_LABELS = {
  deep_read_candidate: "建议精读",
  approve_deep_read: "建议精读",
  quick_read_only: "仅快读",
  archive: "建议归档",
  no_action: "暂无后续动作",
  daily_triage: "生成当日归档",
};

const DECISION_LABELS = {
  strong_candidate: "强候选",
  candidate: "候选",
  quick_read_only: "仅快读",
  already_done: "已完成",
  not_recommended: "暂不推荐",
};

const EVIDENCE_LABELS = {
  page_numbers_available: "页码证据可用",
  abstract_metadata: "摘要元数据",
  abstract_only: "仅摘要证据",
  extracted: "已抽取正文",
  missing: "缺失",
  failed: "抽取失败",
};

const DEEP_INTERACTION_INTENTS = [
  {
    mode: "confirmation",
    label: "确认理解",
    template: "请基于原文证据确认我的理解是否正确，并按“基本正确 / 部分正确 / 证据不足 / 与原文不符”回答。",
  },
  {
    mode: "clarification",
    label: "澄清概念",
    template: "请解释当前精读报告中的一个概念、图示或方法细节，并区分论文明确说明、合理推断和仍不确定之处。",
  },
  {
    mode: "follow_up",
    label: "延伸问题",
    template: "请基于这篇论文的精读报告回答一个延伸问题。",
  },
  {
    mode: "divergent_thinking",
    label: "研究发散",
    template: "请从这篇论文出发，提出与我的研究相关的设计启发、比较维度或实验想法，并清楚标注哪些是推测。",
  },
];

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
  renderModeCounts();
  renderPaperFilterBar();
  renderDailyRunStatus();
}

function renderModeCounts() {
  MODE_TABS.forEach(([mode, label, countFn]) => {
    const button = modeButtons.find((candidate) => candidate.dataset.mode === mode);
    if (!button) return;
    button.innerHTML = `<span class="segment-label">${escapeHtml(label)}</span><strong class="segment-count">${countFn(state.dashboard || {})}</strong>`;
  });
}

function renderPaperFilterBar() {
  if (!paperFilterBar) return;
  if (state.mode !== "papers") {
    paperFilterBar.innerHTML = "";
    paperFilterBar.hidden = true;
    return;
  }

  paperFilterBar.hidden = false;
  const papers = state.dashboard?.papers || [];
  paperFilterBar.innerHTML = PAPER_FILTERS.map(([filter, label, predicate]) => {
    const active = state.paperFilter === filter ? " is-active" : "";
    const count = papers.filter(predicate).length;
    return `<button class="filter-chip${active}" type="button" data-paper-filter="${escapeHtml(filter)}">
      <span>${escapeHtml(label)}</span><strong>${count}</strong>
    </button>`;
  }).join("");

  paperFilterBar.querySelectorAll("[data-paper-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.paperFilter = button.dataset.paperFilter || "all";
      state.selectedId = currentItems()[0]?.id || null;
      render();
    });
  });
}

function renderDailyRunStatus() {
  if (!dailyRunStatus) return;
  const status = state.dashboard?.daily_run_status;
  const logPath = status?.log_path || state.dashboard?.repo?.daily_run_log || "state/daily_run_log.jsonl";
  const logHref = `/api/file?path=${encodeURIComponent(logPath)}`;
  if (dailyRunStatusCollapsed && status?.status !== "running") {
    dailyRunStatus.innerHTML = `<a class="daily-log-link" href="${escapeHtml(logHref)}" target="_blank" rel="noreferrer">查看 codex daily 日志</a>`;
    return;
  }
  if (!status) {
    dailyRunStatus.innerHTML = `<p class="muted compact-text">暂无 Daily 运行记录。</p>`;
    return;
  }
  const statusBadge = status.status === "completed" ? "good" : status.status === "running" ? "" : "warn";
  const logs = status.logs || [];
  const latestLog = logs[logs.length - 1];
  const canClose = status.status && status.status !== "running";
  dailyRunStatus.innerHTML = `<div class="daily-status-card ${status.status === "running" ? "is-running" : ""}">
    <div class="daily-status-head">
      <span class="badge ${statusBadge}">${escapeHtml(status.status || "unknown")}</span>
      <span class="daily-status-date">${escapeHtml(status.date || "")}</span>
    </div>
    ${canClose ? `<button class="daily-status-close" id="closeDailyStatusButton" type="button" aria-label="收起 Daily 运行状态">×</button>` : ""}
    <strong>${escapeHtml(status.step || "daily")}</strong>
    <p>${escapeHtml(status.message || latestLog?.message || "暂无状态消息。")}</p>
    <small>${escapeHtml(status.updated_at || "")}</small>
    <a class="daily-status-log-inline" href="${escapeHtml(logHref)}" target="_blank" rel="noreferrer">查看 codex daily 日志</a>
  </div>`;
  document.querySelector("#closeDailyStatusButton")?.addEventListener("click", () => {
    dailyRunStatusCollapsed = true;
    window.localStorage.setItem("dailyRunStatusCollapsed", "true");
    renderDailyRunStatus();
  });
}

function renderDailyDebugPanel() {
  const status = state.dashboard?.daily_run_status;
  if (!status) return "";
  const logs = status.logs || [];
  const rows = logs
    .slice(-18)
    .reverse()
    .map((log) => `<tr>
      <td>${escapeHtml(log.created_at || "")}</td>
      <td>${escapeHtml(log.step || "")}</td>
      <td>${escapeHtml(log.message || "")}</td>
    </tr>`)
    .join("");
  return `<section class="daily-debug-panel">
    <div class="daily-debug-header">
      <div>
        <h3>Daily 运行状态</h3>
        <p class="muted">外部 Codex 调用 <code>$daily-paper-triage</code> 的状态、产物校验与最近日志。</p>
      </div>
      <span class="badge ${status.status === "completed" ? "good" : status.status === "failed" ? "warn" : ""}">${escapeHtml(status.status || "unknown")}</span>
    </div>
    <div class="meta-grid">
      ${meta("Run ID", status.run_id)}
      ${meta("Date", status.date)}
      ${meta("Step", status.step)}
      ${meta("Log", status.log_path)}
      ${meta("Codex", status.codex_status)}
      ${meta("Archive", status.archive_path)}
    </div>
    ${status.message ? `<p>${escapeHtml(status.message)}</p>` : ""}
    ${status.missing_outputs?.length ? `<p class="daily-error">缺少产物：${escapeHtml(status.missing_outputs.join(", "))}</p>` : ""}
    ${
      status.codex_reply
        ? `<details class="daily-codex-reply">
            <summary>查看 Codex 返回 / 报错</summary>
            <pre><code>${escapeHtml(compactText(status.codex_reply, 8000))}</code></pre>
          </details>`
        : ""
    }
    <details class="daily-log-table" open>
      <summary>最近日志</summary>
      <table>
        <thead><tr><th>时间</th><th>步骤</th><th>消息</th></tr></thead>
        <tbody>${rows || `<tr><td colspan="3">暂无日志。</td></tr>`}</tbody>
      </table>
    </details>
  </section>`;
}

function compactText(value, limit = 4000) {
  const text = String(value || "");
  return text.length <= limit ? text : `${text.slice(0, limit).trimEnd()}\n...`;
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
          <span class="list-id">${escapeHtml(item.id)}</span>
          ${item.subtitle ? `<span>${escapeHtml(item.subtitle)}</span>` : ""}
          <span class="badge ${statusClass(item.status)}" title="${escapeHtml(item.status || "")}">${escapeHtml(labelForStatus(item.status))}</span>
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
  const nextAction = isPaper ? nextActionForPaper(raw) : "";
  detailHeader.innerHTML = `<div class="title-row">
    <div>
      <p class="eyebrow">${escapeHtml(kindLabel(item.kind))}</p>
      <h2>${escapeHtml(item.title)}</h2>
      <div class="list-meta">
        <span class="badge ${statusClass(item.status)}" title="${escapeHtml(item.status || "")}">${escapeHtml(labelForStatus(item.status))}</span>
        ${isPaper && nextAction ? `<span class="badge neutral" title="${escapeHtml(raw.recommended_action || nextAction)}">${escapeHtml(nextAction)}</span>` : ""}
        ${approved ? `<span class="badge good">已批准精读</span>` : ""}
      </div>
    </div>
    <div class="header-actions">
      <div class="primary-actions">
        ${item.kind === "todo" ? `<button class="primary-button" id="handleTodoButton">${todoActionLabel(item.raw)}</button>` : ""}
        ${canApprove ? `<button class="primary-button" id="approveButton">批准精读</button>` : ""}
        ${isPaper ? renderStateSelect(raw) : ""}
      </div>
      <div class="secondary-actions">
        <button class="secondary-button" id="copyIdButton">复制 ID</button>
        ${isPaper ? `<button class="danger-button" id="deletePaperButton" type="button">删除本地记录</button>` : ""}
      </div>
    </div>
  </div>`;
}

function renderStateSelect(paper) {
  const states = ["queued", "quick_read_done", "deep_read_candidate", "deep_read_approved", "deep_read_done"];
  return `<label class="state-picker">
    <span>阅读状态</span>
    <select id="stateSelect">
      ${states
        .map((status) => `<option value="${status}" ${paper.status === status ? "selected" : ""}>${labelForStatus(status)}</option>`)
        .join("")}
    </select>
  </label>`;
}

function todoActionLabel(todo) {
  return ACTION_LABELS[todo.action] || "处理该事项";
}

function renderOverview(item) {
  if (item.kind === "todo") return renderTodoOverview(item.raw);
  if (item.kind === "archive" || item.kind === "archive-summary") return renderArchiveOverview(item.raw);
  if (item.kind === "theme") return renderThemeOverview(item.raw);
  if (item.kind === "message") return renderMessageOverview(item.raw);
  const paper = item.raw;
  return `<div class="overview-stack">
    <section class="overview-section">
      <div class="section-heading">
        <h3>文献概况</h3>
        <span class="badge ${paper.pdf?.available ? "good" : "warn"}">${paper.pdf?.available ? "PDF 可用" : "PDF 缺失"}</span>
      </div>
      <div class="meta-grid">
        ${meta("Paper key", paper.paper_key)}
        ${meta("年份", paper.year)}
        ${meta("会议 / 期刊", paper.venue)}
        ${meta("阅读状态", labelForStatus(paper.status))}
        ${meta("证据状态", labelForEvidence(paper.evidence_status))}
      </div>
    </section>

    <section class="overview-section">
      <div class="section-heading">
        <h3>下一步判断</h3>
      </div>
      ${insightList([
        ["建议动作", nextActionForPaper(paper)],
        ["判定标签", labelForDecision(paper.decision_label)],
        ["精读关注点", paper.quick_read_json?.suggested_deep_read_focus],
        ["精读要点", paper.deep_read_json?.key_takeaway],
      ])}
    </section>

    <section class="overview-section">
      <div class="section-heading">
        <h3>阅读资产</h3>
      </div>
      <div class="asset-grid">
        ${asset("快读报告", paper.quick_read)}
        ${asset("精读报告", paper.deep_read)}
        ${asset("审批记录", paper.approval ? { path: `state/approvals/${paper.paper_key}.json` } : null)}
        ${asset("流程状态", paper.workflow_state?.updated_at ? { path: "state/workflow_state.json" } : null)}
      </div>
    </section>
  </div>`;
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
      ${renderDailyDebugPanel()}
    </section>
    ${linkedPaper ? `<section><h3>关联文献</h3>${renderPaperMini(linkedPaper)}</section>` : ""}
  </div>`;
}

function renderArchiveOverview(run) {
  return `<div class="meta-grid">
    ${meta("Date", run.date)}
    ${asset("Digest", run.digest)}
  </div>
  ${renderMarkdown(run.digest?.content || "")}
  ${renderDailyDebugPanel()}`;
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
  const canInteract = docType === "deep";
  return `<div class="split-reader" id="splitReader" data-paper-key="${escapeHtml(paper.paper_key || "")}">
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
        <h3 id="readerSideTitle">原文对照</h3>
        <div class="toolbar-actions">
          ${canInteract ? `<button class="secondary-button" id="toggleDeepInteractionButton" aria-expanded="false">精读交互</button>` : ""}
          <button class="secondary-button" id="toggleSourcePaneButton" aria-expanded="true">收起原文</button>
        </div>
      </div>
      <div class="source-body" id="sourceBody">${renderSourceFrame(paper)}</div>
      ${canInteract ? renderDeepReadInteractionPanel(paper) : ""}
    </section>
  </div>`;
}

function renderSourceFrame(paper) {
  if (!paper.pdf?.available) {
    return `<div class="empty-state"><h2>没有可打开的原文 PDF</h2><p>当 reading queue 或 source cache 包含可访问 PDF 路径后，这里会以内嵌方式显示。</p></div>`;
  }
  return `<iframe class="source-frame" src="${paper.pdf.url}" title="Original PDF"></iframe>`;
}

function renderDeepReadInteractionPanel(paper) {
  const messages = paper.interaction_messages || [];
  const filteredMessages = filteredDeepInteractionMessages(messages);
  return `<div class="deep-interaction-body is-hidden" id="deepInteractionBody">
    ${renderDeepInteractionToolbar(messages, filteredMessages)}
    <div class="chat-log deep-interaction-log" id="deepInteractionLog">${renderDeepInteractionMessages(filteredMessages)}</div>
    <div class="deep-interaction-composer">
      <textarea id="deepInteractionBodyInput" rows="3" placeholder="输入要交给 deep-read-interaction 的问题；可先点上方意图作为提示。"></textarea>
      <button class="primary-button" id="sendDeepInteractionButton">触发 skill 回复</button>
    </div>
  </div>`;
}

function renderDeepInteractionToolbar(messages, filteredMessages) {
  const filters = state.deepInteractionFilters;
  return `<div class="deep-interaction-tools">
    <div class="deep-toolbar-left">
      <div class="deep-intent-chips" aria-label="精读交互意图筛选">
        ${DEEP_INTERACTION_INTENTS.map((intent) => renderDeepIntentButton(intent, filters.mode)).join("")}
      </div>
    </div>
    <div class="deep-toolbar-right deep-history-actions">
      <span class="muted" id="deepInteractionFilterCount">显示 ${filteredMessages.length} / ${messages.length}</span>
      <input class="deep-keyword-input" id="deepInteractionFilterQuery" value="${escapeHtml(filters.query)}" placeholder="关键词筛选" />
      <button class="danger-button" id="clearDeepInteractionsButton" type="button" ${messages.length ? "" : "disabled"}>清空历史</button>
    </div>
  </div>`;
}

function renderDeepIntentButton(intent, activeMode) {
  const active = activeMode === intent.mode ? " is-active" : "";
  return `<button class="prompt-chip deep-intent-chip${active}" type="button" data-deep-mode="${escapeHtml(intent.mode)}" data-deep-template="${escapeHtml(intent.template)}">${escapeHtml(intent.label)}</button>`;
}

function deepIntentLabel(mode) {
  return DEEP_INTERACTION_INTENTS.find((intent) => intent.mode === mode)?.label || mode || "自动判断";
}

function filteredDeepInteractionMessages(messages) {
  const filters = state.deepInteractionFilters;
  const query = filters.query.trim().toLowerCase();
  return messages.filter((message) => {
    const mode = message.interaction_mode || "follow_up";
    if (filters.mode !== "all" && mode !== filters.mode) return false;
    if (!query) return true;
    return [message.body, message.reply_markdown, message.assistant_reply, mode, message.reply_status, message.forward_status, message.message_id]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query));
  });
}

function renderDeepInteractionMessages(messages) {
  if (!messages.length) return `<div class="empty-state compact"><p>暂无精读交互消息。</p></div>`;
  const latestReplyId = [...messages].reverse().find((message) => message.reply_markdown)?.message_id;
  return messages
    .map((message) => `<article class="chat-message is-own">
      <div class="chat-meta">
        <span>你 · ${escapeHtml(deepIntentLabel(message.interaction_mode || "follow_up"))}</span>
        <span class="deep-message-actions">
          <span>${escapeHtml(message.created_at || "")}</span>
          <button class="text-danger-button" type="button" data-delete-deep-message="${escapeHtml(message.message_id || "")}">删除</button>
        </span>
      </div>
      <p>${escapeHtml(message.body || "")}</p>
    </article>
    ${
      message.reply_markdown
        ? `<article class="chat-message is-assistant">
            <details class="reply-details" ${message.message_id === latestReplyId ? "open" : ""}>
              <summary>
                <span>Codex 回复</span>
                <span class="badge ${message.codex_ok === false ? "warn" : "good"}">${escapeHtml(message.reply_status || message.forward_status || "")}</span>
              </summary>
              <div class="interaction-reply-preview">
                ${renderMarkdown(message.reply_markdown)}
              </div>
            </details>
          </article>`
        : `<article class="chat-message is-assistant"><p>等待外部 Codex 回复。</p></article>`
    }`)
    .join("");
}

function renderMap(item) {
  return renderMindMap(item);
}

function renderInteraction(item) {
  return renderCoreadingWorkspace(item, {
    dashboard: state.dashboard,
    themeById,
    paperByKey,
  });
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

  document.querySelector("#deletePaperButton")?.addEventListener("click", async () => {
    const paperKey = item.raw.paper_key;
    const confirmed = window.confirm(
      `删除 ${paperKey} 的本地派生记录？\n\n这会移除网页队列条目、workflow state、审批记录、outputs/papers 下的报告和本地缓存；不会修改 Zotero，也不会移除 Zotero todo。若 Zotero todo 仍在，下次 Daily 会重新检索并可重新快读。`,
    );
    if (!confirmed) return;
    try {
      await deletePaper(paperKey);
      state.selectedId = null;
      await load();
      state.mode = "papers";
      state.view = "overview";
      state.selectedId = currentItems()[0]?.id || null;
      render();
      toast("本地文献记录已删除；Zotero todo 未修改");
    } catch (error) {
      toast(error.message);
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
    const button = document.querySelector("#sendMessageButton");
    const body = document.querySelector("#messageBody").value.trim();
    const themeId = document.querySelector("#messageTheme").value.trim();
    const paperKey = document.querySelector("#messagePaper").value.trim();
    const intent = document.querySelector("#messageIntent")?.value || "open_question";
    const previousLabel = button?.textContent || "";
    try {
      if (button) {
        button.disabled = true;
        button.textContent = "Codex 调用中...";
      }
      toast("正在调用外部 Codex...");
      await sendCoreadingMessage({ themeId, paperKey, body, intent, sourceView: state.view });
      await load();
      state.mode = "themes";
      state.selectedId = themeId;
      state.view = "interact";
      render();
      toast("Codex 回复已更新到共读聊天");
    } catch (error) {
      toast(error.message);
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = previousLabel;
      }
    }
  });

  document.querySelector("#toggleDeepInteractionButton")?.addEventListener("click", () => {
    const split = document.querySelector("#splitReader");
    setReaderSideMode(split.classList.contains("interaction-open") ? "source" : "interaction");
  });

  document.querySelectorAll("[data-deep-template]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = document.querySelector("#deepInteractionBodyInput");
      const nextMode = state.deepInteractionFilters.mode === button.dataset.deepMode ? "all" : button.dataset.deepMode || "all";
      state.deepInteractionFilters.mode = nextMode;
      input?.focus();
      refreshDeepInteractionLog(item.raw);
    });
  });

  bindDeepInteractionHistoryControls(item.raw);

  document.querySelector("#sendDeepInteractionButton")?.addEventListener("click", async () => {
    const button = document.querySelector("#sendDeepInteractionButton");
    const body = document.querySelector("#deepInteractionBodyInput")?.value.trim() || "";
    const interactionMode = state.deepInteractionFilters.mode === "all" ? "auto" : state.deepInteractionFilters.mode;
    const previousLabel = button?.textContent || "";
    try {
      if (button) {
        button.disabled = true;
        button.textContent = "Codex 调用中...";
      }
      toast("正在调用外部 Codex...");
      await sendDeepReadInteractionMessage({
        paperKey: item.raw.paper_key,
        body,
        interactionMode,
        sourceView: "deep_read_interaction_panel",
      });
      await load();
      state.mode = "papers";
      state.selectedId = item.raw.paper_key;
      state.view = "deep";
      render();
      setReaderSideMode("interaction");
      toast("Codex 回复已更新到交互工作台");
    } catch (error) {
      toast(error.message);
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = previousLabel;
      }
    }
  });

  document.querySelector("#toggleSourcePaneButton")?.addEventListener("click", (event) => {
    const split = document.querySelector("#splitReader");
    if (split.classList.contains("interaction-open") || split.classList.contains("source-collapsed")) {
      setReaderSideMode("source");
    } else {
      setReaderSideMode("collapsed");
    }
  });

  bindMindMapEditor();
  bindCoreadingWorkspace();
  bindCoreadingSaveActions(item);
}

function bindCoreadingSaveActions(item) {
  document.querySelectorAll("[data-save-coreading-markdown]").forEach((button) => {
    button.addEventListener("click", async () => {
      const panel = button.closest("[data-coreading-panel]");
      const editor = panel?.querySelector("[data-coreading-markdown-editor]");
      const path = button.dataset.path || "";
      if (!path || !editor) {
        toast("未找到可保存的共读 Markdown");
        return;
      }
      try {
        await saveMarkdown({ path, content: markdownFromRendered(editor) });
        await load();
        state.view = "interact";
        state.selectedId = item.id;
        render();
        toast("共读 Markdown 已保存");
      } catch (error) {
        toast(error.message);
      }
    });
  });
}

function refreshDeepInteractionLog(paper) {
  const messages = paper.interaction_messages || [];
  const filtered = filteredDeepInteractionMessages(messages);
  const log = document.querySelector("#deepInteractionLog");
  const count = document.querySelector("#deepInteractionFilterCount");
  if (log) log.innerHTML = renderDeepInteractionMessages(filtered);
  if (count) count.textContent = `显示 ${filtered.length} / ${messages.length}`;
  document.querySelectorAll("[data-deep-mode]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.deepMode === state.deepInteractionFilters.mode);
  });
  bindDeepInteractionDeleteButtons(paper);
}

function bindDeepInteractionHistoryControls(paper) {
  const messages = paper.interaction_messages || [];
  document.querySelector("#deepInteractionFilterQuery")?.addEventListener("input", (event) => {
    state.deepInteractionFilters.query = event.target.value;
    refreshDeepInteractionLog(paper);
  });
  document.querySelector("#clearDeepInteractionsButton")?.addEventListener("click", async () => {
    if (!messages.length) return;
    if (!window.confirm(`清空 ${paper.paper_key} 的全部精读交互历史？此操作会重写本地 JSONL。`)) return;
    try {
      await clearDeepReadInteractions({ paperKey: paper.paper_key });
      await load();
      state.mode = "papers";
      state.selectedId = paper.paper_key;
      state.view = "deep";
      render();
      setReaderSideMode("interaction");
      toast("精读交互历史已清空");
    } catch (error) {
      toast(error.message);
    }
  });
  bindDeepInteractionDeleteButtons(paper);
}

function bindDeepInteractionDeleteButtons(paper) {
  document.querySelectorAll("[data-delete-deep-message]").forEach((button) => {
    button.addEventListener("click", async () => {
      const messageId = button.dataset.deleteDeepMessage;
      if (!messageId) return;
      if (!window.confirm("删除这一轮精读交互问答？")) return;
      try {
        await deleteDeepReadInteractionMessage({ paperKey: paper.paper_key, messageId });
        await load();
        state.mode = "papers";
        state.selectedId = paper.paper_key;
        state.view = "deep";
        render();
        setReaderSideMode("interaction");
        toast("精读交互消息已删除");
      } catch (error) {
        toast(error.message);
      }
    });
  });
}

function setReaderSideMode(mode) {
  const split = document.querySelector("#splitReader");
  const sourceButton = document.querySelector("#toggleSourcePaneButton");
  const interactionButton = document.querySelector("#toggleDeepInteractionButton");
  const title = document.querySelector("#readerSideTitle");
  if (!split || !sourceButton) return;

  split.classList.toggle("source-collapsed", mode === "collapsed");
  split.classList.toggle("interaction-open", mode === "interaction");

  const sourceVisible = mode === "source";
  sourceButton.textContent = sourceVisible ? "收起原文" : "展开原文";
  sourceButton.setAttribute("aria-expanded", String(sourceVisible));
  sourceButton.title = sourceVisible ? "收起原文对照" : "展开原文对照";

  if (interactionButton) {
    const interactionVisible = mode === "interaction";
    interactionButton.textContent = interactionVisible ? "返回原文" : "精读交互";
    interactionButton.setAttribute("aria-expanded", String(interactionVisible));
  }
  if (title) {
    const paperKey = split.dataset.paperKey || "";
    title.textContent = mode === "interaction" && paperKey ? `精读交互 · Paper ${paperKey}` : mode === "interaction" ? "精读交互" : "原文对照";
  }
}

async function handleDailyTodo() {
  await handleDailyWorkflow();
}

async function handleDailyWorkflow() {
  const previousLabel = dailyWorkflowButton?.textContent || "";
  try {
    if (dailyWorkflowButton) {
      dailyWorkflowButton.disabled = true;
      dailyWorkflowButton.textContent = "Daily 生成中...";
    }
    setOptimisticDailyRunningStatus();
    startDailyStatusPolling();
    await triggerDailyArchive();
    await load();
    state.mode = "archives";
    state.selectedId = state.dashboard?.latest_daily?.date || currentItems()[0]?.id || null;
    state.view = "overview";
    render();
    toast("已生成当日归档并同步本地状态");
  } catch (error) {
    await refreshDashboardQuietly();
    toast(error.message);
  } finally {
    stopDailyStatusPolling();
    if (dailyWorkflowButton) {
      dailyWorkflowButton.disabled = false;
      dailyWorkflowButton.textContent = previousLabel;
    }
  }
}

function setOptimisticDailyRunningStatus() {
  if (!state.dashboard) return;
  dailyRunStatusCollapsed = false;
  window.localStorage.setItem("dailyRunStatusCollapsed", "false");
  const now = new Date().toISOString();
  state.dashboard.daily_run_status = {
    ...(state.dashboard.daily_run_status || {}),
    status: "running",
    step: "request_started",
    message: "Daily 生成中：正在刷新 Zotero todo 队列并调用 $daily-paper-triage。",
    updated_at: now,
    logs: [
      ...((state.dashboard.daily_run_status || {}).logs || []),
      {
        created_at: now,
        step: "request_started",
        message: "网页端已发起 Daily workflow。",
      },
    ].slice(-80),
  };
  renderDailyRunStatus();
  if (state.mode === "today" || state.mode === "archives") renderDetail();
}

function startDailyStatusPolling() {
  stopDailyStatusPolling();
  dailyStatusPoll = window.setInterval(refreshDashboardQuietly, 2500);
}

function stopDailyStatusPolling() {
  if (!dailyStatusPoll) return;
  window.clearInterval(dailyStatusPoll);
  dailyStatusPoll = null;
}

async function refreshDashboardQuietly() {
  try {
    setDashboard(await fetchDashboard());
    render();
  } catch {
    // Keep the visible running state if the temporary status fetch fails.
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
  return [...node.childNodes].map(nodeToMarkdown).join("").replace(/\n{2,}/g, "\n").trim();
}

function nodeToMarkdown(node) {
  if (node.nodeType === Node.TEXT_NODE) return node.textContent || "";
  if (node.nodeType !== Node.ELEMENT_NODE) return "";
  const tag = node.tagName.toLowerCase();
  if (tag === "br") return "\n";
  if (tag === "code") return `\`${node.textContent || ""}\``;
  if (tag === "strong" || tag === "b") return `**${node.textContent || ""}**`;
  if (tag === "a") return `[${node.textContent || node.href}](${node.getAttribute("href") || ""})`;
  if (tag === "img") {
    const alt = node.getAttribute("alt") || "image";
    const src = node.dataset.markdownSrc || markdownPathFromImageSrc(node.getAttribute("src") || "");
    return `![${alt}](<${src}>)`;
  }
  return [...node.childNodes].map(nodeToMarkdown).join("");
}

function markdownPathFromImageSrc(src) {
  try {
    const url = new URL(src, window.location.origin);
    if (url.pathname === "/api/file") return url.searchParams.get("path") || src;
  } catch {
    return src;
  }
  return src;
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
    ${meta("标题", paper.title)}
    ${meta("阅读状态", labelForStatus(paper.status))}
    ${meta("建议动作", nextActionForPaper(paper))}
    ${meta("证据状态", labelForEvidence(paper.evidence_status))}
  </div>`;
}

function meta(label, value) {
  return `<div class="meta-cell"><span>${escapeHtml(label)}</span>${escapeHtml(value ?? "未记录")}</div>`;
}

function asset(label, record) {
  const value = record?.path || "missing";
  const cls = record ? "good" : "warn";
  return `<div class="asset-cell"><span>${escapeHtml(label)}</span><strong class="badge ${cls}">${escapeHtml(record ? "已生成" : "缺失")}</strong><small>${escapeHtml(value)}</small></div>`;
}

function insightList(rows) {
  return `<dl class="insight-list">
    ${rows
      .map(
        ([label, value]) => `<div class="insight-row">
          <dt>${escapeHtml(label)}</dt>
          <dd>${renderInsightValue(value)}</dd>
        </div>`,
      )
      .join("")}
  </dl>`;
}

function renderInsightValue(value) {
  if (Array.isArray(value)) {
    if (!value.length) return "未记录";
    return `<ul class="compact-list">${value.map((item) => `<li>${escapeHtml(item || "未记录")}</li>`).join("")}</ul>`;
  }
  return escapeHtml(value || "未记录");
}

function jsonBlock(value) {
  return `<pre><code>${escapeHtml(JSON.stringify(value, null, 2))}</code></pre>`;
}

function kindLabel(kind = "") {
  return KIND_LABELS[kind] || kind || "项目";
}

function labelForStatus(status = "") {
  if (!status) return "未记录";
  return STATUS_LABELS[status] || status;
}

function labelForAction(action = "") {
  if (!action) return "未记录";
  return ACTION_LABELS[action] || action;
}

function isPendingDeepReadApproval(paper) {
  if (!paper || paper.approval || paper.deep_read || paper.status === "deep_read_done") return false;
  return paper.status === "deep_read_candidate" || paper.recommended_action === "deep_read_candidate";
}

function nextActionForPaper(paper) {
  if (!paper) return "未记录";
  if (paper.status === "deep_read_done") return "交互精读 / 纳入共读";
  if (paper.status === "deep_read_approved") return "继续精读";
  return labelForAction(paper.recommended_action);
}

function labelForDecision(decision = "") {
  if (!decision) return "未记录";
  return DECISION_LABELS[decision] || decision;
}

function labelForEvidence(evidence = "") {
  if (!evidence) return "未记录";
  return EVIDENCE_LABELS[evidence] || evidence;
}

function statusClass(status = "") {
  if (status.includes("done") || status.includes("approved") || status.includes("ready") || status.includes("queued_for")) return "good";
  if (status.includes("missing") || status.includes("open") || status.includes("failed") || status.includes("error") || status.includes("timeout")) return "warn";
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
