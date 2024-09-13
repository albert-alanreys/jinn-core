import ChartManager from "./ChartManager.js";
import ReportManager from "./ReportManager.js";
import LeftToolbarManager from "./LeftToolbarManager.js";
import RightToolbarManager from "./RightToolbarManager.js";
import { getMode, getLiteData, getMainData } from "./fetchClient.js";

var mode = await getMode();
var liteData = await getLiteData();
document.documentElement.dataset.status = mode;

var chartManager = new ChartManager(mode);
var reportManager = new ReportManager(mode);
var leftToolbarManager = new LeftToolbarManager();
new RightToolbarManager(liteData, mode, renderUI);

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
        chartManager.klineSeries
      );
    });
  });
}

renderUI(Object.keys(liteData)[0]);
