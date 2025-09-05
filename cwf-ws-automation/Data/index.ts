import * as fs from 'fs';

// Function to receive metrics and write them to an HTML file
export function writeMetricsToHTML(metrics: { LCP: number; FCP: number; CLS: number;SI:number;TBT:number ; Performance: number;relativePath:string }) {
    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LightHouse Performance Metrics</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        table {
            width: 50%;
            border-collapse: collapse;
            margin-top: 0; /* Remove top margin from table */ 
        }
        th, td {
            border: 1px solid black; 
            padding: 28px;
            text-align: center;
        }
        th {
            font-weight: bold; 
            background-color: #6495ED; 
            text-align: center;
            padding: 28px;
        }
        #t01 {
            width: 50%;
            background-color: #cce6ff;
        }
        
    </style>
</head>
<body>
    <h1>${metrics.relativePath} LightHouse Performance Metrics</h1>
   <img src="https://c.tenor.com/3INen6pD11gAAAAd/national-lighthouse-day-happy-lighthouse-day.gif" width=50%;height="200>
      
        <table id="t01">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                     <tr>
                    <td>Performance Score</td>
                    <td>${metrics.Performance}</td>
                </tr>
                    <td>Largest Contentful Paint (LCP)</td>
                    <td>${metrics.LCP.toFixed(2)} ms</td>
                </tr>
                 <tr>
                    <td>Total Blocking Time</td>
                    <td>${metrics.TBT.toFixed(2)} ms</td>
                </tr>
                   <tr>
                    <td>Speed Index</td>
                    <td>${metrics.SI.toFixed(2)} ms</td>
                </tr>
                <tr>
                    <td>First Contentful Paint (FCP)</td>
                    <td>${metrics.FCP.toFixed(2)} ms</td>
                </tr>
                <tr>
                    <td>Cumulative Layout Shift (CLS)</td>
                    <td>${metrics.CLS.toFixed(4)}</td>
                </tr>
           
            </tbody>
        </table>
    </div>
</body>
</html>`;
const upperCasePath = metrics.relativePath.toUpperCase();
  fs.writeFileSync(`${upperCasePath}.html`, htmlContent); 

}