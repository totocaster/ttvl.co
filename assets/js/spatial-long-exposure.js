(() => {
  "use strict";

  const root = document.querySelector("[data-spatial-long-exposure]");
  if (!root) return;

  const canvas = root.querySelector("[data-map-canvas]");
  const frame = root.querySelector(".spatial-long-exposure__frame");
  const tileLayer = root.querySelector("[data-map-tiles]");
  const loading = root.querySelector("[data-map-loading]");
  const modeButtons = Array.from(root.querySelectorAll("[data-map-mode]"));
  const resetButton = root.querySelector("[data-map-reset]");
  const fullscreenButton = root.querySelector("[data-map-fullscreen]");
  const context = canvas.getContext("2d");

  const defaultView = { centerX: 0.5, centerY: 0.48, zoom: 1 };
  const maximumZoom = 32768;
  const view = { ...defaultView };
  const pointers = new Map();
  const tiles = new Map();

  let width = 1;
  let height = 1;
  let baseScale = 1;
  let mode = "both";
  let pointData = [];
  let segmentData = [];
  let ready = false;
  let drag = null;
  let pinch = null;
  let drawRequest = 0;
  let isAtDefaultView = true;
  let placeGlow = null;
  let placeGlowColor = "";

  const clamp = (value, minimum, maximum) =>
    Math.max(minimum, Math.min(maximum, value));

  const normalizeView = () => {
    view.centerX = ((view.centerX % 1) + 1) % 1;
    view.centerY = clamp(view.centerY, 0.05, 0.95);
    view.zoom = clamp(view.zoom, 1, maximumZoom);
  };

  const mercator = (longitude, latitude) => {
    const clampedLatitude = clamp(latitude, -85.051129, 85.051129);
    const sine = Math.sin((clampedLatitude * Math.PI) / 180);
    return [
      (longitude + 180) / 360,
      0.5 - Math.log((1 + sine) / (1 - sine)) / (4 * Math.PI),
    ];
  };

  const screenPoint = (point) => {
    let deltaX = point[0] - view.centerX;
    deltaX -= Math.round(deltaX);
    const scale = baseScale * view.zoom;
    return [
      width / 2 + deltaX * scale,
      height / 2 + (point[1] - view.centerY) * scale,
    ];
  };

  const projectedSegment = (segment) => {
    let firstDeltaX = segment[0] - view.centerX;
    let secondDeltaX = segment[2] - view.centerX;
    firstDeltaX -= Math.round(firstDeltaX);
    secondDeltaX -= Math.round(secondDeltaX);
    if (secondDeltaX - firstDeltaX > 0.5) secondDeltaX -= 1;
    if (secondDeltaX - firstDeltaX < -0.5) secondDeltaX += 1;

    const scale = baseScale * view.zoom;
    return [
      width / 2 + firstDeltaX * scale,
      height / 2 + (segment[1] - view.centerY) * scale,
      width / 2 + secondDeltaX * scale,
      height / 2 + (segment[3] - view.centerY) * scale,
    ];
  };

  const fitDefaultView = () => {
    if (!pointData.length) return;

    const xValues = pointData.map((point) => point[0]).sort((a, b) => a - b);
    let largestGap = xValues[0] + 1 - xValues[xValues.length - 1];
    let gapEndIndex = xValues.length - 1;
    for (let index = 0; index < xValues.length - 1; index += 1) {
      const gap = xValues[index + 1] - xValues[index];
      if (gap > largestGap) {
        largestGap = gap;
        gapEndIndex = index;
      }
    }

    const startX = xValues[(gapEndIndex + 1) % xValues.length];
    let endX = xValues[gapEndIndex];
    if (endX < startX) endX += 1;
    const spanX = Math.max(0.01, endX - startX);
    let minimumY = Infinity;
    let maximumY = -Infinity;
    pointData.forEach((point) => {
      minimumY = Math.min(minimumY, point[1]);
      maximumY = Math.max(maximumY, point[1]);
    });
    const spanY = Math.max(0.01, maximumY - minimumY);
    const fittedScale = Math.min(
      (width * 0.86) / spanX,
      (height * 0.82) / spanY,
    );

    defaultView.centerX = ((startX + spanX / 2) % 1 + 1) % 1;
    defaultView.centerY = (minimumY + maximumY) / 2;
    defaultView.zoom = clamp(fittedScale / baseScale, 1, maximumZoom);
    Object.assign(view, defaultView);
    normalizeView();
  };

  const tileURL = (zoom, x, y) =>
    root.dataset.tileTemplate
      .replace("{z}", zoom)
      .replace("{x}", x)
      .replace("{y}", y);

  const updateTiles = () => {
    const worldScale = baseScale * view.zoom;
    const zoom = clamp(
      Math.round(Math.log2(worldScale / 256)),
      1,
      18,
    );
    const tileCount = 2 ** zoom;
    const tileSize = worldScale / tileCount;
    const leftWorld = view.centerX - width / (2 * worldScale);
    const rightWorld = view.centerX + width / (2 * worldScale);
    const topWorld = view.centerY - height / (2 * worldScale);
    const bottomWorld = view.centerY + height / (2 * worldScale);
    const firstX = Math.floor(leftWorld * tileCount);
    const lastX = Math.floor(rightWorld * tileCount);
    const firstY = Math.max(0, Math.floor(topWorld * tileCount));
    const lastY = Math.min(
      tileCount - 1,
      Math.floor(bottomWorld * tileCount),
    );
    const needed = new Set();

    for (let displayX = firstX; displayX <= lastX; displayX += 1) {
      const requestX = ((displayX % tileCount) + tileCount) % tileCount;
      for (let y = firstY; y <= lastY; y += 1) {
        const key = `${zoom}/${displayX}/${y}`;
        needed.add(key);

        let image = tiles.get(key);
        if (!image) {
          image = document.createElement("img");
          image.className = "spatial-long-exposure__tile";
          image.alt = "";
          image.decoding = "async";
          image.src = tileURL(zoom, requestX, y);
          image.addEventListener(
            "error",
            () => {
              image.remove();
              tiles.delete(key);
            },
            { once: true },
          );
          tiles.set(key, image);
          tileLayer.appendChild(image);
        }

        image.style.left = `${width / 2 + (displayX / tileCount - view.centerX) * worldScale}px`;
        image.style.top = `${height / 2 + (y / tileCount - view.centerY) * worldScale}px`;
        image.style.width = `${tileSize + 0.5}px`;
        image.style.height = `${tileSize + 0.5}px`;
      }
    }

    tiles.forEach((image, key) => {
      if (!needed.has(key)) {
        image.remove();
        tiles.delete(key);
      }
    });
  };

  const drawConnections = (traceColor) => {
    context.lineCap = "round";
    context.lineJoin = "round";

    segmentData.forEach((segment) => {
      const screen = projectedSegment(segment);
      const margin = 20;
      if (
        Math.max(screen[0], screen[2]) < -margin ||
        Math.min(screen[0], screen[2]) > width + margin ||
        Math.max(screen[1], screen[3]) < -margin ||
        Math.min(screen[1], screen[3]) > height + margin
      ) {
        return;
      }

      const count = segment[4];
      const recurrence = Math.log2(Math.max(1, count));

      context.strokeStyle = `rgba(${traceColor}, ${Math.min(
        0.12,
        0.025 + recurrence * 0.012,
      )})`;
      context.lineWidth = Math.min(3, 1.5 + recurrence * 0.22);
      context.beginPath();
      context.moveTo(screen[0], screen[1]);
      context.lineTo(screen[2], screen[3]);
      context.stroke();

      context.strokeStyle = `rgba(${traceColor}, ${Math.min(
        0.24,
        0.075 + recurrence * 0.018,
      )})`;
      context.lineWidth = Math.min(1.4, 0.6 + recurrence * 0.11);
      context.beginPath();
      context.moveTo(screen[0], screen[1]);
      context.lineTo(screen[2], screen[3]);
      context.stroke();
    });
  };

  const getPlaceGlow = (placeColor) => {
    if (placeGlow && placeGlowColor === placeColor) return placeGlow;

    const size = 32;
    placeGlow = document.createElement("canvas");
    placeGlow.width = size;
    placeGlow.height = size;
    const glowContext = placeGlow.getContext("2d");
    const gradient = glowContext.createRadialGradient(
      size / 2,
      size / 2,
      0,
      size / 2,
      size / 2,
      size / 2,
    );
    gradient.addColorStop(0, `rgba(${placeColor}, 1)`);
    gradient.addColorStop(0.22, `rgba(${placeColor}, 0.8)`);
    gradient.addColorStop(1, `rgba(${placeColor}, 0)`);
    glowContext.fillStyle = gradient;
    glowContext.fillRect(0, 0, size, size);
    placeGlowColor = placeColor;
    return placeGlow;
  };

  const drawPlaces = (placeColor) => {
    const radius = Math.min(
      3.2,
      1.35 + Math.max(0, Math.log2(view.zoom)) * 0.24,
    );
    const haloDiameter = Math.max(5, radius * 3.8);
    const coreSize = Math.max(1.3, radius * 0.72);
    const glow = getPlaceGlow(placeColor);
    const visiblePoints = [];

    pointData.forEach((point) => {
      const screen = screenPoint(point);
      if (
        screen[0] < -4 ||
        screen[0] > width + 4 ||
        screen[1] < -4 ||
        screen[1] > height + 4
      ) {
        return;
      }

      visiblePoints.push([point, screen]);
    });

    visiblePoints.forEach(([point, screen]) => {
      const recurrence = Math.log2(Math.max(1, point[2]));
      context.globalAlpha = Math.min(
        0.4,
        (point[3] === 2 ? 0.14 : 0.18) + recurrence * 0.035,
      );
      context.drawImage(
        glow,
        screen[0] - haloDiameter / 2,
        screen[1] - haloDiameter / 2,
        haloDiameter,
        haloDiameter,
      );
    });

    context.globalAlpha = 1;
    visiblePoints.forEach(([point, screen]) => {
      const recurrence = Math.log2(Math.max(1, point[2]));
      const coreOpacity = Math.min(
        0.9,
        (point[3] === 2 ? 0.68 : 0.78) + recurrence * 0.025,
      );
      context.fillStyle = `rgba(${placeColor}, ${coreOpacity})`;
      context.fillRect(
        screen[0] - coreSize / 2,
        screen[1] - coreSize / 2,
        coreSize,
        coreSize,
      );
    });
  };

  const draw = () => {
    drawRequest = 0;
    if (!ready) return;

    const styles = getComputedStyle(root);
    const connectionColor = styles
      .getPropertyValue("--spatial-map-connection")
      .trim();
    const placeColor = styles
      .getPropertyValue("--spatial-map-place")
      .trim();

    context.clearRect(0, 0, width, height);
    updateTiles();

    if (mode === "connections" || mode === "both") {
      drawConnections(connectionColor);
    }
    if (mode === "places" || mode === "both") {
      drawPlaces(placeColor);
    }
  };

  const requestDraw = () => {
    if (!drawRequest) drawRequest = requestAnimationFrame(draw);
  };

  const resize = () => {
    const rect = canvas.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = Math.max(1, Math.round(rect.width));
    height = Math.max(1, Math.round(rect.height));
    baseScale = width * 0.94;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    if (ready && isAtDefaultView) fitDefaultView();
    requestDraw();
  };

  const resetView = () => {
    fitDefaultView();
    isAtDefaultView = true;
    requestDraw();
  };

  const isFullscreen = () =>
    document.fullscreenElement === frame ||
    frame.classList.contains("is-fullscreen");

  const updateFullscreenButton = () => {
    const fullscreen = isFullscreen();
    fullscreenButton.setAttribute(
      "aria-label",
      fullscreen ? "Exit full screen" : "View map full screen",
    );
    fullscreenButton.title = fullscreen ? "Exit full screen" : "View full screen";
  };

  const exitFallbackFullscreen = () => {
    frame.classList.remove("is-fullscreen");
    document.documentElement.classList.remove(
      "spatial-long-exposure-fullscreen-active",
    );
  };

  const toggleFullscreen = async () => {
    if (document.fullscreenElement === frame) {
      await document.exitFullscreen();
      return;
    }

    if (frame.classList.contains("is-fullscreen")) {
      exitFallbackFullscreen();
      updateFullscreenButton();
      return;
    }

    if (frame.requestFullscreen) {
      try {
        await frame.requestFullscreen();
        return;
      } catch (error) {
        // Use the fixed-position fallback when full screen is unavailable.
      }
    }

    frame.classList.add("is-fullscreen");
    document.documentElement.classList.add(
      "spatial-long-exposure-fullscreen-active",
    );
    updateFullscreenButton();
  };

  const setMode = (nextMode) => {
    mode = nextMode;
    modeButtons.forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.mapMode === mode),
      );
    });
    requestDraw();
  };

  const zoomAt = (nextZoom, x, y) => {
    isAtDefaultView = false;
    const previousScale = baseScale * view.zoom;
    const worldX = view.centerX + (x - width / 2) / previousScale;
    const worldY = view.centerY + (y - height / 2) / previousScale;
    view.zoom = clamp(nextZoom, 1, maximumZoom);
    const nextScale = baseScale * view.zoom;
    view.centerX = worldX - (x - width / 2) / nextScale;
    view.centerY = worldY - (y - height / 2) / nextScale;
    normalizeView();
    requestDraw();
  };

  const pointerPosition = (event) => {
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  };

  const beginPinch = () => {
    const points = Array.from(pointers.values());
    if (points.length !== 2) {
      pinch = null;
      return;
    }
    const midpoint = {
      x: (points[0].x + points[1].x) / 2,
      y: (points[0].y + points[1].y) / 2,
    };
    const distance = Math.hypot(
      points[1].x - points[0].x,
      points[1].y - points[0].y,
    );
    const scale = baseScale * view.zoom;
    pinch = {
      distance,
      zoom: view.zoom,
      worldX: view.centerX + (midpoint.x - width / 2) / scale,
      worldY: view.centerY + (midpoint.y - height / 2) / scale,
    };
  };

  modeButtons.forEach((button) => {
    button.addEventListener("click", () => setMode(button.dataset.mapMode));
  });
  resetButton.addEventListener("click", resetView);
  fullscreenButton.hidden = false;
  fullscreenButton.addEventListener("click", toggleFullscreen);

  document.addEventListener("fullscreenchange", () => {
    updateFullscreenButton();
    requestAnimationFrame(resize);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && frame.classList.contains("is-fullscreen")) {
      event.preventDefault();
      exitFallbackFullscreen();
      updateFullscreenButton();
      requestAnimationFrame(resize);
    }
  });

  canvas.addEventListener(
    "wheel",
    (event) => {
      event.preventDefault();
      const position = pointerPosition(event);
      zoomAt(view.zoom * Math.exp(-event.deltaY * 0.0015), position.x, position.y);
    },
    { passive: false },
  );

  canvas.addEventListener("pointerdown", (event) => {
    canvas.setPointerCapture(event.pointerId);
    const position = pointerPosition(event);
    pointers.set(event.pointerId, position);

    if (pointers.size === 1) {
      drag = {
        position,
        centerX: view.centerX,
        centerY: view.centerY,
      };
      pinch = null;
    } else if (pointers.size === 2) {
      drag = null;
      beginPinch();
    }
  });

  canvas.addEventListener("pointermove", (event) => {
    const position = pointerPosition(event);

    if (!pointers.has(event.pointerId)) {
      return;
    }

    pointers.set(event.pointerId, position);
    if (pointers.size === 1 && drag) {
      isAtDefaultView = false;
      const scale = baseScale * view.zoom;
      view.centerX =
        drag.centerX - (position.x - drag.position.x) / scale;
      view.centerY =
        drag.centerY - (position.y - drag.position.y) / scale;
      normalizeView();
      requestDraw();
    } else if (pointers.size === 2 && pinch) {
      isAtDefaultView = false;
      const points = Array.from(pointers.values());
      const midpoint = {
        x: (points[0].x + points[1].x) / 2,
        y: (points[0].y + points[1].y) / 2,
      };
      const distance = Math.hypot(
        points[1].x - points[0].x,
        points[1].y - points[0].y,
      );
      view.zoom = clamp(
        pinch.zoom * (distance / Math.max(1, pinch.distance)),
        1,
        maximumZoom,
      );
      const scale = baseScale * view.zoom;
      view.centerX = pinch.worldX - (midpoint.x - width / 2) / scale;
      view.centerY = pinch.worldY - (midpoint.y - height / 2) / scale;
      normalizeView();
      requestDraw();
    }
  });

  const releasePointer = (event) => {
    pointers.delete(event.pointerId);
    if (pointers.size === 1) {
      const remaining = Array.from(pointers.values())[0];
      drag = {
        position: remaining,
        centerX: view.centerX,
        centerY: view.centerY,
      };
      pinch = null;
    } else if (!pointers.size) {
      drag = null;
      pinch = null;
    }
  };

  canvas.addEventListener("pointerup", releasePointer);
  canvas.addEventListener("pointercancel", releasePointer);

  canvas.addEventListener("keydown", (event) => {
    const panDistance = 50 / (baseScale * view.zoom);
    const key = event.key;
    const supportedKeys = [
      "+",
      "=",
      "-",
      "_",
      "0",
      "ArrowLeft",
      "ArrowRight",
      "ArrowUp",
      "ArrowDown",
    ];
    if (!supportedKeys.includes(key)) {
      return;
    }
    event.preventDefault();

    if (key === "+" || key === "=") {
      zoomAt(view.zoom * 1.5, width / 2, height / 2);
    } else if (key === "-" || key === "_") {
      zoomAt(view.zoom / 1.5, width / 2, height / 2);
    } else if (key === "0") {
      resetView();
    } else {
      isAtDefaultView = false;
      if (key === "ArrowLeft") view.centerX -= panDistance;
      if (key === "ArrowRight") view.centerX += panDistance;
      if (key === "ArrowUp") view.centerY -= panDistance;
      if (key === "ArrowDown") view.centerY += panDistance;
      normalizeView();
      requestDraw();
    }
  });

  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(frame);

  const themeQuery = window.matchMedia("(prefers-color-scheme: dark)");
  themeQuery.addEventListener?.("change", requestDraw);

  fetch(root.dataset.traceUrl)
    .then((response) => {
      if (!response.ok) throw new Error("Location data could not be loaded");
      return response.json();
    })
    .then((trace) => {
      pointData = trace.points.map((point) => {
        const projected = mercator(point[0], point[1]);
        return [projected[0], projected[1], point[2], point[3]];
      });
      segmentData = trace.segments.map((segment) => {
        const first = mercator(segment[0], segment[1]);
        const second = mercator(segment[2], segment[3]);
        return [first[0], first[1], second[0], second[1], segment[4]];
      });
      canvas.setAttribute(
        "aria-label",
        `${trace.uniquePointCount.toLocaleString()} undated locations from location history and geotagged photographs, with connections between recorded visits`,
      );
      ready = true;
      loading.hidden = true;
      resize();
    })
    .catch(() => {
      loading.textContent = "The map could not be developed.";
    });
})();
