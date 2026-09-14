(() => {
  const timeline = document.querySelector('#timeline');
  const count = document.querySelector('#entry-count');
  const empty = document.querySelector('#empty-state');
  const filters = [...document.querySelectorAll('fieldset input')];
  const formatDate = value => new Intl.DateTimeFormat('en-US', {
    month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC'
  }).format(new Date(`${value}T00:00:00Z`));
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
    const article = element('article', 'tm-entry');
    article.id = `entry-${index}`;
    article.dataset.tags = entry.tags.join(' ');
    const date = element('time', 'tm-date', formatDate(entry.date));
    date.dateTime = entry.date;
    article.append(date);
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
    copy.append(element('p', 'tm-tags', entry.tags.join(' / ')), element('h2', '', entry.title));
    const context = [entry.place, entry.people.length ? `With ${entry.people.join(' & ')}` : null].filter(Boolean);
    if (context.length) copy.append(element('p', 'tm-context', context.join(' · ')));
    copy.append(element('p', 'tm-blurb', entry.blurb));
    if (entry.blurb.includes('ballpark.build')) {
      const link = element('a', 'tm-product-link', 'Explore Ballpark ↗');
      link.href = 'https://ballpark.build';
      copy.append(link);
    }
    card.append(copy);
    article.append(card);
    timeline.append(article);
    return article;
  });
  if (entries.length) {
    document.querySelector('#last-updated').textContent = formatDate(entries[0].date);
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
  function applyFilters() {
    const selected = filters.filter(input => input.checked).map(input => input.value);
    let visible = 0;
    cards.forEach(card => {
      card.hidden = !card.dataset.tags.split(' ').some(tag => selected.includes(tag));
      if (!card.hidden) visible += 1;
    });
    count.textContent = `${visible} ${visible === 1 ? 'entry' : 'entries'}`;
    empty.hidden = visible !== 0;
    empty.querySelector('h2').textContent = selected.length ? 'No entries to show yet.' : 'No entries selected.';
  }
  filters.forEach(input => input.addEventListener('change', applyFilters));
  applyFilters();
})();
