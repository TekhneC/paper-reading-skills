const escapeMap = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#039;",
};

export function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (char) => escapeMap[char]);
}

export function renderMarkdown(markdown = "") {
  if (!markdown.trim()) {
    return `<div class="empty-state"><p>没有可展示的 Markdown。</p></div>`;
  }

  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let inCode = false;
  let codeLines = [];
  let listOpen = false;
  let tableBuffer = [];

  const closeList = () => {
    if (listOpen) {
      html.push("</ul>");
      listOpen = false;
    }
  };

  const flushTable = () => {
    if (!tableBuffer.length) return;
    closeList();
    const rows = tableBuffer
      .filter((line) => !/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line))
      .map((line) => line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim()));
    if (rows.length) {
      html.push("<table>");
      rows.forEach((row, index) => {
        html.push(index === 0 ? "<thead><tr>" : "<tr>");
        row.forEach((cell) => html.push(`${index === 0 ? "<th>" : "<td>"}${inline(cell)}${index === 0 ? "</th>" : "</td>"}`));
        html.push(index === 0 ? "</tr></thead><tbody>" : "</tr>");
      });
      html.push("</tbody></table>");
    }
    tableBuffer = [];
  };

  for (const line of lines) {
    if (line.startsWith("```")) {
      flushTable();
      closeList();
      if (inCode) {
        html.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
        codeLines = [];
        inCode = false;
      } else {
        inCode = true;
      }
      continue;
    }

    if (inCode) {
      codeLines.push(line);
      continue;
    }

    if (/^\s*\|.*\|\s*$/.test(line)) {
      tableBuffer.push(line);
      continue;
    }
    flushTable();

    if (!line.trim()) {
      closeList();
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      closeList();
      const level = heading[1].length;
      html.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }

    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    if (bullet) {
      if (!listOpen) {
        html.push("<ul>");
        listOpen = true;
      }
      html.push(`<li>${inline(bullet[1])}</li>`);
      continue;
    }

    closeList();
    html.push(`<p>${inline(line)}</p>`);
  }

  flushTable();
  closeList();
  return `<article class="markdown">${html.join("\n")}</article>`;
}

function inline(value) {
  return renderInline(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function renderInline(value) {
  const pattern = /(!?)\[([^\]]*)\]\((<[^>]+>|[^)]+)\)/g;
  let cursor = 0;
  let html = "";
  for (const match of value.matchAll(pattern)) {
    html += escapeHtml(value.slice(cursor, match.index));
    const isImage = match[1] === "!";
    const label = match[2].trim();
    const target = normalizeMarkdownTarget(match[3]);
    html += isImage ? imageHtml(label, target) : linkHtml(label, target);
    cursor = match.index + match[0].length;
  }
  html += escapeHtml(value.slice(cursor));
  return html;
}

function normalizeMarkdownTarget(target = "") {
  const trimmed = target.trim();
  if (trimmed.startsWith("<") && trimmed.endsWith(">")) {
    return trimmed.slice(1, -1).trim();
  }
  return trimmed.split(/\s+(?=["'])/)[0].trim();
}

function resolveMediaUrl(target) {
  if (/^(https?:|data:|blob:|\/)/i.test(target)) return target;
  return `/api/file?path=${encodeURIComponent(target)}`;
}

function imageHtml(alt, target) {
  const src = resolveMediaUrl(target);
  return `<img class="markdown-image" src="${escapeHtml(src)}" alt="${escapeHtml(alt)}" data-markdown-src="${escapeHtml(target)}" loading="lazy" />`;
}

function linkHtml(label, target) {
  const href = /^(https?:|mailto:|\/)/i.test(target) ? target : resolveMediaUrl(target);
  return `<a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(label || target)}</a>`;
}

export function extractHeadings(markdown = "") {
  return markdown
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((line) => line.match(/^(#{1,3})\s+(.+)$/))
    .filter(Boolean)
    .map((match) => ({ level: match[1].length, title: match[2].replace(/[#*_`]/g, "").trim() }))
    .slice(0, 18);
}
