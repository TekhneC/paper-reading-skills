import { escapeHtml, renderMarkdown } from "./markdown.js?v=20260617-workflow-bridge";

const DEFAULT_THEME_ID = "long_memory_multiturn";

const PROMPT_TEMPLATES = [
  {
    intent: "clarify_dimension",
    label: "澄清维度",
    body: "请基于左侧共读 Markdown，澄清当前主题下最关键的比较维度，并指出哪些维度仍缺证据。",
  },
  {
    intent: "evidence_check",
    label: "核查证据",
    body: "请检查当前综合中的强结论，区分论文明确说明、合理推断和助手批判判断。",
  },
  {
    intent: "next_step",
    label: "下一步",
    body: "请根据当前 theme_state 和 synthesis_report，给出下一轮共读最值得推进的 3 个行动。",
  },
];

export function renderThemeOverview(theme) {
  const outputs = themeOutputs(theme);
  const readyCount = outputs.filter((output) => output.file).length;
  const lead = theme.synthesis_report?.content || theme.comparison_matrix?.content || "";

  return `<div class="theme-overview">
    <div class="meta-grid">
      ${meta("Theme ID", theme.theme_id)}
      ${meta("Markdown 产物", `${readyCount}/${outputs.length}`)}
      ${meta("共读消息", theme.messages?.length || 0)}
    </div>
    <div class="coreading-output-grid">
      ${outputs.map(renderOutputCard).join("")}
    </div>
    ${renderMarkdown(lead)}
  </div>`;
}

export function renderMessageOverview(message) {
  return `<div class="chat-panel">
    ${renderChatMessages([message])}
  </div>`;
}

export function renderCoreadingWorkspace(item, context) {
  const { theme, paper, themeId, paperKey, messages } = resolveCoreadingContext(item, context);
  const outputs = themeOutputs(theme);
  const activeOutput = outputs.find((output) => output.file) || outputs[0];

  return `<div class="coreading-workspace">
    <section class="coreading-doc-pane">
      <div class="coreading-section-header">
        <div>
          <p class="eyebrow">Coreading Skill Output</p>
          <h3>共读 Markdown</h3>
        </div>
        <span class="badge">${escapeHtml(themeId)}</span>
      </div>
      <div class="doc-switcher" role="tablist" aria-label="共读 Markdown 产物">
        ${outputs.map((output) => renderDocButton(output, activeOutput.key)).join("")}
      </div>
      <div class="doc-panels">
        ${outputs.map((output) => renderDocPanel(output, activeOutput.key)).join("")}
      </div>
    </section>

    <aside class="coreading-chat-pane">
      <div class="chat-header">
        <div>
          <p class="eyebrow">Co-reading Chat</p>
          <h3>边读边问</h3>
          <p class="muted">发送后调用外部 Codex 的 theme-coreading skill；回复写回聊天记录，用户再手动编辑共读 Markdown。</p>
        </div>
      </div>
      <div class="coreading-context">
        ${meta("主题", themeId)}
        ${meta("关联文献", paperKey || "未指定")}
        ${meta("文献标题", paper?.title || "未指定")}
      </div>
      <div class="prompt-strip" aria-label="共读快捷提问">
        ${PROMPT_TEMPLATES.map(renderPromptTemplate).join("")}
      </div>
      <div class="chat-log" id="chatLog">${renderChatMessages(messages)}</div>
      <div class="chat-composer">
        <label>
          <span>主题</span>
          <input id="messageTheme" value="${escapeHtml(themeId)}" aria-label="Theme ID" />
        </label>
        <label>
          <span>文献</span>
          <input id="messagePaper" value="${escapeHtml(paperKey)}" aria-label="Paper key" placeholder="paper key" />
        </label>
        <label>
          <span>意图</span>
          <select id="messageIntent" aria-label="Message intent">
            <option value="open_question">开放问题</option>
            <option value="clarify_dimension">澄清维度</option>
            <option value="evidence_check">核查证据</option>
            <option value="next_step">下一步</option>
          </select>
        </label>
        <textarea id="messageBody" rows="4" placeholder="像共同阅读一样提问：指出你正在看的段落、想比较的论文、需要核查的证据或下一步请求。"></textarea>
        <button class="primary-button" id="sendMessageButton">发送</button>
      </div>
    </aside>
  </div>`;
}

export function renderChatMessages(messages) {
  if (!messages.length) return `<div class="empty-state compact"><p>暂无共读消息。</p></div>`;
  const latestReplyId = [...messages].reverse().find((message) => message.reply_markdown)?.message_id;
  return messages
    .map((message) => {
      return `<article class="chat-message is-own">
        <div class="chat-meta">
          <span>你 · ${escapeHtml(message.intent || "open_question")}</span>
          <span>${escapeHtml(formatDate(message.created_at))}</span>
        </div>
        <p>${escapeHtml(message.body || "")}</p>
        <div class="list-meta">
          <span class="badge">${escapeHtml(message.reply_skill || "theme-coreading")}</span>
          ${message.paper_key ? `<span>${escapeHtml(message.paper_key)}</span>` : ""}
        </div>
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
      }`;
    })
    .join("");
}

export function bindCoreadingWorkspace() {
  document.querySelectorAll("[data-coreading-doc]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.coreadingDoc;
      document.querySelectorAll("[data-coreading-doc]").forEach((node) => node.classList.toggle("is-active", node === button));
      document.querySelectorAll("[data-coreading-panel]").forEach((panel) => {
        panel.classList.toggle("is-hidden", panel.dataset.coreadingPanel !== key);
      });
    });
  });

  document.querySelectorAll("[data-prompt-template]").forEach((button) => {
    button.addEventListener("click", () => {
      const body = document.querySelector("#messageBody");
      const intent = document.querySelector("#messageIntent");
      if (!body) return;
      body.value = button.dataset.promptTemplate || "";
      if (intent) intent.value = button.dataset.promptIntent || "open_question";
      body.focus();
    });
  });
}

function resolveCoreadingContext(item, { dashboard, themeById, paperByKey }) {
  const raw = item.raw || {};
  const paper = item.kind === "paper" ? raw : raw.paper_key ? paperByKey(raw.paper_key) : null;
  const theme = item.kind === "theme" ? raw : themeById(raw.theme_id || DEFAULT_THEME_ID);
  const themeId = theme?.theme_id || raw.theme_id || DEFAULT_THEME_ID;
  const paperKey = paper?.paper_key || raw.paper_key || "";
  const sourceMessages = theme?.messages?.length ? theme.messages : dashboard?.messages || [];
  const messages = sourceMessages.filter((message) => !themeId || message.theme_id === themeId).slice(-30);
  return { theme, paper, themeId, paperKey, messages };
}

function themeOutputs(theme) {
  if (theme?.coreading_outputs?.length) {
    return theme.coreading_outputs.filter((output) => output.public !== false && output.key !== "theme_state");
  }
  if (!theme) {
    return [
      { key: "comparison_matrix", label: "比较矩阵", filename: "comparison_matrix.md", file: null, public: true },
      { key: "synthesis_report", label: "综合报告", filename: "synthesis_report.md", file: null, public: true },
    ];
  }
  return [
    { key: "comparison_matrix", label: "比较矩阵", filename: "comparison_matrix.md", file: theme.comparison_matrix, public: true },
    { key: "synthesis_report", label: "综合报告", filename: "synthesis_report.md", file: theme.synthesis_report, public: true },
  ];
}

function renderOutputCard(output) {
  const state = output.file ? "ready" : "missing";
  return `<div class="coreading-output-card">
    <span>${escapeHtml(output.label)}</span>
    <strong>${escapeHtml(output.filename)}</strong>
    <span class="badge ${output.file ? "good" : "warn"}">${state}</span>
  </div>`;
}

function renderDocButton(output, activeKey) {
  const active = output.key === activeKey ? " is-active" : "";
  const status = output.file ? "" : " is-missing";
  return `<button class="doc-tab${active}${status}" data-coreading-doc="${escapeHtml(output.key)}" type="button">
    ${escapeHtml(output.label)}
  </button>`;
}

function renderDocPanel(output, activeKey) {
  const hidden = output.key === activeKey ? "" : " is-hidden";
  const content = output.file?.content || `未找到 ${output.filename}。`;
  const saveButton = output.file?.path
    ? `<button class="primary-button" data-save-coreading-markdown data-path="${escapeHtml(output.file.path)}">保存 Markdown</button>`
    : "";
  return `<article class="doc-panel${hidden}" data-coreading-panel="${escapeHtml(output.key)}">
    <div class="doc-panel-header">
      <div>
        <h3>${escapeHtml(output.label)}</h3>
        <p class="muted">${escapeHtml(output.file?.path || output.filename)}</p>
      </div>
      <div class="toolbar-actions">
        <span class="badge ${output.file ? "good" : "warn"}">${output.file ? "ready" : "missing"}</span>
        ${saveButton}
      </div>
    </div>
    <div class="coreading-markdown-editor" data-coreading-markdown-editor contenteditable="${output.file ? "true" : "false"}" spellcheck="false">
      ${renderMarkdown(content)}
    </div>
  </article>`;
}

function renderPromptTemplate(template) {
  return `<button class="prompt-chip" type="button" data-prompt-intent="${escapeHtml(template.intent)}" data-prompt-template="${escapeHtml(template.body)}">
    ${escapeHtml(template.label)}
  </button>`;
}

function meta(label, value) {
  return `<div class="meta-cell"><span>${escapeHtml(label)}</span>${escapeHtml(value ?? "未记录")}</div>`;
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? value : date.toLocaleString("zh-CN", { hour12: false });
}
