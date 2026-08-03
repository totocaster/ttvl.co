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

      const updateBackground = () => {
        const dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        renderer.setClearColor(dark ? 0x1c1c1c : 0xfafafa, 1);
      };

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
        },
      });
      scene.add(splat);

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

      resetButton.addEventListener("click", resetView);
      fullscreenButton.hidden = false;
      fullscreenButton.addEventListener("click", toggleFullscreen);
      canvas.addEventListener("pointerdown", () => canvas.focus({ preventScroll: true }));

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

      const colorScheme = window.matchMedia("(prefers-color-scheme: dark)");
      colorScheme.addEventListener("change", updateBackground);
      updateBackground();

      if ("ResizeObserver" in window) {
        const resizeObserver = new ResizeObserver(resize);
        resizeObserver.observe(frame);
      } else {
        window.addEventListener("resize", resize);
      }
      resize();

      renderer.setAnimationLoop(() => {
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
