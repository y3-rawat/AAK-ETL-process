import base64
from io import BytesIO
import matplotlib.pyplot as plt
import json

# Function to generate base64 string for a chart
def generate_chart_base64():
    plt.plot([1, 2, 3, 4], [10, 20, 25, 30])
    plt.title('Sample Chart')
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Generate base64 strings for multiple charts
charts = [generate_chart_base64() for _ in range(3)]

# Save the base64 strings to a JSON file
with open('charts.json', 'w') as f:
    json.dump(charts, f)