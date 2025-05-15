import ChartManager from './ChartManager.js';
import ReportManager from './ReportManager.js';
import LeftToolbarManager from './LeftToolbarManager.js';
import RightToolbarManager from './RightToolbarManager.js';
import { getLiteData, getMainData } from './fetchClient.js';

const liteData = await getLiteData();
const chartManager = new ChartManager();
const reportManager = new ReportManager();
const leftToolbarManager = new LeftToolbarManager();
new RightToolbarManager(liteData, renderUI);

function renderUI(id) {
  getMainData(id).then((mainData) => {
    chartManager.removeChart();
    reportManager.removeReport();
    chartManager.createChart(mainData.chartData, id);
    reportManager.createReport(mainData.reportData);

    getLiteData().then((liteData) => {
      leftToolbarManager.removeEventListeners();
      leftToolbarManager.manage(
        chartManager.chart,
        liteData[id],
        chartManager.candlestickSeries
      );
    });
  });
}

renderUI(Object.keys(liteData)[0]);
