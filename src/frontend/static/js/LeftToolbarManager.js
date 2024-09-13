export default class LeftToolbarManager {
  lineOptions = {
    lineWidth: 3,
    crosshairMarkerVisible: false,
    lastValueVisible: false,
    priceLineVisible: false,
  };

  constructor() {
    this.screenshotButton = document.getElementById("screenshot-button");
    this.fullScreenButton = document.getElementById("full-screen-button");
    this.lineButton = document.getElementById("line-button");
    this.rulerButton = document.getElementById("ruler-button");
    this.hiderButton = document.getElementById("hider-button");
    this.basketButton = document.getElementById("basket-button");
    this.chartPanel = document.getElementById("chart-panel");

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        this.resetLine();
        this.resetRuler();

        this.lineButton.blur();
        this.rulerButton.blur();
      }
    });
  }

  manage(chart, liteData, klineSeries) {
    this.chart = chart;
    this.liteData = liteData;
    this.klineSeries = klineSeries;
    this.lines = [];

    this.manageScreenshotButton();
    this.manageFullScreenButton();
    this.manageLineButton();
    this.manageRulerButton();
    this.manageHiderButton();
    this.manageBasketButton();
  }

  manageScreenshotButton() {
    this.takeScreenshot = () => {
      this.chart.takeScreenshot().toBlob(openScreenshot, "image/png", 1);

      function openScreenshot(blob) {
        var url = URL.createObjectURL(blob);
        window.open(url, "_blank");
      }
    };

    this.screenshotButton.addEventListener("click", this.takeScreenshot);
  }

  manageFullScreenButton() {
    this.takeFullScreen = () => {
      if (this.chartPanel.requestFullscreen) {
        this.chartPanel.requestFullscreen();
      } else if (this.chartPanel.webkitrequestFullscreen) {
        this.chartPanel.webkitRequestFullscreen();
      } else if (this.chartPanel.mozRequestFullscreen) {
        this.chartPanel.mozRequestFullScreen();
      }
    };

    this.fullScreenButton.addEventListener("click", this.takeFullScreen);
  }

  manageLineButton() {
    this.setLinePoint = (param) => {
      var x = param.time;
      var y = this.klineSeries.coordinateToPrice(param.point.y);

      if (this.startLine == null) {
        this.startLine = { time: x, value: y };
      } else {
        var line = this.chart.addLineSeries(this.lineOptions);
        this.lines.push(line);

        if (x >= this.startLine.time) {
          line.setData([this.startLine, { time: x, value: y }]);
          this.startLine = null;
        } else {
          line.setData([{ time: x, value: y }, this.startLine]);
          this.startLine = null;
        }

        this.resetLine();
      }
    };

    this.lineButtonClickHandler = () => {
      if (this.lineButton.dataset.status == "inactive") {
        this.resetRuler();

        this.startLine = null;
        this.lineButton.dataset.status = "active";
        this.chart.subscribeClick(this.setLinePoint);
      } else {
        this.resetLine();
      }
    };

    this.resetLine();
    this.lineButton.addEventListener("click", this.lineButtonClickHandler);
  }

  manageRulerButton() {
    var mintick = this.liteData.mintick;
    var precision = String(mintick).match(/.\d+$/g)[0].length - 1;

    this.crosshairMoveHandler = (param) => {
      if (param.point) {
        var chartX = param.logical;
        var chartY = this.klineSeries.coordinateToPrice(param.point.y);
        var localX = param.sourceEvent.localX;
        var localY = param.sourceEvent.localY;

        var width = localX - this.rulerStart.localX;
        var height = this.rulerStart.localY - localY;

        var num1 = (chartY - this.rulerStart.chartY).toFixed(precision);
        var num2 = ((chartY / this.rulerStart.chartY - 1) * 100).toFixed(2);
        var num3 = (num1 / mintick).toFixed(0);
        var num4 = (chartX - this.rulerStart.chartX).toFixed(0);

        if (width >= 0) {
          if (this.innerDiv1.dataset.direction == "left") {
            this.innerDiv1.setAttribute("data-direction", "right");
          }

          this.ruler.style.right = `${this.chartPanel.offsetWidth - localX}px`;
          this.ruler.style.width = `${width}px`;
        } else {
          if (this.innerDiv1.dataset.direction == "right") {
            this.innerDiv1.setAttribute("data-direction", "left");
          }

          this.ruler.style.width = `${Math.abs(width) - 3}px`;
        }

        if (height >= 0) {
          if (this.ruler.dataset.direction == "down") {
            this.ruler.setAttribute("data-direction", "up");
            this.innerDiv2.setAttribute("data-direction", "up");
          }

          this.ruler.style.top = `${localY}px`;
          this.ruler.style.height = `${height}px`;
        } else {
          if (this.innerDiv2.dataset.direction == "up") {
            this.ruler.setAttribute("data-direction", "down");
            this.innerDiv2.setAttribute("data-direction", "down");
          }

          this.ruler.style.height = `${Math.abs(height)}px`;
        }

        this.rulerLabel.innerHTML = `${num1} (${num2}%), ${num3}
          <br />Бары: ${num4}`;

        if (Math.abs(width) > 50) {
          this.innerDiv1.style.display = "block";
        } else {
          this.innerDiv1.style.display = "none";
        }

        if (Math.abs(height) > 50) {
          this.innerDiv2.style.display = "block";
        } else {
          this.innerDiv2.style.display = "none";
        }
      }
    };

    this.setRulerPoint = (param) => {
      var chartX = param.logical;
      var chartY = this.klineSeries.coordinateToPrice(param.point.y);
      var localX = param.sourceEvent.localX;
      var localY = param.sourceEvent.localY;

      if (this.rulerStart == null) {
        this.ruler = document.createElement("div");
        this.ruler.setAttribute("id", "ruler");
        this.ruler.setAttribute("data-direction", "up");

        this.rulerLabel = document.createElement("div");
        this.rulerLabel.setAttribute("id", "ruler-label");
        this.ruler.appendChild(this.rulerLabel);

        var arrowHorizontal = document.createElement("div");
        arrowHorizontal.setAttribute("id", "arrow-horizontal");
        this.ruler.appendChild(arrowHorizontal);

        this.innerDiv1 = document.createElement("div");
        this.innerDiv1.setAttribute("data-direction", "right");
        arrowHorizontal.appendChild(this.innerDiv1);

        var arrowVertical = document.createElement("div");
        arrowVertical.setAttribute("id", "arrow-vertical");
        this.ruler.appendChild(arrowVertical);

        this.innerDiv2 = document.createElement("div");
        this.innerDiv2.setAttribute("data-direction", "up");
        arrowVertical.appendChild(this.innerDiv2);

        this.rulerStart = {
          chartX: chartX,
          chartY: chartY,
          localX: localX,
          localY: localY,
        };

        this.rulerLabel.innerHTML = `0.${Array(precision)
          .fill("0")
          .join("")} (0.00%), 0<br />Бары: 0`;
        this.ruler.style.top = `${localY}px`;
        this.ruler.style.right = `${this.chartPanel.offsetWidth - localX}px`;

        this.chartPanel.appendChild(this.ruler);
        this.chart.subscribeCrosshairMove(this.crosshairMoveHandler);
      } else {
        this.resetRuler();
      }
    };

    this.rulerButtonClickHandler = () => {
      if (this.rulerButton.dataset.status == "inactive") {
        this.resetLine();

        this.rulerStart = null;
        this.rulerButton.dataset.status = "active";
        this.chart.subscribeClick(this.setRulerPoint);
      } else {
        this.resetRuler();
      }
    };

    this.resetRuler();
    this.rulerButton.addEventListener("click", this.rulerButtonClickHandler);
  }

  manageHiderButton() {
    this.hideObjects = () => {
      if (this.hiderButton.dataset.status == "inactive") {
        this.hiderButton.dataset.status = "active";

        for (var line of this.lines) {
          line.applyOptions({ visible: false });
        }
      } else {
        this.hiderButton.dataset.status = "inactive";

        for (var line of this.lines) {
          line.applyOptions({ visible: true });
        }
      }
    };

    this.hiderButton.dataset.status = "inactive";
    this.hiderButton.addEventListener("click", this.hideObjects);
  }

  manageBasketButton() {
    this.removeObjects = () => {
      for (var line of this.lines) {
        this.chart.removeSeries(line);
      }

      this.lines = [];
    };

    this.basketButton.addEventListener("click", this.removeObjects);
  }

  resetLine() {
    this.lineButton.dataset.status = "inactive";
    this.chart.unsubscribeClick(this.setLinePoint);
  }

  resetRuler() {
    this.rulerButton.dataset.status = "inactive";
    this.chart.unsubscribeClick(this.setRulerPoint);
    this.chart.unsubscribeCrosshairMove(this.crosshairMoveHandler);

    try {
      this.chartPanel.removeChild(this.ruler);
    } catch {}
  }

  removeEventListeners() {
    this.screenshotButton.removeEventListener("click", this.takeScreenshot);
    this.fullScreenButton.removeEventListener("click", this.takeFullScreen);
    this.lineButton.removeEventListener("click", this.lineButtonClickHandler);
    this.rulerButton.removeEventListener("click", this.rulerButtonClickHandler);
    this.hiderButton.removeEventListener("click", this.hideObjects);
    this.basketButton.removeEventListener("click", this.removeObjects);
  }
}
