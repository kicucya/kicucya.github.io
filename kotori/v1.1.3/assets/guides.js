/* Progressive enhancement: the written steps and FAQ work without JavaScript. */
(() => {
  const cards = [...document.querySelectorAll('[data-guide-card]')];
  const videos = [...document.querySelectorAll('[data-guide-video]')];
  const pauseOthers = (active) => videos.forEach(video => {
    if (video !== active) video.pause();
  });

  document.querySelectorAll('[data-guide-play]').forEach(button => {
    button.disabled = false;
    button.addEventListener('click', async () => {
      const media = button.closest('.guide-media');
      const video = media.querySelector('video');
      video.poster = video.dataset.poster;
      video.querySelectorAll('[data-src]').forEach(node => { node.src = node.dataset.src; });
      button.hidden = true;
      video.hidden = false;
      pauseOthers(video);
      video.load();
      video.focus();
      try { await video.play(); } catch (_) { /* Native controls remain available. */ }
    });
  });

  videos.forEach(video => {
    video.addEventListener('play', () => pauseOthers(video));
    video.addEventListener('error', () => {
      video.closest('.guide-media').querySelector('.guide-video-error').hidden = false;
    });
  });
  cards.forEach(card => card.addEventListener('toggle', () => {
    if (!card.open) card.querySelector('video')?.pause();
  }));

  const searchControls = document.querySelector('[data-guide-search-controls]');
  const search = document.querySelector('#guide-search');
  const status = document.querySelector('[data-guide-status]');
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  const filterCards = () => {
    const words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let count = 0;
    cards.forEach(card => {
      const matches = words.every(word => normalize(card.dataset.search).includes(word));
      card.hidden = !matches;
      if (matches) count += 1;
      else card.querySelector('video')?.pause();
    });
    document.querySelectorAll('[data-guide-group]').forEach(group => {
      group.hidden = ![...group.querySelectorAll('[data-guide-card]')].some(card => !card.hidden);
    });
    status.textContent = !words.length ? '' : count ? `${count} ${status.dataset.countLabel}` : status.dataset.emptyLabel;
  };
  if (searchControls && search && status) {
    searchControls.hidden = false;
    search.addEventListener('input', filterCards);
    document.querySelector('[data-guide-clear]').addEventListener('click', () => {
      search.value = '';
      filterCards();
      search.focus();
    });
    // An already-selected hash does not fire hashchange. Clear filtering before
    // the browser follows a category link, including that same-hash case.
    document.querySelectorAll('.guide-toc a').forEach(link => {
      link.addEventListener('click', () => {
        if (search.value) { search.value = ''; filterCards(); }
      });
    });
  }
  const revealHash = () => {
    let id;
    try { id = decodeURIComponent(window.location.hash.slice(1)); } catch (_) { return; }
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;
    if (search?.value) { search.value = ''; filterCards(); }
    if (target.matches('[data-guide-card]')) target.open = true;
    target.scrollIntoView({block: 'start'});
  };
  window.addEventListener('hashchange', revealHash);
  revealHash();
})();
