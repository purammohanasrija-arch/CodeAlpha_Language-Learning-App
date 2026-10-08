function speakWord(word, lang) {
  if (!window.speechSynthesis) return;
  const s = new SpeechSynthesisUtterance(word);
  s.lang = lang || 'en-US';
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(s);
}

// Legacy shim for old quiz page usage
function checkAnswer(answer) {
  const result = document.getElementById('result');
  if (!result) return;
  if (answer === 'Hola') {
    result.innerHTML = '✅ Correct Answer';
    result.style.color = 'lime';
  } else {
    result.innerHTML = '❌ Wrong Answer';
    result.style.color = 'red';
  }
}

function updateProgress(percent) {
  const bar = document.getElementById('progressBar');
  if (bar) { bar.style.width = percent + '%'; bar.innerHTML = percent + '%'; }
}
