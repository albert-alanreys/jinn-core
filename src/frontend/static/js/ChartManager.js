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
        const date = new Date(time * 1000);
        const dayOfWeek = this.daysOfWeek[date.getUTCDay()];
        const day = date.getUTCDate();
        const month = this.months[date.getUTCMonth()];
        const year = date.getUTCFullYear();
        const hours = String(date.getUTCHours()).padStart(2, '0');
        const minutes = String(date.getUTCMinutes()).padStart(2, '0');
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
        let date = new Date(time * 1000);
        let day = date.getUTCDate();
        let month = date.getUTCMonth();
        let year = date.getUTCFullYear();
        let hours = date.getUTCHours();
        let minutes = date.getUTCMinutes();

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
  klineOptions = {
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
    this.timeScale = this.chart.timeScale();
    this.candlestickSeries = this.chart.addSeries(
      LightweightCharts.CandlestickSeries,
      this.klineOptions
    );
    this.candlestickSeries.applyOptions({
      priceFormat: {
        type: 'price',
        precision: String(data.mintick).match(/.\d+$/g)[0].length - 1,
        minMove: data.mintick,
      },
    });
    this.lineSeriesGroup = {};
    this.visibleRange = this.chartOptions.visibleRange;

    for (let key in data.indicators) {
      const lineSeries = this.chart.addSeries(
        LightweightCharts.LineSeries,
        data.indicators[key].options
      );
      lineSeries.applyOptions(this.lineOptions);

      this.lineSeriesGroup[key] = lineSeries;
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

    const startTime = this.candlestickSeries.data()[0].time;
    const markers = data.markers.filter((item) => {
      if (item.time >= startTime) {
        return item;
      }
    });
    this.seriesMarkers = LightweightCharts.createSeriesMarkers(
      this.candlestickSeries,
      markers
    );

    for (let key in this.lineSeriesGroup) {
      this.lineSeriesGroup[key].setData(
        data.indicators[key].values.slice(-this.visibleRange)
      );
    }
  }

  createLegends(data) {
    const mainLegend = document.createElement('div');
    mainLegend.setAttribute('id', 'main-legend');
    mainLegend.style.position = 'absolute';
    mainLegend.style.left = '12px';
    mainLegend.style.top = '12px';
    mainLegend.style.zIndex = 2;
    document.getElementById('chart-panel').appendChild(mainLegend);

    const strategyLegend = document.createElement('div');
    strategyLegend.setAttribute('id', 'strategy-legend');
    strategyLegend.style.position = 'absolute';
    strategyLegend.style.left = '12px';
    strategyLegend.style.top = '40px';
    strategyLegend.style.zIndex = 2;
    strategyLegend.style.fontSize = '14px';
    document.getElementById('chart-panel').appendChild(strategyLegend);

    let o = data.klines.at(-1).open;
    let h = data.klines.at(-1).high;
    let l = data.klines.at(-1).low;
    let c = data.klines.at(-1).close;

    mainLegend.innerHTML = getMainLegendText(o, h, l, c);
    strategyLegend.innerHTML =
      `${data.name} &nbsp;` +
      Object.values(this.lineSeriesGroup)
        .map((item) => {
          return getStrategyLegendText(
            item.data().at(-1),
            item.options().color,
            o
          );
        })
        .join(' ');

    const crosshairMoveHandler = (crosshairPosition) => {
      if (crosshairPosition.time) {
        if (crosshairPosition.logical >= data.klines.length) {
          this.chart.unsubscribeCrosshairMove(crosshairMoveHandler);
          this.chart.subscribeCrosshairMove(crosshairMoveHandler);
        } else {
          const mainData = crosshairPosition.seriesData.get(
            this.candlestickSeries
          );
          o = mainData.open;
          h = mainData.high;
          l = mainData.low;
          c = mainData.close;
          mainLegend.innerHTML = getMainLegendText(o, h, l, c);
          strategyLegend.innerHTML =
            `${data.name} &nbsp;` +
            Object.values(this.lineSeriesGroup)
              .map((item) => {
                return getStrategyLegendText(
                  crosshairPosition.seriesData.get(item),
                  item.options().color,
                  o
                );
              })
              .join(' ');
        }
      }
    };
    this.chart.subscribeCrosshairMove(crosshairMoveHandler);

    function getMainLegendText(o, h, l, c) {
      let color = c > o ? '#008984' : '#f23645';
      return `${data.symbol} • ${data.market} •
          ${data.interval} • ${data.exchange.toUpperCase()}
          &nbsp;
          O <span style="color:${color};">${o}</span>
          H <span style="color:${color};">${h}</span>
          L <span style="color:${color};">${l}</span>
          C <span style="color:${color};">${c}</span>`;
    }

    function getStrategyLegendText(point, baseColor, o) {
      let color = point.color;
      let value = point.value;

      if (point.color == 'transparent' && value == o) {
        value = '∅';
        color = '#000000';
      } else if (color == 'transparent') {
        color = baseColor;
      }

      return `<span style="color:${color};">${value}</span>`;
    }
  }

  createScrollButton() {
    const button = document.createElement('button');
    const div = document.createElement('div');

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

      for (let item of Array.from(
        document.getElementById('chart-panel').children
      )) {
        item.remove();
      }
    } catch {}
  }
}
