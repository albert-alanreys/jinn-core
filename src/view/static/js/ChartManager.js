import { getDataUpdates, getMainData } from "./fetchClient.js";

export default class ChartManager {
  daysOfWeek = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];
  months = [
    "Янв",
    "Фев",
    "Мар",
    "Апр",
    "Май",
    "Июн",
    "Июл",
    "Авг",
    "Сен",
    "Окт",
    "Ноя",
    "Дек",
  ];
  chartOptions = {
    autoSize: true,
    layout: {
      background: { type: "solid", color: "#ffffff" },
      textColor: "black",
      fontSize: 12,
    },
    rightPriceScale: {
      scaleMargins: { top: 0.05, bottom: 0.05 },
      borderVisible: false,
    },
    crosshair: {
      mode: 0,
      vertLine: {
        color: "#a5a5a5",
        style: 3,
      },
      horzLine: {
        color: "#a5a5a5",
        style: 3,
      },
    },
    grid: {
      vertLines: { color: "#edf0ee" },
      horzLines: { color: "#edf0ee" },
    },
    localization: {
      timeFormatter: (time) => {
        var date = new Date(time * 1000);
        var dayOfWeek = this.daysOfWeek[date.getUTCDay()];
        var day = date.getUTCDate();
        var month = this.months[date.getUTCMonth()];
        var year = date.getUTCFullYear();
        var hours = String(date.getUTCHours()).padStart(2, "0");
        var minutes = String(date.getUTCMinutes()).padStart(2, "0");
        return `${dayOfWeek} ${day} ${month} ${year}   ${hours}:${minutes}`;
      },
    },
    timeScale: {
      rightOffset: 5,
      barSpacing: 8,
      minBarSpacing: 2,
      borderVisible: false,
      tickMarkFormatter: (time) => {
        var date = new Date(time * 1000);
        var day = date.getUTCDate();
        var month = date.getUTCMonth();
        var year = date.getUTCFullYear();
        var hours = date.getUTCHours();
        var minutes = date.getUTCMinutes();

        if (month == 0 && day == 1 && hours == 0 && minutes == 0) {
          return String(year);
        }
        if (day == 1 && hours == 0 && minutes == 0) {
          return this.months[date.getUTCMonth()];
        } else if (hours == 0 && minutes == 0) {
          return String(day);
        } else {
          hours = String(hours).padStart(2, "0");
          minutes = String(minutes).padStart(2, "0");
          return `${hours}:${minutes}`;
        }
      },
    },
    visibleRange: 1000,
  };
  klineOptions = {
    upColor: "#008984",
    downColor: "#f23645",
    borderVisible: false,
    wickUpColor: "#008984",
    wickDownColor: "#f23645",
  };
  lineOptions = {
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
    crosshairMarkerVisible: false,
  };

  constructor(mode) {
    this.mode = mode;
    this.updateTimerId = NaN;
  }

  createChart(data, id) {
    this.createCanvas(data);
    this.createLegends(data);
    this.createScrollButton();

    if (this.mode == "automation") {
      this.manageChartUpdates(id);
    }
  }

  createCanvas(data) {
    this.chart = LightweightCharts.createChart(
      document.getElementById("chart-panel"),
      this.chartOptions
    );
    this.timeScale = this.chart.timeScale();
    this.klineSeries = this.chart.addCandlestickSeries(this.klineOptions);
    this.klineSeries.applyOptions({
      priceFormat: {
        type: "price",
        precision: String(data.mintick).match(/.\d+$/g)[0].length - 1,
        minMove: data.mintick,
      },
    });
    this.lineSeriesGroups = {};
    this.visibleRange = this.chartOptions.visibleRange;

    for (var key in data.indicators) {
      var lineSeries = this.chart.addLineSeries(data.indicators[key].options);
      lineSeries.applyOptions(this.lineOptions);

      this.lineSeriesGroups[key] = lineSeries;
    }

    this.visibleLogicalRangeChangeHandler = (newVisibleTimeRange) => {
      if (newVisibleTimeRange.from < 50) {
        this.visibleRange += this.chartOptions.visibleRange;
        this.setChartData(data);
      }
    };

    this.timeScale.subscribeVisibleLogicalRangeChange(
      this.visibleLogicalRangeChangeHandler
    );
    this.setChartData(data);
  }

  setChartData(data) {
    if (this.visibleRange > data.klines.length) {
      this.timeScale.unsubscribeVisibleLogicalRangeChange(
        this.visibleLogicalRangeChangeHandler
      );
    }

    this.klineSeries.setData(data.klines.slice(-this.visibleRange));

    var startTime = this.klineSeries.data()[0].time;
    var markers = data.markers.filter((item) => {
      if (item.time >= startTime) {
        return item;
      }
    });
    this.klineSeries.setMarkers(markers);

    for (var key in this.lineSeriesGroups) {
      this.lineSeriesGroups[key].setData(
        data.indicators[key].values.slice(-this.visibleRange)
      );
    }
  }

  createLegends(data) {
    var mainLegend = document.createElement("div");
    var o = data.klines.at(-1).open;
    var h = data.klines.at(-1).high;
    var l = data.klines.at(-1).low;
    var c = data.klines.at(-1).close;
    var color = c > o ? "#008984" : "#f23645";
    mainLegend.setAttribute("id", "main-legend");
    mainLegend.style.position = "absolute";
    mainLegend.style.left = "12px";
    mainLegend.style.top = "12px";
    mainLegend.style.zIndex = 2;
    mainLegend.innerHTML = `${data.symbol} •
        ${data.interval} • ${data.exchange.toUpperCase()}
        &nbsp;
        O <span style="color:${color};">${o}</span>
        H <span style="color:${color};">${h}</span>
        L <span style="color:${color};">${l}</span>
        C <span style="color:${color};">${c}</span>`;
    document.getElementById("chart-panel").appendChild(mainLegend);

    var strategyLegend = document.createElement("div");
    strategyLegend.setAttribute("id", "strategy-legend");
    strategyLegend.style.position = "absolute";
    strategyLegend.style.left = "12px";
    strategyLegend.style.top = "40px";
    strategyLegend.style.zIndex = 2;
    strategyLegend.style.fontSize = "14px";
    strategyLegend.innerHTML =
      `${data.name} &nbsp;` +
      Object.values(this.lineSeriesGroups)
        .map((item) => {
          var lastPoint = item.data().at(-1);

          if (lastPoint.color == "transparent") {
            var lastValue = "∅";
            var color = "#000000";
          } else {
            var lastValue = lastPoint.value;
            var color = lastPoint.color;
          }
          return `<span style="color:${color};">${lastValue}</span>`;
        })
        .join(" ");
    document.getElementById("chart-panel").appendChild(strategyLegend);

    this.crosshairMoveHandler = (param) => {
      if (param.time) {
        if (param.logical >= data.klines.length) {
          this.chart.unsubscribeCrosshairMove(this.crosshairMoveHandler);
          this.chart.subscribeCrosshairMove(this.crosshairMoveHandler);
        } else {
          var mainData = param.seriesData.get(this.klineSeries);
          var o = mainData.open;
          var h = mainData.high;
          var l = mainData.low;
          var c = mainData.close;
          var color = c > o ? "#008984" : "#f23645";

          mainLegend.innerHTML = `${data.symbol} •
              ${data.interval} • ${data.exchange.toUpperCase()}
              &nbsp;
              O <span style="color:${color};">${o}</span>
              H <span style="color:${color};">${h}</span>
              L <span style="color:${color};">${l}</span>
              C <span style="color:${color};">${c}</span>`;

          strategyLegend.innerHTML =
            `${data.name} &nbsp;` +
            Object.values(this.lineSeriesGroups)
              .map((item) => {
                var currentPoint = param.seriesData.get(item);
                var currentValue = currentPoint.value;
                var color = currentPoint.color;

                if (color == "transparent" && currentValue == o) {
                  currentValue = "∅";
                  color = "#000000";
                } else if (color == "transparent") {
                  color = item.options().color;
                }

                return `<span style="color:${color};">${currentValue}</span>`;
              })
              .join(" ");
        }
      }
    };

    this.chart.subscribeCrosshairMove(this.crosshairMoveHandler);
  }

  createScrollButton() {
    var button = document.createElement("button");
    var div = document.createElement("div");

    div.setAttribute("unselectable", "on");
    button.setAttribute("id", "scroll-button");
    button.setAttribute("title", "Прокрутить до текущего бара");

    document.getElementById("chart-panel").appendChild(button);
    button.appendChild(div);
    button.addEventListener("click", () => {
      this.timeScale.scrollToRealTime();
    });
  }

  manageChartUpdates(id) {
    clearInterval(this.timerId);

    this.timerId = setInterval(() => {
      getDataUpdates().then((updates) => {
        if (updates.includes(id)) {
          getMainData(id).then((data) => {
            this.setChartData(data.chartData);
          });
        }
      });
    }, 5000);
  }

  removeChart() {
    try {
      this.chart.remove();

      for (var item of Array.from(
        document.getElementById("chart-panel").children
      )) {
        item.remove();
      }
    } catch {}
  }
}
