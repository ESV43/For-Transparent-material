document.getElementById('reflectance-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('file-input');
    const n_s = document.getElementById('n_s_input').value;
    const A_init = document.getElementById('A_input').value;
    const formData = new FormData();

    formData.append('file', fileInput.files[0]);
    formData.append('n_s', n_s);
    formData.append('A_init', A_init);

    fetch('/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('results');
        const output = document.getElementById('output');
        const ctx = document.getElementById('reflectance-plot').getContext('2d');

        output.innerHTML = `Estimated Cauchy's coefficients: A = ${data.A}, B = ${data.B}<br>Estimated film thickness: d = ${data.d} nm`;
        resultsDiv.style.display = 'block';

        if (window.myChart) {
            window.myChart.destroy();
        }

        window.myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.wavelengths,
                datasets: [
                    {
                        label: 'Experimental Data',
                        data: data.experimental_reflectance,
                        borderColor: 'blue',
                        fill: false,
                        pointStyle: 'circle',
                        pointRadius: 5,
                        showLine: false
                    },
                    {
                        label: 'Fitted Curve',
                        data: data.theoretical_reflectance,
                        borderColor: 'red',
                        fill: false
                    }
                ]
            },
            options: {
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Wavelength (nm)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Reflectance'
                        }
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
