/* Keep the current section only when it exists in the destination snapshot. */
(() => {
  const links = document.querySelectorAll('[data-version-link]');
  const update = () => {
    let id = '';
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { /* Leave malformed hashes behind. */ }
    links.forEach(link => {
      const url = new URL(link.href);
      const available = JSON.parse(link.dataset.anchors);
      url.hash = id && available.includes(id) ? id : '';
      link.href = url.href;
    });
  };
  window.addEventListener('hashchange', update);
  update();
})();
