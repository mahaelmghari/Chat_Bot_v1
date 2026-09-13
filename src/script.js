const input = document.gerElementById('userInput');
const body = document.getElementById('body');

  function sendMsg() {
    const val = input.value.trim();
    if (!val) return;
    const div = document.createElement('div');
    div.className = 'msg me';
    div.textContent = val;
    body.appendChild(div);
    input.value = '';
    body.scrollTop = body.scrollHeight;
  }
 
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMsg();
  });
