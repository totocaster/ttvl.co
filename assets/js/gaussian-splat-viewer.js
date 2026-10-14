import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { SparkRenderer, SplatMesh } from "@sparkjsdev/spark";

const gaussianSplatViewer = {
  init() {
    const viewers = document.querySelectorAll("[data-gaussian-splat]");
    viewers.forEach((viewer) => this.initViewer(viewer));
  },

  initViewer(root) {
    if (root.dataset.gaussianSplatReady === "true") return;

    const frame = root.querySelector("[data-splat-frame]");
    const canvas = root.querySelector("[data-splat-canvas]");
    const status = root.querySelector("[data-splat-status]");
    const resetButton = root.querySelector("[data-splat-reset]");
    const fullscreenButton = root.querySelector("[data-splat-fullscreen]");
    const prompt = root.querySelector("[data-splat-prompt]");
    const src = root.dataset.splatSrc;

    if (!frame || !canvas || !status || !resetButton || !fullscreenButton || !src) {
      return;
    }

    try {
      const renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: false,
        alpha: false,
        powerPreference: "high-performance",
      });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
      renderer.outputColorSpace = THREE.SRGBColorSpace;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(55, 1, 0.01, 1000);
      const controls = new OrbitControls(camera, canvas);
      controls.enableDamping = true;
      controls.dampingFactor = 0.08;
      controls.screenSpacePanning = true;

      const spark = new SparkRenderer({ renderer });
      scene.add(spark);

      let defaultPosition = null;
      let defaultTarget = null;
      let fallbackFullscreen = false;

      const readVector = (value) => {
        if (!value || !value.trim()) return null;
        const coordinates = value.trim().split(/\s+/).map(Number);
        return coordinates.length === 3 && coordinates.every(Number.isFinite)
          ? new THREE.Vector3(...coordinates)
          : null;
      };

      // The media well is dark in both themes (components/_model-viewer.scss).
      renderer.setClearColor(0x111111, 1);

      const resize = () => {
        const width = Math.max(frame.clientWidth, 1);
        const height = Math.max(frame.clientHeight, 1);
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
      };

      const frameSplat = (splat) => {
        const centerAxes = [[], [], []];
        splat.forEachSplat((index, center) => {
          centerAxes[0].push(center.x);
          centerAxes[1].push(center.y);
          centerAxes[2].push(center.z);
        });
        centerAxes.forEach((axis) => axis.sort((a, b) => a - b));

        // Photogrammetry exports can contain distant background splats. Frame
        // the room from the central 90% of splat positions so those outliers do
        // not place the camera hundreds of metres away from the actual scan.
        const percentile = (axis, quantile) =>
          axis[Math.floor((axis.length - 1) * quantile)];
        const lower = new THREE.Vector3(
          percentile(centerAxes[0], 0.05),
          percentile(centerAxes[1], 0.05),
          percentile(centerAxes[2], 0.05),
        );
        const upper = new THREE.Vector3(
          percentile(centerAxes[0], 0.95),
          percentile(centerAxes[1], 0.95),
          percentile(centerAxes[2], 0.95),
        );

        splat.updateMatrixWorld(true);
        const box = new THREE.Box3(lower, upper).applyMatrix4(
          splat.matrixWorld,
        );
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const radius = Math.max(size.x, size.y, size.z) * 0.5;
        const safeRadius = Math.max(radius, 0.5);
        const halfFov = THREE.MathUtils.degToRad(camera.fov * 0.5);
        const distance = (safeRadius / Math.sin(halfFov)) * 1.15;
        const direction = new THREE.Vector3(0.8, 0.4, 1).normalize();

        controls.target.copy(center);
        camera.position.copy(center).addScaledVector(direction, distance);
        camera.near = Math.max(distance / 1000, 0.01);
        camera.far = Math.max(distance + safeRadius * 12, 100);
        camera.updateProjectionMatrix();

        controls.minDistance = Math.max(safeRadius * 0.04, 0.05);
        controls.maxDistance = Math.max(safeRadius * 10, 20);
        const cameraPosition = readVector(root.dataset.cameraPosition);
        const cameraTarget = readVector(root.dataset.cameraTarget);
        if (cameraPosition) camera.position.copy(cameraPosition);
        if (cameraTarget) controls.target.copy(cameraTarget);
        controls.update();

        defaultPosition = camera.position.clone();
        defaultTarget = controls.target.clone();
      };

      const splat = new SplatMesh({
        url: src,
        editable: false,
        raycastable: false,
        onProgress: (event) => {
          if (event.lengthComputable && event.total > 0) {
            const percent = Math.min(
              100,
              Math.round((event.loaded / event.total) * 100),
            );
            status.textContent = `Loading scan… ${percent}%`;
          }
        },
        onLoad: (loadedSplat) => {
          frameSplat(loadedSplat);
          root.classList.add("is-loaded");
          status.hidden = true;
          resetButton.disabled = false;
          armPrompt();
        },
      });
      scene.add(splat);

      // The drag hint, as model-viewer's interaction prompt: once the scan
      // has been on screen for three seconds untouched, a hand sways left and
      // right and the camera swings with it around the target. The first
      // drag, wheel, or key ends it for good. Readers who prefer reduced
      // motion get the hand standing still and no camera movement.
      const PROMPT_DELAY = 3000;
      const PROMPT_PERIOD = 5000;
      const PROMPT_SWING = 0.18; // radians each way
      const PROMPT_TRAVEL = 40; // px each way
      const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;
      let promptState = "idle"; // idle → waiting → running → done
      let promptTimer = 0;
      let promptStart = 0;
      let promptBase = null;
      let promptVisible = false;

      // One cycle, after model-viewer's wiggle: out left, across to the
      // right, back to centre, then a rest. Eased between keyframes.
      const promptKeys = [
        [0, 0], [5, -1], [6, -1], [14, 1], [15, 1], [20, 0], [38, 0],
      ];
      const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
      const promptOffset = (elapsed) => {
        const frame = ((elapsed % PROMPT_PERIOD) / PROMPT_PERIOD) * 38;
        for (let i = 1; i < promptKeys.length; i += 1) {
          const [f1, v1] = promptKeys[i];
          const [f0, v0] = promptKeys[i - 1];
          if (frame <= f1) return v0 + (v1 - v0) * ease((frame - f0) / (f1 - f0));
        }
        return 0;
      };

      const endPrompt = () => {
        if (promptState === "done") return;
        promptState = "done";
        clearTimeout(promptTimer);
        if (prompt) prompt.classList.remove("is-visible");
      };

      const startPrompt = () => {
        if (promptState !== "waiting" || !prompt) return;
        promptState = "running";
        promptStart = performance.now();
        promptBase = camera.position.clone().sub(controls.target);
        prompt.hidden = false;
        requestAnimationFrame(() => prompt.classList.add("is-visible"));
      };

      const schedulePrompt = () => {
        clearTimeout(promptTimer);
        if (promptState === "waiting" && promptVisible) {
          promptTimer = setTimeout(startPrompt, PROMPT_DELAY);
        }
      };

      const armPrompt = () => {
        if (!prompt || promptState !== "idle") return;
        promptState = "waiting";
        schedulePrompt();
      };

      const stepPrompt = (now) => {
        if (promptState !== "running" || reducedMotion) return;
        const offset = promptOffset(now - promptStart);
        prompt.style.transform = `translate(-50%, -50%) translateX(${offset * PROMPT_TRAVEL}px)`;
        camera.position
          .copy(promptBase)
          .applyAxisAngle(camera.up, -offset * PROMPT_SWING)
          .add(controls.target);
      };

      controls.addEventListener("start", endPrompt);
      canvas.addEventListener("keydown", endPrompt);
      canvas.addEventListener("pointerdown", endPrompt);

      if ("IntersectionObserver" in window) {
        new IntersectionObserver((entries) => {
          promptVisible = entries.some((entry) => entry.isIntersecting);
          if (promptVisible) schedulePrompt();
          else clearTimeout(promptTimer);
        }, { threshold: 0.5 }).observe(frame);
      } else {
        promptVisible = true;
      }

      const resetView = () => {
        if (!defaultPosition || !defaultTarget) return;
        camera.position.copy(defaultPosition);
        controls.target.copy(defaultTarget);
        controls.update();
      };

      const updateFullscreenButton = () => {
        const fullscreen =
          document.fullscreenElement === frame || fallbackFullscreen;
        fullscreenButton.setAttribute(
          "aria-label",
          fullscreen
            ? "Exit Gaussian splat full screen"
            : "View Gaussian splat full screen",
        );
        fullscreenButton.title = fullscreen ? "Exit full screen" : "View full screen";
      };

      const exitFallbackFullscreen = () => {
        if (!fallbackFullscreen) return;
        fallbackFullscreen = false;
        frame.classList.remove("is-fullscreen");
        document.documentElement.classList.remove(
          "gaussian-splat-fullscreen-active",
        );
      };

      const toggleFullscreen = async () => {
        if (document.fullscreenElement === frame) {
          await document.exitFullscreen();
          return;
        }

        if (fallbackFullscreen) {
          exitFallbackFullscreen();
          updateFullscreenButton();
          requestAnimationFrame(resize);
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

        fallbackFullscreen = true;
        frame.classList.add("is-fullscreen");
        document.documentElement.classList.add(
          "gaussian-splat-fullscreen-active",
        );
        updateFullscreenButton();
        requestAnimationFrame(resize);
      };

      resetButton.addEventListener("click", () => {
        endPrompt();
        resetView();
      });
      fullscreenButton.hidden = false;
      fullscreenButton.addEventListener("click", toggleFullscreen);

      document.addEventListener("fullscreenchange", () => {
        updateFullscreenButton();
        requestAnimationFrame(resize);
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && fallbackFullscreen) {
          event.preventDefault();
          exitFallbackFullscreen();
          updateFullscreenButton();
          requestAnimationFrame(resize);
        }
      });

      if ("ResizeObserver" in window) {
        const resizeObserver = new ResizeObserver(resize);
        resizeObserver.observe(frame);
      } else {
        window.addEventListener("resize", resize);
      }
      resize();

      renderer.setAnimationLoop((now) => {
        stepPrompt(now);
        controls.update();
        renderer.render(scene, camera);
      });

      root.dataset.gaussianSplatReady = "true";
    } catch (error) {
      root.classList.add("has-error");
      status.textContent = "This browser could not display the Gaussian splat.";
      console.error(error);
    }
  },
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => gaussianSplatViewer.init());
} else {
  gaussianSplatViewer.init();
}
