/* ============================================================
   home.js — kotori ホーム(index.html / index-en.html 共用)
   1) 画像のドラッグ/コンテキストメニュー抑止
   2) スクショギャラリー自動横スクロール
      ・手動操作(タッチ/ホイール/キー/ホバー)を優先し、静止後に再開
      ・内容を複製して継ぎ目なしの無限ループ
      ・ループ有効時は横スクロールバーを非表示(CSS .is-looping)。
        バーの往復は「有限の帯」であることを露呈するため(手動操作は維持)
      ・マウスは掴んでドラッグスクロール可(バー非表示後の代替横移動手段)
      ・視口外/タブ非表示では停止、prefers-reduced-motion 尊重
   ============================================================ */
(() => {
  'use strict';

  /* ---------- 1) 画像保護:ドラッグ/右クリックメニュー抑止 ---------- */
  const guardImages = (e) => {
    if (e.target instanceof Element && e.target.closest('img')) e.preventDefault();
  };
  document.addEventListener('dragstart', guardImages);
  document.addEventListener('contextmenu', guardImages);

  /* ---------- 2) ギャラリー自動スクロール ---------- */
  const gallery = document.querySelector('.gallery');
  if (!gallery) return;

  const SPEED = 30;          // 自動スクロール速度(px/秒)
  const RESUME_DELAY = 4000; // 手動操作の静止から再開までの待ち(ms)

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let rafId = 0;
  let lastTime = 0;
  let pos = 0;          // 小数精度の位置(scrollLeft は整数に丸められるため別持ち)
  let loopWidth = 0;    // 1 周ぶんの幅(複製内容の先頭 offset)
  let inView = false;
  let hovered = false;
  let resumeTimer = 0;
  let cloned = false;

  // 継ぎ目なしループ用に内容を複製する。
  // 回り込みは「scrollLeft を loopWidth ぶん一気に巻き戻す」ことで成立するため、
  // 巻き戻しの前後で同じ絵が見えている必要がある = 最大スクロール量
  // (scrollWidth - clientWidth) が loopWidth 以上になるまで複製を追い足す。
  // 不足すると広い視口で scrollLeft が右端に clamp され、画面が数秒止まった後
  // 回り込みで左端へ大きく跳ぶ。視口が広いほど多くの複製が要る(resize で追い足す)。
  const MAX_EXTRA_SETS = 8; // 追い足しの安全上限
  let originals = null;
  const appendSet = () => {
    originals.forEach((shot) => {
      const copy = shot.cloneNode(true);
      copy.setAttribute('aria-hidden', 'true'); // 複製は支援技術に読ませない
      gallery.appendChild(copy);
    });
  };
  const ensureClones = () => {
    if (!cloned) {
      originals = Array.from(gallery.querySelectorAll('.shot'));
      appendSet();
      loopWidth = gallery.children[originals.length].offsetLeft - gallery.children[0].offsetLeft;
      // ループ有効化と同時に snap 常時解除 + 横スクロールバー非表示(CSS .is-looping)。
      // mandatory snap が生きていると自動停止や位置補正のたびに Chrome が最寄り
      // snap 点へ即吸着して最大半カード分の「跳び」が見えるため、付け外しはしない。
      gallery.classList.add('is-looping');
      cloned = true;
    }
    let extraSets = gallery.children.length / originals.length - 1;
    while (gallery.scrollWidth - gallery.clientWidth < loopWidth && extraSets < MAX_EXTRA_SETS) {
      appendSet();
      extraSets++;
    }
  };

  const canRun = () =>
    !reduceMotion.matches && inView && !document.hidden && !hovered && !resumeTimer;

  const step = (t) => {
    if (lastTime) {
      const dt = Math.min((t - lastTime) / 1000, 0.1); // タブ復帰などの巨大 dt を抑制
      pos += SPEED * dt;
      if (pos >= loopWidth) pos -= loopWidth; // 等価位置へ継ぎ目なしで巻き戻す
      gallery.scrollLeft = pos;
    }
    lastTime = t;
    rafId = requestAnimationFrame(step);
  };

  const start = () => {
    if (rafId || !canRun()) return;
    ensureClones();
    // 巻き戻し余地が確保できない(全内容が視口に収まる等)なら回さない
    if (loopWidth <= 0 || gallery.scrollWidth - gallery.clientWidth < loopWidth) return;
    pos = gallery.scrollLeft % loopWidth; // 複製側まで進んでいたら 1 周目の等価位置へ
    gallery.scrollLeft = pos;
    lastTime = 0;
    rafId = requestAnimationFrame(step);
  };

  const stop = () => {
    if (rafId) { cancelAnimationFrame(rafId); rafId = 0; }
  };

  const onResume = () => { resumeTimer = 0; start(); };

  // 手動操作 → 停止し、静止 RESUME_DELAY 後に再開
  const pauseForInteraction = () => {
    stop();
    if (resumeTimer) clearTimeout(resumeTimer);
    resumeTimer = setTimeout(onResume, RESUME_DELAY);
  };
  gallery.addEventListener('pointerdown', pauseForInteraction);
  gallery.addEventListener('wheel', pauseForInteraction, { passive: true });
  gallery.addEventListener('keydown', pauseForInteraction);

  // マウスの掴んでドラッグスクロール(デスクトップ)。
  // スクロールバー非表示後、マウスに残る横移動手段は shift+ホイールだけになるため
  // ドラッグを実装する。pointerType を mouse に絞り、タッチ/トラックパッドは OS
  // ネイティブのスワイプ・慣性に任せて触らない。閾値未満の移動はクリック扱い
  // (クリックを呑まない)。ドラッグ由来の scroll イベントは既存の
  // 「静止 RESUME_DELAY 後に再開」の延期にそのまま乗る。
  const DRAG_THRESHOLD = 3; // px
  let dragPointerId = -1;
  let dragStartX = 0;
  let dragStartScroll = 0;
  let dragMoved = false;
  gallery.addEventListener('pointerdown', (e) => {
    if (e.pointerType !== 'mouse' || e.button !== 0) return;
    dragPointerId = e.pointerId;
    dragStartX = e.clientX;
    dragStartScroll = gallery.scrollLeft;
    dragMoved = false;
  });
  gallery.addEventListener('pointermove', (e) => {
    if (e.pointerId !== dragPointerId) return;
    const dx = e.clientX - dragStartX;
    if (!dragMoved) {
      if (Math.abs(dx) < DRAG_THRESHOLD) return;
      dragMoved = true;
      gallery.classList.add('is-dragging');    // grabbing カーソル + 選択抑止
      gallery.setPointerCapture(e.pointerId);  // ギャラリー外へ出ても追従
    }
    gallery.scrollLeft = dragStartScroll - dx;
  });
  const endDrag = (e) => {
    if (e.pointerId !== dragPointerId) return;
    dragPointerId = -1;
    gallery.classList.remove('is-dragging');
  };
  gallery.addEventListener('pointerup', endDrag);
  gallery.addEventListener('pointercancel', endDrag);

  // 慣性スクロールが続く間は自動再開をさらに延期
  gallery.addEventListener('scroll', () => {
    if (!rafId && resumeTimer) {
      clearTimeout(resumeTimer);
      resumeTimer = setTimeout(onResume, RESUME_DELAY);
    }
  }, { passive: true });

  // マウスが乗っている間は停止(閲覧を優先;スクロールバー操作もこの間に起こる)
  gallery.addEventListener('pointerenter', (e) => {
    if (e.pointerType === 'mouse') { hovered = true; stop(); }
  });
  gallery.addEventListener('pointerleave', (e) => {
    if (e.pointerType === 'mouse') { hovered = false; start(); }
  });

  // 視口外では回さない
  if ('IntersectionObserver' in window) {
    new IntersectionObserver((entries) => {
      inView = entries[0].isIntersecting;
      if (inView) { start(); } else { stop(); }
    }).observe(gallery);
  } else {
    inView = true;
    start();
  }

  // タブ非表示で停止
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { stop(); } else { start(); }
  });

  // 視口が広がったら複製を追い足す(狭まっても減らさない:実害なし)
  window.addEventListener('resize', () => {
    if (cloned) ensureClones();
  });

  // reduced-motion の動的切替に追従
  if (typeof reduceMotion.addEventListener === 'function') {
    reduceMotion.addEventListener('change', () => {
      if (reduceMotion.matches) { stop(); } else { start(); }
    });
  }
})();
