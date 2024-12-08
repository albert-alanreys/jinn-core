import ChartManager from "./ChartManager.js";
import ReportManager from "./ReportManager.js";
import LeftToolbarManager from "./LeftToolbarManager.js";
import RightToolbarManager from "./RightToolbarManager.js";
import { getMode, getLiteData, getMainData } from "./fetchClient.js";

const mode = await getMode();
const liteData = await getLiteData();
document.documentElement.dataset.status = mode;

const chartManager = new ChartManager(mode);
const reportManager = new ReportManager(mode);
const leftToolbarManager = new LeftToolbarManager();
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
        chartManager.candlestickSeries
      );
    });
  });
}

renderUI(Object.keys(liteData)[0]);
