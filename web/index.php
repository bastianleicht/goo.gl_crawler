<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>goo.gl Crawler Statistics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/luxon@2.3.0/build/global/luxon.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.0.0"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: #f9f9f9;
        }
        .container {
            max-width: 90%;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1, h2 {
            text-align: center;
            color: #007bff;
        }
        #totalUrls, #recent5Minutes {
            font-size: 18px;
            text-align: center;
            margin-bottom: 20px;
        }
        canvas {
            display: block;
            max-width: 100%;
            margin: 0 auto;
        }
        .chart-container {
            width: 100%;
            max-width: 100%;
            margin: 0 auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            table-layout: fixed;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        th {
            background-color: #f2f2f2;
        }
        td {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .url-column {
            max-width: 300px;
        }
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            th, td {
                font-size: 14px;
            }
            .url-column {
                max-width: 200px;
            }
            h1, h2 {
                font-size: 18px;
            }
        }
        @media (max-width: 480px) {
            .url-column {
                max-width: 150px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>goo.gl Crawler Statistics</h1>

        <!-- Gesamtanzahl der URLs -->
        <div id="totalUrls">Gesamtanzahl der URLs: </div>

        <!-- Anzahl der URLs in den letzten 5 Minuten -->
        <div id="recent5Minutes">Anzahl der URLs in den letzten 5 Minuten: </div>

        <!-- Diagramm für die Anzahl der URLs pro Stunde -->
        <div class="chart-container">
            <canvas id="hourlyChart" width="400" height="200"></canvas>
        </div>

        <!-- Letzten 10 URLs -->
        <h2>Letzten 10 gecrawlten URLs</h2>
        <table id="last10UrlsTable">
            <thead>
                <tr>
                    <th class="url-column">Original URL</th>
                    <th class="url-column">Redirect URL</th>
                    <th>Scraped At</th>
                </tr>
            </thead>
            <tbody>
                <!-- Daten werden hier dynamisch eingefügt -->
            </tbody>
        </table>
    </div>

    <script>
        // Funktion zum Abrufen der Daten und Aktualisieren des Diagramms und der URLs
        function updateData() {
            fetch('data.php')
                .then(response => response.json())
                .then(data => {
                    let formatter = new Intl.NumberFormat('de-DE', {
                        style: 'decimal', // oder 'currency', 'percent'
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    });

                    //console.log(formatter.format(data.total_urls));

                    // Gesamtanzahl der URLs aktualisieren
                    document.getElementById('totalUrls').innerText = `Gesamtanzahl der URLs: ${formatter.format(data.total_urls)}`;

                    // Anzahl der URLs in den letzten 5 Minuten aktualisieren
                    document.getElementById('recent5Minutes').innerText = `Anzahl der URLs in den letzten 5 Minuten: ${data.recent_5_minutes}`;

                    // Daten für das Diagramm aufbereiten
                    const hourlyDataFromPHP = data.hourly_data;
                    const labels = hourlyDataFromPHP.map(item => new Date(item.hour));
                    const chartData = hourlyDataFromPHP.map(item => item.url_count);

                    // Diagramm aktualisieren
                    hourlyChart.data.labels = labels;
                    hourlyChart.data.datasets[0].data = chartData;
                    hourlyChart.update();

                    // Letzten 10 URLs aktualisieren
                    const last10UrlsTableBody = document.querySelector('#last10UrlsTable tbody');
                    last10UrlsTableBody.innerHTML = '';
                    data.last_10_urls.forEach(url => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td class="url-column" title="${url.original_url}">${url.original_url}</td>
                            <td class="url-column" title="${url.redirect_url}">${url.redirect_url}</td>
                            <td>${new Date(url.scraped_at).toLocaleString()}</td>
                        `;
                        last10UrlsTableBody.appendChild(row);
                    });
                })
                .catch(error => console.error('Fehler beim Abrufen der Daten:', error));
        }

        // Erstellen des Diagramms
        const ctx = document.getElementById('hourlyChart').getContext('2d');
        const hourlyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Anzahl der URLs',
                    data: [],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour',
                            tooltipFormat: 'yyyy-MM-dd HH:mm',
                            displayFormats: {
                                hour: 'MMM d, HH:mm'
                            }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Anzahl der gecrawlten URLs pro Stunde'
                    }
                }
            }
        });

        // Daten initial abrufen und dann alle 5 Sekunden aktualisieren
        updateData();
        setInterval(updateData, 5000);
    </script>
</body>
</html>
