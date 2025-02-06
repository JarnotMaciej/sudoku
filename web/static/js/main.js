document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerText;

    form.addEventListener('submit', function() {
        // Disable button and show loading state
        submitButton.disabled = true;
        submitButton.innerText = 'Generating...';

        // Re-enable after a delay (in case of error)
        setTimeout(() => {
            submitButton.disabled = false;
            submitButton.innerText = originalButtonText;
        }, 10000);
    });

    // Handle radio button styling
    const difficultyOptions = document.querySelectorAll('input[name="difficulty"]');
    difficultyOptions.forEach(radio => {
        radio.addEventListener('change', function() {
            // Remove active state from all buttons
            difficultyOptions.forEach(r => {
                r.parentElement.querySelector('.btn').classList.remove('bg-black', 'text-white');
                r.parentElement.querySelector('.btn').classList.add('bg-white', 'text-black');
            });
            
            // Add active state to selected button
            if (this.checked) {
                this.parentElement.querySelector('.btn').classList.remove('bg-white', 'text-black');
                this.parentElement.querySelector('.btn').classList.add('bg-black', 'text-white');
            }
        });
    });

    // Trigger change event on checked radio button
    const checkedRadio = document.querySelector('input[name="difficulty"]:checked');
    if (checkedRadio) {
        checkedRadio.dispatchEvent(new Event('change'));
    }
});
