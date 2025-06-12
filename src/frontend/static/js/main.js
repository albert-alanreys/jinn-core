import ChartManager from './ChartManager.js';
import ReportManager from './ReportManager.js';
import LeftToolbarManager from './LeftToolbarManager.js';
import RightToolbarManager from './RightToolbarManager.js';
import {
  fetchAlerts,
  fetchSummary,
  fetchUpdates,
  fetchDetails,
} from './fetchClient.js';

async function renderUI(contextId) {
  var freshSummary = await fetchSummary();
  var details = await fetchDetails(contextId);

  chartManager.removeChart();
  reportManager.removeReport();
  leftToolbarManager.removeEventListeners();

  chartManager.createChart(details.chart);
  reportManager.createReport(details.report);
  leftToolbarManager.manage(
    chartManager.chart,
    freshSummary[contextId],
    chartManager.candlestickSeries
  );
}

var summary = await fetchSummary();

var chartManager = new ChartManager();
var reportManager = new ReportManager();
var leftToolbarManager = new LeftToolbarManager();
var rightToolbarManager = new RightToolbarManager(summary, renderUI);

var contextId = Object.keys(summary)[0];

renderUI(contextId);

if (SERVER_MODE == 'AUTOMATION') {
  fetchAlerts().then((alerts) => {
    if (alerts?.length) {
      rightToolbarManager.addAlerts(alerts);
    }
  });

  setInterval(() => {
    fetchUpdates().then((updates) => {
      if (updates?.length) {
        if (updates.includes(contextId)) {
          fetchDetails(contextId).then((data) => {
            chartManager.setChartData(data.chart);
          });
        }

        fetchAlerts().then((alerts) => {
          if (alerts?.length) {
            rightToolbarManager.addAlerts(alerts);
          }
        });
      }
    });
  }, 5000);
}
