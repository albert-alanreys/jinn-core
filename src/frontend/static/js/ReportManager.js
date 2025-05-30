class HorzScaleBehaviorPrice {
  setOptions() {}

  updateFormatter() {}

  createConverterToInternalObj() {
    return (price) => price;
  }

  key(internalItem) {
    return internalItem;
  }

  cacheKey(internalItem) {
    return internalItem;
  }

  convertHorzItemToInternal(item) {
    return item;
  }

  formatHorzItem(item) {
    return item;
  }

  formatTickmark(item) {
    return item.time;
  }

  maxTickMarkWeight(marks) {
    return marks[0].weight;
  }

  fillWeightsForPoints() {}
}

export default class ReportManager {
  chartOptions = {
    autoSize: true,
    layout: {
      background: { type: 'solid', color: '#FFFFFF' },
      textColor: 'black',
      fontSize: 12,
    },
    rightPriceScale: {
      visible: false,
    },
    leftPriceScale: {
      scaleMargins: { top: 0.05, bottom: 0.05 },
      borderVisible: false,
      visible: true,
    },
    crosshair: {
      mode: 0,
      vertLine: {
        color: '#A5A5A5',
        style: 3,
      },
      horzLine: {
        color: '#A5A5A5',
        style: 3,
      },
    },
    grid: {
      vertLines: { visible: false },
      horzLines: { visible: false },
    },
    handleScroll: {
      mouseWheel: false,
      pressedMouseMove: false,
      horzTouchDrag: false,
      vertTouchDrag: false,
    },
    handleScale: {
      mouseWheel: false,
      pinch: false,
      axisPressedMouseMove: false,
      axisDoubleClickReset: false,
    },
    timeScale: {
      rightOffset: 1,
      borderVisible: false,
      allowBoldLabels: false,
    },
  };
  areaOptions = {
    lineColor: '#00A9FF',
    lineWidth: 1,
    topColor: '#78CEFF',
    bottomColor: '#EBF5FB',
    lineVisible: true,
    crosshairMarkerVisible: false,
    lastValueVisible: false,
    priceLineVisible: false,
  };

  constructor() {
    this.placeholder2 = document.getElementById('placeholder-2');
    this.placeholder3 = document.getElementById('placeholder-3');

    this.manageTabs();
    this.manageSize();
  }

  createReport(data) {
    if (MODE == 'TESTING') {
      if (data.dealsLog.length) {
        this.createOverviewReport(data);
      } else {
        this.placeholder2.style.display = 'flex';
      }

      this.createPerformanceReport(data);

      if (data.dealsLog.length) {
        this.createTradesReport(data);
      } else {
        this.placeholder3.style.display = 'flex';
      }
    }
  }

  createOverviewReport(data) {
    var metricsContainer = document.createElement('div');
    metricsContainer.setAttribute('id', 'metrics-container');
    document.getElementById('overview-report').appendChild(metricsContainer);

    var outerDiv = document.createElement('div');
    outerDiv.classList.add('align-start');
    metricsContainer.appendChild(outerDiv);

    var innerDiv1 = document.createElement('div');
    innerDiv1.innerText = 'Чистая прибыль';
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement('div');

    if (data.metrics[0][0] > 0) {
      var color = '#089981';
    } else if (data.metrics[0][0] < 0) {
      var color = '#f23645';
    } else {
      var color = '#212529';
    }

    innerDiv2.innerHTML = `<span style="color: ${color};">${
      data.metrics[0][0] + ' USDT ' + data.metrics[0][1] + '%'
    }</span>`;
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement('div');
    outerDiv.classList.add('align-start');
    metricsContainer.appendChild(outerDiv);

    var innerDiv1 = document.createElement('div');
    innerDiv1.innerText = 'Всего закрытых сделок';
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement('div');
    innerDiv2.innerText = data.metrics[0][8];
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement('div');
    outerDiv.classList.add('align-start');
    metricsContainer.appendChild(outerDiv);

    var innerDiv1 = document.createElement('div');
    innerDiv1.innerText = 'Процент прибыльных';
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement('div');
    innerDiv2.innerHTML = `<span style="color: #089981;">${
      data.metrics[0][11] + '%'
    }</span>`;
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement('div');
    outerDiv.classList.add('align-start');
    metricsContainer.appendChild(outerDiv);

    var innerDiv1 = document.createElement('div');
    innerDiv1.innerText = 'Фактор прибыли';
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement('div');

    if (data.metrics[0][6] > 1) {
      var color = '#089981';
    } else if (data.metrics[0][6] < 1) {
      var color = '#f23645';
    } else {
      var color = '#212529';
    }

    innerDiv2.innerHTML = `<span style="color:
      ${color};">${data.metrics[0][6]}</span>`;
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement('div');
    outerDiv.classList.add('align-start');
    metricsContainer.appendChild(outerDiv);

    var innerDiv1 = document.createElement('div');
    innerDiv1.innerText = 'Максимальная просадка';
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement('div');
    innerDiv2.innerHTML = `<span style="color: #f23645;">${
      data.metrics[0][23] + ' USDT ' + data.metrics[0][24] + '%'
    }</span>`;
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement('div');
    outerDiv.classList.add('align-start');
    metricsContainer.appendChild(outerDiv);

    var innerDiv1 = document.createElement('div');
    innerDiv1.innerText = 'Средняя по сделке';
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement('div');

    if (data.metrics[0][12] > 0) {
      var color = '#089981';
    } else if (data.metrics[0][12] < 0) {
      var color = '#f23645';
    } else {
      var color = '#212529';
    }

    innerDiv2.innerHTML = `<span style="color: ${color};">${
      data.metrics[0][12] + ' USDT ' + data.metrics[0][13] + '%'
    }</span>`;
    outerDiv.appendChild(innerDiv2);

    var chartContainer = document.createElement('div');
    chartContainer.setAttribute('id', 'chart-container');
    document.getElementById('overview-report').appendChild(chartContainer);

    this.chart = LightweightCharts.createChartEx(
      chartContainer,
      new HorzScaleBehaviorPrice(),
      this.chartOptions
    );
    var areaSeries = this.chart.addSeries(
      LightweightCharts.AreaSeries,
      this.areaOptions
    );
    areaSeries.setData(data.equity);

    this.chart.timeScale().subscribeVisibleLogicalRangeChange(() => {
      this.chart
        .timeScale()
        .setVisibleLogicalRange({ from: 0, to: data.equity.length - 1 });
    });
  }

  createPerformanceReport(data) {
    var table = document.createElement('div');
    table.setAttribute('id', 'performance-container');
    table.classList.add('table');
    document.getElementById('performance-report').appendChild(table);

    var thead = document.createElement('div');
    thead.classList.add('thead');
    table.appendChild(thead);

    var tr = document.createElement('div');
    tr.classList.add('tr');
    thead.appendChild(tr);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-start');
    th.innerText = 'Название показателя';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-end');
    th.innerText = 'Все сделки';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-end');
    th.innerText = 'Длинные сделки';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-end');
    th.innerText = 'Короткие сделки';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    tr.appendChild(th);

    var tbody = document.createElement('div');
    tbody.classList.add('tbody');
    table.appendChild(tbody);

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Чистая прибыль';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      td.appendChild(div);

      var div1 = document.createElement('div');
      var div2 = document.createElement('div');
      div1.innerText = data.metrics[i][0] + ' USDT';
      div2.innerText = data.metrics[i][1] + '%';
      div.appendChild(div1);
      div.appendChild(div2);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Валовая прибыль';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      td.appendChild(div);

      var div1 = document.createElement('div');
      var div2 = document.createElement('div');
      div1.innerText = data.metrics[i][2] + ' USDT';
      div2.innerText = data.metrics[i][3] + '%';
      div.appendChild(div1);
      div.appendChild(div2);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Валовой убыток';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      td.appendChild(div);

      var div1 = document.createElement('div');
      var div2 = document.createElement('div');
      div1.innerText = data.metrics[i][4] + ' USDT';
      div2.innerText = data.metrics[i][5] + '%';
      div.appendChild(div1);
      div.appendChild(div2);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Фактор прибыли';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      div.innerText = data.metrics[i][6] != '' ? data.metrics[i][6] : 'Н/Д';
      td.appendChild(div);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Выплаченная комиссия';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      div.innerText = data.metrics[i][7] + ' USDT';
      td.appendChild(div);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Всего закрытых сделок';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      div.innerText = data.metrics[i][8];
      td.appendChild(div);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Количество прибыльных сделок';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      div.innerText = data.metrics[i][9];
      td.appendChild(div);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Количество убыточных сделок';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      div.innerText = data.metrics[i][10];
      td.appendChild(div);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Процент прибыльных сделок';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      div.innerText =
        data.metrics[i][11] != '' ? data.metrics[i][11] + '%' : 'Н/Д';
      td.appendChild(div);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Средняя по сделке';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      td.appendChild(div);

      if (data.metrics[i][12] != '') {
        var div1 = document.createElement('div');
        var div2 = document.createElement('div');
        div1.innerText = data.metrics[i][12] + ' USDT';
        div2.innerText = data.metrics[i][13] + '%';
        div.appendChild(div1);
        div.appendChild(div2);
      } else {
        div.innerText = 'Н/Д';
      }
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Средняя прибыль по сделке';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      td.appendChild(div);

      if (data.metrics[i][14] != '') {
        var div1 = document.createElement('div');
        var div2 = document.createElement('div');
        div1.innerText = data.metrics[i][14] + ' USDT';
        div2.innerText = data.metrics[i][15] + '%';
        div.appendChild(div1);
        div.appendChild(div2);
      } else {
        div.innerText = 'Н/Д';
      }
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Средний убыток по сделке';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      td.appendChild(div);

      if (data.metrics[i][16] != '') {
        var div1 = document.createElement('div');
        var div2 = document.createElement('div');
        div1.innerText = data.metrics[i][16] + ' USDT';
        div2.innerText = data.metrics[i][17] + '%';
        div.appendChild(div1);
        div.appendChild(div2);
      } else {
        div.innerText = 'Н/Д';
      }
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Коэффициент средней прибыли / среднего убытка';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      div.innerText = data.metrics[i][18] != '' ? data.metrics[i][18] : 'Н/Д';
      td.appendChild(div);
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Самая прибыльная сделка';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      td.appendChild(div);

      if (data.metrics[i][19] != '') {
        var div1 = document.createElement('div');
        var div2 = document.createElement('div');
        div1.innerText = data.metrics[i][19] + ' USDT';
        div2.innerText = data.metrics[i][20] + '%';
        div.appendChild(div1);
        div.appendChild(div2);
      } else {
        div.innerText = 'Н/Д';
      }
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Самая убыточная сделка';
    td.appendChild(div);

    for (var i = 0; i < 3; i++) {
      var td = document.createElement('div');
      td.classList.add('td');
      tr.appendChild(td);

      var div = document.createElement('div');
      div.classList.add('h-50');
      div.classList.add('align-end');
      td.appendChild(div);

      if (data.metrics[i][21] != '') {
        var div1 = document.createElement('div');
        var div2 = document.createElement('div');
        div1.innerText = data.metrics[i][21] + ' USDT';
        div2.innerText = data.metrics[i][22] + '%';
        div.appendChild(div1);
        div.appendChild(div2);
      } else {
        div.innerText = 'Н/Д';
      }
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Максимальная просадка';
    td.appendChild(div);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-end');
    td.appendChild(div);

    if (data.metrics[0][23] != '') {
      var div1 = document.createElement('div');
      var div2 = document.createElement('div');
      div1.innerText = data.metrics[0][23] + ' USDT';
      div2.innerText = data.metrics[0][24] + '%';
      div.appendChild(div1);
      div.appendChild(div2);
    } else {
      div.innerText = 'Н/Д';
    }

    var tr = document.createElement('div');
    tr.classList.add('tr');
    tbody.appendChild(tr);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-start');
    div.innerText = 'Коэффициент Сортино';
    td.appendChild(div);

    var td = document.createElement('div');
    td.classList.add('td');
    tr.appendChild(td);

    var div = document.createElement('div');
    div.classList.add('h-50');
    div.classList.add('align-end');
    div.innerText = data.metrics[0][25] != '' ? data.metrics[0][25] : 'Н/Д';
    td.appendChild(div);
  }

  createTradesReport(data) {
    var reverse = false;

    var table = document.createElement('div');
    table.setAttribute('id', 'trades-container');
    table.classList.add('table');
    document.getElementById('trades-report').appendChild(table);

    var thead = document.createElement('div');
    thead.classList.add('thead');
    table.appendChild(thead);

    var tr = document.createElement('div');
    tr.classList.add('tr');
    thead.appendChild(tr);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-start');
    th.classList.add('w-10');
    tr.appendChild(th);

    var span1 = document.createElement('span');
    span1.innerText = '№ Сделки';
    th.appendChild(span1);

    var span2 = document.createElement('span');
    span2.setAttribute('id', 'report-arrow');
    span2.setAttribute('data-status', 'arrow-up');
    th.appendChild(span2);

    th.addEventListener('click', () => {
      data.dealsLog.reverse();
      reverse = !reverse;

      if (reverse) {
        document
          .getElementById('report-arrow')
          .setAttribute('data-status', 'arrow-down');
      } else {
        document
          .getElementById('report-arrow')
          .setAttribute('data-status', 'arrow-up');
      }

      for (var item of Array.from(
        document.querySelector('#trades-container .tbody').children
      )) {
        item.remove();
      }

      fillBody();
    });

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-start');
    th.classList.add('w-18');
    th.innerText = 'Тип';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-start');
    th.classList.add('w-18');
    th.innerText = 'Сигнал';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-start');
    th.classList.add('w-12');
    th.innerText = 'Дата/Время';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-end');
    th.classList.add('w-10');
    th.innerText = 'Цена';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-end');
    th.classList.add('w-10');
    th.innerText = 'Количество';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-end');
    th.classList.add('w-10');
    th.innerText = 'Прибыль';
    tr.appendChild(th);

    var th = document.createElement('div');
    th.classList.add('th');
    th.classList.add('align-end');
    th.classList.add('w-14');
    th.innerText = 'Совокупная прибыль';
    tr.appendChild(th);

    var tbody = document.createElement('div');
    tbody.classList.add('tbody');
    table.appendChild(tbody);
    fillBody();

    function fillBody() {
      var dealNumber;
      var step = !reverse ? 1 : -1;

      if (!reverse) {
        dealNumber = 1;
      } else {
        dealNumber = data.dealsLog.length;
      }

      for (var deal of data.dealsLog) {
        var tr = document.createElement('div');
        tr.classList.add('tr');
        tbody.appendChild(tr);

        var td = document.createElement('div');
        td.classList.add('td');
        td.classList.add('w-10');
        tr.appendChild(td);

        var div = document.createElement('div');
        div.classList.add('h-100');
        div.classList.add('align-start');
        div.innerText = dealNumber;
        td.appendChild(div);
        dealNumber += step;

        var td = document.createElement('div');
        td.classList.add('td');
        td.classList.add('w-18');
        tr.appendChild(td);

        var div1 = document.createElement('div');
        div1.classList.add('h-50');
        div1.classList.add('align-start');
        div1.classList.add('border');

        if (deal[0] == 'long') {
          div1.innerText = 'Выход из длинной позиции';
        } else {
          div1.innerText = 'Выход из короткой позиции';
        }

        td.appendChild(div1);

        var div2 = document.createElement('div');
        div2.classList.add('h-50');
        div2.classList.add('align-start');

        if (deal[0] == 'long') {
          div2.innerText = 'Вход в длинную позицию';
        } else {
          div2.innerText = 'Вход в короткую позицию';
        }

        td.appendChild(div2);

        var td = document.createElement('div');
        td.classList.add('td');
        td.classList.add('w-18');
        tr.appendChild(td);

        var div1 = document.createElement('div');
        div1.classList.add('h-50');
        div1.classList.add('align-start');
        div1.classList.add('border');
        div1.innerText = deal[2];
        td.appendChild(div1);

        var div2 = document.createElement('div');
        div2.classList.add('h-50');
        div2.classList.add('align-start');
        div2.innerText = deal[1];
        td.appendChild(div2);

        var td = document.createElement('div');
        td.classList.add('td');
        td.classList.add('w-12');
        tr.appendChild(td);

        var div1 = document.createElement('div');
        div1.classList.add('h-50');
        div1.classList.add('align-start');
        div1.classList.add('border');
        div1.innerText = deal[4];
        td.appendChild(div1);

        var div2 = document.createElement('div');
        div2.classList.add('h-50');
        div2.classList.add('align-start');
        div2.innerText = deal[3];
        td.appendChild(div2);

        var td = document.createElement('div');
        td.classList.add('td');
        td.classList.add('w-10');
        tr.appendChild(td);

        var div1 = document.createElement('div');
        div1.classList.add('h-50');
        div1.classList.add('align-end');
        div1.classList.add('border');

        if (deal[6]) {
          div1.innerText = deal[6] + ' USDT';
        }

        td.appendChild(div1);

        var div2 = document.createElement('div');
        div2.classList.add('h-50');
        div2.classList.add('align-end');

        if (deal[5]) {
          div2.innerText = deal[5] + ' USDT';
        }

        td.appendChild(div2);

        var td = document.createElement('div');
        td.classList.add('td');
        td.classList.add('w-10');
        tr.appendChild(td);

        var div = document.createElement('div');
        div.classList.add('h-100');
        div.classList.add('align-end');
        div.innerText = deal[7];
        td.appendChild(div);

        var td = document.createElement('div');
        td.classList.add('td');
        td.classList.add('w-10');
        tr.appendChild(td);

        var div = document.createElement('div');
        div.classList.add('h-100');
        div.classList.add('align-end');
        td.appendChild(div);

        var div1 = document.createElement('div');
        var div2 = document.createElement('div');

        if (deal[8] < 0) {
          div1.innerHTML = `<span style="color: #f23645; font-size: 14px;">${
            deal[8] + ' USDT'
          }</span>`;
          div2.innerHTML = `<span style="color: #f23645;">${
            deal[9] + '%'
          }</span>`;
        } else if (deal[8] > 0) {
          div1.innerText = deal[8] + ' USDT';
          div2.innerText = deal[9] + '%';
        }

        div.appendChild(div1);
        div.appendChild(div2);

        var td = document.createElement('div');
        td.classList.add('td');
        td.classList.add('w-14');
        tr.appendChild(td);

        var div = document.createElement('div');
        div.classList.add('h-100');
        div.classList.add('align-end');
        td.appendChild(div);

        var div1 = document.createElement('div');
        var div2 = document.createElement('div');

        if (deal[10] < 0) {
          div1.innerHTML = `<span style="color: #f23645; font-size: 14px;">${
            deal[10] + ' USDT'
          }</span>`;
        } else if (deal[10] > 0) {
          div1.innerText = deal[10] + ' USDT';
        }

        if (deal[11] < 0) {
          div2.innerHTML = `<span style="color: #f23645;">${
            deal[11] + '%'
          }</span>`;
        } else if (deal[11] > 0) {
          div2.innerText = deal[11] + '%';
        }

        div.appendChild(div1);
        div.appendChild(div2);
      }
    }
  }

  removeReport() {
    try {
      if (this.placeholder2.style.display != 'flex') {
        document.getElementById('metrics-container').remove();
        document.getElementById('chart-container').remove();
        this.chart.remove();
      } else {
        this.placeholder2.style.display = 'none';
      }

      document.getElementById('performance-container').remove();

      if (this.placeholder3.style.display != 'flex') {
        document.getElementById('trades-container').remove();
      } else {
        this.placeholder3.style.display = 'none';
      }
    } catch {}
  }

  manageTabs() {
    var overviewButton = document.getElementById('overview-button');
    var performanceButton = document.getElementById('performance-button');
    var tradesButton = document.getElementById('trades-button');
    var overviewReport = document.getElementById('overview-report');
    var performanceReport = document.getElementById('performance-report');
    var tradesReport = document.getElementById('trades-report');

    overviewButton.addEventListener('click', () => {
      overviewButton.dataset.status = 'active';
      performanceButton.dataset.status = 'inactive';
      tradesButton.dataset.status = 'inactive';

      if (MODE == 'TESTING') {
        overviewReport.style.display = 'flex';
        performanceReport.style.display = 'none';
        tradesReport.style.display = 'none';
      }
    });

    performanceButton.addEventListener('click', () => {
      overviewButton.dataset.status = 'inactive';
      performanceButton.dataset.status = 'active';
      tradesButton.dataset.status = 'inactive';

      if (MODE == 'TESTING') {
        overviewReport.style.display = 'none';
        performanceReport.style.display = 'flex';
        tradesReport.style.display = 'none';
      }
    });

    tradesButton.addEventListener('click', () => {
      overviewButton.dataset.status = 'inactive';
      performanceButton.dataset.status = 'inactive';
      tradesButton.dataset.status = 'active';

      if (MODE == 'TESTING') {
        overviewReport.style.display = 'none';
        performanceReport.style.display = 'none';
        tradesReport.style.display = 'flex';
      }
    });
  }

  manageSize() {
    var chartPanel = document.getElementById('chart-panel');
    var reportPanel = document.getElementById('report-panel');
    var reportPanelHandle = document.getElementById('report-panel-handle');
    var reportWrapper = document.getElementById('report-wrapper');

    var hideButton = document.getElementById('hide-button');
    var stretchButton = document.getElementById('stretch-button');

    var reportPanelLastFlex = null;
    var startOffset = NaN;

    hideButton.addEventListener('click', () => {
      if (hideButton.dataset.status == 'opened') {
        if (reportPanelLastFlex == null) {
          reportPanelLastFlex = window
            .getComputedStyle(reportPanel)
            .getPropertyValue('flex');
        }

        chartPanel.style.display = 'block';
        chartPanel.style.flex = '1 1 100%';
        chartPanel.style.maxHeight = '100%';
        reportWrapper.style.display = 'none';
        reportPanelHandle.style.display = 'block';
        reportPanelHandle.style.pointerEvents = 'none';
        reportPanel.style.flex = '1 1 0%';
        reportPanel.style.minHeight = 'auto';
        reportPanel.style.maxHeight = '70%';

        hideButton.setAttribute('data-status', 'closed');
        hideButton.setAttribute('title', 'Открыть панель');
        stretchButton.setAttribute('data-status', 'packed');
        stretchButton.setAttribute('title', 'Развернуть панель');
      } else if (hideButton.dataset.status == 'closed') {
        chartPanel.style.flex = '1 1 0%';
        reportPanelHandle.style.pointerEvents = 'auto';
        reportWrapper.style.display = 'flex';
        reportPanel.style.flex =
          reportPanelLastFlex == null ? '1 1 0%' : reportPanelLastFlex;
        reportPanel.style.minHeight = '30%';
        reportPanelLastFlex = null;

        hideButton.setAttribute('data-status', 'opened');
        hideButton.setAttribute('title', 'Свернуть панель');
      }
    });

    stretchButton.addEventListener('click', () => {
      if (stretchButton.dataset.status == 'packed') {
        if (reportPanelLastFlex == null) {
          reportPanelLastFlex = window
            .getComputedStyle(reportPanel)
            .getPropertyValue('flex');
        }

        chartPanel.style.display = 'none';
        reportPanelHandle.style.display = 'none';
        reportWrapper.style.display = 'flex';
        reportPanel.style.flex = '1 1 0%';
        reportPanel.style.maxHeight = '100%';

        stretchButton.setAttribute('data-status', 'stretched');
        stretchButton.setAttribute('title', 'Восстановить панель');
        hideButton.setAttribute('data-status', 'opened');
        hideButton.setAttribute('title', 'Свернуть панель');
      } else if (stretchButton.dataset.status == 'stretched') {
        chartPanel.style.display = 'block';
        chartPanel.style.flex = '1 1 0%';
        reportPanelHandle.style.display = 'block';
        reportPanelHandle.style.pointerEvents = 'auto';
        reportPanel.style.flex =
          reportPanelLastFlex == null ? '1 1 0%' : reportPanelLastFlex;
        reportPanel.style.minHeight = '30%';
        reportPanel.style.maxHeight = '70%';
        reportPanelLastFlex = null;

        stretchButton.setAttribute('data-status', 'packed');
        stretchButton.setAttribute('title', 'Развернуть панель');
      }
    });

    reportPanelHandle.addEventListener('mousedown', (event) => {
      startOffset = reportPanel.offsetTop - event.clientY;
      document.addEventListener('mousemove', onMouseMove);
      document.body.style.cursor = 'ns-resize';
    });

    document.addEventListener('mouseup', () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.body.style.cursor = 'default';
    });

    function onMouseMove(event) {
      var currentOffset = reportPanel.offsetTop - event.clientY;
      var newReportPanelSize = `0 0 ${
        reportPanel.offsetHeight + (currentOffset - startOffset)
      }px`;
      reportPanel.style.flex = newReportPanelSize;
    }
  }
}
