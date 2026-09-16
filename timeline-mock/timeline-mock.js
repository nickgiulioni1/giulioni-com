(() => {
  const timeline = document.querySelector('#timeline');
  const count = document.querySelector('#entry-count');
  const empty = document.querySelector('#empty-state');
  const filters = [...document.querySelectorAll('fieldset input')];
  const formatPart = (value, precision) => {
    const date = new Date(`${value}T00:00:00Z`);
    if (precision === 'year') {
      return new Intl.DateTimeFormat('en-US', { year: 'numeric', timeZone: 'UTC' }).format(date);
    }
    if (precision === 'month') {
      return new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' }).format(date);
    }
    return new Intl.DateTimeFormat('en-US', {
      month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC'
    }).format(date);
  };
  const formatDateLabel = entry => {
    const precision = entry.date_precision || 'day';
    const start = formatPart(entry.date, precision);
    if (!entry.date_end) return start;
    const end = formatPart(entry.date_end, precision);
    return start === end ? start : `${start} – ${end}`;
  };
  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  };
  // Site-root asset paths become relative URLs so file:// previews work too.
  const assetURL = path => new URL(`../${path.replace(/^\//, '')}`, location.href).href;
  if (!Array.isArray(window.TIMELINE_ENTRIES)) {
    count.textContent = 'Timeline unavailable';
    document.querySelector('#last-updated').textContent = 'Unavailable';
    timeline.textContent = 'The sample entries could not load. Regenerate entries.js using the README instructions.';
    filters.forEach(input => { input.disabled = true; });
    return;
  }
  const entries = window.TIMELINE_ENTRIES.filter(entry => entry.visibility === 'public')
    .sort((a, b) => b.date.localeCompare(a.date));
  const cards = entries.map((entry, index) => {
    const kind = entry.kind || 'moment';
    const article = element('article', `tm-entry tm-entry--${index % 2 ? 'right' : 'left'} tm-kind--${kind}`);
    const inner = element('div', 'tm-entry-inner');
    article.append(inner);
    article.id = `entry-${index}`;
    article.dataset.tags = entry.tags.join(' ');
    if (entry.chapter) article.dataset.chapter = entry.chapter;
    const date = element('time', 'tm-date', formatDateLabel(entry));
    date.dateTime = entry.date_end ? `${entry.date}/${entry.date_end}` : entry.date;
    inner.append(date);
    const card = element('div', 'tm-card');
    if (entry.photo_original || entry.photo_styled) {
      const figure = element('figure', 'tm-photo');
      const addPhoto = (path, styled) => {
        const img = element('img');
        img.src = assetURL(path);
        img.alt = styled ? `Styled companion for ${entry.title}` :
          path.includes('ballpark-estimate') ? 'Existing Ballpark estimating product screenshot' : 'Existing portrait of Nick Giulioni, used as a placeholder';
        img.loading = index === 0 ? 'eager' : 'lazy';
        img.className = path.includes('portrait') ? 'tm-portrait' : 'tm-product';
        img.addEventListener('error', () => { img.replaceWith(element('p', 'tm-missing', 'Photo unavailable in this preview.')); });
        figure.append(img);
        figure.append(element('figcaption', '', styled ? 'Styled companion · Mock asset' : 'Existing site image · Mock asset'));
      };
      if (entry.photo_original) addPhoto(entry.photo_original, false);
      if (entry.photo_styled) addPhoto(entry.photo_styled, true);
      card.append(figure);
    }
    const copy = element('div', 'tm-copy');
    const metaBits = [];
    if (entry.chapter) metaBits.push(entry.chapter);
    metaBits.push(...entry.tags);
    if (kind !== 'moment') metaBits.push(kind);
    copy.append(element('p', 'tm-tags', metaBits.join(' / ')));
    copy.append(element('h2', '', entry.title));
    if (entry.subtitle) copy.append(element('p', 'tm-subtitle', entry.subtitle));
    const people = Array.isArray(entry.people) ? entry.people : [];
    const context = [entry.place, people.length ? `With ${people.join(' & ')}` : null].filter(Boolean);
    if (context.length) copy.append(element('p', 'tm-context', context.join(' · ')));
    copy.append(element('p', 'tm-blurb', entry.blurb));
    if (Array.isArray(entry.metrics) && entry.metrics.length) {
      const list = element('ul', 'tm-metrics');
      entry.metrics.forEach(({ label, value }) => {
        if (!label || value == null || value === '') return;
        const item = element('li', '');
        item.append(element('span', 'tm-metric-label', label), document.createTextNode(': '));
        item.append(element('span', 'tm-metric-value', String(value)));
        list.append(item);
      });
      if (list.childNodes.length) copy.append(list);
    }
    if (Array.isArray(entry.links) && entry.links.length) {
      const nav = element('p', 'tm-links');
      entry.links.forEach(({ label, url }, i) => {
        if (!label || !url) return;
        if (i) nav.append(document.createTextNode(' · '));
        const a = element('a', 'tm-entry-link', label);
        a.href = url;
        a.rel = 'noopener noreferrer';
        if (/^https?:\/\//i.test(url)) a.target = '_blank';
        nav.append(a);
      });
      if (nav.childNodes.length) copy.append(nav);
    }
    if (entry.blurb.includes('ballpark.build')) {
      const link = element('a', 'tm-product-link', 'Explore Ballpark ↗');
      link.href = 'https://ballpark.build';
      copy.append(link);
    }
    card.append(copy);
    inner.append(card);
    timeline.append(article);
    return article;
  });
  if (entries.length) {
    document.querySelector('#last-updated').textContent = formatDateLabel(entries[0]);
    const latest = document.querySelector('#last-entry');
    latest.textContent = entries[0].title + ' ↓';
    latest.href = '#entry-0';
    latest.addEventListener('click', () => {
      filters.forEach(input => { input.checked = true; });
      applyFilters();
    });
  } else {
    document.querySelector('#last-updated').textContent = 'No entries yet';
  }
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const observer = 'IntersectionObserver' in window ? new IntersectionObserver(records => {
    records.forEach(({ target, isIntersecting }) => {
      if (isIntersecting && !target.classList.contains('is-filtered-out')) {
        target.classList.add('is-revealed');
        observer.unobserve(target);
      }
    });
  }, { threshold: 0, rootMargin: '0px 0px -24px 0px' }) : null;
  cards.forEach(card => {
    if (observer && !motion.matches) {
      card.classList.add('tm-reveal');
      observer.observe(card);
    } else card.classList.add('is-revealed');
  });
  motion.addEventListener('change', () => {
    if (motion.matches) cards.forEach(card => {
      card.classList.add('is-revealed');
      observer?.unobserve(card);
    });
  });
  // Keyboard navigation must never land on an unrevealed link.
  timeline.addEventListener('focusin', event => {
    event.target.closest('.tm-entry')?.classList.add('is-revealed');
  });
  function applyFilters() {
    const selected = filters.filter(input => input.checked).map(input => input.value);
    let visible = 0;
    cards.forEach(card => {
      const matches = card.dataset.tags.split(' ').some(tag => selected.includes(tag));
      card.classList.toggle('is-filtered-out', !matches);
      card.inert = !matches;
      card.setAttribute('aria-hidden', String(!matches));
      if (matches) {
        visible += 1;
        if (observer && !card.classList.contains('is-revealed')) {
          observer.unobserve(card);
          observer.observe(card);
        }
      }
    });
    count.textContent = `${visible} ${visible === 1 ? 'entry' : 'entries'}`;
    empty.hidden = visible !== 0;
    empty.querySelector('h2').textContent = selected.length ? 'No entries to show yet.' : 'No entries selected.';
  }
  filters.forEach(input => input.addEventListener('change', applyFilters));
  applyFilters();
})();
