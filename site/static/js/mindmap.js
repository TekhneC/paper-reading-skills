import { escapeHtml, extractHeadings } from "./markdown.js";

const CANVAS_W = 1160;
const CANVAS_H = 680;

export function renderMindMap(item) {
  const data = withNodePositions(buildMapData(item));
  const edges = flattenEdges(data);
  const nodes = flattenNodes(data);
  return `<div class="mindmap-editor">
    <div class="pane-toolbar">
      <h3>思路图</h3>
      <div class="toolbar-actions">
        <button class="secondary-button" id="addRootBranchButton">新增分支</button>
        <button class="primary-button" id="saveMindMapButton">保存思路图</button>
      </div>
    </div>
    <div class="mindmap-canvas" id="mindmapCanvas" style="--map-width:${CANVAS_W}px; --map-height:${CANVAS_H}px">
      <svg class="mindmap-edges" viewBox="0 0 ${CANVAS_W} ${CANVAS_H}" aria-hidden="true">
        ${edges.map(renderEdge).join("")}
      </svg>
      ${nodes.map(renderNode).join("")}
    </div>
    <p class="muted">直接拖动节点调整位置；点击文字即可编辑；用“+”为节点添加子节点。</p>
  </div>`;
}

export function bindMindMapEditor() {
  const canvas = document.querySelector("#mindmapCanvas");
  if (!canvas) return;

  document.querySelector("#addRootBranchButton")?.addEventListener("click", () => {
    const root = canvas.querySelector('.mindmap-node[data-parent-id=""]');
    addNode(root?.dataset.nodeId || "root");
  });

  canvas.addEventListener("click", (event) => {
    const action = event.target.closest("[data-map-action]");
    if (!action) return;
    const node = action.closest(".mindmap-node");
    if (!node) return;
    if (action.dataset.mapAction === "add-child") addNode(node.dataset.nodeId);
    if (action.dataset.mapAction === "delete") removeNode(node.dataset.nodeId);
  });

  canvas.querySelectorAll(".mindmap-node").forEach((node) => {
    node.addEventListener("pointerdown", startDrag);
  });
}

export function readMindMapData() {
  const canvas = document.querySelector("#mindmapCanvas");
  if (!canvas) return { title: "Mind Map", children: [] };
  const nodes = [...canvas.querySelectorAll(".mindmap-node")].map((node) => ({
    id: node.dataset.nodeId,
    parentId: node.dataset.parentId,
    title: node.querySelector(".mindmap-node-title")?.textContent.trim() || "未命名节点",
    x: Number.parseFloat(node.style.left) || 0,
    y: Number.parseFloat(node.style.top) || 0,
  }));
  const root = nodes.find((node) => !node.parentId) || nodes[0];
  const build = (parentId) => nodes
    .filter((node) => node.parentId === parentId)
    .map((node) => ({
      id: node.id,
      title: node.title,
      x: node.x,
      y: node.y,
      children: build(node.id),
    }));
  return {
    id: root?.id || "root",
    title: root?.title || "Mind Map",
    x: root?.x || 40,
    y: root?.y || 280,
    children: build(root?.id || "root"),
  };
}

function renderNode(node) {
  const isRoot = node.parentId ? "" : " is-root";
  const deleteButton = node.parentId ? `<button class="node-button" data-map-action="delete" title="删除节点">×</button>` : "";
  return `<article class="mindmap-node${isRoot}" data-node-id="${escapeHtml(node.id)}" data-parent-id="${escapeHtml(node.parentId || "")}" style="left:${node.x}px; top:${node.y}px">
    <div class="node-tools">
      <button class="node-button" data-map-action="add-child" title="新增子节点">+</button>
      ${deleteButton}
    </div>
    <div class="mindmap-node-title" contenteditable="true" spellcheck="false">${escapeHtml(node.title)}</div>
  </article>`;
}

function renderEdge(edge) {
  return `<path class="edge" data-from="${escapeHtml(edge.from)}" data-to="${escapeHtml(edge.to)}" d="${edgePath(edge)}" />`;
}

function edgePath(edge) {
  const sx = edge.fromX + 220;
  const sy = edge.fromY + 34;
  const tx = edge.toX;
  const ty = edge.toY + 34;
  return `M ${sx} ${sy} C ${sx + 54} ${sy}, ${tx - 54} ${ty}, ${tx} ${ty}`;
}

function addNode(parentId) {
  const canvas = document.querySelector("#mindmapCanvas");
  const parent = canvas.querySelector(`.mindmap-node[data-node-id="${cssEscape(parentId)}"]`);
  const id = `node-${Date.now()}`;
  const x = Math.min(CANVAS_W - 260, (Number.parseFloat(parent?.style.left) || 40) + 300);
  const y = Math.min(CANVAS_H - 90, (Number.parseFloat(parent?.style.top) || 80) + 90);
  canvas.insertAdjacentHTML("beforeend", renderNode({ id, parentId, title: "新节点", x, y }));
  canvas.querySelector(`[data-node-id="${id}"]`).addEventListener("pointerdown", startDrag);
  redrawEdges();
}

function removeNode(nodeId) {
  const canvas = document.querySelector("#mindmapCanvas");
  const ids = collectDescendantIds(nodeId);
  ids.push(nodeId);
  ids.forEach((id) => canvas.querySelector(`.mindmap-node[data-node-id="${cssEscape(id)}"]`)?.remove());
  redrawEdges();
}

function collectDescendantIds(parentId) {
  const canvas = document.querySelector("#mindmapCanvas");
  const children = [...canvas.querySelectorAll(`.mindmap-node[data-parent-id="${cssEscape(parentId)}"]`)].map((node) => node.dataset.nodeId);
  return children.flatMap((id) => [id, ...collectDescendantIds(id)]);
}

function startDrag(event) {
  if (event.target.closest("[data-map-action]") || event.target.closest(".mindmap-node-title") === event.target) return;
  const node = event.currentTarget;
  const canvas = document.querySelector("#mindmapCanvas");
  node.setPointerCapture(event.pointerId);
  const startX = event.clientX;
  const startY = event.clientY;
  const left = Number.parseFloat(node.style.left) || 0;
  const top = Number.parseFloat(node.style.top) || 0;

  const move = (moveEvent) => {
    const nextLeft = clamp(left + moveEvent.clientX - startX, 8, CANVAS_W - node.offsetWidth - 8);
    const nextTop = clamp(top + moveEvent.clientY - startY, 8, CANVAS_H - node.offsetHeight - 8);
    node.style.left = `${nextLeft}px`;
    node.style.top = `${nextTop}px`;
    redrawEdges();
  };
  const up = () => {
    node.removeEventListener("pointermove", move);
    node.removeEventListener("pointerup", up);
    node.removeEventListener("pointercancel", up);
  };
  node.addEventListener("pointermove", move);
  node.addEventListener("pointerup", up);
  node.addEventListener("pointercancel", up);
}

function redrawEdges() {
  const canvas = document.querySelector("#mindmapCanvas");
  const svg = canvas.querySelector(".mindmap-edges");
  const nodes = [...canvas.querySelectorAll(".mindmap-node")].map((node) => ({
    id: node.dataset.nodeId,
    parentId: node.dataset.parentId,
    x: Number.parseFloat(node.style.left) || 0,
    y: Number.parseFloat(node.style.top) || 0,
  }));
  const edges = nodes
    .filter((node) => node.parentId)
    .map((node) => {
      const parent = nodes.find((candidate) => candidate.id === node.parentId);
      return parent ? { from: parent.id, to: node.id, fromX: parent.x, fromY: parent.y, toX: node.x, toY: node.y } : null;
    })
    .filter(Boolean);
  svg.innerHTML = edges.map(renderEdge).join("");
}

function buildMapData(item) {
  if (item.raw?.mindmap?.data?.title && Array.isArray(item.raw.mindmap.data.children)) {
    return item.raw.mindmap.data;
  }

  if (item.kind === "todo") {
    const todo = item.raw;
    return {
      title: todo.title,
      children: [
        valueBranch("动作", [todo.action, todo.priority, todo.status].filter(Boolean)),
        valueBranch("关联对象", [todo.paper_key, todo.theme_id].filter(Boolean)),
        valueBranch("处理入口", [todo.target?.mode, todo.target?.id, todo.target?.view].filter(Boolean)),
        valueBranch("原因", [todo.reason].filter(Boolean)),
      ].filter((child) => child.children.length),
    };
  }

  if (item.kind === "theme") {
    const theme = item.raw;
    return {
      title: item.title,
      children: [
        branch("Theme state", theme.theme_state?.content),
        branch("Comparison matrix", theme.comparison_matrix?.content),
        branch("Synthesis", theme.synthesis_report?.content),
        valueBranch("Messages", (theme.messages || []).map((message) => message.body).slice(-4)),
      ].filter((child) => child.children.length),
    };
  }

  if (item.kind === "archive" || item.kind === "archive-summary") {
    const run = item.raw;
    return {
      title: item.title,
      children: [
        branch("Digest", run.digest?.content),
        jsonBranch("Candidates", run.deep_read_candidates),
        jsonBranch("Quick reads", run.quick_reads),
      ].filter((child) => child.children.length),
    };
  }

  if (item.kind === "message") {
    const message = item.raw;
    return {
      title: "共读消息",
      children: [
        valueBranch("目标", [message.target, message.forward_status].filter(Boolean)),
        valueBranch("上下文", [message.theme_id, message.paper_key].filter(Boolean)),
        valueBranch("内容", [message.body].filter(Boolean)),
      ].filter((child) => child.children.length),
    };
  }

  const paper = item.raw;
  return {
    title: paper.title || paper.paper_key,
    children: [
      valueBranch("状态", [paper.status, paper.recommended_action, paper.decision_label].filter(Boolean)),
      branch("快读", paper.quick_read?.content),
      branch("精读", paper.deep_read?.content),
      valueBranch("证据", [paper.evidence_status, paper.pdf?.available ? "PDF available" : "PDF missing"].filter(Boolean)),
    ].filter((child) => child.children.length),
  };
}

function withNodePositions(data) {
  const assign = (node, parentId, index, depth) => {
    const id = node.id || `${parentId || "root"}-${index}`;
    const positioned = {
      ...node,
      id,
      parentId,
      x: typeof node.x === "number" ? node.x : 40 + depth * 300,
      y: typeof node.y === "number" ? node.y : 80 + index * 110,
      children: [],
    };
    positioned.children = (node.children || []).map((child, childIndex) => assign(child, id, childIndex, depth + 1));
    if (!parentId) {
      positioned.x = typeof node.x === "number" ? node.x : 40;
      positioned.y = typeof node.y === "number" ? node.y : 280;
    }
    return positioned;
  };
  return assign(data, "", 0, 0);
}

function flattenNodes(root) {
  return [root, ...(root.children || []).flatMap(flattenNodes)];
}

function flattenEdges(root) {
  return (root.children || []).flatMap((child) => [
    { from: root.id, to: child.id, fromX: root.x, fromY: root.y, toX: child.x, toY: child.y },
    ...flattenEdges(child),
  ]);
}

function branch(title, markdown) {
  return {
    title,
    children: extractHeadings(markdown || "").slice(0, 5).map((heading) => ({ title: heading.title, children: [] })),
  };
}

function jsonBranch(title, value) {
  if (!value) return { title, children: [] };
  const children = Object.keys(value)
    .slice(0, 6)
    .map((key) => ({ title: key, children: [] }));
  return { title, children };
}

function valueBranch(title, values) {
  return {
    title,
    children: values.map((value) => ({ title: String(value), children: [] })).slice(0, 6),
  };
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function cssEscape(value) {
  return String(value).replace(/["\\]/g, "\\$&");
}
