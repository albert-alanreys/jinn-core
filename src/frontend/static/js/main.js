import ChartManager from './ChartManager.js';
import ReportManager from './ReportManager.js';
import LeftToolbarManager from './LeftToolbarManager.js';
import RightToolbarManager from './RightToolbarManager.js';
import { getLiteData, getMainData } from './fetchClient.js';

async function renderUI(id) {
  var mainData = await getMainData(id);
  var freshLiteData = await getLiteData();

  chartManager.removeChart();
  reportManager.removeReport();
  chartManager.createChart(mainData.chartData, id);
  reportManager.createReport(mainData.reportData);

  leftToolbarManager.removeEventListeners();
  leftToolbarManager.manage(
    chartManager.chart,
    freshLiteData[id],
    chartManager.candlestickSeries
  );
}

var liteData = await getLiteData();

var chartManager = new ChartManager();
var reportManager = new ReportManager();
var leftToolbarManager = new LeftToolbarManager();
new RightToolbarManager(liteData, renderUI);

renderUI(Object.keys(liteData)[0]);
