// A deliberately small scheduling model: whole tasks take the first free
// interval they fit in, in the supplied priority order. Appointments and
// their travel are reserved first. Unplaced work stays visible; the day
// never stretches and a task never silently shrinks or splits.
(() => {
  const clock = (minute) => `${String(Math.floor(minute / 60)).padStart(2, "0")}:${String(minute % 60).padStart(2, "0")}`;
  const times = ({ start, end }) => `${clock(start)}–${clock(end)}`;
  const write = (element, text) => {
    element.replaceChildren(...text.split(/(\d+(?::\d+)?(?:–\d+:\d+)?)/).map((part, i) => {
      if (i % 2 === 0) return part;
      const span = document.createElement("span");
      span.className = "n";
      span.textContent = part;
      return span;
    }));
  };

  for (const figure of document.querySelectorAll(".day-wall")) {
    const data = JSON.parse(figure.querySelector("[data-day-wall]").textContent);
    const writing = figure.querySelector("[data-writing]");
    const pickup = figure.querySelector("[data-pickup]");
    const board = figure.querySelector("[data-board]");
    // A gap is [start, end), so back-to-back reservations are valid.
    const gapsBetween = (events) => {
      const gaps = [];
      let start = data.start;
      for (const event of [...events].sort((a, b) => a.start - b.start)) {
        if (event.start > start) gaps.push({ start, end: event.start });
        start = Math.max(start, event.end);
      }
      if (start < data.end) gaps.push({ start, end: data.end });
      return gaps;
    };

    const update = () => {
      const duration = Number(writing.value);
      const appointment = Number(pickup.value);
      const { travel, duration: pickupDuration } = data.pickup;
      const reservations = [
        ...data.fixed,
        { name: "Travel out", start: appointment - travel, end: appointment },
        { name: "Print pickup", start: appointment, end: appointment + pickupDuration },
        { name: "Travel back", start: appointment + pickupDuration, end: appointment + pickupDuration + travel }
      ].map((event) => ({ ...event, kind: "fixed" }));
      const events = [...reservations];
      const unplanned = [];
      for (const task of data.tasks) {
        const minutes = task.id === "writing" ? duration : task.duration;
        const gap = gapsBetween(events).find((slot) => slot.end - slot.start >= minutes);
        if (gap) events.push({ name: task.name, start: gap.start, end: gap.start + minutes, kind: "work" });
        else unplanned.push({ name: task.name, duration: minutes });
      }
      const gaps = gapsBetween(events);
      const free = gaps.reduce((sum, gap) => sum + gap.end - gap.start, 0);
      const longest = Math.max(0, ...gaps.map((gap) => gap.end - gap.start));
      const fragment = document.createDocumentFragment();
      const blocks = [...events, ...gaps.map((gap) => ({ ...gap, name: "Free", kind: "free" }))];
      for (const event of blocks.sort((a, b) => a.start - b.start)) {
        const block = document.createElement("div");
        block.className = `day-wall__event day-wall__event--${event.kind}`;
        block.setAttribute("role", "listitem");
        block.style.gridRow = `${event.start - data.start + 1} / span ${event.end - event.start}`;
        const time = document.createElement("span");
        time.className = "n";
        time.textContent = times(event);
        const name = document.createElement("span");
        name.textContent = event.name;
        block.append(time, name);
        // Very short free gaps retain an accessible name and exact times,
        // without squeezing words below 14 px.
        if (event.end - event.start < 30) {
          block.classList.add("day-wall__event--short");
          block.setAttribute("aria-label", `${times(event)}, ${event.name}`);
          time.setAttribute("aria-hidden", "true");
          name.setAttribute("aria-hidden", "true");
        }
        fragment.append(block);
      }
      board.replaceChildren(fragment);
      figure.querySelector("[data-writing-value]").textContent = duration;
      figure.querySelector("[data-pickup-value]").textContent = clock(appointment);
      writing.setAttribute("aria-valuetext", `${duration} minutes`);
      pickup.setAttribute("aria-valuetext", clock(appointment));
      const count = data.tasks.length - unplanned.length;
      write(figure.querySelector("[data-result]"), `${count} of ${data.tasks.length} tasks fit · ${free} min free · longest gap ${longest} min`);
      write(figure.querySelector("[data-unplanned]"), unplanned.length
        ? `Unplanned: ${unplanned.map((task) => `${task.name} (${task.duration} min)`).join("; ")}.`
        : "All work fits before 18:00.");
    };

    figure.addEventListener("input", update);
    update();
    figure.hidden = false;
    const fallback = figure.nextElementSibling;
    if (fallback?.classList.contains("day-wall-fallback")) fallback.hidden = true;
  }
})();
