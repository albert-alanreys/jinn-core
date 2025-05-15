import { getDataUpdates, getMainData } from './fetchClient.js';

export default class ChartManager {
  daysOfWeek = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'];
  months = [
    'Янв',
    'Фев',
    'Мар',
    'Апр',
    'Май',
    'Июн',
    'Июл',
    'Авг',
    'Сен',
    'Окт',
    'Ноя',
    'Дек',
  ];
  chartOptions = {
    autoSize: true,
    layout: {
      background: { type: 'solid', color: '#ffffff' },
      textColor: 'black',
      fontSize: 12,
    },
    rightPriceScale: {
      scaleMargins: { top: 0.05, bottom: 0.05 },
      borderVisible: false,
    },
    crosshair: {
      mode: 0,
      vertLine: {
        color: '#a5a5a5',
        style: 3,
      },
      horzLine: {
        color: '#a5a5a5',
        style: 3,
      },
    },
    grid: {
      vertLines: { color: '#edf0ee' },
      horzLines: { color: '#edf0ee' },
    },
    localization: {
      timeFormatter: (time) => {
        var date = new Date(time * 1000);
        var dayOfWeek = this.daysOfWeek[date.getUTCDay()];
        var day = date.getUTCDate();
        var month = this.months[date.getUTCMonth()];
        var year = date.getUTCFullYear();
        var hours = String(date.getUTCHours()).padStart(2, '0');
        var minutes = String(date.getUTCMinutes()).padStart(2, '0');
        return `${dayOfWeek} ${day} ${month} ${year}   ${hours}:${minutes}`;
      },
    },
    timeScale: {
      rightOffset: 5,
      barSpacing: 8,
      minBarSpacing: 2,
      borderVisible: false,
      rightBarStaysOnScroll: true,
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
          hours = String(hours).padStart(2, '0');
          minutes = String(minutes).padStart(2, '0');
          return `${hours}:${minutes}`;
        }
      },
    },
    visibleRange: 1000,
  };
  candlestickOptions = {
    upColor: '#008984',
    downColor: '#f23645',
    borderVisible: false,
    wickUpColor: '#008984',
    wickDownColor: '#f23645',
  };
  lineOptions = {
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
    crosshairMarkerVisible: false,
  };

  constructor() {
    this.updateTimerId = NaN;
  }

  createChart(data, id) {
    this.createCanvas(data);
    this.createLegends(data);
    this.createScrollButton();

    if (MODE == 'AUTOMATION') {
      this.manageChartUpdates(id);
    }
  }

  createCanvas(data) {
    this.chart = LightweightCharts.createChart(
      document.getElementById('chart-panel'),
      this.chartOptions
    );

    this.visibleRange = this.chartOptions.visibleRange;
    this.timeScale = this.chart.timeScale();

    this.candlestickSeries = this.chart.addSeries(
      LightweightCharts.CandlestickSeries,
      this.candlestickOptions
    );
    this.candlestickSeries.applyOptions({
      priceFormat: {
        type: 'price',
        precision: String(data.mintick).match(/.\d+$/g)[0].length - 1,
        minMove: data.mintick,
      },
    });

    this.lineSeriesGroup = {};

    for (var name in data.lines) {
      var lineSeries = this.chart.addSeries(
        LightweightCharts.LineSeries,
        data.lines[name].options
      );
      lineSeries.applyOptions(this.lineOptions);

      this.lineSeriesGroup[name] = lineSeries;
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

    this.candlestickSeries.setData(data.klines.slice(-this.visibleRange));

    var startTime = this.candlestickSeries.data()[0].time;
    var markers = data.markers.filter((marker) => {
      if (marker.time >= startTime) {
        return marker;
      }
    });

    if (!this.seriesMarkers) {
      this.seriesMarkers = LightweightCharts.createSeriesMarkers(
        this.candlestickSeries,
        markers
      );
    } else {
      this.seriesMarkers.setMarkers(markers);
    }

    for (var name in this.lineSeriesGroup) {
      this.lineSeriesGroup[name].setData(
        data.lines[name].values.slice(-this.visibleRange)
      );
    }
  }

  createLegends(data) {
    var mainLegend = document.createElement('div');
    var o = data.klines.at(-1).open;
    var h = data.klines.at(-1).high;
    var l = data.klines.at(-1).low;
    var c = data.klines.at(-1).close;

    mainLegend.setAttribute('id', 'main-legend');
    mainLegend.style.position = 'absolute';
    mainLegend.style.left = '12px';
    mainLegend.style.top = '12px';
    mainLegend.style.zIndex = 2;
    mainLegend.innerHTML = getMainLegendText(o, h, l, c);

    document.getElementById('chart-panel').appendChild(mainLegend);

    var linesLegend = document.createElement('div');
    linesLegend.setAttribute('id', 'strategy-legend');
    linesLegend.style.position = 'absolute';
    linesLegend.style.left = '12px';
    linesLegend.style.top = '40px';
    linesLegend.style.zIndex = 2;
    linesLegend.style.fontSize = '14px';
    linesLegend.innerHTML = Object.entries(this.lineSeriesGroup)
      .map(([name, series]) => {
        var point = series.data().at(-1);
        return getLineLegendText(name, point, data.lines[name].options);
      })
      .join(' ');

    document.getElementById('chart-panel').appendChild(linesLegend);

    var crosshairMoveHandler = (crosshairPosition) => {
      if (crosshairPosition.time) {
        if (crosshairPosition.logical >= data.klines.length) {
          this.chart.unsubscribeCrosshairMove(crosshairMoveHandler);
          this.chart.subscribeCrosshairMove(crosshairMoveHandler);
        } else {
          var mainData = crosshairPosition.seriesData.get(
            this.candlestickSeries
          );
          var o = mainData.open;
          var h = mainData.high;
          var l = mainData.low;
          var c = mainData.close;

          mainLegend.innerHTML = getMainLegendText(o, h, l, c);

          linesLegend.innerHTML = Object.entries(this.lineSeriesGroup)
            .map(([name, series]) => {
              const point = crosshairPosition.seriesData.get(series);
              return getLineLegendText(name, point, data.lines[name].options);
            })
            .join(' ');
        }
      }
    };
    this.chart.subscribeCrosshairMove(crosshairMoveHandler);

    function getMainLegendText(o, h, l, c) {
      var color = c > o ? '#008984' : '#f23645';
      return `${data.symbol} • ${data.market} •
          ${data.interval} • ${data.exchange.toUpperCase()}
          &nbsp;
          O <span style="color:${color};">${o}</span>
          H <span style="color:${color};">${h}</span>
          L <span style="color:${color};">${l}</span>
          C <span style="color:${color};">${c}</span>`;
    }

    function getLineLegendText(name, point, options) {
      if (!point) {
        var value = '∅';
        var color = '#000000';
      } else {
        var value = point.value;
        var color = point.color ? '#000000' : options.color;
      }

      return `<span>${name}</span>
          <span style="color:${color};">${value}</span>
          &nbsp;`;
    }
  }

  createScrollButton() {
    var button = document.createElement('button');
    var div = document.createElement('div');

    div.setAttribute('unselectable', 'on');
    button.setAttribute('id', 'scroll-button');
    button.setAttribute('title', 'Прокрутить до текущего бара');

    document.getElementById('chart-panel').appendChild(button);
    button.appendChild(div);
    button.addEventListener('click', () => {
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
        document.getElementById('chart-panel').children
      )) {
        item.remove();
      }
    } catch {}
  }
}
