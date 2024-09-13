document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('searchButton');
    const personNameInput = document.getElementById('personName');
    const resultsContainer = document.getElementById('results');
    const errorContainer = document.getElementById('error');

    searchButton.addEventListener('click', searchPerson);
    personNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchPerson();
        }
    });

    async function searchPerson() {
        const name = personNameInput.value.trim();
        if (!name) {
            showError('Please enter a person\'s name');
            return;
        }

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'An error occurred');
            }

            const credits = await response.json();
            displayResults(credits);
        } catch (error) {
            showError(error.message);
        }
    }

    function displayResults(credits) {
        resultsContainer.innerHTML = '';
        errorContainer.classList.add('hidden');

        if (credits.length === 0) {
            showError('No credits found for this person');
            return;
        }

        credits.forEach(credit => {
            const creditElement = document.createElement('div');
            creditElement.className = 'bg-white rounded-lg shadow-md p-6 mb-4';
            creditElement.innerHTML = `
                <h2 class="text-2xl font-bold mb-2">${credit.title}</h2>
                <p class="text-gray-600 mb-2">${credit.type} - ${credit.role}</p>
                <p class="text-gray-800 mb-4">${credit.description || 'No description available'}</p>
                ${credit.trailer ? `<a href="${credit.trailer}" target="_blank" class="inline-block bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors mb-4">Watch Trailer</a>` : ''}
                ${credit.streaming_platforms && credit.streaming_platforms.length > 0 ? 
                    `<div class="mt-4">
                        <h3 class="font-bold mb-2">Available on:</h3>
                        <ul class="list-disc list-inside">
                            ${credit.streaming_platforms.map(platform => `<li>${platform}</li>`).join('')}
                        </ul>
                    </div>` : ''
                }
            `;
            resultsContainer.appendChild(creditElement);
        });
    }

    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
        resultsContainer.innerHTML = '';
    }
});
