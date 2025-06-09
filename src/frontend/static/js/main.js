import ChartManager from './ChartManager.js';
import ReportManager from './ReportManager.js';
import LeftToolbarManager from './LeftToolbarManager.js';
import RightToolbarManager from './RightToolbarManager.js';
import { getSummary, getDetails } from './fetchClient.js';

async function renderUI(id) {
  var details = await getDetails(id);
  var freshSummary = await getSummary();

  chartManager.removeChart();
  reportManager.removeReport();
  chartManager.createChart(details.chart, id);
  reportManager.createReport(details.report);

  leftToolbarManager.removeEventListeners();
  leftToolbarManager.manage(
    chartManager.chart,
    freshSummary[id],
    chartManager.candlestickSeries
  );
}

var summary = await getSummary();

var chartManager = new ChartManager();
var reportManager = new ReportManager();
var leftToolbarManager = new LeftToolbarManager();
new RightToolbarManager(summary, renderUI);

renderUI(Object.keys(summary)[0]);
