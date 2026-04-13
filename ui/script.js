// Screen Navigation
const navChips = document.querySelectorAll('.nav-chip');
const screens = document.querySelectorAll('.screen');

navChips.forEach((chip) => {
  chip.addEventListener('click', () => {
    const targetId = chip.getAttribute('data-target');
    const targetScreen = document.getElementById(targetId);

    // Remove active state from all
    navChips.forEach((c) => c.classList.remove('is-active'));
    screens.forEach((s) => s.classList.remove('is-active'));

    // Add active state to clicked
    chip.classList.add('is-active');
    if (targetScreen) {
      targetScreen.classList.add('is-active');
    }
  });
});

// Quick login demo buttons
document.querySelectorAll('.btn-demo').forEach((btn) => {
  btn.addEventListener('click', () => {
    const role = btn.getAttribute('data-role');
    const screen = role === 'customer' ? 'screen-customer' : 'screen-caterer';

    // Navigate to the appropriate screen
    const chip = document.querySelector(`[data-target="${screen}"]`);
    if (chip) {
      chip.click();
    }
  });
});
