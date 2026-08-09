const playTimerRingSound = () => {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const playTone = (freq, duration, startTime) => {
      const oscillator = audioCtx.createOscillator();
      const gainNode = audioCtx.createGain();
      oscillator.type = 'triangle'; // Triangle wave has more harmonics and sounds like an actual electronic buzzer/alarm
      oscillator.frequency.value = freq;
      gainNode.gain.setValueAtTime(0.8, startTime); 
      gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + duration);
      oscillator.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      oscillator.start(startTime);
      oscillator.stop(startTime + duration);
    };
    const now = audioCtx.currentTime;

    for (let i = 0; i < 3; i++) {
      const timeOffset = i * 0.65;
      playTone(987.77, 0.12, now + timeOffset);        // Beep 1
      playTone(987.77, 0.12, now + timeOffset + 0.18); // Beep 2
    }
  } catch (e) {
    console.warn("Audio play blocked/unsupported: ", e);
  }
};