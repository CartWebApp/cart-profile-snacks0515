
// Select the elements we need to manipulate
const theButton = document.getElementById('button');
const panels = document.querySelectorAll('.panel');
const closeButton = document.getElementById('close');


// Add the event listener to the profile button
theButton.addEventListener('click', () => {
  panels.forEach((panel) => {
    panel.classList.toggle('open');
  });
});

// Add the event listener to the close button
closeButton.addEventListener('click', () => {
  panels.forEach((panel) => { 
    panel.classList.remove('open');
  });
});