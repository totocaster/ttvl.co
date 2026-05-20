(() => {
  function pronunciationName(button) {
    return button.dataset.pronunciationName || 'this name';
  }

  function setPaused(button) {
    const name = pronunciationName(button);

    button.classList.remove('is-playing');
    button.setAttribute('aria-label', `Play pronunciation of ${name}`);
    button.setAttribute('aria-pressed', 'false');
    button.dataset.pronunciationState = 'paused';
    button.title = `Play pronunciation of ${name}`;
  }

  function setPlaying(button) {
    const name = pronunciationName(button);

    button.classList.add('is-playing');
    button.setAttribute('aria-label', `Pause pronunciation of ${name}`);
    button.setAttribute('aria-pressed', 'true');
    button.dataset.pronunciationState = 'playing';
    button.title = `Pause pronunciation of ${name}`;
  }

  function pauseAudio(button, audio) {
    audio.pause();
    setPaused(button);
  }

  function initPronunciationButtons() {
    document.querySelectorAll('[data-pronunciation-button]').forEach((button) => {
      const wrapper = button.closest('.pronunciation-name');
      const audio = wrapper?.querySelector('.pronunciation-audio');

      if (!audio) {
        return;
      }

      audio.loop = false;
      audio.addEventListener('ended', () => setPaused(button));
      audio.addEventListener('pause', () => setPaused(button));

      button.addEventListener('click', async () => {
        if (!audio.paused) {
          pauseAudio(button, audio);
          return;
        }

        if (audio.ended || audio.currentTime >= audio.duration) {
          audio.currentTime = 0;
        }

        setPlaying(button);

        try {
          await audio.play();
        } catch (_error) {
          setPaused(button);
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPronunciationButtons);
  } else {
    initPronunciationButtons();
  }
})();
