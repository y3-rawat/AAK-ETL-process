document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById('myChart').getContext('2d');
    const country_code = 'AF'; // Replace with the desired country code

    fetch(`/api/indicator-data/${country_code}`)
        .then(response => response.json())
        .then(data => {
            const indicatorData = data.indicator_data;
            const indicatorKey = 'AG.LND.AGRI.ZS'; // Replace with the desired indicator key
            const indicatorValues = indicatorData[country_code][indicatorKey];

            const years = Object.keys(indicatorValues).filter(year => !isNaN(year));
            const values = years.map(year => indicatorValues[year]);

            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: years,
                    datasets: [{
                        label: 'Indicator Data',
                        data: values,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Year'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Value'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching indicator data:', error));
});