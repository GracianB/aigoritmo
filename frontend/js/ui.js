
export function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value;
  return div.innerHTML;
}

export function timeNow() {
  return new Intl.DateTimeFormat("es-ES", {
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date()).toUpperCase();
}

export function scrollToBottom(container, force = false) {
  const distance = container.scrollHeight - container.scrollTop - container.clientHeight;
  if (force || distance < 140) container.scrollTop = container.scrollHeight;
}
