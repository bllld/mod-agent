const form = document.querySelector('#assessment-form');
const input = document.querySelector('#input');
const conversation = document.querySelector('#conversation');

function analyze(text) {
  const lower = text.toLowerCase();
  const signals = [];
  let score = 0;
  if (/https?:\/\//.test(lower)) { signals.push('Contains a link. Avoid opening it until you verify the sender independently.'); score += 1; }
  if (/(urgent|immediately|today|final warning|closed|suspended|limited time)/.test(lower)) { signals.push('Uses urgency or pressure, a common phishing tactic.'); score += 2; }
  if (/(password|verification code|one-time code|otp|login|sign in|credentials)/.test(lower)) { signals.push('Requests access or verification information. Never share a password or one-time code.'); score += 3; }
  if (/(gift card|crypto|bitcoin|wire transfer|payment)/.test(lower)) { signals.push('Mentions a payment method often used to make scams hard to reverse.'); score += 2; }
  if (!signals.length) signals.push('No obvious high-risk pattern was found in this short text, but sender identity still needs independent verification.');
  const level = score >= 5 ? 'High' : score >= 2 ? 'Medium' : 'Low';
  const actions = level === 'High'
    ? ['Do not open the link or reply.', 'Go to the official app or website yourself.', 'Report the message and change exposed credentials immediately.']
    : level === 'Medium'
      ? ['Pause before acting and verify through an official channel.', 'Check the exact domain name carefully.', 'Do not share codes, passwords, or payment information.']
      : ['Verify the sender using a trusted contact method.', 'Avoid entering credentials through a link in a message.', 'Keep security updates and two-factor authentication enabled.'];
  return { level, signals, actions };
}

function addMessage(className, html) { const el = document.createElement('article'); el.className = `message ${className}`; el.innerHTML = html; conversation.append(el); conversation.scrollTop = conversation.scrollHeight; }
form.addEventListener('submit', (event) => {
  event.preventDefault(); const text = input.value.trim(); if (!text) return;
  addMessage('user', text.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])));
  const { level, signals, actions } = analyze(text);
  const cls = level.toLowerCase();
  addMessage('result', `<h2>ModShield assessment: <span class="risk ${cls}">${level} risk</span></h2><strong>Why:</strong><ul>${signals.map(x => `<li>${x}</li>`).join('')}</ul><strong>Safer next steps:</strong><ul>${actions.map(x => `<li>${x}</li>`).join('')}</ul>`);
  input.value = '';
});
