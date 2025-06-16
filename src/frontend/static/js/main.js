import ChartManager from './ChartManager.js';
import ReportManager from './ReportManager.js';
import LeftToolbarManager from './LeftToolbarManager.js';
import RightToolbarManager from './RightToolbarManager.js';
import {
  fetchAlerts,
  fetchSummary,
  fetchUpdates,
  fetchChartDetails,
  fetchReportDetails,
} from './fetchClient.js';

async function renderUI(contextId) {
  var freshSummary = await fetchSummary();
  var chartDetails = await fetchChartDetails(contextId);
  var reportDetails = await fetchReportDetails(contextId);

  chartManager.removeChart();
  reportManager.removeReport();
  leftToolbarManager.removeEventListeners();

  chartManager.createChart(chartDetails);
  reportManager.createReport(reportDetails);
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
          fetchChartDetails(contextId).then((chartDetails) => {
            chartManager.setChartData(chartDetails);
          });

          fetchReportDetails(contextId).then((reportDetails) => {
            reportManager.removeReport();
            reportManager.createReport(reportDetails);
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
