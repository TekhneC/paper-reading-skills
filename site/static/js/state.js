export const state = {
  mode: "today",
  view: "overview",
  query: "",
  selectedId: null,
  dashboard: null,
  sidebarCollapsed: false,
};

export function setDashboard(dashboard) {
  state.dashboard = dashboard;
  if (!state.selectedId) {
    state.selectedId = currentItems()[0]?.id || null;
  }
}

export function currentItems() {
  if (!state.dashboard) return [];
  const query = state.query.trim().toLowerCase();
  const items = normalizeItems(state.dashboard, state.mode);
  if (!query) return items;
  return items.filter((item) =>
    [item.title, item.id, item.subtitle, item.status, item.searchText]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query)),
  );
}

export function selectedItem() {
  const items = currentItems();
  return items.find((item) => item.id === state.selectedId) || items[0] || null;
}

export function paperByKey(key) {
  return (state.dashboard?.papers || []).find((paper) => paper.paper_key === key) || null;
}

export function themeById(themeId) {
  return (state.dashboard?.themes || []).find((theme) => theme.theme_id === themeId) || null;
}

export function jumpTo(target) {
  if (!target) return;
  state.mode = target.mode || state.mode;
  state.selectedId = target.id || null;
  state.view = target.view || "overview";
}

export function normalizeItems(dashboard, mode) {
  if (mode === "today") {
    const latest = dashboard.latest_daily
      ? [{
          id: `archive:${dashboard.latest_daily.date}`,
          kind: "archive-summary",
          title: `当日阅读：${dashboard.latest_daily.date}`,
          subtitle: "归档摘要",
          status: dashboard.latest_daily.digest ? "ready" : "missing",
          searchText: dashboard.latest_daily.digest?.content || "",
          raw: dashboard.latest_daily,
        }]
      : [];
    const todos = dashboard.todos.map((todo) => ({
      id: todo.id,
      kind: "todo",
      title: todo.title,
      subtitle: [todo.priority, todo.action].filter(Boolean).join(" · "),
      status: todo.status,
      searchText: [todo.paper_key, todo.theme_id, todo.reason].filter(Boolean).join(" "),
      raw: todo,
    }));
    return [...latest, ...todos];
  }

  if (mode === "themes") {
    return dashboard.themes.map((theme) => ({
      id: theme.theme_id,
      kind: "theme",
      title: theme.theme_id,
      subtitle: "Theme co-reading",
      status: theme.synthesis_report ? "synthesis_ready" : "state_only",
      searchText: [theme.theme_state?.content, theme.comparison_matrix?.content, theme.synthesis_report?.content].join(" "),
      raw: theme,
    }));
  }

  if (mode === "archives") {
    return dashboard.daily_runs.map((run) => ({
      id: run.date,
      kind: "archive",
      title: run.date,
      subtitle: "Daily archive",
      status: run.digest ? "digest_ready" : "metadata_only",
      searchText: run.digest?.content || "",
      raw: run,
    }));
  }

  if (mode === "messages") {
    return dashboard.messages.map((message) => ({
      id: message.message_id,
      kind: "message",
      title: message.body.slice(0, 80),
      subtitle: [message.theme_id, message.forward_status].filter(Boolean).join(" · "),
      status: message.forward_status,
      searchText: [message.body, message.paper_key, message.theme_id].join(" "),
      raw: message,
    }));
  }

  return dashboard.papers.map((paper) => ({
    id: paper.paper_key,
    kind: "paper",
    title: paper.title || paper.paper_key,
    subtitle: [paper.year, paper.venue].filter(Boolean).join(" · "),
    status: paper.status || "queued",
    searchText: [paper.recommended_action, paper.decision_label, paper.evidence_status].join(" "),
    raw: paper,
  }));
}
