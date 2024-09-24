/*!
 * @license
 * TradingView Lightweight Charts™ v4.1.4
 * Copyright (c) 2024 TradingView, Inc.
 * Licensed under Apache License 2.0 https://www.apache.org/licenses/LICENSE-2.0
 */
!(function () {
  "use strict";
  const t = {
      upColor: "#26a69a",
      downColor: "#ef5350",
      wickVisible: !0,
      borderVisible: !0,
      borderColor: "#378658",
      borderUpColor: "#26a69a",
      borderDownColor: "#ef5350",
      wickColor: "#737375",
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    },
    i = {
      upColor: "#26a69a",
      downColor: "#ef5350",
      openVisible: !0,
      thinBars: !0,
    },
    n = {
      color: "#2196f3",
      lineStyle: 0,
      lineWidth: 3,
      lineType: 0,
      lineVisible: !0,
      crosshairMarkerVisible: !0,
      crosshairMarkerRadius: 4,
      crosshairMarkerBorderColor: "",
      crosshairMarkerBorderWidth: 2,
      crosshairMarkerBackgroundColor: "",
      lastPriceAnimation: 0,
      pointMarkersVisible: !1,
    },
    s = {
      topColor: "rgba( 46, 220, 135, 0.4)",
      bottomColor: "rgba( 40, 221, 100, 0)",
      invertFilledArea: !1,
      lineColor: "#33D778",
      lineStyle: 0,
      lineWidth: 3,
      lineType: 0,
      lineVisible: !0,
      crosshairMarkerVisible: !0,
      crosshairMarkerRadius: 4,
      crosshairMarkerBorderColor: "",
      crosshairMarkerBorderWidth: 2,
      crosshairMarkerBackgroundColor: "",
      lastPriceAnimation: 0,
      pointMarkersVisible: !1,
    },
    e = {
      baseValue: { type: "price", price: 0 },
      topFillColor1: "rgba(38, 166, 154, 0.28)",
      topFillColor2: "rgba(38, 166, 154, 0.05)",
      topLineColor: "rgba(38, 166, 154, 1)",
      bottomFillColor1: "rgba(239, 83, 80, 0.05)",
      bottomFillColor2: "rgba(239, 83, 80, 0.28)",
      bottomLineColor: "rgba(239, 83, 80, 1)",
      lineWidth: 3,
      lineStyle: 0,
      lineType: 0,
      lineVisible: !0,
      crosshairMarkerVisible: !0,
      crosshairMarkerRadius: 4,
      crosshairMarkerBorderColor: "",
      crosshairMarkerBorderWidth: 2,
      crosshairMarkerBackgroundColor: "",
      lastPriceAnimation: 0,
      pointMarkersVisible: !1,
    },
    r = { color: "#26a69a", base: 0 },
    h = { color: "#2196f3" },
    l = {
      title: "",
      visible: !0,
      lastValueVisible: !0,
      priceLineVisible: !0,
      priceLineSource: 0,
      priceLineWidth: 1,
      priceLineColor: "",
      priceLineStyle: 2,
      baseLineVisible: !0,
      baseLineWidth: 1,
      baseLineColor: "#B2B5BE",
      baseLineStyle: 0,
      priceFormat: { type: "price", precision: 2, minMove: 0.01 },
    };
  var a, o;
  function _(t, i) {
    const n = {
      0: [],
      1: [t.lineWidth, t.lineWidth],
      2: [2 * t.lineWidth, 2 * t.lineWidth],
      3: [6 * t.lineWidth, 6 * t.lineWidth],
      4: [t.lineWidth, 4 * t.lineWidth],
    }[i];
    t.setLineDash(n);
  }
  function u(t, i, n, s) {
    t.beginPath();
    const e = t.lineWidth % 2 ? 0.5 : 0;
    t.moveTo(n, i + e), t.lineTo(s, i + e), t.stroke();
  }
  function c(t, i) {
    if (!t) throw new Error("Assertion failed" + (i ? ": " + i : ""));
  }
  function d(t) {
    if (void 0 === t) throw new Error("Value is undefined");
    return t;
  }
  function f(t) {
    if (null === t) throw new Error("Value is null");
    return t;
  }
  function v(t) {
    return f(d(t));
  }
  !(function (t) {
    (t[(t.Simple = 0)] = "Simple"),
      (t[(t.WithSteps = 1)] = "WithSteps"),
      (t[(t.Curved = 2)] = "Curved");
  })(a || (a = {})),
    (function (t) {
      (t[(t.Solid = 0)] = "Solid"),
        (t[(t.Dotted = 1)] = "Dotted"),
        (t[(t.Dashed = 2)] = "Dashed"),
        (t[(t.LargeDashed = 3)] = "LargeDashed"),
        (t[(t.SparseDotted = 4)] = "SparseDotted");
    })(o || (o = {}));
  const p = {
    khaki: "#f0e68c",
    azure: "#f0ffff",
    aliceblue: "#f0f8ff",
    ghostwhite: "#f8f8ff",
    gold: "#ffd700",
    goldenrod: "#daa520",
    gainsboro: "#dcdcdc",
    gray: "#808080",
    green: "#008000",
    honeydew: "#f0fff0",
    floralwhite: "#fffaf0",
    lightblue: "#add8e6",
    lightcoral: "#f08080",
    lemonchiffon: "#fffacd",
    hotpink: "#ff69b4",
    lightyellow: "#ffffe0",
    greenyellow: "#adff2f",
    lightgoldenrodyellow: "#fafad2",
    limegreen: "#32cd32",
    linen: "#faf0e6",
    lightcyan: "#e0ffff",
    magenta: "#f0f",
    maroon: "#800000",
    olive: "#808000",
    orange: "#ffa500",
    oldlace: "#fdf5e6",
    mediumblue: "#0000cd",
    transparent: "#0000",
    lime: "#0f0",
    lightpink: "#ffb6c1",
    mistyrose: "#ffe4e1",
    moccasin: "#ffe4b5",
    midnightblue: "#191970",
    orchid: "#da70d6",
    mediumorchid: "#ba55d3",
    mediumturquoise: "#48d1cc",
    orangered: "#ff4500",
    royalblue: "#4169e1",
    powderblue: "#b0e0e6",
    red: "#f00",
    coral: "#ff7f50",
    turquoise: "#40e0d0",
    white: "#fff",
    whitesmoke: "#f5f5f5",
    wheat: "#f5deb3",
    teal: "#008080",
    steelblue: "#4682b4",
    bisque: "#ffe4c4",
    aquamarine: "#7fffd4",
    aqua: "#0ff",
    sienna: "#a0522d",
    silver: "#c0c0c0",
    springgreen: "#00ff7f",
    antiquewhite: "#faebd7",
    burlywood: "#deb887",
    brown: "#a52a2a",
    beige: "#f5f5dc",
    chocolate: "#d2691e",
    chartreuse: "#7fff00",
    cornflowerblue: "#6495ed",
    cornsilk: "#fff8dc",
    crimson: "#dc143c",
    cadetblue: "#5f9ea0",
    tomato: "#ff6347",
    fuchsia: "#f0f",
    blue: "#00f",
    salmon: "#fa8072",
    blanchedalmond: "#ffebcd",
    slateblue: "#6a5acd",
    slategray: "#708090",
    thistle: "#d8bfd8",
    tan: "#d2b48c",
    cyan: "#0ff",
    darkblue: "#00008b",
    darkcyan: "#008b8b",
    darkgoldenrod: "#b8860b",
    darkgray: "#a9a9a9",
    blueviolet: "#8a2be2",
    black: "#000",
    darkmagenta: "#8b008b",
    darkslateblue: "#483d8b",
    darkkhaki: "#bdb76b",
    darkorchid: "#9932cc",
    darkorange: "#ff8c00",
    darkgreen: "#006400",
    darkred: "#8b0000",
    dodgerblue: "#1e90ff",
    darkslategray: "#2f4f4f",
    dimgray: "#696969",
    deepskyblue: "#00bfff",
    firebrick: "#b22222",
    forestgreen: "#228b22",
    indigo: "#4b0082",
    ivory: "#fffff0",
    lavenderblush: "#fff0f5",
    feldspar: "#d19275",
    indianred: "#cd5c5c",
    lightgreen: "#90ee90",
    lightgrey: "#d3d3d3",
    lightskyblue: "#87cefa",
    lightslategray: "#789",
    lightslateblue: "#8470ff",
    snow: "#fffafa",
    lightseagreen: "#20b2aa",
    lightsalmon: "#ffa07a",
    darksalmon: "#e9967a",
    darkviolet: "#9400d3",
    mediumpurple: "#9370d8",
    mediumaquamarine: "#66cdaa",
    skyblue: "#87ceeb",
    lavender: "#e6e6fa",
    lightsteelblue: "#b0c4de",
    mediumvioletred: "#c71585",
    mintcream: "#f5fffa",
    navajowhite: "#ffdead",
    navy: "#000080",
    olivedrab: "#6b8e23",
    palevioletred: "#d87093",
    violetred: "#d02090",
    yellow: "#ff0",
    yellowgreen: "#9acd32",
    lawngreen: "#7cfc00",
    pink: "#ffc0cb",
    paleturquoise: "#afeeee",
    palegoldenrod: "#eee8aa",
    darkolivegreen: "#556b2f",
    darkseagreen: "#8fbc8f",
    darkturquoise: "#00ced1",
    peachpuff: "#ffdab9",
    deeppink: "#ff1493",
    violet: "#ee82ee",
    palegreen: "#98fb98",
    mediumseagreen: "#3cb371",
    peru: "#cd853f",
    saddlebrown: "#8b4513",
    sandybrown: "#f4a460",
    rosybrown: "#bc8f8f",
    purple: "#800080",
    seagreen: "#2e8b57",
    seashell: "#fff5ee",
    papayawhip: "#ffefd5",
    mediumslateblue: "#7b68ee",
    plum: "#dda0dd",
    mediumspringgreen: "#00fa9a",
  };
  function m(t) {
    return t < 0 ? 0 : t > 255 ? 255 : Math.round(t) || 0;
  }
  function b(t) {
    return t <= 0 || t > 1
      ? Math.min(Math.max(t, 0), 1)
      : Math.round(1e4 * t) / 1e4;
  }
  const w = /^#([0-9a-f])([0-9a-f])([0-9a-f])([0-9a-f])?$/i,
    g = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})?$/i,
    M = /^rgb\(\s*(-?\d{1,10})\s*,\s*(-?\d{1,10})\s*,\s*(-?\d{1,10})\s*\)$/,
    x =
      /^rgba\(\s*(-?\d{1,10})\s*,\s*(-?\d{1,10})\s*,\s*(-?\d{1,10})\s*,\s*(-?\d*\.?\d+)\s*\)$/;
  function S(t) {
    (t = t.toLowerCase()) in p && (t = p[t]);
    {
      const i = x.exec(t) || M.exec(t);
      if (i)
        return [
          m(parseInt(i[1], 10)),
          m(parseInt(i[2], 10)),
          m(parseInt(i[3], 10)),
          b(i.length < 5 ? 1 : parseFloat(i[4])),
        ];
    }
    {
      const i = g.exec(t);
      if (i)
        return [
          m(parseInt(i[1], 16)),
          m(parseInt(i[2], 16)),
          m(parseInt(i[3], 16)),
          1,
        ];
    }
    {
      const i = w.exec(t);
      if (i)
        return [
          m(17 * parseInt(i[1], 16)),
          m(17 * parseInt(i[2], 16)),
          m(17 * parseInt(i[3], 16)),
          1,
        ];
    }
    throw new Error(`Cannot parse color: ${t}`);
  }
  function y(t) {
    const i = S(t);
    return {
      t: `rgb(${i[0]}, ${i[1]}, ${i[2]})`,
      i:
        ((n = i),
        0.199 * n[0] + 0.687 * n[1] + 0.114 * n[2] > 160 ? "black" : "white"),
    };
    var n;
  }
  class k {
    constructor() {
      this.h = [];
    }
    l(t, i, n) {
      const s = { o: t, _: i, u: !0 === n };
      this.h.push(s);
    }
    v(t) {
      const i = this.h.findIndex((i) => t === i.o);
      i > -1 && this.h.splice(i, 1);
    }
    p(t) {
      this.h = this.h.filter((i) => i._ !== t);
    }
    m(t, i, n) {
      const s = [...this.h];
      (this.h = this.h.filter((t) => !t.u)), s.forEach((s) => s.o(t, i, n));
    }
    M() {
      return this.h.length > 0;
    }
    S() {
      this.h = [];
    }
  }
  function C(t, ...i) {
    for (const n of i)
      for (const i in n)
        void 0 !== n[i] &&
          ("object" != typeof n[i] || void 0 === t[i] || Array.isArray(n[i])
            ? (t[i] = n[i])
            : C(t[i], n[i]));
    return t;
  }
  function T(t) {
    return "number" == typeof t && isFinite(t);
  }
  function P(t) {
    return "number" == typeof t && t % 1 == 0;
  }
  function R(t) {
    return "string" == typeof t;
  }
  function D(t) {
    return "boolean" == typeof t;
  }
  function O(t) {
    const i = t;
    if (!i || "object" != typeof i) return i;
    let n, s, e;
    for (s in ((n = Array.isArray(i) ? [] : {}), i))
      i.hasOwnProperty(s) &&
        ((e = i[s]), (n[s] = e && "object" == typeof e ? O(e) : e));
    return n;
  }
  function B(t) {
    return null !== t;
  }
  function A(t) {
    return null === t ? void 0 : t;
  }
  const V =
    "-apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif";
  function z(t, i, n) {
    return (
      void 0 === i && (i = V), `${(n = void 0 !== n ? `${n} ` : "")}${t}px ${i}`
    );
  }
  class E {
    constructor(t) {
      (this.k = {
        C: 1,
        T: 5,
        P: NaN,
        R: "",
        D: "",
        O: "",
        B: "",
        A: 0,
        V: 0,
        I: 0,
        L: 0,
        N: 0,
      }),
        (this.F = t);
    }
    W() {
      const t = this.k,
        i = this.j(),
        n = this.H();
      return (
        (t.P === i && t.D === n) ||
          ((t.P = i),
          (t.D = n),
          (t.R = z(i, n)),
          (t.L = (2.5 / 12) * i),
          (t.A = t.L),
          (t.V = (i / 12) * t.T),
          (t.I = (i / 12) * t.T),
          (t.N = 0)),
        (t.O = this.$()),
        (t.B = this.U()),
        this.k
      );
    }
    $() {
      return this.F.W().layout.textColor;
    }
    U() {
      return this.F.q();
    }
    j() {
      return this.F.W().layout.fontSize;
    }
    H() {
      return this.F.W().layout.fontFamily;
    }
  }
  class I {
    constructor() {
      this.Y = [];
    }
    X(t) {
      this.Y = t;
    }
    K(t, i, n) {
      this.Y.forEach((s) => {
        s.K(t, i, n);
      });
    }
  }
  class L {
    K(t, i, n) {
      t.useBitmapCoordinateSpace((t) => this.Z(t, i, n));
    }
  }
  class N extends L {
    constructor() {
      super(...arguments), (this.G = null);
    }
    J(t) {
      this.G = t;
    }
    Z({ context: t, horizontalPixelRatio: i, verticalPixelRatio: n }) {
      if (null === this.G || null === this.G.tt) return;
      const s = this.G.tt,
        e = this.G,
        r = (Math.max(1, Math.floor(i)) % 2) / 2,
        h = (h) => {
          t.beginPath();
          for (let l = s.to - 1; l >= s.from; --l) {
            const s = e.it[l],
              a = Math.round(s.nt * i) + r,
              o = s.st * n,
              _ = h * n + r;
            t.moveTo(a, o), t.arc(a, o, _, 0, 2 * Math.PI);
          }
          t.fill();
        };
      e.et > 0 && ((t.fillStyle = e.rt), h(e.ht + e.et)),
        (t.fillStyle = e.lt),
        h(e.ht);
    }
  }
  function F() {
    return {
      it: [{ nt: 0, st: 0, ot: 0, _t: 0 }],
      lt: "",
      rt: "",
      ht: 0,
      et: 0,
      tt: null,
    };
  }
  const W = { from: 0, to: 1 };
  class j {
    constructor(t, i) {
      (this.ut = new I()),
        (this.ct = []),
        (this.dt = []),
        (this.ft = !0),
        (this.F = t),
        (this.vt = i),
        this.ut.X(this.ct);
    }
    bt(t) {
      const i = this.F.wt();
      i.length !== this.ct.length &&
        ((this.dt = i.map(F)),
        (this.ct = this.dt.map((t) => {
          const i = new N();
          return i.J(t), i;
        })),
        this.ut.X(this.ct)),
        (this.ft = !0);
    }
    gt() {
      return this.ft && (this.Mt(), (this.ft = !1)), this.ut;
    }
    Mt() {
      const t = 2 === this.vt.W().mode,
        i = this.F.wt(),
        n = this.vt.xt(),
        s = this.F.St();
      i.forEach((i, e) => {
        var r;
        const h = this.dt[e],
          l = i.yt(n);
        if (t || null === l || !i.kt()) return void (h.tt = null);
        const a = f(i.Ct());
        (h.lt = l.Tt),
          (h.ht = l.ht),
          (h.et = l.Pt),
          (h.it[0]._t = l._t),
          (h.it[0].st = i.Dt().Rt(l._t, a.Ot)),
          (h.rt =
            null !== (r = l.Bt) && void 0 !== r
              ? r
              : this.F.At(h.it[0].st / i.Dt().Vt())),
          (h.it[0].ot = n),
          (h.it[0].nt = s.zt(n)),
          (h.tt = W);
      });
    }
  }
  class H extends L {
    constructor(t) {
      super(), (this.Et = t);
    }
    Z({
      context: t,
      bitmapSize: i,
      horizontalPixelRatio: n,
      verticalPixelRatio: s,
    }) {
      if (null === this.Et) return;
      const e = this.Et.It.kt,
        r = this.Et.Lt.kt;
      if (!e && !r) return;
      const h = Math.round(this.Et.nt * n),
        l = Math.round(this.Et.st * s);
      (t.lineCap = "butt"),
        e &&
          h >= 0 &&
          ((t.lineWidth = Math.floor(this.Et.It.et * n)),
          (t.strokeStyle = this.Et.It.O),
          (t.fillStyle = this.Et.It.O),
          _(t, this.Et.It.Nt),
          (function (t, i, n, s) {
            t.beginPath();
            const e = t.lineWidth % 2 ? 0.5 : 0;
            t.moveTo(i + e, n), t.lineTo(i + e, s), t.stroke();
          })(t, h, 0, i.height)),
        r &&
          l >= 0 &&
          ((t.lineWidth = Math.floor(this.Et.Lt.et * s)),
          (t.strokeStyle = this.Et.Lt.O),
          (t.fillStyle = this.Et.Lt.O),
          _(t, this.Et.Lt.Nt),
          u(t, l, 0, i.width));
    }
  }
  class $ {
    constructor(t) {
      (this.ft = !0),
        (this.Ft = {
          It: { et: 1, Nt: 0, O: "", kt: !1 },
          Lt: { et: 1, Nt: 0, O: "", kt: !1 },
          nt: 0,
          st: 0,
        }),
        (this.Wt = new H(this.Ft)),
        (this.jt = t);
    }
    bt() {
      this.ft = !0;
    }
    gt() {
      return this.ft && (this.Mt(), (this.ft = !1)), this.Wt;
    }
    Mt() {
      const t = this.jt.kt(),
        i = f(this.jt.Ht()),
        n = i.$t().W().crosshair,
        s = this.Ft;
      if (2 === n.mode) return (s.Lt.kt = !1), void (s.It.kt = !1);
      (s.Lt.kt = t && this.jt.Ut(i)),
        (s.It.kt = t && this.jt.qt()),
        (s.Lt.et = n.horzLine.width),
        (s.Lt.Nt = n.horzLine.style),
        (s.Lt.O = n.horzLine.color),
        (s.It.et = n.vertLine.width),
        (s.It.Nt = n.vertLine.style),
        (s.It.O = n.vertLine.color),
        (s.nt = this.jt.Yt()),
        (s.st = this.jt.Xt());
    }
  }
  function U(t, i, n, s, e, r) {
    t.fillRect(i + r, n, s - 2 * r, r),
      t.fillRect(i + r, n + e - r, s - 2 * r, r),
      t.fillRect(i, n, r, e),
      t.fillRect(i + s - r, n, r, e);
  }
  function q(t, i, n, s, e, r) {
    t.save(),
      (t.globalCompositeOperation = "copy"),
      (t.fillStyle = r),
      t.fillRect(i, n, s, e),
      t.restore();
  }
  function Y(t, i, n, s, e, r) {
    t.beginPath(),
      t.roundRect
        ? t.roundRect(i, n, s, e, r)
        : (t.lineTo(i + s - r[1], n),
          0 !== r[1] && t.arcTo(i + s, n, i + s, n + r[1], r[1]),
          t.lineTo(i + s, n + e - r[2]),
          0 !== r[2] && t.arcTo(i + s, n + e, i + s - r[2], n + e, r[2]),
          t.lineTo(i + r[3], n + e),
          0 !== r[3] && t.arcTo(i, n + e, i, n + e - r[3], r[3]),
          t.lineTo(i, n + r[0]),
          0 !== r[0] && t.arcTo(i, n, i + r[0], n, r[0]));
  }
  function X(t, i, n, s, e, r, h = 0, l = [0, 0, 0, 0], a = "") {
    if ((t.save(), !h || !a || a === r))
      return Y(t, i, n, s, e, l), (t.fillStyle = r), t.fill(), void t.restore();
    const o = h / 2;
    var _;
    Y(
      t,
      i + o,
      n + o,
      s - h,
      e - h,
      ((_ = -o), l.map((t) => (0 === t ? t : t + _)))
    ),
      "transparent" !== r && ((t.fillStyle = r), t.fill()),
      "transparent" !== a &&
        ((t.lineWidth = h), (t.strokeStyle = a), t.closePath(), t.stroke()),
      t.restore();
  }
  function K(t, i, n, s, e, r, h) {
    t.save(), (t.globalCompositeOperation = "copy");
    const l = t.createLinearGradient(0, 0, 0, e);
    l.addColorStop(0, r),
      l.addColorStop(1, h),
      (t.fillStyle = l),
      t.fillRect(i, n, s, e),
      t.restore();
  }
  class Z {
    constructor(t, i) {
      this.J(t, i);
    }
    J(t, i) {
      (this.Et = t), (this.Kt = i);
    }
    Vt(t, i) {
      return this.Et.kt ? t.P + t.L + t.A : 0;
    }
    K(t, i, n, s) {
      if (!this.Et.kt || 0 === this.Et.Zt.length) return;
      const e = this.Et.O,
        r = this.Kt.t,
        h = t.useBitmapCoordinateSpace((t) => {
          const h = t.context;
          h.font = i.R;
          const l = this.Gt(t, i, n, s),
            a = l.Jt,
            o = (t, i) => {
              l.Qt
                ? X(h, a.ti, a.ii, a.ni, a.si, t, a.ei, [a.ht, 0, 0, a.ht], i)
                : X(h, a.ri, a.ii, a.ni, a.si, t, a.ei, [0, a.ht, a.ht, 0], i);
            };
          return (
            o(r, "transparent"),
            this.Et.hi &&
              ((h.fillStyle = e), h.fillRect(a.ri, a.li, a.ai - a.ri, a.oi)),
            o("transparent", r),
            this.Et._i &&
              ((h.fillStyle = i.B),
              h.fillRect(l.Qt ? a.ui - a.ei : 0, a.ii, a.ei, a.ci - a.ii)),
            l
          );
        });
      t.useMediaCoordinateSpace(({ context: t }) => {
        const n = h.di;
        (t.font = i.R),
          (t.textAlign = h.Qt ? "right" : "left"),
          (t.textBaseline = "middle"),
          (t.fillStyle = e),
          t.fillText(this.Et.Zt, n.fi, (n.ii + n.ci) / 2 + n.vi);
      });
    }
    Gt(t, i, n, s) {
      var e;
      const {
          context: r,
          bitmapSize: h,
          mediaSize: l,
          horizontalPixelRatio: a,
          verticalPixelRatio: o,
        } = t,
        _ = this.Et.hi || !this.Et.pi ? i.T : 0,
        u = this.Et.mi ? i.C : 0,
        c = i.L + this.Kt.bi,
        d = i.A + this.Kt.wi,
        f = i.V,
        v = i.I,
        p = this.Et.Zt,
        m = i.P,
        b = n.gi(r, p),
        w = Math.ceil(n.Mi(r, p)),
        g = m + c + d,
        M = i.C + f + v + w + _,
        x = Math.max(1, Math.floor(o));
      let S = Math.round(g * o);
      S % 2 != x % 2 && (S += 1);
      const y = u > 0 ? Math.max(1, Math.floor(u * a)) : 0,
        k = Math.round(M * a),
        C = Math.round(_ * a),
        T = null !== (e = this.Kt.xi) && void 0 !== e ? e : this.Kt.Si,
        P = Math.round(T * o) - Math.floor(0.5 * o),
        R = Math.floor(P + x / 2 - S / 2),
        D = R + S,
        O = "right" === s,
        B = O ? l.width - u : u,
        A = O ? h.width - y : y;
      let V, z, E;
      return (
        O
          ? ((V = A - k), (z = A - C), (E = B - _ - f - u))
          : ((V = A + k), (z = A + C), (E = B + _ + f)),
        {
          Qt: O,
          Jt: {
            ii: R,
            li: P,
            ci: D,
            ni: k,
            si: S,
            ht: 2 * a,
            ei: y,
            ti: V,
            ri: A,
            ai: z,
            oi: x,
            ui: h.width,
          },
          di: { ii: R / o, ci: D / o, fi: E, vi: b },
        }
      );
    }
  }
  class G {
    constructor(t) {
      (this.yi = { Si: 0, t: "#000", wi: 0, bi: 0 }),
        (this.ki = {
          Zt: "",
          kt: !1,
          hi: !0,
          pi: !1,
          Bt: "",
          O: "#FFF",
          _i: !1,
          mi: !1,
        }),
        (this.Ci = {
          Zt: "",
          kt: !1,
          hi: !1,
          pi: !0,
          Bt: "",
          O: "#FFF",
          _i: !0,
          mi: !0,
        }),
        (this.ft = !0),
        (this.Ti = new (t || Z)(this.ki, this.yi)),
        (this.Pi = new (t || Z)(this.Ci, this.yi));
    }
    Zt() {
      return this.Ri(), this.ki.Zt;
    }
    Si() {
      return this.Ri(), this.yi.Si;
    }
    bt() {
      this.ft = !0;
    }
    Vt(t, i = !1) {
      return Math.max(this.Ti.Vt(t, i), this.Pi.Vt(t, i));
    }
    Di() {
      return this.yi.xi || 0;
    }
    Oi(t) {
      this.yi.xi = t;
    }
    Bi() {
      return this.Ri(), this.ki.kt || this.Ci.kt;
    }
    Ai() {
      return this.Ri(), this.ki.kt;
    }
    gt(t) {
      return (
        this.Ri(),
        (this.ki.hi = this.ki.hi && t.W().ticksVisible),
        (this.Ci.hi = this.Ci.hi && t.W().ticksVisible),
        this.Ti.J(this.ki, this.yi),
        this.Pi.J(this.Ci, this.yi),
        this.Ti
      );
    }
    Vi() {
      return (
        this.Ri(),
        this.Ti.J(this.ki, this.yi),
        this.Pi.J(this.Ci, this.yi),
        this.Pi
      );
    }
    Ri() {
      this.ft &&
        ((this.ki.hi = !0),
        (this.Ci.hi = !1),
        this.zi(this.ki, this.Ci, this.yi));
    }
  }
  class J extends G {
    constructor(t, i, n) {
      super(), (this.jt = t), (this.Ei = i), (this.Ii = n);
    }
    zi(t, i, n) {
      if (((t.kt = !1), 2 === this.jt.W().mode)) return;
      const s = this.jt.W().horzLine;
      if (!s.labelVisible) return;
      const e = this.Ei.Ct();
      if (!this.jt.kt() || this.Ei.Li() || null === e) return;
      const r = y(s.labelBackgroundColor);
      (n.t = r.t), (t.O = r.i);
      const h = (2 / 12) * this.Ei.P();
      (n.bi = h), (n.wi = h);
      const l = this.Ii(this.Ei);
      (n.Si = l.Si), (t.Zt = this.Ei.Ni(l._t, e)), (t.kt = !0);
    }
  }
  const Q = /[1-9]/g;
  class tt {
    constructor() {
      this.Et = null;
    }
    J(t) {
      this.Et = t;
    }
    K(t, i) {
      if (null === this.Et || !1 === this.Et.kt || 0 === this.Et.Zt.length)
        return;
      const n = t.useMediaCoordinateSpace(
        ({ context: t }) => (
          (t.font = i.R), Math.round(i.Fi.Mi(t, f(this.Et).Zt, Q))
        )
      );
      if (n <= 0) return;
      const s = i.Wi,
        e = n + 2 * s,
        r = e / 2,
        h = this.Et.ji;
      let l = this.Et.Si,
        a = Math.floor(l - r) + 0.5;
      a < 0
        ? ((l += Math.abs(0 - a)), (a = Math.floor(l - r) + 0.5))
        : a + e > h &&
          ((l -= Math.abs(h - (a + e))), (a = Math.floor(l - r) + 0.5));
      const o = a + e,
        _ = Math.ceil(0 + i.C + i.T + i.L + i.P + i.A);
      t.useBitmapCoordinateSpace(
        ({ context: t, horizontalPixelRatio: n, verticalPixelRatio: s }) => {
          const e = f(this.Et);
          t.fillStyle = e.t;
          const r = Math.round(a * n),
            h = Math.round(0 * s),
            l = Math.round(o * n),
            u = Math.round(_ * s),
            c = Math.round(2 * n);
          if (
            (t.beginPath(),
            t.moveTo(r, h),
            t.lineTo(r, u - c),
            t.arcTo(r, u, r + c, u, c),
            t.lineTo(l - c, u),
            t.arcTo(l, u, l, u - c, c),
            t.lineTo(l, h),
            t.fill(),
            e.hi)
          ) {
            const r = Math.round(e.Si * n),
              l = h,
              a = Math.round((l + i.T) * s);
            t.fillStyle = e.O;
            const o = Math.max(1, Math.floor(n)),
              _ = Math.floor(0.5 * n);
            t.fillRect(r - _, l, o, a - l);
          }
        }
      ),
        t.useMediaCoordinateSpace(({ context: t }) => {
          const n = f(this.Et),
            e = 0 + i.C + i.T + i.L + i.P / 2;
          (t.font = i.R),
            (t.textAlign = "left"),
            (t.textBaseline = "middle"),
            (t.fillStyle = n.O);
          const r = i.Fi.gi(t, "Apr0");
          t.translate(a + s, e + r), t.fillText(n.Zt, 0, 0);
        });
    }
  }
  class it {
    constructor(t, i, n) {
      (this.ft = !0),
        (this.Wt = new tt()),
        (this.Ft = {
          kt: !1,
          t: "#4c525e",
          O: "white",
          Zt: "",
          ji: 0,
          Si: NaN,
          hi: !0,
        }),
        (this.vt = t),
        (this.Hi = i),
        (this.Ii = n);
    }
    bt() {
      this.ft = !0;
    }
    gt() {
      return (
        this.ft && (this.Mt(), (this.ft = !1)), this.Wt.J(this.Ft), this.Wt
      );
    }
    Mt() {
      const t = this.Ft;
      if (((t.kt = !1), 2 === this.vt.W().mode)) return;
      const i = this.vt.W().vertLine;
      if (!i.labelVisible) return;
      const n = this.Hi.St();
      if (n.Li()) return;
      t.ji = n.ji();
      const s = this.Ii();
      if (null === s) return;
      t.Si = s.Si;
      const e = n.$i(this.vt.xt());
      (t.Zt = n.Ui(f(e))), (t.kt = !0);
      const r = y(i.labelBackgroundColor);
      (t.t = r.t), (t.O = r.i), (t.hi = n.W().ticksVisible);
    }
  }
  class nt {
    constructor() {
      (this.qi = null), (this.Yi = 0);
    }
    Xi() {
      return this.Yi;
    }
    Ki(t) {
      this.Yi = t;
    }
    Dt() {
      return this.qi;
    }
    Zi(t) {
      this.qi = t;
    }
    Gi(t) {
      return [];
    }
    Ji() {
      return [];
    }
    kt() {
      return !0;
    }
  }
  var st;
  !(function (t) {
    (t[(t.Normal = 0)] = "Normal"),
      (t[(t.Magnet = 1)] = "Magnet"),
      (t[(t.Hidden = 2)] = "Hidden");
  })(st || (st = {}));
  class et extends nt {
    constructor(t, i) {
      super(),
        (this.Qi = null),
        (this.tn = NaN),
        (this.nn = 0),
        (this.sn = !0),
        (this.en = new Map()),
        (this.rn = !1),
        (this.hn = NaN),
        (this.ln = NaN),
        (this.an = NaN),
        (this.on = NaN),
        (this.Hi = t),
        (this._n = i),
        (this.un = new j(t, this));
      this.cn = ((t, i) => (n) => {
        const s = i(),
          e = t();
        if (n === f(this.Qi).dn()) return { _t: e, Si: s };
        {
          const t = f(n.Ct());
          return { _t: n.fn(s, t), Si: s };
        }
      })(
        () => this.tn,
        () => this.ln
      );
      const n = ((t, i) => () => {
        const n = this.Hi.St().vn(t()),
          s = i();
        return n && Number.isFinite(s) ? { ot: n, Si: s } : null;
      })(
        () => this.nn,
        () => this.Yt()
      );
      (this.pn = new it(this, t, n)), (this.mn = new $(this));
    }
    W() {
      return this._n;
    }
    bn(t, i) {
      (this.an = t), (this.on = i);
    }
    wn() {
      (this.an = NaN), (this.on = NaN);
    }
    gn() {
      return this.an;
    }
    Mn() {
      return this.on;
    }
    xn(t, i, n) {
      this.rn || (this.rn = !0), (this.sn = !0), this.Sn(t, i, n);
    }
    xt() {
      return this.nn;
    }
    Yt() {
      return this.hn;
    }
    Xt() {
      return this.ln;
    }
    kt() {
      return this.sn;
    }
    yn() {
      (this.sn = !1),
        this.kn(),
        (this.tn = NaN),
        (this.hn = NaN),
        (this.ln = NaN),
        (this.Qi = null),
        this.wn();
    }
    Cn(t) {
      return null !== this.Qi ? [this.mn, this.un] : [];
    }
    Ut(t) {
      return t === this.Qi && this._n.horzLine.visible;
    }
    qt() {
      return this._n.vertLine.visible;
    }
    Tn(t, i) {
      (this.sn && this.Qi === t) || this.en.clear();
      const n = [];
      return this.Qi === t && n.push(this.Pn(this.en, i, this.cn)), n;
    }
    Ji() {
      return this.sn ? [this.pn] : [];
    }
    Ht() {
      return this.Qi;
    }
    Rn() {
      this.mn.bt(), this.en.forEach((t) => t.bt()), this.pn.bt(), this.un.bt();
    }
    Dn(t) {
      return t && !t.dn().Li() ? t.dn() : null;
    }
    Sn(t, i, n) {
      this.On(t, i, n) && this.Rn();
    }
    On(t, i, n) {
      const s = this.hn,
        e = this.ln,
        r = this.tn,
        h = this.nn,
        l = this.Qi,
        a = this.Dn(n);
      (this.nn = t),
        (this.hn = isNaN(t) ? NaN : this.Hi.St().zt(t)),
        (this.Qi = n);
      const o = null !== a ? a.Ct() : null;
      return (
        null !== a && null !== o
          ? ((this.tn = i), (this.ln = a.Rt(i, o)))
          : ((this.tn = NaN), (this.ln = NaN)),
        s !== this.hn ||
          e !== this.ln ||
          h !== this.nn ||
          r !== this.tn ||
          l !== this.Qi
      );
    }
    kn() {
      const t = this.Hi.wt()
          .map((t) => t.An().Bn())
          .filter(B),
        i = 0 === t.length ? null : Math.max(...t);
      this.nn = null !== i ? i : NaN;
    }
    Pn(t, i, n) {
      let s = t.get(i);
      return void 0 === s && ((s = new J(this, i, n)), t.set(i, s)), s;
    }
  }
  function rt(t) {
    return "left" === t || "right" === t;
  }
  class ht {
    constructor(t) {
      (this.Vn = new Map()), (this.zn = []), (this.En = t);
    }
    In(t, i) {
      const n = (function (t, i) {
        return void 0 === t
          ? i
          : { Ln: Math.max(t.Ln, i.Ln), Nn: t.Nn || i.Nn };
      })(this.Vn.get(t), i);
      this.Vn.set(t, n);
    }
    Fn() {
      return this.En;
    }
    Wn(t) {
      const i = this.Vn.get(t);
      return void 0 === i
        ? { Ln: this.En }
        : { Ln: Math.max(this.En, i.Ln), Nn: i.Nn };
    }
    jn() {
      this.Hn(), (this.zn = [{ $n: 0 }]);
    }
    Un(t) {
      this.Hn(), (this.zn = [{ $n: 1, Ot: t }]);
    }
    qn(t) {
      this.Yn(), this.zn.push({ $n: 5, Ot: t });
    }
    Hn() {
      this.Yn(), this.zn.push({ $n: 6 });
    }
    Xn() {
      this.Hn(), (this.zn = [{ $n: 4 }]);
    }
    Kn(t) {
      this.Hn(), this.zn.push({ $n: 2, Ot: t });
    }
    Zn(t) {
      this.Hn(), this.zn.push({ $n: 3, Ot: t });
    }
    Gn() {
      return this.zn;
    }
    Jn(t) {
      for (const i of t.zn) this.Qn(i);
      (this.En = Math.max(this.En, t.En)),
        t.Vn.forEach((t, i) => {
          this.In(i, t);
        });
    }
    static ts() {
      return new ht(2);
    }
    static ns() {
      return new ht(3);
    }
    Qn(t) {
      switch (t.$n) {
        case 0:
          this.jn();
          break;
        case 1:
          this.Un(t.Ot);
          break;
        case 2:
          this.Kn(t.Ot);
          break;
        case 3:
          this.Zn(t.Ot);
          break;
        case 4:
          this.Xn();
          break;
        case 5:
          this.qn(t.Ot);
          break;
        case 6:
          this.Yn();
      }
    }
    Yn() {
      const t = this.zn.findIndex((t) => 5 === t.$n);
      -1 !== t && this.zn.splice(t, 1);
    }
  }
  const lt = ".";
  function at(t, i) {
    if (!T(t)) return "n/a";
    if (!P(i)) throw new TypeError("invalid length");
    if (i < 0 || i > 16) throw new TypeError("invalid length");
    if (0 === i) return t.toString();
    return ("0000000000000000" + t.toString()).slice(-i);
  }
  class ot {
    constructor(t, i) {
      if ((i || (i = 1), (T(t) && P(t)) || (t = 100), t < 0))
        throw new TypeError("invalid base");
      (this.Ei = t), (this.ss = i), this.es();
    }
    format(t) {
      const i = t < 0 ? "−" : "";
      return (t = Math.abs(t)), i + this.rs(t);
    }
    es() {
      if (((this.hs = 0), this.Ei > 0 && this.ss > 0)) {
        let t = this.Ei;
        for (; t > 1; ) (t /= 10), this.hs++;
      }
    }
    rs(t) {
      const i = this.Ei / this.ss;
      let n = Math.floor(t),
        s = "";
      const e = void 0 !== this.hs ? this.hs : NaN;
      if (i > 1) {
        let r = +(Math.round(t * i) - n * i).toFixed(this.hs);
        r >= i && ((r -= i), (n += 1)),
          (s = lt + at(+r.toFixed(this.hs) * this.ss, e));
      } else (n = Math.round(n * i) / i), e > 0 && (s = lt + at(0, e));
      return n.toFixed(0) + s;
    }
  }
  class _t extends ot {
    constructor(t = 100) {
      super(t);
    }
    format(t) {
      return `${super.format(t)}%`;
    }
  }
  class ut {
    constructor(t) {
      this.ls = t;
    }
    format(t) {
      let i = "";
      return (
        t < 0 && ((i = "-"), (t = -t)),
        t < 995
          ? i + this.os(t)
          : t < 999995
          ? i + this.os(t / 1e3) + "K"
          : t < 999999995
          ? ((t = 1e3 * Math.round(t / 1e3)), i + this.os(t / 1e6) + "M")
          : ((t = 1e6 * Math.round(t / 1e6)), i + this.os(t / 1e9) + "B")
      );
    }
    os(t) {
      let i;
      const n = Math.pow(10, this.ls);
      return (
        (i =
          (t = Math.round(t * n) / n) >= 1e-15 && t < 1
            ? t.toFixed(this.ls).replace(/\.?0+$/, "")
            : String(t)),
        i.replace(/(\.[1-9]*)0+$/, (t, i) => i)
      );
    }
  }
  function ct(t, i, n, s, e, r, h) {
    if (0 === i.length || s.from >= i.length || s.to <= 0) return;
    const { context: l, horizontalPixelRatio: a, verticalPixelRatio: o } = t,
      _ = i[s.from];
    let u = r(t, _),
      c = _;
    if (s.to - s.from < 2) {
      const i = e / 2;
      l.beginPath();
      const n = { nt: _.nt - i, st: _.st },
        s = { nt: _.nt + i, st: _.st };
      l.moveTo(n.nt * a, n.st * o), l.lineTo(s.nt * a, s.st * o), h(t, u, n, s);
    } else {
      const e = (i, n) => {
        h(t, u, c, n), l.beginPath(), (u = i), (c = n);
      };
      let d = c;
      l.beginPath(), l.moveTo(_.nt * a, _.st * o);
      for (let h = s.from + 1; h < s.to; ++h) {
        d = i[h];
        const s = r(t, d);
        switch (n) {
          case 0:
            l.lineTo(d.nt * a, d.st * o);
            break;
          case 1:
            l.lineTo(d.nt * a, i[h - 1].st * o),
              s !== u && (e(s, d), l.lineTo(d.nt * a, i[h - 1].st * o)),
              l.lineTo(d.nt * a, d.st * o);
            break;
          case 2: {
            const [t, n] = pt(i, h - 1, h);
            l.bezierCurveTo(
              t.nt * a,
              t.st * o,
              n.nt * a,
              n.st * o,
              d.nt * a,
              d.st * o
            );
            break;
          }
        }
        1 !== n && s !== u && (e(s, d), l.moveTo(d.nt * a, d.st * o));
      }
      (c !== d || (c === d && 1 === n)) && h(t, u, c, d);
    }
  }
  const dt = 6;
  function ft(t, i) {
    return { nt: t.nt - i.nt, st: t.st - i.st };
  }
  function vt(t, i) {
    return { nt: t.nt / i, st: t.st / i };
  }
  function pt(t, i, n) {
    const s = Math.max(0, i - 1),
      e = Math.min(t.length - 1, n + 1);
    var r, h;
    return [
      ((r = t[i]),
      (h = vt(ft(t[n], t[s]), dt)),
      { nt: r.nt + h.nt, st: r.st + h.st }),
      ft(t[n], vt(ft(t[e], t[i]), dt)),
    ];
  }
  function mt(t, i, n, s, e) {
    const { context: r, horizontalPixelRatio: h, verticalPixelRatio: l } = i;
    r.lineTo(e.nt * h, t * l),
      r.lineTo(s.nt * h, t * l),
      r.closePath(),
      (r.fillStyle = n),
      r.fill();
  }
  class bt extends L {
    constructor() {
      super(...arguments), (this.G = null);
    }
    J(t) {
      this.G = t;
    }
    Z(t) {
      var i;
      if (null === this.G) return;
      const { it: n, tt: s, _s: e, et: r, Nt: h, us: l } = this.G,
        a =
          null !== (i = this.G.cs) && void 0 !== i
            ? i
            : this.G.ds
            ? 0
            : t.mediaSize.height;
      if (null === s) return;
      const o = t.context;
      (o.lineCap = "butt"),
        (o.lineJoin = "round"),
        (o.lineWidth = r),
        _(o, h),
        (o.lineWidth = 1),
        ct(t, n, l, s, e, this.fs.bind(this), mt.bind(null, a));
    }
  }
  function wt(t, i, n) {
    return Math.min(Math.max(t, i), n);
  }
  function gt(t, i, n) {
    return i - t <= n;
  }
  function Mt(t) {
    const i = Math.ceil(t);
    return i % 2 == 0 ? i - 1 : i;
  }
  class xt {
    vs(t, i) {
      const n = this.ps,
        { bs: s, ws: e, gs: r, Ms: h, xs: l, cs: a } = i;
      if (
        void 0 === this.Ss ||
        void 0 === n ||
        n.bs !== s ||
        n.ws !== e ||
        n.gs !== r ||
        n.Ms !== h ||
        n.cs !== a ||
        n.xs !== l
      ) {
        const n = t.context.createLinearGradient(0, 0, 0, l);
        if ((n.addColorStop(0, s), null != a)) {
          const i = wt((a * t.verticalPixelRatio) / l, 0, 1);
          n.addColorStop(i, e), n.addColorStop(i, r);
        }
        n.addColorStop(1, h), (this.Ss = n), (this.ps = i);
      }
      return this.Ss;
    }
  }
  class St extends bt {
    constructor() {
      super(...arguments), (this.ys = new xt());
    }
    fs(t, i) {
      return this.ys.vs(t, {
        bs: i.ks,
        ws: "",
        gs: "",
        Ms: i.Cs,
        xs: t.bitmapSize.height,
      });
    }
  }
  function yt(t, i) {
    const n = t.context;
    (n.strokeStyle = i), n.stroke();
  }
  class kt extends L {
    constructor() {
      super(...arguments), (this.G = null);
    }
    J(t) {
      this.G = t;
    }
    Z(t) {
      if (null === this.G) return;
      const { it: i, tt: n, _s: s, us: e, et: r, Nt: h, Ts: l } = this.G;
      if (null === n) return;
      const a = t.context;
      (a.lineCap = "butt"),
        (a.lineWidth = r * t.verticalPixelRatio),
        _(a, h),
        (a.lineJoin = "round");
      const o = this.Ps.bind(this);
      void 0 !== e && ct(t, i, e, n, s, o, yt),
        l &&
          (function (t, i, n, s, e) {
            const {
              horizontalPixelRatio: r,
              verticalPixelRatio: h,
              context: l,
            } = t;
            let a = null;
            const o = (Math.max(1, Math.floor(r)) % 2) / 2,
              _ = n * h + o;
            for (let n = s.to - 1; n >= s.from; --n) {
              const s = i[n];
              if (s) {
                const i = e(t, s);
                i !== a &&
                  (l.beginPath(),
                  null !== a && l.fill(),
                  (l.fillStyle = i),
                  (a = i));
                const n = Math.round(s.nt * r) + o,
                  u = s.st * h;
                l.moveTo(n, u), l.arc(n, u, _, 0, 2 * Math.PI);
              }
            }
            l.fill();
          })(t, i, l, n, o);
    }
  }
  class Ct extends kt {
    Ps(t, i) {
      return i.lt;
    }
  }
  function Tt(t, i, n, s, e = 0, r = i.length) {
    let h = r - e;
    for (; 0 < h; ) {
      const r = h >> 1,
        l = e + r;
      s(i[l], n) === t ? ((e = l + 1), (h -= r + 1)) : (h = r);
    }
    return e;
  }
  const Pt = Tt.bind(null, !0),
    Rt = Tt.bind(null, !1);
  function Dt(t, i) {
    return t.ot < i;
  }
  function Ot(t, i) {
    return i < t.ot;
  }
  function Bt(t, i, n) {
    const s = i.Rs(),
      e = i.ui(),
      r = Pt(t, s, Dt),
      h = Rt(t, e, Ot);
    if (!n) return { from: r, to: h };
    let l = r,
      a = h;
    return (
      r > 0 && r < t.length && t[r].ot >= s && (l = r - 1),
      h > 0 && h < t.length && t[h - 1].ot <= e && (a = h + 1),
      { from: l, to: a }
    );
  }
  class At {
    constructor(t, i, n) {
      (this.Ds = !0),
        (this.Os = !0),
        (this.Bs = !0),
        (this.As = []),
        (this.Vs = null),
        (this.zs = t),
        (this.Es = i),
        (this.Is = n);
    }
    bt(t) {
      (this.Ds = !0),
        "data" === t && (this.Os = !0),
        "options" === t && (this.Bs = !0);
    }
    gt() {
      return this.zs.kt()
        ? (this.Ls(), null === this.Vs ? null : this.Ns)
        : null;
    }
    Fs() {
      this.As = this.As.map((t) =>
        Object.assign(Object.assign({}, t), this.zs.js().Ws(t.ot))
      );
    }
    Hs() {
      this.Vs = null;
    }
    Ls() {
      this.Os && (this.$s(), (this.Os = !1)),
        this.Bs && (this.Fs(), (this.Bs = !1)),
        this.Ds && (this.Us(), (this.Ds = !1));
    }
    Us() {
      const t = this.zs.Dt(),
        i = this.Es.St();
      if ((this.Hs(), i.Li() || t.Li())) return;
      const n = i.qs();
      if (null === n) return;
      if (0 === this.zs.An().Ys()) return;
      const s = this.zs.Ct();
      null !== s &&
        ((this.Vs = Bt(this.As, n, this.Is)), this.Xs(t, i, s.Ot), this.Ks());
    }
  }
  class Vt extends At {
    constructor(t, i) {
      super(t, i, !0);
    }
    Xs(t, i, n) {
      i.Zs(this.As, A(this.Vs)), t.Gs(this.As, n, A(this.Vs));
    }
    Js(t, i) {
      return { ot: t, _t: i, nt: NaN, st: NaN };
    }
    $s() {
      const t = this.zs.js();
      this.As = this.zs
        .An()
        .Qs()
        .map((i) => {
          const n = i.Ot[3];
          return this.te(i.ie, n, t);
        });
    }
  }
  class zt extends Vt {
    constructor(t, i) {
      super(t, i),
        (this.Ns = new I()),
        (this.ne = new St()),
        (this.se = new Ct()),
        this.Ns.X([this.ne, this.se]);
    }
    te(t, i, n) {
      return Object.assign(Object.assign({}, this.Js(t, i)), n.Ws(t));
    }
    Ks() {
      const t = this.zs.W();
      this.ne.J({
        us: t.lineType,
        it: this.As,
        Nt: t.lineStyle,
        et: t.lineWidth,
        cs: null,
        ds: t.invertFilledArea,
        tt: this.Vs,
        _s: this.Es.St().ee(),
      }),
        this.se.J({
          us: t.lineVisible ? t.lineType : void 0,
          it: this.As,
          Nt: t.lineStyle,
          et: t.lineWidth,
          tt: this.Vs,
          _s: this.Es.St().ee(),
          Ts: t.pointMarkersVisible
            ? t.pointMarkersRadius || t.lineWidth / 2 + 2
            : void 0,
        });
    }
  }
  class Et extends L {
    constructor() {
      super(...arguments), (this.Et = null), (this.re = 0), (this.he = 0);
    }
    J(t) {
      this.Et = t;
    }
    Z({ context: t, horizontalPixelRatio: i, verticalPixelRatio: n }) {
      if (null === this.Et || 0 === this.Et.An.length || null === this.Et.tt)
        return;
      if (((this.re = this.le(i)), this.re >= 2)) {
        Math.max(1, Math.floor(i)) % 2 != this.re % 2 && this.re--;
      }
      this.he = this.Et.ae ? Math.min(this.re, Math.floor(i)) : this.re;
      let s = null;
      const e = this.he <= this.re && this.Et.ee >= Math.floor(1.5 * i);
      for (let r = this.Et.tt.from; r < this.Et.tt.to; ++r) {
        const h = this.Et.An[r];
        s !== h.oe && ((t.fillStyle = h.oe), (s = h.oe));
        const l = Math.floor(0.5 * this.he),
          a = Math.round(h.nt * i),
          o = a - l,
          _ = this.he,
          u = o + _ - 1,
          c = Math.min(h._e, h.ue),
          d = Math.max(h._e, h.ue),
          f = Math.round(c * n) - l,
          v = Math.round(d * n) + l,
          p = Math.max(v - f, this.he);
        t.fillRect(o, f, _, p);
        const m = Math.ceil(1.5 * this.re);
        if (e) {
          if (this.Et.ce) {
            const i = a - m;
            let s = Math.max(f, Math.round(h.de * n) - l),
              e = s + _ - 1;
            e > f + p - 1 && ((e = f + p - 1), (s = e - _ + 1)),
              t.fillRect(i, s, o - i, e - s + 1);
          }
          const i = a + m;
          let s = Math.max(f, Math.round(h.fe * n) - l),
            e = s + _ - 1;
          e > f + p - 1 && ((e = f + p - 1), (s = e - _ + 1)),
            t.fillRect(u + 1, s, i - u, e - s + 1);
        }
      }
    }
    le(t) {
      const i = Math.floor(t);
      return Math.max(
        i,
        Math.floor(
          (function (t, i) {
            return Math.floor(0.3 * t * i);
          })(f(this.Et).ee, t)
        )
      );
    }
  }
  class It extends At {
    constructor(t, i) {
      super(t, i, !1);
    }
    Xs(t, i, n) {
      i.Zs(this.As, A(this.Vs)), t.ve(this.As, n, A(this.Vs));
    }
    pe(t, i, n) {
      return {
        ot: t,
        me: i.Ot[0],
        be: i.Ot[1],
        we: i.Ot[2],
        ge: i.Ot[3],
        nt: NaN,
        de: NaN,
        _e: NaN,
        ue: NaN,
        fe: NaN,
      };
    }
    $s() {
      const t = this.zs.js();
      this.As = this.zs
        .An()
        .Qs()
        .map((i) => this.te(i.ie, i, t));
    }
  }
  class Lt extends It {
    constructor() {
      super(...arguments), (this.Ns = new Et());
    }
    te(t, i, n) {
      return Object.assign(Object.assign({}, this.pe(t, i, n)), n.Ws(t));
    }
    Ks() {
      const t = this.zs.W();
      this.Ns.J({
        An: this.As,
        ee: this.Es.St().ee(),
        ce: t.openVisible,
        ae: t.thinBars,
        tt: this.Vs,
      });
    }
  }
  class Nt extends bt {
    constructor() {
      super(...arguments), (this.ys = new xt());
    }
    fs(t, i) {
      const n = this.G;
      return this.ys.vs(t, {
        bs: i.Me,
        ws: i.xe,
        gs: i.Se,
        Ms: i.ye,
        xs: t.bitmapSize.height,
        cs: n.cs,
      });
    }
  }
  class Ft extends kt {
    constructor() {
      super(...arguments), (this.ke = new xt());
    }
    Ps(t, i) {
      const n = this.G;
      return this.ke.vs(t, {
        bs: i.Ce,
        ws: i.Ce,
        gs: i.Te,
        Ms: i.Te,
        xs: t.bitmapSize.height,
        cs: n.cs,
      });
    }
  }
  class Wt extends Vt {
    constructor(t, i) {
      super(t, i),
        (this.Ns = new I()),
        (this.Pe = new Nt()),
        (this.Re = new Ft()),
        this.Ns.X([this.Pe, this.Re]);
    }
    te(t, i, n) {
      return Object.assign(Object.assign({}, this.Js(t, i)), n.Ws(t));
    }
    Ks() {
      const t = this.zs.Ct();
      if (null === t) return;
      const i = this.zs.W(),
        n = this.zs.Dt().Rt(i.baseValue.price, t.Ot),
        s = this.Es.St().ee();
      this.Pe.J({
        it: this.As,
        et: i.lineWidth,
        Nt: i.lineStyle,
        us: i.lineType,
        cs: n,
        ds: !1,
        tt: this.Vs,
        _s: s,
      }),
        this.Re.J({
          it: this.As,
          et: i.lineWidth,
          Nt: i.lineStyle,
          us: i.lineVisible ? i.lineType : void 0,
          Ts: i.pointMarkersVisible
            ? i.pointMarkersRadius || i.lineWidth / 2 + 2
            : void 0,
          cs: n,
          tt: this.Vs,
          _s: s,
        });
    }
  }
  class jt extends L {
    constructor() {
      super(...arguments), (this.Et = null), (this.re = 0);
    }
    J(t) {
      this.Et = t;
    }
    Z(t) {
      if (null === this.Et || 0 === this.Et.An.length || null === this.Et.tt)
        return;
      const { horizontalPixelRatio: i } = t;
      if (
        ((this.re = (function (t, i) {
          if (t >= 2.5 && t <= 4) return Math.floor(3 * i);
          const n = 1 - (0.2 * Math.atan(Math.max(4, t) - 4)) / (0.5 * Math.PI),
            s = Math.floor(t * n * i),
            e = Math.floor(t * i),
            r = Math.min(s, e);
          return Math.max(Math.floor(i), r);
        })(this.Et.ee, i)),
        this.re >= 2)
      ) {
        Math.floor(i) % 2 != this.re % 2 && this.re--;
      }
      const n = this.Et.An;
      this.Et.De && this.Oe(t, n, this.Et.tt),
        this.Et._i && this.Be(t, n, this.Et.tt);
      const s = this.Ae(i);
      (!this.Et._i || this.re > 2 * s) && this.Ve(t, n, this.Et.tt);
    }
    Oe(t, i, n) {
      if (null === this.Et) return;
      const { context: s, horizontalPixelRatio: e, verticalPixelRatio: r } = t;
      let h = "",
        l = Math.min(Math.floor(e), Math.floor(this.Et.ee * e));
      l = Math.max(Math.floor(e), Math.min(l, this.re));
      const a = Math.floor(0.5 * l);
      let o = null;
      for (let t = n.from; t < n.to; t++) {
        const n = i[t];
        n.ze !== h && ((s.fillStyle = n.ze), (h = n.ze));
        const _ = Math.round(Math.min(n.de, n.fe) * r),
          u = Math.round(Math.max(n.de, n.fe) * r),
          c = Math.round(n._e * r),
          d = Math.round(n.ue * r);
        let f = Math.round(e * n.nt) - a;
        const v = f + l - 1;
        null !== o && ((f = Math.max(o + 1, f)), (f = Math.min(f, v)));
        const p = v - f + 1;
        s.fillRect(f, c, p, _ - c), s.fillRect(f, u + 1, p, d - u), (o = v);
      }
    }
    Ae(t) {
      let i = Math.floor(1 * t);
      this.re <= 2 * i && (i = Math.floor(0.5 * (this.re - 1)));
      const n = Math.max(Math.floor(t), i);
      return this.re <= 2 * n ? Math.max(Math.floor(t), Math.floor(1 * t)) : n;
    }
    Be(t, i, n) {
      if (null === this.Et) return;
      const { context: s, horizontalPixelRatio: e, verticalPixelRatio: r } = t;
      let h = "";
      const l = this.Ae(e);
      let a = null;
      for (let t = n.from; t < n.to; t++) {
        const n = i[t];
        n.Ee !== h && ((s.fillStyle = n.Ee), (h = n.Ee));
        let o = Math.round(n.nt * e) - Math.floor(0.5 * this.re);
        const _ = o + this.re - 1,
          u = Math.round(Math.min(n.de, n.fe) * r),
          c = Math.round(Math.max(n.de, n.fe) * r);
        if (
          (null !== a && ((o = Math.max(a + 1, o)), (o = Math.min(o, _))),
          this.Et.ee * e > 2 * l)
        )
          U(s, o, u, _ - o + 1, c - u + 1, l);
        else {
          const t = _ - o + 1;
          s.fillRect(o, u, t, c - u + 1);
        }
        a = _;
      }
    }
    Ve(t, i, n) {
      if (null === this.Et) return;
      const { context: s, horizontalPixelRatio: e, verticalPixelRatio: r } = t;
      let h = "";
      const l = this.Ae(e);
      for (let t = n.from; t < n.to; t++) {
        const n = i[t];
        let a = Math.round(Math.min(n.de, n.fe) * r),
          o = Math.round(Math.max(n.de, n.fe) * r),
          _ = Math.round(n.nt * e) - Math.floor(0.5 * this.re),
          u = _ + this.re - 1;
        if (n.oe !== h) {
          const t = n.oe;
          (s.fillStyle = t), (h = t);
        }
        this.Et._i && ((_ += l), (a += l), (u -= l), (o -= l)),
          a > o || s.fillRect(_, a, u - _ + 1, o - a + 1);
      }
    }
  }
  class Ht extends It {
    constructor() {
      super(...arguments), (this.Ns = new jt());
    }
    te(t, i, n) {
      return Object.assign(Object.assign({}, this.pe(t, i, n)), n.Ws(t));
    }
    Ks() {
      const t = this.zs.W();
      this.Ns.J({
        An: this.As,
        ee: this.Es.St().ee(),
        De: t.wickVisible,
        _i: t.borderVisible,
        tt: this.Vs,
      });
    }
  }
  class $t {
    constructor(t, i) {
      (this.Ie = t), (this.Ei = i);
    }
    K(t, i, n) {
      this.Ie.draw(t, this.Ei, i, n);
    }
  }
  class Ut extends At {
    constructor(t, i, n) {
      super(t, i, !1),
        (this.mn = n),
        (this.Ns = new $t(this.mn.renderer(), (i) => {
          const n = t.Ct();
          return null === n ? null : t.Dt().Rt(i, n.Ot);
        }));
    }
    Le(t) {
      return this.mn.priceValueBuilder(t);
    }
    Ne(t) {
      return this.mn.isWhitespace(t);
    }
    $s() {
      const t = this.zs.js();
      this.As = this.zs
        .An()
        .Qs()
        .map((i) =>
          Object.assign(Object.assign({ ot: i.ie, nt: NaN }, t.Ws(i.ie)), {
            Fe: i.We,
          })
        );
    }
    Xs(t, i) {
      i.Zs(this.As, A(this.Vs));
    }
    Ks() {
      this.mn.update(
        {
          bars: this.As.map(qt),
          barSpacing: this.Es.St().ee(),
          visibleRange: this.Vs,
        },
        this.zs.W()
      );
    }
  }
  function qt(t) {
    return { x: t.nt, time: t.ot, originalData: t.Fe, barColor: t.oe };
  }
  class Yt extends L {
    constructor() {
      super(...arguments), (this.Et = null), (this.je = []);
    }
    J(t) {
      (this.Et = t), (this.je = []);
    }
    Z({ context: t, horizontalPixelRatio: i, verticalPixelRatio: n }) {
      if (null === this.Et || 0 === this.Et.it.length || null === this.Et.tt)
        return;
      this.je.length || this.He(i);
      const s = Math.max(1, Math.floor(n)),
        e = Math.round(this.Et.$e * n) - Math.floor(s / 2),
        r = e + s;
      for (let i = this.Et.tt.from; i < this.Et.tt.to; i++) {
        const h = this.Et.it[i],
          l = this.je[i - this.Et.tt.from],
          a = Math.round(h.st * n);
        let o, _;
        (t.fillStyle = h.oe),
          a <= e
            ? ((o = a), (_ = r))
            : ((o = e), (_ = a - Math.floor(s / 2) + s)),
          t.fillRect(l.Rs, o, l.ui - l.Rs + 1, _ - o);
      }
    }
    He(t) {
      if (null === this.Et || 0 === this.Et.it.length || null === this.Et.tt)
        return void (this.je = []);
      const i = Math.ceil(this.Et.ee * t) <= 1 ? 0 : Math.max(1, Math.floor(t)),
        n = Math.round(this.Et.ee * t) - i;
      this.je = new Array(this.Et.tt.to - this.Et.tt.from);
      for (let i = this.Et.tt.from; i < this.Et.tt.to; i++) {
        const s = this.Et.it[i],
          e = Math.round(s.nt * t);
        let r, h;
        if (n % 2) {
          const t = (n - 1) / 2;
          (r = e - t), (h = e + t);
        } else {
          const t = n / 2;
          (r = e - t), (h = e + t - 1);
        }
        this.je[i - this.Et.tt.from] = {
          Rs: r,
          ui: h,
          Ue: e,
          qe: s.nt * t,
          ot: s.ot,
        };
      }
      for (let t = this.Et.tt.from + 1; t < this.Et.tt.to; t++) {
        const n = this.je[t - this.Et.tt.from],
          s = this.je[t - this.Et.tt.from - 1];
        n.ot === s.ot + 1 &&
          n.Rs - s.ui !== i + 1 &&
          (s.Ue > s.qe ? (s.ui = n.Rs - i - 1) : (n.Rs = s.ui + i + 1));
      }
      let s = Math.ceil(this.Et.ee * t);
      for (let t = this.Et.tt.from; t < this.Et.tt.to; t++) {
        const i = this.je[t - this.Et.tt.from];
        i.ui < i.Rs && (i.ui = i.Rs);
        const n = i.ui - i.Rs + 1;
        s = Math.min(n, s);
      }
      if (i > 0 && s < 4)
        for (let t = this.Et.tt.from; t < this.Et.tt.to; t++) {
          const i = this.je[t - this.Et.tt.from];
          i.ui - i.Rs + 1 > s && (i.Ue > i.qe ? (i.ui -= 1) : (i.Rs += 1));
        }
    }
  }
  class Xt extends Vt {
    constructor() {
      super(...arguments), (this.Ns = new Yt());
    }
    te(t, i, n) {
      return Object.assign(Object.assign({}, this.Js(t, i)), n.Ws(t));
    }
    Ks() {
      const t = {
        it: this.As,
        ee: this.Es.St().ee(),
        tt: this.Vs,
        $e: this.zs.Dt().Rt(this.zs.W().base, f(this.zs.Ct()).Ot),
      };
      this.Ns.J(t);
    }
  }
  class Kt extends Vt {
    constructor() {
      super(...arguments), (this.Ns = new Ct());
    }
    te(t, i, n) {
      return Object.assign(Object.assign({}, this.Js(t, i)), n.Ws(t));
    }
    Ks() {
      const t = this.zs.W(),
        i = {
          it: this.As,
          Nt: t.lineStyle,
          us: t.lineVisible ? t.lineType : void 0,
          et: t.lineWidth,
          Ts: t.pointMarkersVisible
            ? t.pointMarkersRadius || t.lineWidth / 2 + 2
            : void 0,
          tt: this.Vs,
          _s: this.Es.St().ee(),
        };
      this.Ns.J(i);
    }
  }
  const Zt = /[2-9]/g;
  class Gt {
    constructor(t = 50) {
      (this.Ye = 0),
        (this.Xe = 1),
        (this.Ke = 1),
        (this.Ze = {}),
        (this.Ge = new Map()),
        (this.Je = t);
    }
    Qe() {
      (this.Ye = 0),
        this.Ge.clear(),
        (this.Xe = 1),
        (this.Ke = 1),
        (this.Ze = {});
    }
    Mi(t, i, n) {
      return this.tr(t, i, n).width;
    }
    gi(t, i, n) {
      const s = this.tr(t, i, n);
      return (
        ((s.actualBoundingBoxAscent || 0) - (s.actualBoundingBoxDescent || 0)) /
        2
      );
    }
    tr(t, i, n) {
      const s = n || Zt,
        e = String(i).replace(s, "0");
      if (this.Ge.has(e)) return d(this.Ge.get(e)).ir;
      if (this.Ye === this.Je) {
        const t = this.Ze[this.Ke];
        delete this.Ze[this.Ke], this.Ge.delete(t), this.Ke++, this.Ye--;
      }
      t.save(), (t.textBaseline = "middle");
      const r = t.measureText(e);
      return (
        t.restore(),
        (0 === r.width && i.length) ||
          (this.Ge.set(e, { ir: r, nr: this.Xe }),
          (this.Ze[this.Xe] = e),
          this.Ye++,
          this.Xe++),
        r
      );
    }
  }
  class Jt {
    constructor(t) {
      (this.sr = null), (this.k = null), (this.er = "right"), (this.rr = t);
    }
    hr(t, i, n) {
      (this.sr = t), (this.k = i), (this.er = n);
    }
    K(t) {
      null !== this.k &&
        null !== this.sr &&
        this.sr.K(t, this.k, this.rr, this.er);
    }
  }
  class Qt {
    constructor(t, i, n) {
      (this.lr = t),
        (this.rr = new Gt(50)),
        (this.ar = i),
        (this.F = n),
        (this.j = -1),
        (this.Wt = new Jt(this.rr));
    }
    gt() {
      const t = this.F._r(this.ar);
      if (null === t) return null;
      const i = t.ur(this.ar) ? t.cr() : this.ar.Dt();
      if (null === i) return null;
      const n = t.dr(i);
      if ("overlay" === n) return null;
      const s = this.F.vr();
      return (
        s.P !== this.j && ((this.j = s.P), this.rr.Qe()),
        this.Wt.hr(this.lr.Vi(), s, n),
        this.Wt
      );
    }
  }
  class ti extends L {
    constructor() {
      super(...arguments), (this.Et = null);
    }
    J(t) {
      this.Et = t;
    }
    pr(t, i) {
      var n;
      if (!(null === (n = this.Et) || void 0 === n ? void 0 : n.kt))
        return null;
      const { st: s, et: e, mr: r } = this.Et;
      return i >= s - e - 7 && i <= s + e + 7 ? { br: this.Et, mr: r } : null;
    }
    Z({
      context: t,
      bitmapSize: i,
      horizontalPixelRatio: n,
      verticalPixelRatio: s,
    }) {
      if (null === this.Et) return;
      if (!1 === this.Et.kt) return;
      const e = Math.round(this.Et.st * s);
      e < 0 ||
        e > i.height ||
        ((t.lineCap = "butt"),
        (t.strokeStyle = this.Et.O),
        (t.lineWidth = Math.floor(this.Et.et * n)),
        _(t, this.Et.Nt),
        u(t, e, 0, i.width));
    }
  }
  class ii {
    constructor(t) {
      (this.wr = { st: 0, O: "rgba(0, 0, 0, 0)", et: 1, Nt: 0, kt: !1 }),
        (this.gr = new ti()),
        (this.ft = !0),
        (this.zs = t),
        (this.Es = t.$t()),
        this.gr.J(this.wr);
    }
    bt() {
      this.ft = !0;
    }
    gt() {
      return this.zs.kt()
        ? (this.ft && (this.Mr(), (this.ft = !1)), this.gr)
        : null;
    }
  }
  class ni extends ii {
    constructor(t) {
      super(t);
    }
    Mr() {
      this.wr.kt = !1;
      const t = this.zs.Dt(),
        i = t.Sr().Sr;
      if (2 !== i && 3 !== i) return;
      const n = this.zs.W();
      if (!n.baseLineVisible || !this.zs.kt()) return;
      const s = this.zs.Ct();
      null !== s &&
        ((this.wr.kt = !0),
        (this.wr.st = t.Rt(s.Ot, s.Ot)),
        (this.wr.O = n.baseLineColor),
        (this.wr.et = n.baseLineWidth),
        (this.wr.Nt = n.baseLineStyle));
    }
  }
  class si extends L {
    constructor() {
      super(...arguments), (this.Et = null);
    }
    J(t) {
      this.Et = t;
    }
    We() {
      return this.Et;
    }
    Z({ context: t, horizontalPixelRatio: i, verticalPixelRatio: n }) {
      const s = this.Et;
      if (null === s) return;
      const e = Math.max(1, Math.floor(i)),
        r = (e % 2) / 2,
        h = Math.round(s.qe.x * i) + r,
        l = s.qe.y * n;
      (t.fillStyle = s.yr), t.beginPath();
      const a = Math.max(2, 1.5 * s.kr) * i;
      t.arc(h, l, a, 0, 2 * Math.PI, !1),
        t.fill(),
        (t.fillStyle = s.Cr),
        t.beginPath(),
        t.arc(h, l, s.ht * i, 0, 2 * Math.PI, !1),
        t.fill(),
        (t.lineWidth = e),
        (t.strokeStyle = s.Tr),
        t.beginPath(),
        t.arc(h, l, s.ht * i + e / 2, 0, 2 * Math.PI, !1),
        t.stroke();
    }
  }
  const ei = [
    { Pr: 0, Rr: 0.25, Dr: 4, Or: 10, Br: 0.25, Ar: 0, Vr: 0.4, zr: 0.8 },
    { Pr: 0.25, Rr: 0.525, Dr: 10, Or: 14, Br: 0, Ar: 0, Vr: 0.8, zr: 0 },
    { Pr: 0.525, Rr: 1, Dr: 14, Or: 14, Br: 0, Ar: 0, Vr: 0, zr: 0 },
  ];
  function ri(t, i, n, s) {
    return (function (t, i) {
      if ("transparent" === t) return t;
      const n = S(t),
        s = n[3];
      return `rgba(${n[0]}, ${n[1]}, ${n[2]}, ${i * s})`;
    })(t, n + (s - n) * i);
  }
  function hi(t, i) {
    const n = (t % 2600) / 2600;
    let s;
    for (const t of ei)
      if (n >= t.Pr && n <= t.Rr) {
        s = t;
        break;
      }
    c(void 0 !== s, "Last price animation internal logic error");
    const e = (n - s.Pr) / (s.Rr - s.Pr);
    return {
      Cr: ri(i, e, s.Br, s.Ar),
      Tr: ri(i, e, s.Vr, s.zr),
      ht: ((r = e), (h = s.Dr), (l = s.Or), h + (l - h) * r),
    };
    var r, h, l;
  }
  class li {
    constructor(t) {
      (this.Wt = new si()),
        (this.ft = !0),
        (this.Er = !0),
        (this.Ir = performance.now()),
        (this.Lr = this.Ir - 1),
        (this.Nr = t);
    }
    Fr() {
      (this.Lr = this.Ir - 1), this.bt();
    }
    Wr() {
      if ((this.bt(), 2 === this.Nr.W().lastPriceAnimation)) {
        const t = performance.now(),
          i = this.Lr - t;
        if (i > 0) return void (i < 650 && (this.Lr += 2600));
        (this.Ir = t), (this.Lr = t + 2600);
      }
    }
    bt() {
      this.ft = !0;
    }
    jr() {
      this.Er = !0;
    }
    kt() {
      return 0 !== this.Nr.W().lastPriceAnimation;
    }
    Hr() {
      switch (this.Nr.W().lastPriceAnimation) {
        case 0:
          return !1;
        case 1:
          return !0;
        case 2:
          return performance.now() <= this.Lr;
      }
    }
    gt() {
      return (
        this.ft
          ? (this.Mt(), (this.ft = !1), (this.Er = !1))
          : this.Er && (this.$r(), (this.Er = !1)),
        this.Wt
      );
    }
    Mt() {
      this.Wt.J(null);
      const t = this.Nr.$t().St(),
        i = t.qs(),
        n = this.Nr.Ct();
      if (null === i || null === n) return;
      const s = this.Nr.Ur(!0);
      if (s.qr || !i.Yr(s.ie)) return;
      const e = { x: t.zt(s.ie), y: this.Nr.Dt().Rt(s._t, n.Ot) },
        r = s.O,
        h = this.Nr.W().lineWidth,
        l = hi(this.Xr(), r);
      this.Wt.J({ yr: r, kr: h, Cr: l.Cr, Tr: l.Tr, ht: l.ht, qe: e });
    }
    $r() {
      const t = this.Wt.We();
      if (null !== t) {
        const i = hi(this.Xr(), t.yr);
        (t.Cr = i.Cr), (t.Tr = i.Tr), (t.ht = i.ht);
      }
    }
    Xr() {
      return this.Hr() ? performance.now() - this.Ir : 2599;
    }
  }
  function ai(t, i) {
    return Mt(Math.min(Math.max(t, 12), 30) * i);
  }
  function oi(t, i) {
    switch (t) {
      case "arrowDown":
      case "arrowUp":
        return ai(i, 1);
      case "circle":
        return ai(i, 0.8);
      case "square":
        return ai(i, 0.7);
    }
  }
  function _i(t) {
    return (function (t) {
      const i = Math.ceil(t);
      return i % 2 != 0 ? i - 1 : i;
    })(ai(t, 1));
  }
  function ui(t) {
    return Math.max(ai(t, 0.1), 3);
  }
  function ci(t, i, n) {
    return i ? t : n ? Math.ceil(t / 2) : 0;
  }
  function di(t, i, n, s, e) {
    const r = oi("square", n),
      h = (r - 1) / 2,
      l = t - h,
      a = i - h;
    return s >= l && s <= l + r && e >= a && e <= a + r;
  }
  function fi(t, i, n, s) {
    const e = ((oi("arrowUp", s) - 1) / 2) * n.Kr,
      r = ((Mt(s / 2) - 1) / 2) * n.Kr;
    i.beginPath(),
      t
        ? (i.moveTo(n.nt - e, n.st),
          i.lineTo(n.nt, n.st - e),
          i.lineTo(n.nt + e, n.st),
          i.lineTo(n.nt + r, n.st),
          i.lineTo(n.nt + r, n.st + e),
          i.lineTo(n.nt - r, n.st + e),
          i.lineTo(n.nt - r, n.st))
        : (i.moveTo(n.nt - e, n.st),
          i.lineTo(n.nt, n.st + e),
          i.lineTo(n.nt + e, n.st),
          i.lineTo(n.nt + r, n.st),
          i.lineTo(n.nt + r, n.st - e),
          i.lineTo(n.nt - r, n.st - e),
          i.lineTo(n.nt - r, n.st)),
      i.fill();
  }
  function vi(t, i, n, s, e, r) {
    return di(i, n, s, e, r);
  }
  class pi extends L {
    constructor() {
      super(...arguments),
        (this.Et = null),
        (this.rr = new Gt()),
        (this.j = -1),
        (this.H = ""),
        (this.Zr = "");
    }
    J(t) {
      this.Et = t;
    }
    hr(t, i) {
      (this.j === t && this.H === i) ||
        ((this.j = t), (this.H = i), (this.Zr = z(t, i)), this.rr.Qe());
    }
    pr(t, i) {
      if (null === this.Et || null === this.Et.tt) return null;
      for (let n = this.Et.tt.from; n < this.Et.tt.to; n++) {
        const s = this.Et.it[n];
        if (bi(s, t, i)) return { br: s.Gr, mr: s.mr };
      }
      return null;
    }
    Z({ context: t, horizontalPixelRatio: i, verticalPixelRatio: n }, s, e) {
      if (null !== this.Et && null !== this.Et.tt) {
        (t.textBaseline = "middle"), (t.font = this.Zr);
        for (let s = this.Et.tt.from; s < this.Et.tt.to; s++) {
          const e = this.Et.it[s];
          void 0 !== e.Zt &&
            ((e.Zt.ji = this.rr.Mi(t, e.Zt.Jr)),
            (e.Zt.Vt = this.j),
            (e.Zt.nt = e.nt - e.Zt.ji / 2)),
            mi(e, t, i, n);
        }
      }
    }
  }
  function mi(t, i, n, s) {
    (i.fillStyle = t.O),
      void 0 !== t.Zt &&
        (function (t, i, n, s, e, r) {
          t.save(), t.scale(e, r), t.fillText(i, n, s), t.restore();
        })(i, t.Zt.Jr, t.Zt.nt, t.Zt.st, n, s),
      (function (t, i, n) {
        if (0 === t.Ys) return;
        switch (t.Qr) {
          case "arrowDown":
            return void fi(!1, i, n, t.Ys);
          case "arrowUp":
            return void fi(!0, i, n, t.Ys);
          case "circle":
            return void (function (t, i, n) {
              const s = (oi("circle", n) - 1) / 2;
              t.beginPath(),
                t.arc(i.nt, i.st, s * i.Kr, 0, 2 * Math.PI, !1),
                t.fill();
            })(i, n, t.Ys);
          case "square":
            return void (function (t, i, n) {
              const s = oi("square", n),
                e = ((s - 1) * i.Kr) / 2,
                r = i.nt - e,
                h = i.st - e;
              t.fillRect(r, h, s * i.Kr, s * i.Kr);
            })(i, n, t.Ys);
        }
        t.Qr;
      })(
        t,
        i,
        (function (t, i, n) {
          const s = (Math.max(1, Math.floor(i)) % 2) / 2;
          return { nt: Math.round(t.nt * i) + s, st: t.st * n, Kr: i };
        })(t, n, s)
      );
  }
  function bi(t, i, n) {
    return (
      !(
        void 0 === t.Zt ||
        !(function (t, i, n, s, e, r) {
          const h = s / 2;
          return e >= t && e <= t + n && r >= i - h && r <= i + h;
        })(t.Zt.nt, t.Zt.st, t.Zt.ji, t.Zt.Vt, i, n)
      ) ||
      (function (t, i, n) {
        if (0 === t.Ys) return !1;
        switch (t.Qr) {
          case "arrowDown":
          case "arrowUp":
            return vi(0, t.nt, t.st, t.Ys, i, n);
          case "circle":
            return (function (t, i, n, s, e) {
              const r = 2 + oi("circle", n) / 2,
                h = t - s,
                l = i - e;
              return Math.sqrt(h * h + l * l) <= r;
            })(t.nt, t.st, t.Ys, i, n);
          case "square":
            return di(t.nt, t.st, t.Ys, i, n);
        }
      })(t, i, n)
    );
  }
  function wi(t, i, n, s, e, r, h, l, a) {
    const o = T(n) ? n : n.ge,
      _ = T(n) ? n : n.be,
      u = T(n) ? n : n.we,
      c = T(i.size) ? Math.max(i.size, 0) : 1,
      d = _i(l.ee()) * c,
      f = d / 2;
    switch (((t.Ys = d), i.position)) {
      case "inBar":
        return (
          (t.st = h.Rt(o, a)),
          void (void 0 !== t.Zt && (t.Zt.st = t.st + f + r + 0.6 * e))
        );
      case "aboveBar":
        return (
          (t.st = h.Rt(_, a) - f - s.th),
          void 0 !== t.Zt &&
            ((t.Zt.st = t.st - f - 0.6 * e), (s.th += 1.2 * e)),
          void (s.th += d + r)
        );
      case "belowBar":
        return (
          (t.st = h.Rt(u, a) + f + s.ih),
          void 0 !== t.Zt &&
            ((t.Zt.st = t.st + f + r + 0.6 * e), (s.ih += 1.2 * e)),
          void (s.ih += d + r)
        );
    }
    i.position;
  }
  class gi {
    constructor(t, i) {
      (this.ft = !0),
        (this.nh = !0),
        (this.sh = !0),
        (this.eh = null),
        (this.rh = null),
        (this.Wt = new pi()),
        (this.Nr = t),
        (this.Hi = i),
        (this.Et = { it: [], tt: null });
    }
    bt(t) {
      (this.ft = !0),
        (this.sh = !0),
        "data" === t && ((this.nh = !0), (this.rh = null));
    }
    gt(t) {
      if (!this.Nr.kt()) return null;
      this.ft && this.hh();
      const i = this.Hi.W().layout;
      return this.Wt.hr(i.fontSize, i.fontFamily), this.Wt.J(this.Et), this.Wt;
    }
    lh() {
      if (this.sh) {
        if (this.Nr.ah().length > 0) {
          const t = this.Hi.St().ee(),
            i = ui(t),
            n = 1.5 * _i(t) + 2 * i,
            s = this.oh();
          this.eh = {
            above: ci(n, s.aboveBar, s.inBar),
            below: ci(n, s.belowBar, s.inBar),
          };
        } else this.eh = null;
        this.sh = !1;
      }
      return this.eh;
    }
    oh() {
      return (
        null === this.rh &&
          (this.rh = this.Nr.ah().reduce(
            (t, i) => (t[i.position] || (t[i.position] = !0), t),
            { inBar: !1, aboveBar: !1, belowBar: !1 }
          )),
        this.rh
      );
    }
    hh() {
      const t = this.Nr.Dt(),
        i = this.Hi.St(),
        n = this.Nr.ah();
      this.nh &&
        ((this.Et.it = n.map((t) => ({
          ot: t.time,
          nt: 0,
          st: 0,
          Ys: 0,
          Qr: t.shape,
          O: t.color,
          Gr: t.Gr,
          mr: t.id,
          Zt: void 0,
        }))),
        (this.nh = !1));
      const s = this.Hi.W().layout;
      this.Et.tt = null;
      const e = i.qs();
      if (null === e) return;
      const r = this.Nr.Ct();
      if (null === r) return;
      if (0 === this.Et.it.length) return;
      let h = NaN;
      const l = ui(i.ee()),
        a = { th: l, ih: l };
      this.Et.tt = Bt(this.Et.it, e, !0);
      for (let e = this.Et.tt.from; e < this.Et.tt.to; e++) {
        const o = n[e];
        o.time !== h && ((a.th = l), (a.ih = l), (h = o.time));
        const _ = this.Et.it[e];
        (_.nt = i.zt(o.time)),
          void 0 !== o.text &&
            o.text.length > 0 &&
            (_.Zt = { Jr: o.text, nt: 0, st: 0, ji: 0, Vt: 0 });
        const u = this.Nr._h(o.time);
        null !== u && wi(_, o, u, a, s.fontSize, l, t, i, r.Ot);
      }
      this.ft = !1;
    }
  }
  class Mi extends ii {
    constructor(t) {
      super(t);
    }
    Mr() {
      const t = this.wr;
      t.kt = !1;
      const i = this.zs.W();
      if (!i.priceLineVisible || !this.zs.kt()) return;
      const n = this.zs.Ur(0 === i.priceLineSource);
      n.qr ||
        ((t.kt = !0),
        (t.st = n.Si),
        (t.O = this.zs.uh(n.O)),
        (t.et = i.priceLineWidth),
        (t.Nt = i.priceLineStyle));
    }
  }
  class xi extends G {
    constructor(t) {
      super(), (this.jt = t);
    }
    zi(t, i, n) {
      (t.kt = !1), (i.kt = !1);
      const s = this.jt;
      if (!s.kt()) return;
      const e = s.W(),
        r = e.lastValueVisible,
        h = "" !== s.dh(),
        l = 0 === e.seriesLastValueMode,
        a = s.Ur(!1);
      if (a.qr) return;
      r && ((t.Zt = this.fh(a, r, l)), (t.kt = 0 !== t.Zt.length)),
        (h || l) && ((i.Zt = this.ph(a, r, h, l)), (i.kt = i.Zt.length > 0));
      const o = s.uh(a.O),
        _ = y(o);
      (n.t = _.t),
        (n.Si = a.Si),
        (i.Bt = s.$t().At(a.Si / s.Dt().Vt())),
        (t.Bt = o),
        (t.O = _.i),
        (i.O = _.i);
    }
    ph(t, i, n, s) {
      let e = "";
      const r = this.jt.dh();
      return (
        n && 0 !== r.length && (e += `${r} `),
        i && s && (e += this.jt.Dt().mh() ? t.bh : t.wh),
        e.trim()
      );
    }
    fh(t, i, n) {
      return i ? (n ? (this.jt.Dt().mh() ? t.wh : t.bh) : t.Zt) : "";
    }
  }
  function Si(t, i, n, s) {
    const e = Number.isFinite(i),
      r = Number.isFinite(n);
    return e && r ? t(i, n) : e || r ? (e ? i : n) : s;
  }
  class yi {
    constructor(t, i) {
      (this.gh = t), (this.Mh = i);
    }
    xh(t) {
      return null !== t && this.gh === t.gh && this.Mh === t.Mh;
    }
    Sh() {
      return new yi(this.gh, this.Mh);
    }
    yh() {
      return this.gh;
    }
    kh() {
      return this.Mh;
    }
    Ch() {
      return this.Mh - this.gh;
    }
    Li() {
      return (
        this.Mh === this.gh || Number.isNaN(this.Mh) || Number.isNaN(this.gh)
      );
    }
    Jn(t) {
      return null === t
        ? this
        : new yi(
            Si(Math.min, this.yh(), t.yh(), -1 / 0),
            Si(Math.max, this.kh(), t.kh(), 1 / 0)
          );
    }
    Th(t) {
      if (!T(t)) return;
      if (0 === this.Mh - this.gh) return;
      const i = 0.5 * (this.Mh + this.gh);
      let n = this.Mh - i,
        s = this.gh - i;
      (n *= t), (s *= t), (this.Mh = i + n), (this.gh = i + s);
    }
    Ph(t) {
      T(t) && ((this.Mh += t), (this.gh += t));
    }
    Rh() {
      return { minValue: this.gh, maxValue: this.Mh };
    }
    static Dh(t) {
      return null === t ? null : new yi(t.minValue, t.maxValue);
    }
  }
  class ki {
    constructor(t, i) {
      (this.Oh = t), (this.Bh = i || null);
    }
    Ah() {
      return this.Oh;
    }
    Vh() {
      return this.Bh;
    }
    Rh() {
      return null === this.Oh
        ? null
        : { priceRange: this.Oh.Rh(), margins: this.Bh || void 0 };
    }
    static Dh(t) {
      return null === t ? null : new ki(yi.Dh(t.priceRange), t.margins);
    }
  }
  class Ci extends ii {
    constructor(t, i) {
      super(t), (this.zh = i);
    }
    Mr() {
      const t = this.wr;
      t.kt = !1;
      const i = this.zh.W();
      if (!this.zs.kt() || !i.lineVisible) return;
      const n = this.zh.Eh();
      null !== n &&
        ((t.kt = !0),
        (t.st = n),
        (t.O = i.color),
        (t.et = i.lineWidth),
        (t.Nt = i.lineStyle),
        (t.mr = this.zh.W().id));
    }
  }
  class Ti extends G {
    constructor(t, i) {
      super(), (this.Nr = t), (this.zh = i);
    }
    zi(t, i, n) {
      (t.kt = !1), (i.kt = !1);
      const s = this.zh.W(),
        e = s.axisLabelVisible,
        r = "" !== s.title,
        h = this.Nr;
      if (!e || !h.kt()) return;
      const l = this.zh.Eh();
      if (null === l) return;
      r && ((i.Zt = s.title), (i.kt = !0)),
        (i.Bt = h.$t().At(l / h.Dt().Vt())),
        (t.Zt = this.Ih(s.price)),
        (t.kt = !0);
      const a = y(s.axisLabelColor || s.color);
      n.t = a.t;
      const o = s.axisLabelTextColor || a.i;
      (t.O = o), (i.O = o), (n.Si = l);
    }
    Ih(t) {
      const i = this.Nr.Ct();
      return null === i ? "" : this.Nr.Dt().Ni(t, i.Ot);
    }
  }
  class Pi {
    constructor(t, i) {
      (this.Nr = t),
        (this._n = i),
        (this.Lh = new Ci(t, this)),
        (this.lr = new Ti(t, this)),
        (this.Nh = new Qt(this.lr, t, t.$t()));
    }
    Fh(t) {
      C(this._n, t), this.bt(), this.Nr.$t().Wh();
    }
    W() {
      return this._n;
    }
    jh() {
      return this.Lh;
    }
    Hh() {
      return this.Nh;
    }
    $h() {
      return this.lr;
    }
    bt() {
      this.Lh.bt(), this.lr.bt();
    }
    Eh() {
      const t = this.Nr,
        i = t.Dt();
      if (t.$t().St().Li() || i.Li()) return null;
      const n = t.Ct();
      return null === n ? null : i.Rt(this._n.price, n.Ot);
    }
  }
  class Ri extends nt {
    constructor(t) {
      super(), (this.Hi = t);
    }
    $t() {
      return this.Hi;
    }
  }
  const Di = {
    Bar: (t, i, n, s) => {
      var e;
      const r = i.upColor,
        h = i.downColor,
        l = f(t(n, s)),
        a = v(l.Ot[0]) <= v(l.Ot[3]);
      return { oe: null !== (e = l.O) && void 0 !== e ? e : a ? r : h };
    },
    Candlestick: (t, i, n, s) => {
      var e, r, h;
      const l = i.upColor,
        a = i.downColor,
        o = i.borderUpColor,
        _ = i.borderDownColor,
        u = i.wickUpColor,
        c = i.wickDownColor,
        d = f(t(n, s)),
        p = v(d.Ot[0]) <= v(d.Ot[3]);
      return {
        oe: null !== (e = d.O) && void 0 !== e ? e : p ? l : a,
        Ee: null !== (r = d.Bt) && void 0 !== r ? r : p ? o : _,
        ze: null !== (h = d.Uh) && void 0 !== h ? h : p ? u : c,
      };
    },
    Custom: (t, i, n, s) => {
      var e;
      return { oe: null !== (e = f(t(n, s)).O) && void 0 !== e ? e : i.color };
    },
    Area: (t, i, n, s) => {
      var e, r, h, l;
      const a = f(t(n, s));
      return {
        oe: null !== (e = a.lt) && void 0 !== e ? e : i.lineColor,
        lt: null !== (r = a.lt) && void 0 !== r ? r : i.lineColor,
        ks: null !== (h = a.ks) && void 0 !== h ? h : i.topColor,
        Cs: null !== (l = a.Cs) && void 0 !== l ? l : i.bottomColor,
      };
    },
    Baseline: (t, i, n, s) => {
      var e, r, h, l, a, o;
      const _ = f(t(n, s));
      return {
        oe: _.Ot[3] >= i.baseValue.price ? i.topLineColor : i.bottomLineColor,
        Ce: null !== (e = _.Ce) && void 0 !== e ? e : i.topLineColor,
        Te: null !== (r = _.Te) && void 0 !== r ? r : i.bottomLineColor,
        Me: null !== (h = _.Me) && void 0 !== h ? h : i.topFillColor1,
        xe: null !== (l = _.xe) && void 0 !== l ? l : i.topFillColor2,
        Se: null !== (a = _.Se) && void 0 !== a ? a : i.bottomFillColor1,
        ye: null !== (o = _.ye) && void 0 !== o ? o : i.bottomFillColor2,
      };
    },
    Line: (t, i, n, s) => {
      var e, r;
      const h = f(t(n, s));
      return {
        oe: null !== (e = h.O) && void 0 !== e ? e : i.color,
        lt: null !== (r = h.O) && void 0 !== r ? r : i.color,
      };
    },
    Histogram: (t, i, n, s) => {
      var e;
      return { oe: null !== (e = f(t(n, s)).O) && void 0 !== e ? e : i.color };
    },
  };
  class Oi {
    constructor(t) {
      (this.qh = (t, i) => (void 0 !== i ? i.Ot : this.Nr.An().Yh(t))),
        (this.Nr = t),
        (this.Xh = Di[t.Kh()]);
    }
    Ws(t, i) {
      return this.Xh(this.qh, this.Nr.W(), t, i);
    }
  }
  var Bi;
  !(function (t) {
    (t[(t.NearestLeft = -1)] = "NearestLeft"),
      (t[(t.None = 0)] = "None"),
      (t[(t.NearestRight = 1)] = "NearestRight");
  })(Bi || (Bi = {}));
  const Ai = 30;
  class Vi {
    constructor() {
      (this.Zh = []), (this.Gh = new Map()), (this.Jh = new Map());
    }
    Qh() {
      return this.Ys() > 0 ? this.Zh[this.Zh.length - 1] : null;
    }
    tl() {
      return this.Ys() > 0 ? this.il(0) : null;
    }
    Bn() {
      return this.Ys() > 0 ? this.il(this.Zh.length - 1) : null;
    }
    Ys() {
      return this.Zh.length;
    }
    Li() {
      return 0 === this.Ys();
    }
    Yr(t) {
      return null !== this.nl(t, 0);
    }
    Yh(t) {
      return this.sl(t);
    }
    sl(t, i = 0) {
      const n = this.nl(t, i);
      return null === n
        ? null
        : Object.assign(Object.assign({}, this.el(n)), { ie: this.il(n) });
    }
    Qs() {
      return this.Zh;
    }
    rl(t, i, n) {
      if (this.Li()) return null;
      let s = null;
      for (const e of n) {
        s = zi(s, this.hl(t, i, e));
      }
      return s;
    }
    J(t) {
      this.Jh.clear(), this.Gh.clear(), (this.Zh = t);
    }
    il(t) {
      return this.Zh[t].ie;
    }
    el(t) {
      return this.Zh[t];
    }
    nl(t, i) {
      const n = this.ll(t);
      if (null === n && 0 !== i)
        switch (i) {
          case -1:
            return this.al(t);
          case 1:
            return this.ol(t);
          default:
            throw new TypeError("Unknown search mode");
        }
      return n;
    }
    al(t) {
      let i = this._l(t);
      return (
        i > 0 && (i -= 1), i !== this.Zh.length && this.il(i) < t ? i : null
      );
    }
    ol(t) {
      const i = this.ul(t);
      return i !== this.Zh.length && t < this.il(i) ? i : null;
    }
    ll(t) {
      const i = this._l(t);
      return i === this.Zh.length || t < this.Zh[i].ie ? null : i;
    }
    _l(t) {
      return Pt(this.Zh, t, (t, i) => t.ie < i);
    }
    ul(t) {
      return Rt(this.Zh, t, (t, i) => t.ie > i);
    }
    cl(t, i, n) {
      let s = null;
      for (let e = t; e < i; e++) {
        const t = this.Zh[e].Ot[n];
        Number.isNaN(t) ||
          (null === s
            ? (s = { dl: t, fl: t })
            : (t < s.dl && (s.dl = t), t > s.fl && (s.fl = t)));
      }
      return s;
    }
    hl(t, i, n) {
      if (this.Li()) return null;
      let s = null;
      const e = f(this.tl()),
        r = f(this.Bn()),
        h = Math.max(t, e),
        l = Math.min(i, r),
        a = Math.ceil(h / Ai) * Ai,
        o = Math.max(a, Math.floor(l / Ai) * Ai);
      {
        const t = this._l(h),
          e = this.ul(Math.min(l, a, i));
        s = zi(s, this.cl(t, e, n));
      }
      let _ = this.Gh.get(n);
      void 0 === _ && ((_ = new Map()), this.Gh.set(n, _));
      for (let t = Math.max(a + 1, h); t < o; t += Ai) {
        const i = Math.floor(t / Ai);
        let e = _.get(i);
        if (void 0 === e) {
          const t = this._l(i * Ai),
            s = this.ul((i + 1) * Ai - 1);
          (e = this.cl(t, s, n)), _.set(i, e);
        }
        s = zi(s, e);
      }
      {
        const t = this._l(o),
          i = this.ul(l);
        s = zi(s, this.cl(t, i, n));
      }
      return s;
    }
  }
  function zi(t, i) {
    if (null === t) return i;
    if (null === i) return t;
    return { dl: Math.min(t.dl, i.dl), fl: Math.max(t.fl, i.fl) };
  }
  class Ei {
    constructor(t) {
      this.vl = t;
    }
    K(t, i, n) {
      this.vl.draw(t);
    }
    pl(t, i, n) {
      var s, e;
      null === (e = (s = this.vl).drawBackground) ||
        void 0 === e ||
        e.call(s, t);
    }
  }
  class Ii {
    constructor(t) {
      (this.Ge = null), (this.mn = t);
    }
    gt() {
      var t;
      const i = this.mn.renderer();
      if (null === i) return null;
      if ((null === (t = this.Ge) || void 0 === t ? void 0 : t.ml) === i)
        return this.Ge.bl;
      const n = new Ei(i);
      return (this.Ge = { ml: i, bl: n }), n;
    }
    wl() {
      var t, i, n;
      return null !==
        (n =
          null === (i = (t = this.mn).zOrder) || void 0 === i
            ? void 0
            : i.call(t)) && void 0 !== n
        ? n
        : "normal";
    }
  }
  function Li(t) {
    var i, n, s, e, r;
    return {
      Zt: t.text(),
      Si: t.coordinate(),
      xi: null === (i = t.fixedCoordinate) || void 0 === i ? void 0 : i.call(t),
      O: t.textColor(),
      t: t.backColor(),
      kt:
        null ===
          (s = null === (n = t.visible) || void 0 === n ? void 0 : n.call(t)) ||
        void 0 === s ||
        s,
      hi:
        null ===
          (r =
            null === (e = t.tickVisible) || void 0 === e
              ? void 0
              : e.call(t)) ||
        void 0 === r ||
        r,
    };
  }
  class Ni {
    constructor(t, i) {
      (this.Wt = new tt()), (this.gl = t), (this.Ml = i);
    }
    gt() {
      return (
        this.Wt.J(Object.assign({ ji: this.Ml.ji() }, Li(this.gl))), this.Wt
      );
    }
  }
  class Fi extends G {
    constructor(t, i) {
      super(), (this.gl = t), (this.Ei = i);
    }
    zi(t, i, n) {
      const s = Li(this.gl);
      (n.t = s.t), (t.O = s.O);
      const e = (2 / 12) * this.Ei.P();
      (n.bi = e),
        (n.wi = e),
        (n.Si = s.Si),
        (n.xi = s.xi),
        (t.Zt = s.Zt),
        (t.kt = s.kt),
        (t.hi = s.hi);
    }
  }
  class Wi {
    constructor(t, i) {
      (this.xl = null),
        (this.Sl = null),
        (this.yl = null),
        (this.kl = null),
        (this.Cl = null),
        (this.Tl = t),
        (this.Nr = i);
    }
    Pl() {
      return this.Tl;
    }
    Rn() {
      var t, i;
      null === (i = (t = this.Tl).updateAllViews) || void 0 === i || i.call(t);
    }
    Cn() {
      var t, i, n, s;
      const e =
        null !==
          (n =
            null === (i = (t = this.Tl).paneViews) || void 0 === i
              ? void 0
              : i.call(t)) && void 0 !== n
          ? n
          : [];
      if ((null === (s = this.xl) || void 0 === s ? void 0 : s.ml) === e)
        return this.xl.bl;
      const r = e.map((t) => new Ii(t));
      return (this.xl = { ml: e, bl: r }), r;
    }
    Ji() {
      var t, i, n, s;
      const e =
        null !==
          (n =
            null === (i = (t = this.Tl).timeAxisViews) || void 0 === i
              ? void 0
              : i.call(t)) && void 0 !== n
          ? n
          : [];
      if ((null === (s = this.Sl) || void 0 === s ? void 0 : s.ml) === e)
        return this.Sl.bl;
      const r = this.Nr.$t().St(),
        h = e.map((t) => new Ni(t, r));
      return (this.Sl = { ml: e, bl: h }), h;
    }
    Tn() {
      var t, i, n, s;
      const e =
        null !==
          (n =
            null === (i = (t = this.Tl).priceAxisViews) || void 0 === i
              ? void 0
              : i.call(t)) && void 0 !== n
          ? n
          : [];
      if ((null === (s = this.yl) || void 0 === s ? void 0 : s.ml) === e)
        return this.yl.bl;
      const r = this.Nr.Dt(),
        h = e.map((t) => new Fi(t, r));
      return (this.yl = { ml: e, bl: h }), h;
    }
    Rl() {
      var t, i, n, s;
      const e =
        null !==
          (n =
            null === (i = (t = this.Tl).priceAxisPaneViews) || void 0 === i
              ? void 0
              : i.call(t)) && void 0 !== n
          ? n
          : [];
      if ((null === (s = this.kl) || void 0 === s ? void 0 : s.ml) === e)
        return this.kl.bl;
      const r = e.map((t) => new Ii(t));
      return (this.kl = { ml: e, bl: r }), r;
    }
    Dl() {
      var t, i, n, s;
      const e =
        null !==
          (n =
            null === (i = (t = this.Tl).timeAxisPaneViews) || void 0 === i
              ? void 0
              : i.call(t)) && void 0 !== n
          ? n
          : [];
      if ((null === (s = this.Cl) || void 0 === s ? void 0 : s.ml) === e)
        return this.Cl.bl;
      const r = e.map((t) => new Ii(t));
      return (this.Cl = { ml: e, bl: r }), r;
    }
    Ol(t, i) {
      var n, s, e;
      return null !==
        (e =
          null === (s = (n = this.Tl).autoscaleInfo) || void 0 === s
            ? void 0
            : s.call(n, t, i)) && void 0 !== e
        ? e
        : null;
    }
    pr(t, i) {
      var n, s, e;
      return null !==
        (e =
          null === (s = (n = this.Tl).hitTest) || void 0 === s
            ? void 0
            : s.call(n, t, i)) && void 0 !== e
        ? e
        : null;
    }
  }
  function ji(t, i, n, s) {
    t.forEach((t) => {
      i(t).forEach((t) => {
        t.wl() === n && s.push(t);
      });
    });
  }
  function Hi(t) {
    return t.Cn();
  }
  function $i(t) {
    return t.Rl();
  }
  function Ui(t) {
    return t.Dl();
  }
  class qi extends Ri {
    constructor(t, i, n, s, e) {
      super(t),
        (this.Et = new Vi()),
        (this.Lh = new Mi(this)),
        (this.Bl = []),
        (this.Al = new ni(this)),
        (this.Vl = null),
        (this.zl = null),
        (this.El = []),
        (this.Il = []),
        (this.Ll = null),
        (this.Nl = []),
        (this._n = i),
        (this.Fl = n);
      const r = new xi(this);
      (this.en = [r]),
        (this.Nh = new Qt(r, this, t)),
        ("Area" !== n && "Line" !== n && "Baseline" !== n) ||
          (this.Vl = new li(this)),
        this.Wl(),
        this.jl(e);
    }
    S() {
      null !== this.Ll && clearTimeout(this.Ll);
    }
    uh(t) {
      return this._n.priceLineColor || t;
    }
    Ur(t) {
      const i = { qr: !0 },
        n = this.Dt();
      if (this.$t().St().Li() || n.Li() || this.Et.Li()) return i;
      const s = this.$t().St().qs(),
        e = this.Ct();
      if (null === s || null === e) return i;
      let r, h;
      if (t) {
        const t = this.Et.Qh();
        if (null === t) return i;
        (r = t), (h = t.ie);
      } else {
        const t = this.Et.sl(s.ui(), -1);
        if (null === t) return i;
        if (((r = this.Et.Yh(t.ie)), null === r)) return i;
        h = t.ie;
      }
      const l = r.Ot[3],
        a = this.js().Ws(h, { Ot: r }),
        o = n.Rt(l, e.Ot);
      return {
        qr: !1,
        _t: l,
        Zt: n.Ni(l, e.Ot),
        bh: n.Hl(l),
        wh: n.$l(l, e.Ot),
        O: a.oe,
        Si: o,
        ie: h,
      };
    }
    js() {
      return null !== this.zl || (this.zl = new Oi(this)), this.zl;
    }
    W() {
      return this._n;
    }
    Fh(t) {
      const i = t.priceScaleId;
      void 0 !== i && i !== this._n.priceScaleId && this.$t().Ul(this, i),
        C(this._n, t),
        void 0 !== t.priceFormat && (this.Wl(), this.$t().ql()),
        this.$t().Yl(this),
        this.$t().Xl(),
        this.mn.bt("options");
    }
    J(t, i) {
      this.Et.J(t),
        this.Kl(),
        this.mn.bt("data"),
        this.un.bt("data"),
        null !== this.Vl &&
          (i && i.Zl ? this.Vl.Wr() : 0 === t.length && this.Vl.Fr());
      const n = this.$t()._r(this);
      this.$t().Gl(n), this.$t().Yl(this), this.$t().Xl(), this.$t().Wh();
    }
    Jl(t) {
      (this.El = t), this.Kl();
      const i = this.$t()._r(this);
      this.un.bt("data"),
        this.$t().Gl(i),
        this.$t().Yl(this),
        this.$t().Xl(),
        this.$t().Wh();
    }
    Ql() {
      return this.El;
    }
    ah() {
      return this.Il;
    }
    ta(t) {
      const i = new Pi(this, t);
      return this.Bl.push(i), this.$t().Yl(this), i;
    }
    ia(t) {
      const i = this.Bl.indexOf(t);
      -1 !== i && this.Bl.splice(i, 1), this.$t().Yl(this);
    }
    Kh() {
      return this.Fl;
    }
    Ct() {
      const t = this.na();
      return null === t ? null : { Ot: t.Ot[3], sa: t.ot };
    }
    na() {
      const t = this.$t().St().qs();
      if (null === t) return null;
      const i = t.Rs();
      return this.Et.sl(i, 1);
    }
    An() {
      return this.Et;
    }
    _h(t) {
      const i = this.Et.Yh(t);
      return null === i
        ? null
        : "Bar" === this.Fl || "Candlestick" === this.Fl || "Custom" === this.Fl
        ? { me: i.Ot[0], be: i.Ot[1], we: i.Ot[2], ge: i.Ot[3] }
        : i.Ot[3];
    }
    ea(t) {
      const i = [];
      ji(this.Nl, Hi, "top", i);
      const n = this.Vl;
      return null !== n && n.kt()
        ? (null === this.Ll &&
            n.Hr() &&
            (this.Ll = setTimeout(() => {
              (this.Ll = null), this.$t().ra();
            }, 0)),
          n.jr(),
          i.unshift(n),
          i)
        : i;
    }
    Cn() {
      const t = [];
      this.ha() || t.push(this.Al), t.push(this.mn, this.Lh, this.un);
      const i = this.Bl.map((t) => t.jh());
      return t.push(...i), ji(this.Nl, Hi, "normal", t), t;
    }
    la() {
      return this.aa(Hi, "bottom");
    }
    oa(t) {
      return this.aa($i, t);
    }
    _a(t) {
      return this.aa(Ui, t);
    }
    ua(t, i) {
      return this.Nl.map((n) => n.pr(t, i)).filter((t) => null !== t);
    }
    Gi(t) {
      return [this.Nh, ...this.Bl.map((t) => t.Hh())];
    }
    Tn(t, i) {
      if (i !== this.qi && !this.ha()) return [];
      const n = [...this.en];
      for (const t of this.Bl) n.push(t.$h());
      return (
        this.Nl.forEach((t) => {
          n.push(...t.Tn());
        }),
        n
      );
    }
    Ji() {
      const t = [];
      return (
        this.Nl.forEach((i) => {
          t.push(...i.Ji());
        }),
        t
      );
    }
    Ol(t, i) {
      if (void 0 !== this._n.autoscaleInfoProvider) {
        const n = this._n.autoscaleInfoProvider(() => {
          const n = this.ca(t, i);
          return null === n ? null : n.Rh();
        });
        return ki.Dh(n);
      }
      return this.ca(t, i);
    }
    da() {
      return this._n.priceFormat.minMove;
    }
    fa() {
      return this.va;
    }
    Rn() {
      var t;
      this.mn.bt(), this.un.bt();
      for (const t of this.en) t.bt();
      for (const t of this.Bl) t.bt();
      this.Lh.bt(),
        this.Al.bt(),
        null === (t = this.Vl) || void 0 === t || t.bt(),
        this.Nl.forEach((t) => t.Rn());
    }
    Dt() {
      return f(super.Dt());
    }
    yt(t) {
      if (
        !(
          ("Line" === this.Fl ||
            "Area" === this.Fl ||
            "Baseline" === this.Fl) &&
          this._n.crosshairMarkerVisible
        )
      )
        return null;
      const i = this.Et.Yh(t);
      if (null === i) return null;
      return {
        _t: i.Ot[3],
        ht: this.pa(),
        Bt: this.ma(),
        Pt: this.ba(),
        Tt: this.wa(t),
      };
    }
    dh() {
      return this._n.title;
    }
    kt() {
      return this._n.visible;
    }
    ga(t) {
      this.Nl.push(new Wi(t, this));
    }
    Ma(t) {
      this.Nl = this.Nl.filter((i) => i.Pl() !== t);
    }
    xa() {
      if (this.mn instanceof Ut != !1) return (t) => this.mn.Le(t);
    }
    Sa() {
      if (this.mn instanceof Ut != !1) return (t) => this.mn.Ne(t);
    }
    ha() {
      return !rt(this.Dt().ya());
    }
    ca(t, i) {
      if (!P(t) || !P(i) || this.Et.Li()) return null;
      const n =
          "Line" === this.Fl ||
          "Area" === this.Fl ||
          "Baseline" === this.Fl ||
          "Histogram" === this.Fl
            ? [3]
            : [2, 1],
        s = this.Et.rl(t, i, n);
      let e = null !== s ? new yi(s.dl, s.fl) : null;
      if ("Histogram" === this.Kh()) {
        const t = this._n.base,
          i = new yi(t, t);
        e = null !== e ? e.Jn(i) : i;
      }
      let r = this.un.lh();
      return (
        this.Nl.forEach((n) => {
          const s = n.Ol(t, i);
          if (null == s ? void 0 : s.priceRange) {
            const t = new yi(s.priceRange.minValue, s.priceRange.maxValue);
            e = null !== e ? e.Jn(t) : t;
          }
          var h, l, a, o;
          (null == s ? void 0 : s.margins) &&
            ((h = r),
            (l = s.margins),
            (r = {
              above: Math.max(
                null !== (a = null == h ? void 0 : h.above) && void 0 !== a
                  ? a
                  : 0,
                l.above
              ),
              below: Math.max(
                null !== (o = null == h ? void 0 : h.below) && void 0 !== o
                  ? o
                  : 0,
                l.below
              ),
            }));
        }),
        new ki(e, r)
      );
    }
    pa() {
      switch (this.Fl) {
        case "Line":
        case "Area":
        case "Baseline":
          return this._n.crosshairMarkerRadius;
      }
      return 0;
    }
    ma() {
      switch (this.Fl) {
        case "Line":
        case "Area":
        case "Baseline": {
          const t = this._n.crosshairMarkerBorderColor;
          if (0 !== t.length) return t;
        }
      }
      return null;
    }
    ba() {
      switch (this.Fl) {
        case "Line":
        case "Area":
        case "Baseline":
          return this._n.crosshairMarkerBorderWidth;
      }
      return 0;
    }
    wa(t) {
      switch (this.Fl) {
        case "Line":
        case "Area":
        case "Baseline": {
          const t = this._n.crosshairMarkerBackgroundColor;
          if (0 !== t.length) return t;
        }
      }
      return this.js().Ws(t).oe;
    }
    Wl() {
      switch (this._n.priceFormat.type) {
        case "custom":
          this.va = { format: this._n.priceFormat.formatter };
          break;
        case "volume":
          this.va = new ut(this._n.priceFormat.precision);
          break;
        case "percent":
          this.va = new _t(this._n.priceFormat.precision);
          break;
        default: {
          const t = Math.pow(10, this._n.priceFormat.precision);
          this.va = new ot(t, this._n.priceFormat.minMove * t);
        }
      }
      null !== this.qi && this.qi.ka();
    }
    Kl() {
      const t = this.$t().St();
      if (!t.Ca() || this.Et.Li()) return void (this.Il = []);
      const i = f(this.Et.tl());
      this.Il = this.El.map((n, s) => {
        const e = f(t.Ta(n.time, !0)),
          r = e < i ? 1 : -1;
        return {
          time: f(this.Et.sl(e, r)).ie,
          position: n.position,
          shape: n.shape,
          color: n.color,
          id: n.id,
          Gr: s,
          text: n.text,
          size: n.size,
          originalTime: n.originalTime,
        };
      });
    }
    jl(t) {
      switch (((this.un = new gi(this, this.$t())), this.Fl)) {
        case "Bar":
          this.mn = new Lt(this, this.$t());
          break;
        case "Candlestick":
          this.mn = new Ht(this, this.$t());
          break;
        case "Line":
          this.mn = new Kt(this, this.$t());
          break;
        case "Custom":
          this.mn = new Ut(this, this.$t(), d(t));
          break;
        case "Area":
          this.mn = new zt(this, this.$t());
          break;
        case "Baseline":
          this.mn = new Wt(this, this.$t());
          break;
        case "Histogram":
          this.mn = new Xt(this, this.$t());
          break;
        default:
          throw Error("Unknown chart style assigned: " + this.Fl);
      }
    }
    aa(t, i) {
      const n = [];
      return ji(this.Nl, t, i, n), n;
    }
  }
  class Yi {
    constructor(t) {
      this._n = t;
    }
    Pa(t, i, n) {
      let s = t;
      if (0 === this._n.mode) return s;
      const e = n.dn(),
        r = e.Ct();
      if (null === r) return s;
      const h = e.Rt(t, r),
        l = n
          .Ra()
          .filter((t) => t instanceof qi)
          .reduce((t, s) => {
            if (n.ur(s) || !s.kt()) return t;
            const e = s.Dt(),
              r = s.An();
            if (e.Li() || !r.Yr(i)) return t;
            const h = r.Yh(i);
            if (null === h) return t;
            const l = v(s.Ct());
            return t.concat([e.Rt(h.Ot[3], l.Ot)]);
          }, []);
      if (0 === l.length) return s;
      l.sort((t, i) => Math.abs(t - h) - Math.abs(i - h));
      const a = l[0];
      return (s = e.fn(a, r)), s;
    }
  }
  class Xi extends L {
    constructor() {
      super(...arguments), (this.Et = null);
    }
    J(t) {
      this.Et = t;
    }
    Z({
      context: t,
      bitmapSize: i,
      horizontalPixelRatio: n,
      verticalPixelRatio: s,
    }) {
      if (null === this.Et) return;
      const e = Math.max(1, Math.floor(n));
      (t.lineWidth = e),
        (function (t, i) {
          t.save(), t.lineWidth % 2 && t.translate(0.5, 0.5), i(), t.restore();
        })(t, () => {
          const r = f(this.Et);
          if (r.Da) {
            (t.strokeStyle = r.Oa), _(t, r.Ba), t.beginPath();
            for (const s of r.Aa) {
              const r = Math.round(s.Va * n);
              t.moveTo(r, -e), t.lineTo(r, i.height + e);
            }
            t.stroke();
          }
          if (r.za) {
            (t.strokeStyle = r.Ea), _(t, r.Ia), t.beginPath();
            for (const n of r.La) {
              const r = Math.round(n.Va * s);
              t.moveTo(-e, r), t.lineTo(i.width + e, r);
            }
            t.stroke();
          }
        });
    }
  }
  class Ki {
    constructor(t) {
      (this.Wt = new Xi()), (this.ft = !0), (this.Qi = t);
    }
    bt() {
      this.ft = !0;
    }
    gt() {
      if (this.ft) {
        const t = this.Qi.$t().W().grid,
          i = {
            za: t.horzLines.visible,
            Da: t.vertLines.visible,
            Ea: t.horzLines.color,
            Oa: t.vertLines.color,
            Ia: t.horzLines.style,
            Ba: t.vertLines.style,
            La: this.Qi.dn().Na(),
            Aa: (this.Qi.$t().St().Na() || []).map((t) => ({ Va: t.coord })),
          };
        this.Wt.J(i), (this.ft = !1);
      }
      return this.Wt;
    }
  }
  class Zi {
    constructor(t) {
      this.mn = new Ki(t);
    }
    jh() {
      return this.mn;
    }
  }
  const Gi = { Fa: 4, Wa: 1e-4 };
  function Ji(t, i) {
    const n = (100 * (t - i)) / i;
    return i < 0 ? -n : n;
  }
  function Qi(t, i) {
    const n = Ji(t.yh(), i),
      s = Ji(t.kh(), i);
    return new yi(n, s);
  }
  function tn(t, i) {
    const n = (100 * (t - i)) / i + 100;
    return i < 0 ? -n : n;
  }
  function nn(t, i) {
    const n = tn(t.yh(), i),
      s = tn(t.kh(), i);
    return new yi(n, s);
  }
  function sn(t, i) {
    const n = Math.abs(t);
    if (n < 1e-15) return 0;
    const s = Math.log10(n + i.Wa) + i.Fa;
    return t < 0 ? -s : s;
  }
  function en(t, i) {
    const n = Math.abs(t);
    if (n < 1e-15) return 0;
    const s = Math.pow(10, n - i.Fa) - i.Wa;
    return t < 0 ? -s : s;
  }
  function rn(t, i) {
    if (null === t) return null;
    const n = sn(t.yh(), i),
      s = sn(t.kh(), i);
    return new yi(n, s);
  }
  function hn(t, i) {
    if (null === t) return null;
    const n = en(t.yh(), i),
      s = en(t.kh(), i);
    return new yi(n, s);
  }
  function ln(t) {
    if (null === t) return Gi;
    const i = Math.abs(t.kh() - t.yh());
    if (i >= 1 || i < 1e-15) return Gi;
    const n = Math.ceil(Math.abs(Math.log10(i))),
      s = Gi.Fa + n;
    return { Fa: s, Wa: 1 / Math.pow(10, s) };
  }
  class an {
    constructor(t, i) {
      if (
        ((this.ja = t),
        (this.Ha = i),
        (function (t) {
          if (t < 0) return !1;
          for (let i = t; i > 1; i /= 10) if (i % 10 != 0) return !1;
          return !0;
        })(this.ja))
      )
        this.$a = [2, 2.5, 2];
      else {
        this.$a = [];
        for (let t = this.ja; 1 !== t; ) {
          if (t % 2 == 0) this.$a.push(2), (t /= 2);
          else {
            if (t % 5 != 0) throw new Error("unexpected base");
            this.$a.push(2, 2.5), (t /= 5);
          }
          if (this.$a.length > 100)
            throw new Error("something wrong with base");
        }
      }
    }
    Ua(t, i, n) {
      const s = 0 === this.ja ? 0 : 1 / this.ja;
      let e = Math.pow(10, Math.max(0, Math.ceil(Math.log10(t - i)))),
        r = 0,
        h = this.Ha[0];
      for (;;) {
        const t = gt(e, s, 1e-14) && e > s + 1e-14,
          i = gt(e, n * h, 1e-14),
          l = gt(e, 1, 1e-14);
        if (!(t && i && l)) break;
        (e /= h), (h = this.Ha[++r % this.Ha.length]);
      }
      if (
        (e <= s + 1e-14 && (e = s),
        (e = Math.max(1, e)),
        this.$a.length > 0 &&
          ((l = e), (a = 1), (o = 1e-14), Math.abs(l - a) < o))
      )
        for (r = 0, h = this.$a[0]; gt(e, n * h, 1e-14) && e > s + 1e-14; )
          (e /= h), (h = this.$a[++r % this.$a.length]);
      var l, a, o;
      return e;
    }
  }
  class on {
    constructor(t, i, n, s) {
      (this.qa = []),
        (this.Ei = t),
        (this.ja = i),
        (this.Ya = n),
        (this.Xa = s);
    }
    Ua(t, i) {
      if (t < i) throw new Error("high < low");
      const n = this.Ei.Vt(),
        s = ((t - i) * this.Ka()) / n,
        e = new an(this.ja, [2, 2.5, 2]),
        r = new an(this.ja, [2, 2, 2.5]),
        h = new an(this.ja, [2.5, 2, 2]),
        l = [];
      return (
        l.push(e.Ua(t, i, s), r.Ua(t, i, s), h.Ua(t, i, s)),
        (function (t) {
          if (t.length < 1) throw Error("array is empty");
          let i = t[0];
          for (let n = 1; n < t.length; ++n) t[n] < i && (i = t[n]);
          return i;
        })(l)
      );
    }
    Za() {
      const t = this.Ei,
        i = t.Ct();
      if (null === i) return void (this.qa = []);
      const n = t.Vt(),
        s = this.Ya(n - 1, i),
        e = this.Ya(0, i),
        r = this.Ei.W().entireTextOnly ? this.Ga() / 2 : 0,
        h = r,
        l = n - 1 - r,
        a = Math.max(s, e),
        o = Math.min(s, e);
      if (a === o) return void (this.qa = []);
      let _ = this.Ua(a, o),
        u = a % _;
      u += u < 0 ? _ : 0;
      const c = a >= o ? 1 : -1;
      let d = null,
        f = 0;
      for (let n = a - u; n > o; n -= _) {
        const s = this.Xa(n, i, !0);
        (null !== d && Math.abs(s - d) < this.Ka()) ||
          s < h ||
          s > l ||
          (f < this.qa.length
            ? ((this.qa[f].Va = s), (this.qa[f].Ja = t.Qa(n)))
            : this.qa.push({ Va: s, Ja: t.Qa(n) }),
          f++,
          (d = s),
          t.io() && (_ = this.Ua(n * c, o)));
      }
      this.qa.length = f;
    }
    Na() {
      return this.qa;
    }
    Ga() {
      return this.Ei.P();
    }
    Ka() {
      return Math.ceil(2.5 * this.Ga());
    }
  }
  function _n(t) {
    return t.slice().sort((t, i) => f(t.Xi()) - f(i.Xi()));
  }
  var un;
  !(function (t) {
    (t[(t.Normal = 0)] = "Normal"),
      (t[(t.Logarithmic = 1)] = "Logarithmic"),
      (t[(t.Percentage = 2)] = "Percentage"),
      (t[(t.IndexedTo100 = 3)] = "IndexedTo100");
  })(un || (un = {}));
  const cn = new _t(),
    dn = new ot(100, 1);
  class fn {
    constructor(t, i, n, s) {
      (this.no = 0),
        (this.so = null),
        (this.Oh = null),
        (this.eo = null),
        (this.ro = { ho: !1, lo: null }),
        (this.ao = 0),
        (this.oo = 0),
        (this._o = new k()),
        (this.uo = new k()),
        (this.co = []),
        (this.do = null),
        (this.fo = null),
        (this.vo = null),
        (this.po = null),
        (this.va = dn),
        (this.mo = ln(null)),
        (this.bo = t),
        (this._n = i),
        (this.wo = n),
        (this.Mo = s),
        (this.xo = new on(this, 100, this.So.bind(this), this.yo.bind(this)));
    }
    ya() {
      return this.bo;
    }
    W() {
      return this._n;
    }
    Fh(t) {
      if (
        (C(this._n, t),
        this.ka(),
        void 0 !== t.mode && this.ko({ Sr: t.mode }),
        void 0 !== t.scaleMargins)
      ) {
        const i = d(t.scaleMargins.top),
          n = d(t.scaleMargins.bottom);
        if (i < 0 || i > 1)
          throw new Error(
            `Invalid top margin - expect value between 0 and 1, given=${i}`
          );
        if (n < 0 || n > 1)
          throw new Error(
            `Invalid bottom margin - expect value between 0 and 1, given=${n}`
          );
        if (i + n > 1)
          throw new Error(
            `Invalid margins - sum of margins must be less than 1, given=${
              i + n
            }`
          );
        this.Co(), (this.fo = null);
      }
    }
    To() {
      return this._n.autoScale;
    }
    io() {
      return 1 === this._n.mode;
    }
    mh() {
      return 2 === this._n.mode;
    }
    Po() {
      return 3 === this._n.mode;
    }
    Sr() {
      return {
        Nn: this._n.autoScale,
        Ro: this._n.invertScale,
        Sr: this._n.mode,
      };
    }
    ko(t) {
      const i = this.Sr();
      let n = null;
      void 0 !== t.Nn && (this._n.autoScale = t.Nn),
        void 0 !== t.Sr &&
          ((this._n.mode = t.Sr),
          (2 !== t.Sr && 3 !== t.Sr) || (this._n.autoScale = !0),
          (this.ro.ho = !1)),
        1 === i.Sr &&
          t.Sr !== i.Sr &&
          (!(function (t, i) {
            if (null === t) return !1;
            const n = en(t.yh(), i),
              s = en(t.kh(), i);
            return isFinite(n) && isFinite(s);
          })(this.Oh, this.mo)
            ? (this._n.autoScale = !0)
            : ((n = hn(this.Oh, this.mo)), null !== n && this.Do(n))),
        1 === t.Sr &&
          t.Sr !== i.Sr &&
          ((n = rn(this.Oh, this.mo)), null !== n && this.Do(n));
      const s = i.Sr !== this._n.mode;
      s && (2 === i.Sr || this.mh()) && this.ka(),
        s && (3 === i.Sr || this.Po()) && this.ka(),
        void 0 !== t.Ro &&
          i.Ro !== t.Ro &&
          ((this._n.invertScale = t.Ro), this.Oo()),
        this.uo.m(i, this.Sr());
    }
    Bo() {
      return this.uo;
    }
    P() {
      return this.wo.fontSize;
    }
    Vt() {
      return this.no;
    }
    Ao(t) {
      this.no !== t && ((this.no = t), this.Co(), (this.fo = null));
    }
    Vo() {
      if (this.so) return this.so;
      const t = this.Vt() - this.zo() - this.Eo();
      return (this.so = t), t;
    }
    Ah() {
      return this.Io(), this.Oh;
    }
    Do(t, i) {
      const n = this.Oh;
      (i || (null === n && null !== t) || (null !== n && !n.xh(t))) &&
        ((this.fo = null), (this.Oh = t));
    }
    Li() {
      return this.Io(), 0 === this.no || !this.Oh || this.Oh.Li();
    }
    Lo(t) {
      return this.Ro() ? t : this.Vt() - 1 - t;
    }
    Rt(t, i) {
      return (
        this.mh() ? (t = Ji(t, i)) : this.Po() && (t = tn(t, i)), this.yo(t, i)
      );
    }
    Gs(t, i, n) {
      this.Io();
      const s = this.Eo(),
        e = f(this.Ah()),
        r = e.yh(),
        h = e.kh(),
        l = this.Vo() - 1,
        a = this.Ro(),
        o = l / (h - r),
        _ = void 0 === n ? 0 : n.from,
        u = void 0 === n ? t.length : n.to,
        c = this.No();
      for (let n = _; n < u; n++) {
        const e = t[n],
          h = e._t;
        if (isNaN(h)) continue;
        let l = h;
        null !== c && (l = c(e._t, i));
        const _ = s + o * (l - r),
          u = a ? _ : this.no - 1 - _;
        e.st = u;
      }
    }
    ve(t, i, n) {
      this.Io();
      const s = this.Eo(),
        e = f(this.Ah()),
        r = e.yh(),
        h = e.kh(),
        l = this.Vo() - 1,
        a = this.Ro(),
        o = l / (h - r),
        _ = void 0 === n ? 0 : n.from,
        u = void 0 === n ? t.length : n.to,
        c = this.No();
      for (let n = _; n < u; n++) {
        const e = t[n];
        let h = e.me,
          l = e.be,
          _ = e.we,
          u = e.ge;
        null !== c &&
          ((h = c(e.me, i)),
          (l = c(e.be, i)),
          (_ = c(e.we, i)),
          (u = c(e.ge, i)));
        let d = s + o * (h - r),
          f = a ? d : this.no - 1 - d;
        (e.de = f),
          (d = s + o * (l - r)),
          (f = a ? d : this.no - 1 - d),
          (e._e = f),
          (d = s + o * (_ - r)),
          (f = a ? d : this.no - 1 - d),
          (e.ue = f),
          (d = s + o * (u - r)),
          (f = a ? d : this.no - 1 - d),
          (e.fe = f);
      }
    }
    fn(t, i) {
      const n = this.So(t, i);
      return this.Fo(n, i);
    }
    Fo(t, i) {
      let n = t;
      return (
        this.mh()
          ? (n = (function (t, i) {
              return i < 0 && (t = -t), (t / 100) * i + i;
            })(n, i))
          : this.Po() &&
            (n = (function (t, i) {
              return (t -= 100), i < 0 && (t = -t), (t / 100) * i + i;
            })(n, i)),
        n
      );
    }
    Ra() {
      return this.co;
    }
    Wo() {
      if (this.do) return this.do;
      let t = [];
      for (let i = 0; i < this.co.length; i++) {
        const n = this.co[i];
        null === n.Xi() && n.Ki(i + 1), t.push(n);
      }
      return (t = _n(t)), (this.do = t), this.do;
    }
    jo(t) {
      -1 === this.co.indexOf(t) && (this.co.push(t), this.ka(), this.Ho());
    }
    $o(t) {
      const i = this.co.indexOf(t);
      if (-1 === i) throw new Error("source is not attached to scale");
      this.co.splice(i, 1),
        0 === this.co.length && (this.ko({ Nn: !0 }), this.Do(null)),
        this.ka(),
        this.Ho();
    }
    Ct() {
      let t = null;
      for (const i of this.co) {
        const n = i.Ct();
        null !== n && (null === t || n.sa < t.sa) && (t = n);
      }
      return null === t ? null : t.Ot;
    }
    Ro() {
      return this._n.invertScale;
    }
    Na() {
      const t = null === this.Ct();
      if (null !== this.fo && (t || this.fo.Uo === t)) return this.fo.Na;
      this.xo.Za();
      const i = this.xo.Na();
      return (this.fo = { Na: i, Uo: t }), this._o.m(), i;
    }
    qo() {
      return this._o;
    }
    Yo(t) {
      this.mh() ||
        this.Po() ||
        (null === this.vo &&
          null === this.eo &&
          (this.Li() ||
            ((this.vo = this.no - t), (this.eo = f(this.Ah()).Sh()))));
    }
    Xo(t) {
      if (this.mh() || this.Po()) return;
      if (null === this.vo) return;
      this.ko({ Nn: !1 }), (t = this.no - t) < 0 && (t = 0);
      let i = (this.vo + 0.2 * (this.no - 1)) / (t + 0.2 * (this.no - 1));
      const n = f(this.eo).Sh();
      (i = Math.max(i, 0.1)), n.Th(i), this.Do(n);
    }
    Ko() {
      this.mh() || this.Po() || ((this.vo = null), (this.eo = null));
    }
    Zo(t) {
      this.To() ||
        (null === this.po &&
          null === this.eo &&
          (this.Li() || ((this.po = t), (this.eo = f(this.Ah()).Sh()))));
    }
    Go(t) {
      if (this.To()) return;
      if (null === this.po) return;
      const i = f(this.Ah()).Ch() / (this.Vo() - 1);
      let n = t - this.po;
      this.Ro() && (n *= -1);
      const s = n * i,
        e = f(this.eo).Sh();
      e.Ph(s), this.Do(e, !0), (this.fo = null);
    }
    Jo() {
      this.To() || (null !== this.po && ((this.po = null), (this.eo = null)));
    }
    fa() {
      return this.va || this.ka(), this.va;
    }
    Ni(t, i) {
      switch (this._n.mode) {
        case 2:
          return this.Qo(Ji(t, i));
        case 3:
          return this.fa().format(tn(t, i));
        default:
          return this.Ih(t);
      }
    }
    Qa(t) {
      switch (this._n.mode) {
        case 2:
          return this.Qo(t);
        case 3:
          return this.fa().format(t);
        default:
          return this.Ih(t);
      }
    }
    Hl(t) {
      return this.Ih(t, f(this.t_()).fa());
    }
    $l(t, i) {
      return (t = Ji(t, i)), this.Qo(t, cn);
    }
    i_() {
      return this.co;
    }
    n_(t) {
      this.ro = { lo: t, ho: !1 };
    }
    Rn() {
      this.co.forEach((t) => t.Rn());
    }
    ka() {
      this.fo = null;
      const t = this.t_();
      let i = 100;
      null !== t && (i = Math.round(1 / t.da())),
        (this.va = dn),
        this.mh()
          ? ((this.va = cn), (i = 100))
          : this.Po()
          ? ((this.va = new ot(100, 1)), (i = 100))
          : null !== t && (this.va = t.fa()),
        (this.xo = new on(this, i, this.So.bind(this), this.yo.bind(this))),
        this.xo.Za();
    }
    Ho() {
      this.do = null;
    }
    t_() {
      return this.co[0] || null;
    }
    zo() {
      return this.Ro()
        ? this._n.scaleMargins.bottom * this.Vt() + this.oo
        : this._n.scaleMargins.top * this.Vt() + this.ao;
    }
    Eo() {
      return this.Ro()
        ? this._n.scaleMargins.top * this.Vt() + this.ao
        : this._n.scaleMargins.bottom * this.Vt() + this.oo;
    }
    Io() {
      this.ro.ho || ((this.ro.ho = !0), this.s_());
    }
    Co() {
      this.so = null;
    }
    yo(t, i) {
      if ((this.Io(), this.Li())) return 0;
      t = this.io() && t ? sn(t, this.mo) : t;
      const n = f(this.Ah()),
        s = this.Eo() + ((this.Vo() - 1) * (t - n.yh())) / n.Ch();
      return this.Lo(s);
    }
    So(t, i) {
      if ((this.Io(), this.Li())) return 0;
      const n = this.Lo(t),
        s = f(this.Ah()),
        e = s.yh() + s.Ch() * ((n - this.Eo()) / (this.Vo() - 1));
      return this.io() ? en(e, this.mo) : e;
    }
    Oo() {
      (this.fo = null), this.xo.Za();
    }
    s_() {
      const t = this.ro.lo;
      if (null === t) return;
      let i = null;
      const n = this.i_();
      let s = 0,
        e = 0;
      for (const r of n) {
        if (!r.kt()) continue;
        const n = r.Ct();
        if (null === n) continue;
        const h = r.Ol(t.Rs(), t.ui());
        let l = h && h.Ah();
        if (null !== l) {
          switch (this._n.mode) {
            case 1:
              l = rn(l, this.mo);
              break;
            case 2:
              l = Qi(l, n.Ot);
              break;
            case 3:
              l = nn(l, n.Ot);
          }
          if (((i = null === i ? l : i.Jn(f(l))), null !== h)) {
            const t = h.Vh();
            null !== t &&
              ((s = Math.max(s, t.above)), (e = Math.max(e, t.below)));
          }
        }
      }
      if (
        ((s === this.ao && e === this.oo) ||
          ((this.ao = s), (this.oo = e), (this.fo = null), this.Co()),
        null !== i)
      ) {
        if (i.yh() === i.kh()) {
          const t = this.t_(),
            n = 5 * (null === t || this.mh() || this.Po() ? 1 : t.da());
          this.io() && (i = hn(i, this.mo)),
            (i = new yi(i.yh() - n, i.kh() + n)),
            this.io() && (i = rn(i, this.mo));
        }
        if (this.io()) {
          const t = hn(i, this.mo),
            n = ln(t);
          if (((r = n), (h = this.mo), r.Fa !== h.Fa || r.Wa !== h.Wa)) {
            const s = null !== this.eo ? hn(this.eo, this.mo) : null;
            (this.mo = n), (i = rn(t, n)), null !== s && (this.eo = rn(s, n));
          }
        }
        this.Do(i);
      } else
        null === this.Oh && (this.Do(new yi(-0.5, 0.5)), (this.mo = ln(null)));
      var r, h;
      this.ro.ho = !0;
    }
    No() {
      return this.mh()
        ? Ji
        : this.Po()
        ? tn
        : this.io()
        ? (t) => sn(t, this.mo)
        : null;
    }
    e_(t, i, n) {
      return void 0 === i
        ? (void 0 === n && (n = this.fa()), n.format(t))
        : i(t);
    }
    Ih(t, i) {
      return this.e_(t, this.Mo.priceFormatter, i);
    }
    Qo(t, i) {
      return this.e_(t, this.Mo.percentageFormatter, i);
    }
  }
  class vn {
    constructor(t, i) {
      (this.co = []),
        (this.r_ = new Map()),
        (this.no = 0),
        (this.h_ = 0),
        (this.l_ = 1e3),
        (this.do = null),
        (this.a_ = new k()),
        (this.Ml = t),
        (this.Hi = i),
        (this.o_ = new Zi(this));
      const n = i.W();
      (this.__ = this.u_("left", n.leftPriceScale)),
        (this.c_ = this.u_("right", n.rightPriceScale)),
        this.__.Bo().l(this.d_.bind(this, this.__), this),
        this.c_.Bo().l(this.d_.bind(this, this.c_), this),
        this.f_(n);
    }
    f_(t) {
      if (
        (t.leftPriceScale && this.__.Fh(t.leftPriceScale),
        t.rightPriceScale && this.c_.Fh(t.rightPriceScale),
        t.localization && (this.__.ka(), this.c_.ka()),
        t.overlayPriceScales)
      ) {
        const i = Array.from(this.r_.values());
        for (const n of i) {
          const i = f(n[0].Dt());
          i.Fh(t.overlayPriceScales), t.localization && i.ka();
        }
      }
    }
    v_(t) {
      switch (t) {
        case "left":
          return this.__;
        case "right":
          return this.c_;
      }
      return this.r_.has(t) ? d(this.r_.get(t))[0].Dt() : null;
    }
    S() {
      this.$t().p_().p(this),
        this.__.Bo().p(this),
        this.c_.Bo().p(this),
        this.co.forEach((t) => {
          t.S && t.S();
        }),
        this.a_.m();
    }
    m_() {
      return this.l_;
    }
    b_(t) {
      this.l_ = t;
    }
    $t() {
      return this.Hi;
    }
    ji() {
      return this.h_;
    }
    Vt() {
      return this.no;
    }
    w_(t) {
      (this.h_ = t), this.g_();
    }
    Ao(t) {
      (this.no = t),
        this.__.Ao(t),
        this.c_.Ao(t),
        this.co.forEach((i) => {
          if (this.ur(i)) {
            const n = i.Dt();
            null !== n && n.Ao(t);
          }
        }),
        this.g_();
    }
    Ra() {
      return this.co;
    }
    ur(t) {
      const i = t.Dt();
      return null === i || (this.__ !== i && this.c_ !== i);
    }
    jo(t, i, n) {
      const s = void 0 !== n ? n : this.x_().M_ + 1;
      this.S_(t, i, s);
    }
    $o(t) {
      const i = this.co.indexOf(t);
      c(-1 !== i, "removeDataSource: invalid data source"),
        this.co.splice(i, 1);
      const n = f(t.Dt()).ya();
      if (this.r_.has(n)) {
        const i = d(this.r_.get(n)),
          s = i.indexOf(t);
        -1 !== s && (i.splice(s, 1), 0 === i.length && this.r_.delete(n));
      }
      const s = t.Dt();
      s && s.Ra().indexOf(t) >= 0 && s.$o(t),
        null !== s && (s.Ho(), this.y_(s)),
        (this.do = null);
    }
    dr(t) {
      return t === this.__ ? "left" : t === this.c_ ? "right" : "overlay";
    }
    k_() {
      return this.__;
    }
    C_() {
      return this.c_;
    }
    T_(t, i) {
      t.Yo(i);
    }
    P_(t, i) {
      t.Xo(i), this.g_();
    }
    R_(t) {
      t.Ko();
    }
    D_(t, i) {
      t.Zo(i);
    }
    O_(t, i) {
      t.Go(i), this.g_();
    }
    B_(t) {
      t.Jo();
    }
    g_() {
      this.co.forEach((t) => {
        t.Rn();
      });
    }
    dn() {
      let t = null;
      return (
        this.Hi.W().rightPriceScale.visible && 0 !== this.c_.Ra().length
          ? (t = this.c_)
          : this.Hi.W().leftPriceScale.visible && 0 !== this.__.Ra().length
          ? (t = this.__)
          : 0 !== this.co.length && (t = this.co[0].Dt()),
        null === t && (t = this.c_),
        t
      );
    }
    cr() {
      let t = null;
      return (
        this.Hi.W().rightPriceScale.visible
          ? (t = this.c_)
          : this.Hi.W().leftPriceScale.visible && (t = this.__),
        t
      );
    }
    y_(t) {
      null !== t && t.To() && this.A_(t);
    }
    V_(t) {
      const i = this.Ml.qs();
      t.ko({ Nn: !0 }), null !== i && t.n_(i), this.g_();
    }
    z_() {
      this.A_(this.__), this.A_(this.c_);
    }
    E_() {
      this.y_(this.__),
        this.y_(this.c_),
        this.co.forEach((t) => {
          this.ur(t) && this.y_(t.Dt());
        }),
        this.g_(),
        this.Hi.Wh();
    }
    Wo() {
      return null === this.do && (this.do = _n(this.co)), this.do;
    }
    I_() {
      return this.a_;
    }
    L_() {
      return this.o_;
    }
    A_(t) {
      const i = t.i_();
      if (i && i.length > 0 && !this.Ml.Li()) {
        const i = this.Ml.qs();
        null !== i && t.n_(i);
      }
      t.Rn();
    }
    x_() {
      const t = this.Wo();
      if (0 === t.length) return { N_: 0, M_: 0 };
      let i = 0,
        n = 0;
      for (let s = 0; s < t.length; s++) {
        const e = t[s].Xi();
        null !== e && (e < i && (i = e), e > n && (n = e));
      }
      return { N_: i, M_: n };
    }
    S_(t, i, n) {
      let s = this.v_(i);
      if (
        (null === s && (s = this.u_(i, this.Hi.W().overlayPriceScales)),
        this.co.push(t),
        !rt(i))
      ) {
        const n = this.r_.get(i) || [];
        n.push(t), this.r_.set(i, n);
      }
      s.jo(t), t.Zi(s), t.Ki(n), this.y_(s), (this.do = null);
    }
    d_(t, i, n) {
      i.Sr !== n.Sr && this.A_(t);
    }
    u_(t, i) {
      const n = Object.assign({ visible: !0, autoScale: !0 }, O(i)),
        s = new fn(t, n, this.Hi.W().layout, this.Hi.W().localization);
      return s.Ao(this.Vt()), s;
    }
  }
  class pn {
    constructor(t, i, n = 50) {
      (this.Ye = 0),
        (this.Xe = 1),
        (this.Ke = 1),
        (this.Ge = new Map()),
        (this.Ze = new Map()),
        (this.F_ = t),
        (this.W_ = i),
        (this.Je = n);
    }
    j_(t) {
      const i = t.time,
        n = this.W_.cacheKey(i),
        s = this.Ge.get(n);
      if (void 0 !== s) return s.H_;
      if (this.Ye === this.Je) {
        const t = this.Ze.get(this.Ke);
        this.Ze.delete(this.Ke), this.Ge.delete(d(t)), this.Ke++, this.Ye--;
      }
      const e = this.F_(t);
      return (
        this.Ge.set(n, { H_: e, nr: this.Xe }),
        this.Ze.set(this.Xe, n),
        this.Ye++,
        this.Xe++,
        e
      );
    }
  }
  class mn {
    constructor(t, i) {
      c(t <= i, "right should be >= left"), (this.U_ = t), (this.q_ = i);
    }
    Rs() {
      return this.U_;
    }
    ui() {
      return this.q_;
    }
    Y_() {
      return this.q_ - this.U_ + 1;
    }
    Yr(t) {
      return this.U_ <= t && t <= this.q_;
    }
    xh(t) {
      return this.U_ === t.Rs() && this.q_ === t.ui();
    }
  }
  function bn(t, i) {
    return null === t || null === i ? t === i : t.xh(i);
  }
  class wn {
    constructor() {
      (this.X_ = new Map()), (this.Ge = null), (this.K_ = !1);
    }
    Z_(t) {
      (this.K_ = t), (this.Ge = null);
    }
    G_(t, i) {
      this.J_(i), (this.Ge = null);
      for (let n = i; n < t.length; ++n) {
        const i = t[n];
        let s = this.X_.get(i.timeWeight);
        void 0 === s && ((s = []), this.X_.set(i.timeWeight, s)),
          s.push({
            index: n,
            time: i.time,
            weight: i.timeWeight,
            originalTime: i.originalTime,
          });
      }
    }
    Q_(t, i) {
      const n = Math.ceil(i / t);
      return (
        (null !== this.Ge && this.Ge.tu === n) ||
          (this.Ge = { Na: this.iu(n), tu: n }),
        this.Ge.Na
      );
    }
    J_(t) {
      if (0 === t) return void this.X_.clear();
      const i = [];
      this.X_.forEach((n, s) => {
        t <= n[0].index
          ? i.push(s)
          : n.splice(
              Pt(n, t, (i) => i.index < t),
              1 / 0
            );
      });
      for (const t of i) this.X_.delete(t);
    }
    iu(t) {
      let i = [];
      for (const n of Array.from(this.X_.keys()).sort((t, i) => i - t)) {
        if (!this.X_.get(n)) continue;
        const s = i;
        i = [];
        const e = s.length;
        let r = 0;
        const h = d(this.X_.get(n)),
          l = h.length;
        let a = 1 / 0,
          o = -1 / 0;
        for (let n = 0; n < l; n++) {
          const l = h[n],
            _ = l.index;
          for (; r < e; ) {
            const t = s[r],
              n = t.index;
            if (!(n < _)) {
              a = n;
              break;
            }
            r++, i.push(t), (o = n), (a = 1 / 0);
          }
          if (a - _ >= t && _ - o >= t) i.push(l), (o = _);
          else if (this.K_) return s;
        }
        for (; r < e; r++) i.push(s[r]);
      }
      return i;
    }
  }
  class gn {
    constructor(t) {
      this.nu = t;
    }
    su() {
      return null === this.nu
        ? null
        : new mn(Math.floor(this.nu.Rs()), Math.ceil(this.nu.ui()));
    }
    eu() {
      return this.nu;
    }
    static ru() {
      return new gn(null);
    }
  }
  function Mn(t, i) {
    return t.weight > i.weight ? t : i;
  }
  class xn {
    constructor(t, i, n, s) {
      (this.h_ = 0),
        (this.hu = null),
        (this.lu = []),
        (this.po = null),
        (this.vo = null),
        (this.au = new wn()),
        (this.ou = new Map()),
        (this._u = gn.ru()),
        (this.uu = !0),
        (this.cu = new k()),
        (this.du = new k()),
        (this.fu = new k()),
        (this.vu = null),
        (this.pu = null),
        (this.mu = []),
        (this._n = i),
        (this.Mo = n),
        (this.bu = i.rightOffset),
        (this.wu = i.barSpacing),
        (this.Hi = t),
        (this.W_ = s),
        this.gu(),
        this.au.Z_(i.uniformDistribution);
    }
    W() {
      return this._n;
    }
    Mu(t) {
      C(this.Mo, t), this.xu(), this.gu();
    }
    Fh(t, i) {
      var n;
      C(this._n, t),
        this._n.fixLeftEdge && this.Su(),
        this._n.fixRightEdge && this.yu(),
        void 0 !== t.barSpacing && this.Hi.Kn(t.barSpacing),
        void 0 !== t.rightOffset && this.Hi.Zn(t.rightOffset),
        void 0 !== t.minBarSpacing &&
          this.Hi.Kn(null !== (n = t.barSpacing) && void 0 !== n ? n : this.wu),
        this.xu(),
        this.gu(),
        this.fu.m();
    }
    vn(t) {
      var i, n;
      return null !==
        (n = null === (i = this.lu[t]) || void 0 === i ? void 0 : i.time) &&
        void 0 !== n
        ? n
        : null;
    }
    $i(t) {
      var i;
      return null !== (i = this.lu[t]) && void 0 !== i ? i : null;
    }
    Ta(t, i) {
      if (this.lu.length < 1) return null;
      if (this.W_.key(t) > this.W_.key(this.lu[this.lu.length - 1].time))
        return i ? this.lu.length - 1 : null;
      const n = Pt(this.lu, this.W_.key(t), (t, i) => this.W_.key(t.time) < i);
      return this.W_.key(t) < this.W_.key(this.lu[n].time) ? (i ? n : null) : n;
    }
    Li() {
      return 0 === this.h_ || 0 === this.lu.length || null === this.hu;
    }
    Ca() {
      return this.lu.length > 0;
    }
    qs() {
      return this.ku(), this._u.su();
    }
    Cu() {
      return this.ku(), this._u.eu();
    }
    Tu() {
      const t = this.qs();
      if (null === t) return null;
      const i = { from: t.Rs(), to: t.ui() };
      return this.Pu(i);
    }
    Pu(t) {
      const i = Math.round(t.from),
        n = Math.round(t.to),
        s = f(this.Ru()),
        e = f(this.Du());
      return {
        from: f(this.$i(Math.max(s, i))),
        to: f(this.$i(Math.min(e, n))),
      };
    }
    Ou(t) {
      return { from: f(this.Ta(t.from, !0)), to: f(this.Ta(t.to, !0)) };
    }
    ji() {
      return this.h_;
    }
    w_(t) {
      if (!isFinite(t) || t <= 0) return;
      if (this.h_ === t) return;
      const i = this.Cu(),
        n = this.h_;
      if (
        ((this.h_ = t),
        (this.uu = !0),
        this._n.lockVisibleTimeRangeOnResize && 0 !== n)
      ) {
        const i = (this.wu * t) / n;
        this.wu = i;
      }
      if (this._n.fixLeftEdge && null !== i && i.Rs() <= 0) {
        const i = n - t;
        (this.bu -= Math.round(i / this.wu) + 1), (this.uu = !0);
      }
      this.Bu(), this.Au();
    }
    zt(t) {
      if (this.Li() || !P(t)) return 0;
      const i = this.Vu() + this.bu - t;
      return this.h_ - (i + 0.5) * this.wu - 1;
    }
    Zs(t, i) {
      const n = this.Vu(),
        s = void 0 === i ? 0 : i.from,
        e = void 0 === i ? t.length : i.to;
      for (let i = s; i < e; i++) {
        const s = t[i].ot,
          e = n + this.bu - s,
          r = this.h_ - (e + 0.5) * this.wu - 1;
        t[i].nt = r;
      }
    }
    zu(t) {
      return Math.ceil(this.Eu(t));
    }
    Zn(t) {
      (this.uu = !0), (this.bu = t), this.Au(), this.Hi.Iu(), this.Hi.Wh();
    }
    ee() {
      return this.wu;
    }
    Kn(t) {
      this.Lu(t), this.Au(), this.Hi.Iu(), this.Hi.Wh();
    }
    Nu() {
      return this.bu;
    }
    Na() {
      if (this.Li()) return null;
      if (null !== this.pu) return this.pu;
      const t = this.wu,
        i =
          ((5 * (this.Hi.W().layout.fontSize + 4)) / 8) *
          (this._n.tickMarkMaxCharacterLength || 8),
        n = Math.round(i / t),
        s = f(this.qs()),
        e = Math.max(s.Rs(), s.Rs() - n),
        r = Math.max(s.ui(), s.ui() - n),
        h = this.au.Q_(t, i),
        l = this.Ru() + n,
        a = this.Du() - n,
        o = this.Fu(),
        _ = this._n.fixLeftEdge || o,
        u = this._n.fixRightEdge || o;
      let c = 0;
      for (const t of h) {
        if (!(e <= t.index && t.index <= r)) continue;
        let n;
        c < this.mu.length
          ? ((n = this.mu[c]),
            (n.coord = this.zt(t.index)),
            (n.label = this.Wu(t)),
            (n.weight = t.weight))
          : ((n = {
              needAlignCoordinate: !1,
              coord: this.zt(t.index),
              label: this.Wu(t),
              weight: t.weight,
            }),
            this.mu.push(n)),
          this.wu > i / 2 && !o
            ? (n.needAlignCoordinate = !1)
            : (n.needAlignCoordinate =
                (_ && t.index <= l) || (u && t.index >= a)),
          c++;
      }
      return (this.mu.length = c), (this.pu = this.mu), this.mu;
    }
    ju() {
      (this.uu = !0), this.Kn(this._n.barSpacing), this.Zn(this._n.rightOffset);
    }
    Hu(t) {
      (this.uu = !0), (this.hu = t), this.Au(), this.Su();
    }
    $u(t, i) {
      const n = this.Eu(t),
        s = this.ee(),
        e = s + i * (s / 10);
      this.Kn(e),
        this._n.rightBarStaysOnScroll || this.Zn(this.Nu() + (n - this.Eu(t)));
    }
    Yo(t) {
      this.po && this.Jo(),
        null === this.vo &&
          null === this.vu &&
          (this.Li() || ((this.vo = t), this.Uu()));
    }
    Xo(t) {
      if (null === this.vu) return;
      const i = wt(this.h_ - t, 0, this.h_),
        n = wt(this.h_ - f(this.vo), 0, this.h_);
      0 !== i && 0 !== n && this.Kn((this.vu.ee * i) / n);
    }
    Ko() {
      null !== this.vo && ((this.vo = null), this.qu());
    }
    Zo(t) {
      null === this.po &&
        null === this.vu &&
        (this.Li() || ((this.po = t), this.Uu()));
    }
    Go(t) {
      if (null === this.po) return;
      const i = (this.po - t) / this.ee();
      (this.bu = f(this.vu).Nu + i), (this.uu = !0), this.Au();
    }
    Jo() {
      null !== this.po && ((this.po = null), this.qu());
    }
    Yu() {
      this.Xu(this._n.rightOffset);
    }
    Xu(t, i = 400) {
      if (!isFinite(t))
        throw new RangeError("offset is required and must be finite number");
      if (!isFinite(i) || i <= 0)
        throw new RangeError(
          "animationDuration (optional) must be finite positive number"
        );
      const n = this.bu,
        s = performance.now();
      this.Hi.qn({
        Ku: (t) => (t - s) / i >= 1,
        Zu: (e) => {
          const r = (e - s) / i;
          return r >= 1 ? t : n + (t - n) * r;
        },
      });
    }
    bt(t, i) {
      (this.uu = !0), (this.lu = t), this.au.G_(t, i), this.Au();
    }
    Gu() {
      return this.cu;
    }
    Ju() {
      return this.du;
    }
    Qu() {
      return this.fu;
    }
    Vu() {
      return this.hu || 0;
    }
    tc(t) {
      const i = t.Y_();
      this.Lu(this.h_ / i),
        (this.bu = t.ui() - this.Vu()),
        this.Au(),
        (this.uu = !0),
        this.Hi.Iu(),
        this.Hi.Wh();
    }
    ic() {
      const t = this.Ru(),
        i = this.Du();
      null !== t && null !== i && this.tc(new mn(t, i + this._n.rightOffset));
    }
    nc(t) {
      const i = new mn(t.from, t.to);
      this.tc(i);
    }
    Ui(t) {
      return void 0 !== this.Mo.timeFormatter
        ? this.Mo.timeFormatter(t.originalTime)
        : this.W_.formatHorzItem(t.time);
    }
    Fu() {
      const { handleScroll: t, handleScale: i } = this.Hi.W();
      return !(
        t.horzTouchDrag ||
        t.mouseWheel ||
        t.pressedMouseMove ||
        t.vertTouchDrag ||
        i.axisDoubleClickReset.time ||
        i.axisPressedMouseMove.time ||
        i.mouseWheel ||
        i.pinch
      );
    }
    Ru() {
      return 0 === this.lu.length ? null : 0;
    }
    Du() {
      return 0 === this.lu.length ? null : this.lu.length - 1;
    }
    sc(t) {
      return (this.h_ - 1 - t) / this.wu;
    }
    Eu(t) {
      const i = this.sc(t),
        n = this.Vu() + this.bu - i;
      return Math.round(1e6 * n) / 1e6;
    }
    Lu(t) {
      const i = this.wu;
      (this.wu = t), this.Bu(), i !== this.wu && ((this.uu = !0), this.ec());
    }
    ku() {
      if (!this.uu) return;
      if (((this.uu = !1), this.Li())) return void this.rc(gn.ru());
      const t = this.Vu(),
        i = this.h_ / this.wu,
        n = this.bu + t,
        s = new mn(n - i + 1, n);
      this.rc(new gn(s));
    }
    Bu() {
      const t = this.hc();
      if ((this.wu < t && ((this.wu = t), (this.uu = !0)), 0 !== this.h_)) {
        const t = 0.5 * this.h_;
        this.wu > t && ((this.wu = t), (this.uu = !0));
      }
    }
    hc() {
      return this._n.fixLeftEdge && this._n.fixRightEdge && 0 !== this.lu.length
        ? this.h_ / this.lu.length
        : this._n.minBarSpacing;
    }
    Au() {
      const t = this.lc();
      this.bu > t && ((this.bu = t), (this.uu = !0));
      const i = this.ac();
      null !== i && this.bu < i && ((this.bu = i), (this.uu = !0));
    }
    ac() {
      const t = this.Ru(),
        i = this.hu;
      if (null === t || null === i) return null;
      return (
        t -
        i -
        1 +
        (this._n.fixLeftEdge ? this.h_ / this.wu : Math.min(2, this.lu.length))
      );
    }
    lc() {
      return this._n.fixRightEdge
        ? 0
        : this.h_ / this.wu - Math.min(2, this.lu.length);
    }
    Uu() {
      this.vu = { ee: this.ee(), Nu: this.Nu() };
    }
    qu() {
      this.vu = null;
    }
    Wu(t) {
      let i = this.ou.get(t.weight);
      return (
        void 0 === i &&
          ((i = new pn((t) => this.oc(t), this.W_)), this.ou.set(t.weight, i)),
        i.j_(t)
      );
    }
    oc(t) {
      return this.W_.formatTickmark(t, this.Mo);
    }
    rc(t) {
      const i = this._u;
      (this._u = t),
        bn(i.su(), this._u.su()) || this.cu.m(),
        bn(i.eu(), this._u.eu()) || this.du.m(),
        this.ec();
    }
    ec() {
      this.pu = null;
    }
    xu() {
      this.ec(), this.ou.clear();
    }
    gu() {
      this.W_.updateFormatter(this.Mo);
    }
    Su() {
      if (!this._n.fixLeftEdge) return;
      const t = this.Ru();
      if (null === t) return;
      const i = this.qs();
      if (null === i) return;
      const n = i.Rs() - t;
      if (n < 0) {
        const t = this.bu - n - 1;
        this.Zn(t);
      }
      this.Bu();
    }
    yu() {
      this.Au(), this.Bu();
    }
  }
  class Sn {
    K(t, i, n) {
      t.useMediaCoordinateSpace((t) => this.Z(t, i, n));
    }
    pl(t, i, n) {
      t.useMediaCoordinateSpace((t) => this._c(t, i, n));
    }
    _c(t, i, n) {}
  }
  class yn extends Sn {
    constructor(t) {
      super(), (this.uc = new Map()), (this.Et = t);
    }
    Z(t) {}
    _c(t) {
      if (!this.Et.kt) return;
      const { context: i, mediaSize: n } = t;
      let s = 0;
      for (const t of this.Et.cc) {
        if (0 === t.Zt.length) continue;
        i.font = t.R;
        const e = this.dc(i, t.Zt);
        e > n.width ? (t.$u = n.width / e) : (t.$u = 1), (s += t.fc * t.$u);
      }
      let e = 0;
      switch (this.Et.vc) {
        case "top":
          e = 0;
          break;
        case "center":
          e = Math.max((n.height - s) / 2, 0);
          break;
        case "bottom":
          e = Math.max(n.height - s, 0);
      }
      i.fillStyle = this.Et.O;
      for (const t of this.Et.cc) {
        i.save();
        let s = 0;
        switch (this.Et.mc) {
          case "left":
            (i.textAlign = "left"), (s = t.fc / 2);
            break;
          case "center":
            (i.textAlign = "center"), (s = n.width / 2);
            break;
          case "right":
            (i.textAlign = "right"), (s = n.width - 1 - t.fc / 2);
        }
        i.translate(s, e),
          (i.textBaseline = "top"),
          (i.font = t.R),
          i.scale(t.$u, t.$u),
          i.fillText(t.Zt, 0, t.bc),
          i.restore(),
          (e += t.fc * t.$u);
      }
    }
    dc(t, i) {
      const n = this.wc(t.font);
      let s = n.get(i);
      return void 0 === s && ((s = t.measureText(i).width), n.set(i, s)), s;
    }
    wc(t) {
      let i = this.uc.get(t);
      return void 0 === i && ((i = new Map()), this.uc.set(t, i)), i;
    }
  }
  class kn {
    constructor(t) {
      (this.ft = !0),
        (this.Ft = { kt: !1, O: "", cc: [], vc: "center", mc: "center" }),
        (this.Wt = new yn(this.Ft)),
        (this.jt = t);
    }
    bt() {
      this.ft = !0;
    }
    gt() {
      return this.ft && (this.Mt(), (this.ft = !1)), this.Wt;
    }
    Mt() {
      const t = this.jt.W(),
        i = this.Ft;
      (i.kt = t.visible),
        i.kt &&
          ((i.O = t.color),
          (i.mc = t.horzAlign),
          (i.vc = t.vertAlign),
          (i.cc = [
            {
              Zt: t.text,
              R: z(t.fontSize, t.fontFamily, t.fontStyle),
              fc: 1.2 * t.fontSize,
              bc: 0,
              $u: 0,
            },
          ]));
    }
  }
  class Cn extends nt {
    constructor(t, i) {
      super(), (this._n = i), (this.mn = new kn(this));
    }
    Tn() {
      return [];
    }
    Cn() {
      return [this.mn];
    }
    W() {
      return this._n;
    }
    Rn() {
      this.mn.bt();
    }
  }
  var Tn, Pn, Rn, Dn, On;
  !(function (t) {
    (t[(t.OnTouchEnd = 0)] = "OnTouchEnd"),
      (t[(t.OnNextTap = 1)] = "OnNextTap");
  })(Tn || (Tn = {}));
  class Bn {
    constructor(t, i, n) {
      (this.gc = []),
        (this.Mc = []),
        (this.h_ = 0),
        (this.xc = null),
        (this.Sc = new k()),
        (this.yc = new k()),
        (this.kc = null),
        (this.Cc = t),
        (this._n = i),
        (this.W_ = n),
        (this.Tc = new E(this)),
        (this.Ml = new xn(this, i.timeScale, this._n.localization, n)),
        (this.vt = new et(this, i.crosshair)),
        (this.Pc = new Yi(i.crosshair)),
        (this.Rc = new Cn(this, i.watermark)),
        this.Dc(),
        this.gc[0].b_(2e3),
        (this.Oc = this.Bc(0)),
        (this.Ac = this.Bc(1));
    }
    ql() {
      this.Vc(ht.ns());
    }
    Wh() {
      this.Vc(ht.ts());
    }
    ra() {
      this.Vc(new ht(1));
    }
    Yl(t) {
      const i = this.zc(t);
      this.Vc(i);
    }
    Ec() {
      return this.xc;
    }
    Ic(t) {
      const i = this.xc;
      (this.xc = t), null !== i && this.Yl(i.Lc), null !== t && this.Yl(t.Lc);
    }
    W() {
      return this._n;
    }
    Fh(t) {
      C(this._n, t),
        this.gc.forEach((i) => i.f_(t)),
        void 0 !== t.timeScale && this.Ml.Fh(t.timeScale),
        void 0 !== t.localization && this.Ml.Mu(t.localization),
        (t.leftPriceScale || t.rightPriceScale) && this.Sc.m(),
        (this.Oc = this.Bc(0)),
        (this.Ac = this.Bc(1)),
        this.ql();
    }
    Nc(t, i) {
      if ("left" === t) return void this.Fh({ leftPriceScale: i });
      if ("right" === t) return void this.Fh({ rightPriceScale: i });
      const n = this.Fc(t);
      null !== n && (n.Dt.Fh(i), this.Sc.m());
    }
    Fc(t) {
      for (const i of this.gc) {
        const n = i.v_(t);
        if (null !== n) return { Ht: i, Dt: n };
      }
      return null;
    }
    St() {
      return this.Ml;
    }
    Wc() {
      return this.gc;
    }
    jc() {
      return this.Rc;
    }
    Hc() {
      return this.vt;
    }
    $c() {
      return this.yc;
    }
    Uc(t, i) {
      t.Ao(i), this.Iu();
    }
    w_(t) {
      (this.h_ = t),
        this.Ml.w_(this.h_),
        this.gc.forEach((i) => i.w_(t)),
        this.Iu();
    }
    Dc(t) {
      const i = new vn(this.Ml, this);
      void 0 !== t ? this.gc.splice(t, 0, i) : this.gc.push(i);
      const n = void 0 === t ? this.gc.length - 1 : t,
        s = ht.ns();
      return s.In(n, { Ln: 0, Nn: !0 }), this.Vc(s), i;
    }
    T_(t, i, n) {
      t.T_(i, n);
    }
    P_(t, i, n) {
      t.P_(i, n), this.Xl(), this.Vc(this.qc(t, 2));
    }
    R_(t, i) {
      t.R_(i), this.Vc(this.qc(t, 2));
    }
    D_(t, i, n) {
      i.To() || t.D_(i, n);
    }
    O_(t, i, n) {
      i.To() || (t.O_(i, n), this.Xl(), this.Vc(this.qc(t, 2)));
    }
    B_(t, i) {
      i.To() || (t.B_(i), this.Vc(this.qc(t, 2)));
    }
    V_(t, i) {
      t.V_(i), this.Vc(this.qc(t, 2));
    }
    Yc(t) {
      this.Ml.Yo(t);
    }
    Xc(t, i) {
      const n = this.St();
      if (n.Li() || 0 === i) return;
      const s = n.ji();
      (t = Math.max(1, Math.min(t, s))), n.$u(t, i), this.Iu();
    }
    Kc(t) {
      this.Zc(0), this.Gc(t), this.Jc();
    }
    Qc(t) {
      this.Ml.Xo(t), this.Iu();
    }
    td() {
      this.Ml.Ko(), this.Wh();
    }
    Zc(t) {
      this.Ml.Zo(t);
    }
    Gc(t) {
      this.Ml.Go(t), this.Iu();
    }
    Jc() {
      this.Ml.Jo(), this.Wh();
    }
    wt() {
      return this.Mc;
    }
    nd(t, i, n, s, e) {
      this.vt.bn(t, i);
      let r = NaN,
        h = this.Ml.zu(t);
      const l = this.Ml.qs();
      null !== l && (h = Math.min(Math.max(l.Rs(), h), l.ui()));
      const a = s.dn(),
        o = a.Ct();
      null !== o && (r = a.fn(i, o)),
        (r = this.Pc.Pa(r, h, s)),
        this.vt.xn(h, r, s),
        this.ra(),
        e || this.yc.m(this.vt.xt(), { x: t, y: i }, n);
    }
    sd(t, i, n) {
      const s = n.dn(),
        e = s.Ct(),
        r = s.Rt(t, f(e)),
        h = this.Ml.Ta(i, !0),
        l = this.Ml.zt(f(h));
      this.nd(l, r, null, n, !0);
    }
    ed(t) {
      this.Hc().yn(), this.ra(), t || this.yc.m(null, null, null);
    }
    Xl() {
      const t = this.vt.Ht();
      if (null !== t) {
        const i = this.vt.gn(),
          n = this.vt.Mn();
        this.nd(i, n, null, t);
      }
      this.vt.Rn();
    }
    rd(t, i, n) {
      const s = this.Ml.vn(0);
      void 0 !== i && void 0 !== n && this.Ml.bt(i, n);
      const e = this.Ml.vn(0),
        r = this.Ml.Vu(),
        h = this.Ml.qs();
      if (null !== h && null !== s && null !== e) {
        const i = h.Yr(r),
          l = this.W_.key(s) > this.W_.key(e),
          a = null !== t && t > r && !l,
          o = this.Ml.W().allowShiftVisibleRangeOnWhitespaceReplacement,
          _ =
            i &&
            (!(void 0 === n) || o) &&
            this.Ml.W().shiftVisibleRangeOnNewBar;
        if (a && !_) {
          const i = t - r;
          this.Ml.Zn(this.Ml.Nu() - i);
        }
      }
      this.Ml.Hu(t);
    }
    Gl(t) {
      null !== t && t.E_();
    }
    _r(t) {
      const i = this.gc.find((i) => i.Wo().includes(t));
      return void 0 === i ? null : i;
    }
    Iu() {
      this.Rc.Rn(), this.gc.forEach((t) => t.E_()), this.Xl();
    }
    S() {
      this.gc.forEach((t) => t.S()),
        (this.gc.length = 0),
        (this._n.localization.priceFormatter = void 0),
        (this._n.localization.percentageFormatter = void 0),
        (this._n.localization.timeFormatter = void 0);
    }
    hd() {
      return this.Tc;
    }
    vr() {
      return this.Tc.W();
    }
    p_() {
      return this.Sc;
    }
    ld(t, i, n) {
      const s = this.gc[0],
        e = this.ad(i, t, s, n);
      return this.Mc.push(e), 1 === this.Mc.length ? this.ql() : this.Wh(), e;
    }
    od(t) {
      const i = this._r(t),
        n = this.Mc.indexOf(t);
      c(-1 !== n, "Series not found"),
        this.Mc.splice(n, 1),
        f(i).$o(t),
        t.S && t.S();
    }
    Ul(t, i) {
      const n = f(this._r(t));
      n.$o(t);
      const s = this.Fc(i);
      if (null === s) {
        const s = t.Xi();
        n.jo(t, i, s);
      } else {
        const e = s.Ht === n ? t.Xi() : void 0;
        s.Ht.jo(t, i, e);
      }
    }
    ic() {
      const t = ht.ts();
      t.jn(), this.Vc(t);
    }
    _d(t) {
      const i = ht.ts();
      i.Un(t), this.Vc(i);
    }
    Xn() {
      const t = ht.ts();
      t.Xn(), this.Vc(t);
    }
    Kn(t) {
      const i = ht.ts();
      i.Kn(t), this.Vc(i);
    }
    Zn(t) {
      const i = ht.ts();
      i.Zn(t), this.Vc(i);
    }
    qn(t) {
      const i = ht.ts();
      i.qn(t), this.Vc(i);
    }
    Hn() {
      const t = ht.ts();
      t.Hn(), this.Vc(t);
    }
    ud() {
      return this._n.rightPriceScale.visible ? "right" : "left";
    }
    dd() {
      return this.Ac;
    }
    q() {
      return this.Oc;
    }
    At(t) {
      const i = this.Ac,
        n = this.Oc;
      if (i === n) return i;
      if (
        ((t = Math.max(0, Math.min(100, Math.round(100 * t)))),
        null === this.kc || this.kc.ks !== n || this.kc.Cs !== i)
      )
        this.kc = { ks: n, Cs: i, fd: new Map() };
      else {
        const i = this.kc.fd.get(t);
        if (void 0 !== i) return i;
      }
      const s = (function (t, i, n) {
        const [s, e, r, h] = S(t),
          [l, a, o, _] = S(i),
          u = [
            m(s + n * (l - s)),
            m(e + n * (a - e)),
            m(r + n * (o - r)),
            b(h + n * (_ - h)),
          ];
        return `rgba(${u[0]}, ${u[1]}, ${u[2]}, ${u[3]})`;
      })(n, i, t / 100);
      return this.kc.fd.set(t, s), s;
    }
    qc(t, i) {
      const n = new ht(i);
      if (null !== t) {
        const s = this.gc.indexOf(t);
        n.In(s, { Ln: i });
      }
      return n;
    }
    zc(t, i) {
      return void 0 === i && (i = 2), this.qc(this._r(t), i);
    }
    Vc(t) {
      this.Cc && this.Cc(t), this.gc.forEach((t) => t.L_().jh().bt());
    }
    ad(t, i, n, s) {
      const e = new qi(this, t, i, n, s),
        r = void 0 !== t.priceScaleId ? t.priceScaleId : this.ud();
      return n.jo(e, r), rt(r) || e.Fh(t), e;
    }
    Bc(t) {
      const i = this._n.layout;
      return "gradient" === i.background.type
        ? 0 === t
          ? i.background.topColor
          : i.background.bottomColor
        : i.background.color;
    }
  }
  function An(t) {
    return !T(t) && !R(t);
  }
  function Vn(t) {
    return T(t);
  }
  !(function (t) {
    (t[(t.Disabled = 0)] = "Disabled"),
      (t[(t.Continuous = 1)] = "Continuous"),
      (t[(t.OnDataUpdate = 2)] = "OnDataUpdate");
  })(Pn || (Pn = {})),
    (function (t) {
      (t[(t.LastBar = 0)] = "LastBar"),
        (t[(t.LastVisible = 1)] = "LastVisible");
    })(Rn || (Rn = {})),
    (function (t) {
      (t.Solid = "solid"), (t.VerticalGradient = "gradient");
    })(Dn || (Dn = {})),
    (function (t) {
      (t[(t.Year = 0)] = "Year"),
        (t[(t.Month = 1)] = "Month"),
        (t[(t.DayOfMonth = 2)] = "DayOfMonth"),
        (t[(t.Time = 3)] = "Time"),
        (t[(t.TimeWithSeconds = 4)] = "TimeWithSeconds");
    })(On || (On = {}));
  const zn = (t) => t.getUTCFullYear();
  function En(t, i, n) {
    return i
      .replace(/yyyy/g, ((t) => at(zn(t), 4))(t))
      .replace(/yy/g, ((t) => at(zn(t) % 100, 2))(t))
      .replace(
        /MMMM/g,
        ((t, i) =>
          new Date(t.getUTCFullYear(), t.getUTCMonth(), 1).toLocaleString(i, {
            month: "long",
          }))(t, n)
      )
      .replace(
        /MMM/g,
        ((t, i) =>
          new Date(t.getUTCFullYear(), t.getUTCMonth(), 1).toLocaleString(i, {
            month: "short",
          }))(t, n)
      )
      .replace(/MM/g, ((t) => at(((t) => t.getUTCMonth() + 1)(t), 2))(t))
      .replace(/dd/g, ((t) => at(((t) => t.getUTCDate())(t), 2))(t));
  }
  class In {
    constructor(t = "yyyy-MM-dd", i = "default") {
      (this.vd = t), (this.pd = i);
    }
    j_(t) {
      return En(t, this.vd, this.pd);
    }
  }
  class Ln {
    constructor(t) {
      this.md = t || "%h:%m:%s";
    }
    j_(t) {
      return this.md
        .replace("%h", at(t.getUTCHours(), 2))
        .replace("%m", at(t.getUTCMinutes(), 2))
        .replace("%s", at(t.getUTCSeconds(), 2));
    }
  }
  const Nn = { bd: "yyyy-MM-dd", wd: "%h:%m:%s", gd: " ", Md: "default" };
  class Fn {
    constructor(t = {}) {
      const i = Object.assign(Object.assign({}, Nn), t);
      (this.xd = new In(i.bd, i.Md)),
        (this.Sd = new Ln(i.wd)),
        (this.yd = i.gd);
    }
    j_(t) {
      return `${this.xd.j_(t)}${this.yd}${this.Sd.j_(t)}`;
    }
  }
  function Wn(t) {
    return 60 * t * 60 * 1e3;
  }
  function jn(t) {
    return 60 * t * 1e3;
  }
  const Hn = [
    { kd: (($n = 1), 1e3 * $n), Cd: 10 },
    { kd: jn(1), Cd: 20 },
    { kd: jn(5), Cd: 21 },
    { kd: jn(30), Cd: 22 },
    { kd: Wn(1), Cd: 30 },
    { kd: Wn(3), Cd: 31 },
    { kd: Wn(6), Cd: 32 },
    { kd: Wn(12), Cd: 33 },
  ];
  var $n;
  function Un(t, i) {
    if (t.getUTCFullYear() !== i.getUTCFullYear()) return 70;
    if (t.getUTCMonth() !== i.getUTCMonth()) return 60;
    if (t.getUTCDate() !== i.getUTCDate()) return 50;
    for (let n = Hn.length - 1; n >= 0; --n)
      if (
        Math.floor(i.getTime() / Hn[n].kd) !==
        Math.floor(t.getTime() / Hn[n].kd)
      )
        return Hn[n].Cd;
    return 0;
  }
  function qn(t) {
    let i = t;
    if ((R(t) && (i = Xn(t)), !An(i)))
      throw new Error("time must be of type BusinessDay");
    const n = new Date(Date.UTC(i.year, i.month - 1, i.day, 0, 0, 0, 0));
    return { Td: Math.round(n.getTime() / 1e3), Pd: i };
  }
  function Yn(t) {
    if (!Vn(t)) throw new Error("time must be of type isUTCTimestamp");
    return { Td: t };
  }
  function Xn(t) {
    const i = new Date(t);
    if (isNaN(i.getTime()))
      throw new Error(`Invalid date string=${t}, expected format=yyyy-mm-dd`);
    return {
      day: i.getUTCDate(),
      month: i.getUTCMonth() + 1,
      year: i.getUTCFullYear(),
    };
  }
  function Kn(t) {
    R(t.time) && (t.time = Xn(t.time));
  }
  class Zn {
    options() {
      return this._n;
    }
    setOptions(t) {
      (this._n = t), this.updateFormatter(t.localization);
    }
    preprocessData(t) {
      Array.isArray(t)
        ? (function (t) {
            t.forEach(Kn);
          })(t)
        : Kn(t);
    }
    createConverterToInternalObj(t) {
      return f(
        (function (t) {
          return 0 === t.length
            ? null
            : An(t[0].time) || R(t[0].time)
            ? qn
            : Yn;
        })(t)
      );
    }
    key(t) {
      return "object" == typeof t && "Td" in t
        ? t.Td
        : this.key(this.convertHorzItemToInternal(t));
    }
    cacheKey(t) {
      const i = t;
      return void 0 === i.Pd
        ? new Date(1e3 * i.Td).getTime()
        : new Date(Date.UTC(i.Pd.year, i.Pd.month - 1, i.Pd.day)).getTime();
    }
    convertHorzItemToInternal(t) {
      return Vn((i = t)) ? Yn(i) : An(i) ? qn(i) : qn(Xn(i));
      var i;
    }
    updateFormatter(t) {
      if (!this._n) return;
      const i = t.dateFormat;
      this._n.timeScale.timeVisible
        ? (this.Rd = new Fn({
            bd: i,
            wd: this._n.timeScale.secondsVisible ? "%h:%m:%s" : "%h:%m",
            gd: "   ",
            Md: t.locale,
          }))
        : (this.Rd = new In(i, t.locale));
    }
    formatHorzItem(t) {
      const i = t;
      return this.Rd.j_(new Date(1e3 * i.Td));
    }
    formatTickmark(t, i) {
      const n = (function (t, i, n) {
          switch (t) {
            case 0:
            case 10:
              return i ? (n ? 4 : 3) : 2;
            case 20:
            case 21:
            case 22:
            case 30:
            case 31:
            case 32:
            case 33:
              return i ? 3 : 2;
            case 50:
              return 2;
            case 60:
              return 1;
            case 70:
              return 0;
          }
        })(
          t.weight,
          this._n.timeScale.timeVisible,
          this._n.timeScale.secondsVisible
        ),
        s = this._n.timeScale;
      if (void 0 !== s.tickMarkFormatter) {
        const e = s.tickMarkFormatter(t.originalTime, n, i.locale);
        if (null !== e) return e;
      }
      return (function (t, i, n) {
        const s = {};
        switch (i) {
          case 0:
            s.year = "numeric";
            break;
          case 1:
            s.month = "short";
            break;
          case 2:
            s.day = "numeric";
            break;
          case 3:
            (s.hour12 = !1), (s.hour = "2-digit"), (s.minute = "2-digit");
            break;
          case 4:
            (s.hour12 = !1),
              (s.hour = "2-digit"),
              (s.minute = "2-digit"),
              (s.second = "2-digit");
        }
        const e =
          void 0 === t.Pd
            ? new Date(1e3 * t.Td)
            : new Date(Date.UTC(t.Pd.year, t.Pd.month - 1, t.Pd.day));
        return new Date(
          e.getUTCFullYear(),
          e.getUTCMonth(),
          e.getUTCDate(),
          e.getUTCHours(),
          e.getUTCMinutes(),
          e.getUTCSeconds(),
          e.getUTCMilliseconds()
        ).toLocaleString(n, s);
      })(t.time, n, i.locale);
    }
    maxTickMarkWeight(t) {
      let i = t.reduce(Mn, t[0]).weight;
      return i > 30 && i < 50 && (i = 30), i;
    }
    fillWeightsForPoints(t, i) {
      !(function (t, i = 0) {
        if (0 === t.length) return;
        let n = 0 === i ? null : t[i - 1].time.Td,
          s = null !== n ? new Date(1e3 * n) : null,
          e = 0;
        for (let r = i; r < t.length; ++r) {
          const i = t[r],
            h = new Date(1e3 * i.time.Td);
          null !== s && (i.timeWeight = Un(h, s)),
            (e += i.time.Td - (n || i.time.Td)),
            (n = i.time.Td),
            (s = h);
        }
        if (0 === i && t.length > 1) {
          const i = Math.ceil(e / (t.length - 1)),
            n = new Date(1e3 * (t[0].time.Td - i));
          t[0].timeWeight = Un(new Date(1e3 * t[0].time.Td), n);
        }
      })(t, i);
    }
    static Dd(t) {
      return C(
        { localization: { dateFormat: "dd MMM 'yy" } },
        null != t ? t : {}
      );
    }
  }
  function Gn(t) {
    var i = t.width,
      n = t.height;
    if (i < 0) throw new Error("Negative width is not allowed for Size");
    if (n < 0) throw new Error("Negative height is not allowed for Size");
    return { width: i, height: n };
  }
  function Jn(t, i) {
    return t.width === i.width && t.height === i.height;
  }
  var Qn = (function () {
    function t(t) {
      var i = this;
      (this._resolutionListener = function () {
        return i._onResolutionChanged();
      }),
        (this._resolutionMediaQueryList = null),
        (this._observers = []),
        (this._window = t),
        this._installResolutionListener();
    }
    return (
      (t.prototype.dispose = function () {
        this._uninstallResolutionListener(), (this._window = null);
      }),
      Object.defineProperty(t.prototype, "value", {
        get: function () {
          return this._window.devicePixelRatio;
        },
        enumerable: !1,
        configurable: !0,
      }),
      (t.prototype.subscribe = function (t) {
        var i = this,
          n = { next: t };
        return (
          this._observers.push(n),
          {
            unsubscribe: function () {
              i._observers = i._observers.filter(function (t) {
                return t !== n;
              });
            },
          }
        );
      }),
      (t.prototype._installResolutionListener = function () {
        if (null !== this._resolutionMediaQueryList)
          throw new Error("Resolution listener is already installed");
        var t = this._window.devicePixelRatio;
        (this._resolutionMediaQueryList = this._window.matchMedia(
          "all and (resolution: ".concat(t, "dppx)")
        )),
          this._resolutionMediaQueryList.addListener(this._resolutionListener);
      }),
      (t.prototype._uninstallResolutionListener = function () {
        null !== this._resolutionMediaQueryList &&
          (this._resolutionMediaQueryList.removeListener(
            this._resolutionListener
          ),
          (this._resolutionMediaQueryList = null));
      }),
      (t.prototype._reinstallResolutionListener = function () {
        this._uninstallResolutionListener(), this._installResolutionListener();
      }),
      (t.prototype._onResolutionChanged = function () {
        var t = this;
        this._observers.forEach(function (i) {
          return i.next(t._window.devicePixelRatio);
        }),
          this._reinstallResolutionListener();
      }),
      t
    );
  })();
  var ts = (function () {
    function t(t, i, n) {
      var s;
      (this._canvasElement = null),
        (this._bitmapSizeChangedListeners = []),
        (this._suggestedBitmapSize = null),
        (this._suggestedBitmapSizeChangedListeners = []),
        (this._devicePixelRatioObservable = null),
        (this._canvasElementResizeObserver = null),
        (this._canvasElement = t),
        (this._canvasElementClientSize = Gn({
          width: this._canvasElement.clientWidth,
          height: this._canvasElement.clientHeight,
        })),
        (this._transformBitmapSize =
          null != i
            ? i
            : function (t) {
                return t;
              }),
        (this._allowResizeObserver =
          null === (s = null == n ? void 0 : n.allowResizeObserver) ||
          void 0 === s ||
          s),
        this._chooseAndInitObserver();
    }
    return (
      (t.prototype.dispose = function () {
        var t, i;
        if (null === this._canvasElement) throw new Error("Object is disposed");
        null === (t = this._canvasElementResizeObserver) ||
          void 0 === t ||
          t.disconnect(),
          (this._canvasElementResizeObserver = null),
          null === (i = this._devicePixelRatioObservable) ||
            void 0 === i ||
            i.dispose(),
          (this._devicePixelRatioObservable = null),
          (this._suggestedBitmapSizeChangedListeners.length = 0),
          (this._bitmapSizeChangedListeners.length = 0),
          (this._canvasElement = null);
      }),
      Object.defineProperty(t.prototype, "canvasElement", {
        get: function () {
          if (null === this._canvasElement)
            throw new Error("Object is disposed");
          return this._canvasElement;
        },
        enumerable: !1,
        configurable: !0,
      }),
      Object.defineProperty(t.prototype, "canvasElementClientSize", {
        get: function () {
          return this._canvasElementClientSize;
        },
        enumerable: !1,
        configurable: !0,
      }),
      Object.defineProperty(t.prototype, "bitmapSize", {
        get: function () {
          return Gn({
            width: this.canvasElement.width,
            height: this.canvasElement.height,
          });
        },
        enumerable: !1,
        configurable: !0,
      }),
      (t.prototype.resizeCanvasElement = function (t) {
        (this._canvasElementClientSize = Gn(t)),
          (this.canvasElement.style.width = "".concat(
            this._canvasElementClientSize.width,
            "px"
          )),
          (this.canvasElement.style.height = "".concat(
            this._canvasElementClientSize.height,
            "px"
          )),
          this._invalidateBitmapSize();
      }),
      (t.prototype.subscribeBitmapSizeChanged = function (t) {
        this._bitmapSizeChangedListeners.push(t);
      }),
      (t.prototype.unsubscribeBitmapSizeChanged = function (t) {
        this._bitmapSizeChangedListeners =
          this._bitmapSizeChangedListeners.filter(function (i) {
            return i !== t;
          });
      }),
      Object.defineProperty(t.prototype, "suggestedBitmapSize", {
        get: function () {
          return this._suggestedBitmapSize;
        },
        enumerable: !1,
        configurable: !0,
      }),
      (t.prototype.subscribeSuggestedBitmapSizeChanged = function (t) {
        this._suggestedBitmapSizeChangedListeners.push(t);
      }),
      (t.prototype.unsubscribeSuggestedBitmapSizeChanged = function (t) {
        this._suggestedBitmapSizeChangedListeners =
          this._suggestedBitmapSizeChangedListeners.filter(function (i) {
            return i !== t;
          });
      }),
      (t.prototype.applySuggestedBitmapSize = function () {
        if (null !== this._suggestedBitmapSize) {
          var t = this._suggestedBitmapSize;
          (this._suggestedBitmapSize = null),
            this._resizeBitmap(t),
            this._emitSuggestedBitmapSizeChanged(t, this._suggestedBitmapSize);
        }
      }),
      (t.prototype._resizeBitmap = function (t) {
        var i = this.bitmapSize;
        Jn(i, t) ||
          ((this.canvasElement.width = t.width),
          (this.canvasElement.height = t.height),
          this._emitBitmapSizeChanged(i, t));
      }),
      (t.prototype._emitBitmapSizeChanged = function (t, i) {
        var n = this;
        this._bitmapSizeChangedListeners.forEach(function (s) {
          return s.call(n, t, i);
        });
      }),
      (t.prototype._suggestNewBitmapSize = function (t) {
        var i = this._suggestedBitmapSize,
          n = Gn(this._transformBitmapSize(t, this._canvasElementClientSize)),
          s = Jn(this.bitmapSize, n) ? null : n;
        (null === i && null === s) ||
          (null !== i && null !== s && Jn(i, s)) ||
          ((this._suggestedBitmapSize = s),
          this._emitSuggestedBitmapSizeChanged(i, s));
      }),
      (t.prototype._emitSuggestedBitmapSizeChanged = function (t, i) {
        var n = this;
        this._suggestedBitmapSizeChangedListeners.forEach(function (s) {
          return s.call(n, t, i);
        });
      }),
      (t.prototype._chooseAndInitObserver = function () {
        var t = this;
        this._allowResizeObserver
          ? new Promise(function (t) {
              var i = new ResizeObserver(function (n) {
                t(
                  n.every(function (t) {
                    return "devicePixelContentBoxSize" in t;
                  })
                ),
                  i.disconnect();
              });
              i.observe(document.body, { box: "device-pixel-content-box" });
            })
              .catch(function () {
                return !1;
              })
              .then(function (i) {
                return i
                  ? t._initResizeObserver()
                  : t._initDevicePixelRatioObservable();
              })
          : this._initDevicePixelRatioObservable();
      }),
      (t.prototype._initDevicePixelRatioObservable = function () {
        var t = this;
        if (null !== this._canvasElement) {
          var i = is(this._canvasElement);
          if (null === i)
            throw new Error("No window is associated with the canvas");
          (this._devicePixelRatioObservable = (function (t) {
            return new Qn(t);
          })(i)),
            this._devicePixelRatioObservable.subscribe(function () {
              return t._invalidateBitmapSize();
            }),
            this._invalidateBitmapSize();
        }
      }),
      (t.prototype._invalidateBitmapSize = function () {
        var t, i;
        if (null !== this._canvasElement) {
          var n = is(this._canvasElement);
          if (null !== n) {
            var s =
                null !==
                  (i =
                    null === (t = this._devicePixelRatioObservable) ||
                    void 0 === t
                      ? void 0
                      : t.value) && void 0 !== i
                  ? i
                  : n.devicePixelRatio,
              e = this._canvasElement.getClientRects(),
              r =
                void 0 !== e[0]
                  ? (function (t, i) {
                      return Gn({
                        width:
                          Math.round(t.left * i + t.width * i) -
                          Math.round(t.left * i),
                        height:
                          Math.round(t.top * i + t.height * i) -
                          Math.round(t.top * i),
                      });
                    })(e[0], s)
                  : Gn({
                      width: this._canvasElementClientSize.width * s,
                      height: this._canvasElementClientSize.height * s,
                    });
            this._suggestNewBitmapSize(r);
          }
        }
      }),
      (t.prototype._initResizeObserver = function () {
        var t = this;
        null !== this._canvasElement &&
          ((this._canvasElementResizeObserver = new ResizeObserver(function (
            i
          ) {
            var n = i.find(function (i) {
              return i.target === t._canvasElement;
            });
            if (
              n &&
              n.devicePixelContentBoxSize &&
              n.devicePixelContentBoxSize[0]
            ) {
              var s = n.devicePixelContentBoxSize[0],
                e = Gn({ width: s.inlineSize, height: s.blockSize });
              t._suggestNewBitmapSize(e);
            }
          })),
          this._canvasElementResizeObserver.observe(this._canvasElement, {
            box: "device-pixel-content-box",
          }));
      }),
      t
    );
  })();
  function is(t) {
    return t.ownerDocument.defaultView;
  }
  var ns = (function () {
    function t(t, i, n) {
      if (0 === i.width || 0 === i.height)
        throw new TypeError(
          "Rendering target could only be created on a media with positive width and height"
        );
      if (((this._mediaSize = i), 0 === n.width || 0 === n.height))
        throw new TypeError(
          "Rendering target could only be created using a bitmap with positive integer width and height"
        );
      (this._bitmapSize = n), (this._context = t);
    }
    return (
      (t.prototype.useMediaCoordinateSpace = function (t) {
        try {
          return (
            this._context.save(),
            this._context.setTransform(1, 0, 0, 1, 0, 0),
            this._context.scale(
              this._horizontalPixelRatio,
              this._verticalPixelRatio
            ),
            t({ context: this._context, mediaSize: this._mediaSize })
          );
        } finally {
          this._context.restore();
        }
      }),
      (t.prototype.useBitmapCoordinateSpace = function (t) {
        try {
          return (
            this._context.save(),
            this._context.setTransform(1, 0, 0, 1, 0, 0),
            t({
              context: this._context,
              mediaSize: this._mediaSize,
              bitmapSize: this._bitmapSize,
              horizontalPixelRatio: this._horizontalPixelRatio,
              verticalPixelRatio: this._verticalPixelRatio,
            })
          );
        } finally {
          this._context.restore();
        }
      }),
      Object.defineProperty(t.prototype, "_horizontalPixelRatio", {
        get: function () {
          return this._bitmapSize.width / this._mediaSize.width;
        },
        enumerable: !1,
        configurable: !0,
      }),
      Object.defineProperty(t.prototype, "_verticalPixelRatio", {
        get: function () {
          return this._bitmapSize.height / this._mediaSize.height;
        },
        enumerable: !1,
        configurable: !0,
      }),
      t
    );
  })();
  function ss(t, i) {
    var n = t.canvasElementClientSize;
    if (0 === n.width || 0 === n.height) return null;
    var s = t.bitmapSize;
    if (0 === s.width || 0 === s.height) return null;
    var e = t.canvasElement.getContext("2d", i);
    return null === e ? null : new ns(e, n, s);
  }
  const es = "undefined" != typeof window;
  function rs() {
    return (
      !!es && window.navigator.userAgent.toLowerCase().indexOf("firefox") > -1
    );
  }
  function hs() {
    return !!es && /iPhone|iPad|iPod/.test(window.navigator.platform);
  }
  function ls(t) {
    return t + (t % 2);
  }
  function as(t, i) {
    return t.Od - i.Od;
  }
  function os(t, i, n) {
    const s = (t.Od - i.Od) / (t.ot - i.ot);
    return Math.sign(s) * Math.min(Math.abs(s), n);
  }
  class _s {
    constructor(t, i, n, s) {
      (this.Bd = null),
        (this.Ad = null),
        (this.Vd = null),
        (this.zd = null),
        (this.Ed = null),
        (this.Id = 0),
        (this.Ld = 0),
        (this.Nd = t),
        (this.Fd = i),
        (this.Wd = n),
        (this.ss = s);
    }
    jd(t, i) {
      if (null !== this.Bd) {
        if (this.Bd.ot === i) return void (this.Bd.Od = t);
        if (Math.abs(this.Bd.Od - t) < this.ss) return;
      }
      (this.zd = this.Vd),
        (this.Vd = this.Ad),
        (this.Ad = this.Bd),
        (this.Bd = { ot: i, Od: t });
    }
    Pr(t, i) {
      if (null === this.Bd || null === this.Ad) return;
      if (i - this.Bd.ot > 50) return;
      let n = 0;
      const s = os(this.Bd, this.Ad, this.Fd),
        e = as(this.Bd, this.Ad),
        r = [s],
        h = [e];
      if (((n += e), null !== this.Vd)) {
        const t = os(this.Ad, this.Vd, this.Fd);
        if (Math.sign(t) === Math.sign(s)) {
          const i = as(this.Ad, this.Vd);
          if ((r.push(t), h.push(i), (n += i), null !== this.zd)) {
            const t = os(this.Vd, this.zd, this.Fd);
            if (Math.sign(t) === Math.sign(s)) {
              const i = as(this.Vd, this.zd);
              r.push(t), h.push(i), (n += i);
            }
          }
        }
      }
      let l = 0;
      for (let t = 0; t < r.length; ++t) l += (h[t] / n) * r[t];
      Math.abs(l) < this.Nd ||
        ((this.Ed = { Od: t, ot: i }),
        (this.Ld = l),
        (this.Id = (function (t, i) {
          const n = Math.log(i);
          return Math.log((1 * n) / -t) / n;
        })(Math.abs(l), this.Wd)));
    }
    Zu(t) {
      const i = f(this.Ed),
        n = t - i.ot;
      return i.Od + (this.Ld * (Math.pow(this.Wd, n) - 1)) / Math.log(this.Wd);
    }
    Ku(t) {
      return null === this.Ed || this.Hd(t) === this.Id;
    }
    Hd(t) {
      const i = t - f(this.Ed).ot;
      return Math.min(i, this.Id);
    }
  }
  function us(t, i) {
    const n = f(t.ownerDocument).createElement("canvas");
    t.appendChild(n);
    const s = (function (t, i) {
      if ("device-pixel-content-box" === i.type)
        return new ts(t, i.transform, i.options);
      throw new Error("Unsupported binding target");
    })(n, {
      type: "device-pixel-content-box",
      options: { allowResizeObserver: !1 },
      transform: (t, i) => ({
        width: Math.max(t.width, i.width),
        height: Math.max(t.height, i.height),
      }),
    });
    return s.resizeCanvasElement(i), s;
  }
  function cs(t) {
    var i;
    (t.width = 1),
      (t.height = 1),
      null === (i = t.getContext("2d")) ||
        void 0 === i ||
        i.clearRect(0, 0, 1, 1);
  }
  function ds(t, i, n, s) {
    t.pl && t.pl(i, n, s);
  }
  function fs(t, i, n, s) {
    t.K(i, n, s);
  }
  function vs(t, i, n, s) {
    const e = t(n, s);
    for (const t of e) {
      const n = t.gt();
      null !== n && i(n);
    }
  }
  function ps(t) {
    es &&
      void 0 !== window.chrome &&
      t.addEventListener("mousedown", (t) => {
        if (1 === t.button) return t.preventDefault(), !1;
      });
  }
  class ms {
    constructor(t, i, n) {
      (this.$d = 0),
        (this.Ud = null),
        (this.qd = {
          nt: Number.NEGATIVE_INFINITY,
          st: Number.POSITIVE_INFINITY,
        }),
        (this.Yd = 0),
        (this.Xd = null),
        (this.Kd = {
          nt: Number.NEGATIVE_INFINITY,
          st: Number.POSITIVE_INFINITY,
        }),
        (this.Zd = null),
        (this.Gd = !1),
        (this.Jd = null),
        (this.Qd = null),
        (this.tf = !1),
        (this.if = !1),
        (this.nf = !1),
        (this.sf = null),
        (this.ef = null),
        (this.rf = null),
        (this.hf = null),
        (this.lf = null),
        (this.af = null),
        (this._f = null),
        (this.uf = 0),
        (this.cf = !1),
        (this.df = !1),
        (this.ff = !1),
        (this.vf = 0),
        (this.pf = null),
        (this.mf = !hs()),
        (this.bf = (t) => {
          this.wf(t);
        }),
        (this.gf = (t) => {
          if (this.Mf(t)) {
            const i = this.xf(t);
            if ((++this.Yd, this.Xd && this.Yd > 1)) {
              const { Sf: n } = this.yf(gs(t), this.Kd);
              n < 30 && !this.nf && this.kf(i, this.Tf.Cf), this.Pf();
            }
          } else {
            const i = this.xf(t);
            if ((++this.$d, this.Ud && this.$d > 1)) {
              const { Sf: n } = this.yf(gs(t), this.qd);
              n < 5 && !this.if && this.Rf(i, this.Tf.Df), this.Of();
            }
          }
        }),
        (this.Bf = t),
        (this.Tf = i),
        (this._n = n),
        this.Af();
    }
    S() {
      null !== this.sf && (this.sf(), (this.sf = null)),
        null !== this.ef && (this.ef(), (this.ef = null)),
        null !== this.hf && (this.hf(), (this.hf = null)),
        null !== this.lf && (this.lf(), (this.lf = null)),
        null !== this.af && (this.af(), (this.af = null)),
        null !== this.rf && (this.rf(), (this.rf = null)),
        this.Vf(),
        this.Of();
    }
    zf(t) {
      this.hf && this.hf();
      const i = this.Ef.bind(this);
      if (
        ((this.hf = () => {
          this.Bf.removeEventListener("mousemove", i);
        }),
        this.Bf.addEventListener("mousemove", i),
        this.Mf(t))
      )
        return;
      const n = this.xf(t);
      this.Rf(n, this.Tf.If), (this.mf = !0);
    }
    Of() {
      null !== this.Ud && clearTimeout(this.Ud),
        (this.$d = 0),
        (this.Ud = null),
        (this.qd = {
          nt: Number.NEGATIVE_INFINITY,
          st: Number.POSITIVE_INFINITY,
        });
    }
    Pf() {
      null !== this.Xd && clearTimeout(this.Xd),
        (this.Yd = 0),
        (this.Xd = null),
        (this.Kd = {
          nt: Number.NEGATIVE_INFINITY,
          st: Number.POSITIVE_INFINITY,
        });
    }
    Ef(t) {
      if (this.ff || null !== this.Qd) return;
      if (this.Mf(t)) return;
      const i = this.xf(t);
      this.Rf(i, this.Tf.Lf), (this.mf = !0);
    }
    Nf(t) {
      const i = xs(t.changedTouches, f(this.pf));
      if (null === i) return;
      if (((this.vf = Ms(t)), null !== this._f)) return;
      if (this.df) return;
      this.cf = !0;
      const n = this.yf(gs(i), f(this.Qd)),
        { Ff: s, Wf: e, Sf: r } = n;
      if (this.tf || !(r < 5)) {
        if (!this.tf) {
          const t = 0.5 * s,
            i = e >= t && !this._n.jf(),
            n = t > e && !this._n.Hf();
          i || n || (this.df = !0),
            (this.tf = !0),
            (this.nf = !0),
            this.Vf(),
            this.Pf();
        }
        if (!this.df) {
          const n = this.xf(t, i);
          this.kf(n, this.Tf.$f), ws(t);
        }
      }
    }
    Uf(t) {
      if (0 !== t.button) return;
      const i = this.yf(gs(t), f(this.Jd)),
        { Sf: n } = i;
      if ((n >= 5 && ((this.if = !0), this.Of()), this.if)) {
        const i = this.xf(t);
        this.Rf(i, this.Tf.qf);
      }
    }
    yf(t, i) {
      const n = Math.abs(i.nt - t.nt),
        s = Math.abs(i.st - t.st);
      return { Ff: n, Wf: s, Sf: n + s };
    }
    Yf(t) {
      let i = xs(t.changedTouches, f(this.pf));
      if (
        (null === i && 0 === t.touches.length && (i = t.changedTouches[0]),
        null === i)
      )
        return;
      (this.pf = null),
        (this.vf = Ms(t)),
        this.Vf(),
        (this.Qd = null),
        this.af && (this.af(), (this.af = null));
      const n = this.xf(t, i);
      if ((this.kf(n, this.Tf.Xf), ++this.Yd, this.Xd && this.Yd > 1)) {
        const { Sf: t } = this.yf(gs(i), this.Kd);
        t < 30 && !this.nf && this.kf(n, this.Tf.Cf), this.Pf();
      } else this.nf || (this.kf(n, this.Tf.Kf), this.Tf.Kf && ws(t));
      0 === this.Yd && ws(t),
        0 === t.touches.length && this.Gd && ((this.Gd = !1), ws(t));
    }
    wf(t) {
      if (0 !== t.button) return;
      const i = this.xf(t);
      if (
        ((this.Jd = null),
        (this.ff = !1),
        this.lf && (this.lf(), (this.lf = null)),
        rs())
      ) {
        this.Bf.ownerDocument.documentElement.removeEventListener(
          "mouseleave",
          this.bf
        );
      }
      if (!this.Mf(t))
        if ((this.Rf(i, this.Tf.Zf), ++this.$d, this.Ud && this.$d > 1)) {
          const { Sf: n } = this.yf(gs(t), this.qd);
          n < 5 && !this.if && this.Rf(i, this.Tf.Df), this.Of();
        } else this.if || this.Rf(i, this.Tf.Gf);
    }
    Vf() {
      null !== this.Zd && (clearTimeout(this.Zd), (this.Zd = null));
    }
    Jf(t) {
      if (null !== this.pf) return;
      const i = t.changedTouches[0];
      (this.pf = i.identifier), (this.vf = Ms(t));
      const n = this.Bf.ownerDocument.documentElement;
      (this.nf = !1),
        (this.tf = !1),
        (this.df = !1),
        (this.Qd = gs(i)),
        this.af && (this.af(), (this.af = null));
      {
        const i = this.Nf.bind(this),
          s = this.Yf.bind(this);
        (this.af = () => {
          n.removeEventListener("touchmove", i),
            n.removeEventListener("touchend", s);
        }),
          n.addEventListener("touchmove", i, { passive: !1 }),
          n.addEventListener("touchend", s, { passive: !1 }),
          this.Vf(),
          (this.Zd = setTimeout(this.Qf.bind(this, t), 240));
      }
      const s = this.xf(t, i);
      this.kf(s, this.Tf.tv),
        this.Xd ||
          ((this.Yd = 0),
          (this.Xd = setTimeout(this.Pf.bind(this), 500)),
          (this.Kd = gs(i)));
    }
    iv(t) {
      if (0 !== t.button) return;
      const i = this.Bf.ownerDocument.documentElement;
      rs() && i.addEventListener("mouseleave", this.bf),
        (this.if = !1),
        (this.Jd = gs(t)),
        this.lf && (this.lf(), (this.lf = null));
      {
        const t = this.Uf.bind(this),
          n = this.wf.bind(this);
        (this.lf = () => {
          i.removeEventListener("mousemove", t),
            i.removeEventListener("mouseup", n);
        }),
          i.addEventListener("mousemove", t),
          i.addEventListener("mouseup", n);
      }
      if (((this.ff = !0), this.Mf(t))) return;
      const n = this.xf(t);
      this.Rf(n, this.Tf.nv),
        this.Ud ||
          ((this.$d = 0),
          (this.Ud = setTimeout(this.Of.bind(this), 500)),
          (this.qd = gs(t)));
    }
    Af() {
      this.Bf.addEventListener("mouseenter", this.zf.bind(this)),
        this.Bf.addEventListener("touchcancel", this.Vf.bind(this));
      {
        const t = this.Bf.ownerDocument,
          i = (t) => {
            this.Tf.sv &&
              ((t.composed && this.Bf.contains(t.composedPath()[0])) ||
                (t.target && this.Bf.contains(t.target)) ||
                this.Tf.sv());
          };
        (this.ef = () => {
          t.removeEventListener("touchstart", i);
        }),
          (this.sf = () => {
            t.removeEventListener("mousedown", i);
          }),
          t.addEventListener("mousedown", i),
          t.addEventListener("touchstart", i, { passive: !0 });
      }
      hs() &&
        ((this.rf = () => {
          this.Bf.removeEventListener("dblclick", this.gf);
        }),
        this.Bf.addEventListener("dblclick", this.gf)),
        this.Bf.addEventListener("mouseleave", this.ev.bind(this)),
        this.Bf.addEventListener("touchstart", this.Jf.bind(this), {
          passive: !0,
        }),
        ps(this.Bf),
        this.Bf.addEventListener("mousedown", this.iv.bind(this)),
        this.rv(),
        this.Bf.addEventListener("touchmove", () => {}, { passive: !1 });
    }
    rv() {
      (void 0 === this.Tf.hv &&
        void 0 === this.Tf.lv &&
        void 0 === this.Tf.av) ||
        (this.Bf.addEventListener("touchstart", (t) => this.ov(t.touches), {
          passive: !0,
        }),
        this.Bf.addEventListener(
          "touchmove",
          (t) => {
            if (
              2 === t.touches.length &&
              null !== this._f &&
              void 0 !== this.Tf.lv
            ) {
              const i = bs(t.touches[0], t.touches[1]) / this.uf;
              this.Tf.lv(this._f, i), ws(t);
            }
          },
          { passive: !1 }
        ),
        this.Bf.addEventListener("touchend", (t) => {
          this.ov(t.touches);
        }));
    }
    ov(t) {
      1 === t.length && (this.cf = !1),
        2 !== t.length || this.cf || this.Gd ? this._v() : this.uv(t);
    }
    uv(t) {
      const i = this.Bf.getBoundingClientRect() || { left: 0, top: 0 };
      (this._f = {
        nt: (t[0].clientX - i.left + (t[1].clientX - i.left)) / 2,
        st: (t[0].clientY - i.top + (t[1].clientY - i.top)) / 2,
      }),
        (this.uf = bs(t[0], t[1])),
        void 0 !== this.Tf.hv && this.Tf.hv(),
        this.Vf();
    }
    _v() {
      null !== this._f &&
        ((this._f = null), void 0 !== this.Tf.av && this.Tf.av());
    }
    ev(t) {
      if ((this.hf && this.hf(), this.Mf(t))) return;
      if (!this.mf) return;
      const i = this.xf(t);
      this.Rf(i, this.Tf.cv), (this.mf = !hs());
    }
    Qf(t) {
      const i = xs(t.touches, f(this.pf));
      if (null === i) return;
      const n = this.xf(t, i);
      this.kf(n, this.Tf.dv), (this.nf = !0), (this.Gd = !0);
    }
    Mf(t) {
      return t.sourceCapabilities &&
        void 0 !== t.sourceCapabilities.firesTouchEvents
        ? t.sourceCapabilities.firesTouchEvents
        : Ms(t) < this.vf + 500;
    }
    kf(t, i) {
      i && i.call(this.Tf, t);
    }
    Rf(t, i) {
      i && i.call(this.Tf, t);
    }
    xf(t, i) {
      const n = i || t,
        s = this.Bf.getBoundingClientRect() || { left: 0, top: 0 };
      return {
        clientX: n.clientX,
        clientY: n.clientY,
        pageX: n.pageX,
        pageY: n.pageY,
        screenX: n.screenX,
        screenY: n.screenY,
        localX: n.clientX - s.left,
        localY: n.clientY - s.top,
        ctrlKey: t.ctrlKey,
        altKey: t.altKey,
        shiftKey: t.shiftKey,
        metaKey: t.metaKey,
        fv:
          !t.type.startsWith("mouse") &&
          "contextmenu" !== t.type &&
          "click" !== t.type,
        vv: t.type,
        pv: n.target,
        mv: t.view,
        bv: () => {
          "touchstart" !== t.type && ws(t);
        },
      };
    }
  }
  function bs(t, i) {
    const n = t.clientX - i.clientX,
      s = t.clientY - i.clientY;
    return Math.sqrt(n * n + s * s);
  }
  function ws(t) {
    t.cancelable && t.preventDefault();
  }
  function gs(t) {
    return { nt: t.pageX, st: t.pageY };
  }
  function Ms(t) {
    return t.timeStamp || performance.now();
  }
  function xs(t, i) {
    for (let n = 0; n < t.length; ++n) if (t[n].identifier === i) return t[n];
    return null;
  }
  function Ss(t) {
    return { Lc: t.Lc, wv: { mr: t.gv.externalId }, Mv: t.gv.cursorStyle };
  }
  function ys(t, i, n) {
    for (const s of t) {
      const t = s.gt();
      if (null !== t && t.pr) {
        const e = t.pr(i, n);
        if (null !== e) return { mv: s, wv: e };
      }
    }
    return null;
  }
  function ks(t, i) {
    return (n) => {
      var s, e, r, h;
      return (null !==
        (e = null === (s = n.Dt()) || void 0 === s ? void 0 : s.ya()) &&
      void 0 !== e
        ? e
        : "") !== i
        ? []
        : null !==
            (h = null === (r = n.oa) || void 0 === r ? void 0 : r.call(n, t)) &&
          void 0 !== h
        ? h
        : [];
    };
  }
  class Cs {
    constructor(t, i, n, s) {
      (this.Ei = null),
        (this.xv = null),
        (this.Sv = !1),
        (this.yv = new Gt(200)),
        (this.Zr = null),
        (this.kv = 0),
        (this.Cv = !1),
        (this.Tv = () => {
          this.Cv || this.Qi.Pv().$t().Wh();
        }),
        (this.Rv = () => {
          this.Cv || this.Qi.Pv().$t().Wh();
        }),
        (this.Qi = t),
        (this._n = i),
        (this.wo = i.layout),
        (this.Tc = n),
        (this.Dv = "left" === s),
        (this.Ov = ks("normal", s)),
        (this.Bv = ks("top", s)),
        (this.Av = ks("bottom", s)),
        (this.Vv = document.createElement("div")),
        (this.Vv.style.height = "100%"),
        (this.Vv.style.overflow = "hidden"),
        (this.Vv.style.width = "25px"),
        (this.Vv.style.left = "0"),
        (this.Vv.style.position = "relative"),
        (this.zv = us(this.Vv, Gn({ width: 16, height: 16 }))),
        this.zv.subscribeSuggestedBitmapSizeChanged(this.Tv);
      const e = this.zv.canvasElement;
      (e.style.position = "absolute"),
        (e.style.zIndex = "1"),
        (e.style.left = "0"),
        (e.style.top = "0"),
        (this.Ev = us(this.Vv, Gn({ width: 16, height: 16 }))),
        this.Ev.subscribeSuggestedBitmapSizeChanged(this.Rv);
      const r = this.Ev.canvasElement;
      (r.style.position = "absolute"),
        (r.style.zIndex = "2"),
        (r.style.left = "0"),
        (r.style.top = "0");
      const h = {
        nv: this.Iv.bind(this),
        tv: this.Iv.bind(this),
        qf: this.Lv.bind(this),
        $f: this.Lv.bind(this),
        sv: this.Nv.bind(this),
        Zf: this.Fv.bind(this),
        Xf: this.Fv.bind(this),
        Df: this.Wv.bind(this),
        Cf: this.Wv.bind(this),
        If: this.jv.bind(this),
        cv: this.Hv.bind(this),
      };
      this.$v = new ms(this.Ev.canvasElement, h, {
        jf: () => !this._n.handleScroll.vertTouchDrag,
        Hf: () => !0,
      });
    }
    S() {
      this.$v.S(),
        this.Ev.unsubscribeSuggestedBitmapSizeChanged(this.Rv),
        cs(this.Ev.canvasElement),
        this.Ev.dispose(),
        this.zv.unsubscribeSuggestedBitmapSizeChanged(this.Tv),
        cs(this.zv.canvasElement),
        this.zv.dispose(),
        null !== this.Ei && this.Ei.qo().p(this),
        (this.Ei = null);
    }
    Uv() {
      return this.Vv;
    }
    P() {
      return this.wo.fontSize;
    }
    qv() {
      const t = this.Tc.W();
      return this.Zr !== t.R && (this.yv.Qe(), (this.Zr = t.R)), t;
    }
    Yv() {
      if (null === this.Ei) return 0;
      let t = 0;
      const i = this.qv(),
        n = f(this.zv.canvasElement.getContext("2d"));
      n.save();
      const s = this.Ei.Na();
      (n.font = this.Xv()),
        s.length > 0 &&
          (t = Math.max(
            this.yv.Mi(n, s[0].Ja),
            this.yv.Mi(n, s[s.length - 1].Ja)
          ));
      const e = this.Kv();
      for (let i = e.length; i--; ) {
        const s = this.yv.Mi(n, e[i].Zt());
        s > t && (t = s);
      }
      const r = this.Ei.Ct();
      if (null !== r && null !== this.xv) {
        const i = this.Ei.fn(1, r),
          s = this.Ei.fn(this.xv.height - 2, r);
        t = Math.max(
          t,
          this.yv.Mi(
            n,
            this.Ei.Ni(Math.floor(Math.min(i, s)) + 0.11111111111111, r)
          ),
          this.yv.Mi(
            n,
            this.Ei.Ni(Math.ceil(Math.max(i, s)) - 0.11111111111111, r)
          )
        );
      }
      n.restore();
      const h = t || 34;
      return ls(Math.ceil(i.C + i.T + i.V + i.I + 5 + h));
    }
    Zv(t) {
      (null !== this.xv && Jn(this.xv, t)) ||
        ((this.xv = t),
        (this.Cv = !0),
        this.zv.resizeCanvasElement(t),
        this.Ev.resizeCanvasElement(t),
        (this.Cv = !1),
        (this.Vv.style.width = `${t.width}px`),
        (this.Vv.style.height = `${t.height}px`));
    }
    Gv() {
      return f(this.xv).width;
    }
    Zi(t) {
      this.Ei !== t &&
        (null !== this.Ei && this.Ei.qo().p(this),
        (this.Ei = t),
        t.qo().l(this._o.bind(this), this));
    }
    Dt() {
      return this.Ei;
    }
    Qe() {
      const t = this.Qi.Jv();
      this.Qi.Pv().$t().V_(t, f(this.Dt()));
    }
    Qv(t) {
      if (null === this.xv) return;
      if (1 !== t) {
        this.tp(), this.zv.applySuggestedBitmapSize();
        const t = ss(this.zv);
        null !== t &&
          (t.useBitmapCoordinateSpace((t) => {
            this.ip(t), this.Be(t);
          }),
          this.Qi.np(t, this.Av),
          this.sp(t),
          this.Qi.np(t, this.Ov),
          this.ep(t));
      }
      this.Ev.applySuggestedBitmapSize();
      const i = ss(this.Ev);
      null !== i &&
        (i.useBitmapCoordinateSpace(({ context: t, bitmapSize: i }) => {
          t.clearRect(0, 0, i.width, i.height);
        }),
        this.rp(i),
        this.Qi.np(i, this.Bv));
    }
    hp() {
      return this.zv.bitmapSize;
    }
    lp(t, i, n) {
      const s = this.hp();
      s.width > 0 && s.height > 0 && t.drawImage(this.zv.canvasElement, i, n);
    }
    bt() {
      var t;
      null === (t = this.Ei) || void 0 === t || t.Na();
    }
    Iv(t) {
      if (
        null === this.Ei ||
        this.Ei.Li() ||
        !this._n.handleScale.axisPressedMouseMove.price
      )
        return;
      const i = this.Qi.Pv().$t(),
        n = this.Qi.Jv();
      (this.Sv = !0), i.T_(n, this.Ei, t.localY);
    }
    Lv(t) {
      if (null === this.Ei || !this._n.handleScale.axisPressedMouseMove.price)
        return;
      const i = this.Qi.Pv().$t(),
        n = this.Qi.Jv(),
        s = this.Ei;
      i.P_(n, s, t.localY);
    }
    Nv() {
      if (null === this.Ei || !this._n.handleScale.axisPressedMouseMove.price)
        return;
      const t = this.Qi.Pv().$t(),
        i = this.Qi.Jv(),
        n = this.Ei;
      this.Sv && ((this.Sv = !1), t.R_(i, n));
    }
    Fv(t) {
      if (null === this.Ei || !this._n.handleScale.axisPressedMouseMove.price)
        return;
      const i = this.Qi.Pv().$t(),
        n = this.Qi.Jv();
      (this.Sv = !1), i.R_(n, this.Ei);
    }
    Wv(t) {
      this._n.handleScale.axisDoubleClickReset.price && this.Qe();
    }
    jv(t) {
      if (null === this.Ei) return;
      !this.Qi.Pv().$t().W().handleScale.axisPressedMouseMove.price ||
        this.Ei.mh() ||
        this.Ei.Po() ||
        this.ap(1);
    }
    Hv(t) {
      this.ap(0);
    }
    Kv() {
      const t = [],
        i = null === this.Ei ? void 0 : this.Ei;
      return (
        ((n) => {
          for (let s = 0; s < n.length; ++s) {
            const e = n[s].Tn(this.Qi.Jv(), i);
            for (let i = 0; i < e.length; i++) t.push(e[i]);
          }
        })(this.Qi.Jv().Wo()),
        t
      );
    }
    ip({ context: t, bitmapSize: i }) {
      const { width: n, height: s } = i,
        e = this.Qi.Jv().$t(),
        r = e.q(),
        h = e.dd();
      r === h ? q(t, 0, 0, n, s, r) : K(t, 0, 0, n, s, r, h);
    }
    Be({ context: t, bitmapSize: i, horizontalPixelRatio: n }) {
      if (null === this.xv || null === this.Ei || !this.Ei.W().borderVisible)
        return;
      t.fillStyle = this.Ei.W().borderColor;
      const s = Math.max(1, Math.floor(this.qv().C * n));
      let e;
      (e = this.Dv ? i.width - s : 0), t.fillRect(e, 0, s, i.height);
    }
    sp(t) {
      if (null === this.xv || null === this.Ei) return;
      const i = this.Ei.Na(),
        n = this.Ei.W(),
        s = this.qv(),
        e = this.Dv ? this.xv.width - s.T : 0;
      n.borderVisible &&
        n.ticksVisible &&
        t.useBitmapCoordinateSpace(
          ({ context: t, horizontalPixelRatio: r, verticalPixelRatio: h }) => {
            t.fillStyle = n.borderColor;
            const l = Math.max(1, Math.floor(h)),
              a = Math.floor(0.5 * h),
              o = Math.round(s.T * r);
            t.beginPath();
            for (const n of i)
              t.rect(Math.floor(e * r), Math.round(n.Va * h) - a, o, l);
            t.fill();
          }
        ),
        t.useMediaCoordinateSpace(({ context: t }) => {
          var r;
          (t.font = this.Xv()),
            (t.fillStyle =
              null !== (r = n.textColor) && void 0 !== r
                ? r
                : this.wo.textColor),
            (t.textAlign = this.Dv ? "right" : "left"),
            (t.textBaseline = "middle");
          const h = this.Dv ? Math.round(e - s.V) : Math.round(e + s.T + s.V),
            l = i.map((i) => this.yv.gi(t, i.Ja));
          for (let n = i.length; n--; ) {
            const s = i[n];
            t.fillText(s.Ja, h, s.Va + l[n]);
          }
        });
    }
    tp() {
      if (null === this.xv || null === this.Ei) return;
      let t = this.xv.height / 2;
      const i = [],
        n = this.Ei.Wo().slice(),
        s = this.Qi.Jv(),
        e = this.qv();
      this.Ei === s.cr() &&
        this.Qi.Jv()
          .Wo()
          .forEach((t) => {
            s.ur(t) && n.push(t);
          });
      const r = this.Ei.Ra()[0],
        h = this.Ei;
      n.forEach((n) => {
        const e = n.Tn(s, h);
        e.forEach((t) => {
          t.Oi(null), t.Bi() && i.push(t);
        }),
          r === n && e.length > 0 && (t = e[0].Si());
      }),
        i.forEach((t) => t.Oi(t.Si()));
      this.Ei.W().alignLabels && this.op(i, e, t);
    }
    op(t, i, n) {
      if (null === this.xv) return;
      const s = t.filter((t) => t.Si() <= n),
        e = t.filter((t) => t.Si() > n);
      s.sort((t, i) => i.Si() - t.Si()),
        s.length && e.length && e.push(s[0]),
        e.sort((t, i) => t.Si() - i.Si());
      for (const n of t) {
        const t = Math.floor(n.Vt(i) / 2),
          s = n.Si();
        s > -t && s < t && n.Oi(t),
          s > this.xv.height - t &&
            s < this.xv.height + t &&
            n.Oi(this.xv.height - t);
      }
      for (let t = 1; t < s.length; t++) {
        const n = s[t],
          e = s[t - 1],
          r = e.Vt(i, !1),
          h = n.Si(),
          l = e.Di();
        h > l - r && n.Oi(l - r);
      }
      for (let t = 1; t < e.length; t++) {
        const n = e[t],
          s = e[t - 1],
          r = s.Vt(i, !0),
          h = n.Si(),
          l = s.Di();
        h < l + r && n.Oi(l + r);
      }
    }
    ep(t) {
      if (null === this.xv) return;
      const i = this.Kv(),
        n = this.qv(),
        s = this.Dv ? "right" : "left";
      i.forEach((i) => {
        if (i.Ai()) {
          i.gt(f(this.Ei)).K(t, n, this.yv, s);
        }
      });
    }
    rp(t) {
      if (null === this.xv || null === this.Ei) return;
      const i = this.Qi.Pv().$t(),
        n = [],
        s = this.Qi.Jv(),
        e = i.Hc().Tn(s, this.Ei);
      e.length && n.push(e);
      const r = this.qv(),
        h = this.Dv ? "right" : "left";
      n.forEach((i) => {
        i.forEach((i) => {
          i.gt(f(this.Ei)).K(t, r, this.yv, h);
        });
      });
    }
    ap(t) {
      this.Vv.style.cursor = 1 === t ? "ns-resize" : "default";
    }
    _o() {
      const t = this.Yv();
      this.kv < t && this.Qi.Pv().$t().ql(), (this.kv = t);
    }
    Xv() {
      return z(this.wo.fontSize, this.wo.fontFamily);
    }
  }
  function Ts(t, i) {
    var n, s;
    return null !==
      (s = null === (n = t.la) || void 0 === n ? void 0 : n.call(t, i)) &&
      void 0 !== s
      ? s
      : [];
  }
  function Ps(t, i) {
    var n, s;
    return null !==
      (s = null === (n = t.Cn) || void 0 === n ? void 0 : n.call(t, i)) &&
      void 0 !== s
      ? s
      : [];
  }
  function Rs(t, i) {
    var n, s;
    return null !==
      (s = null === (n = t.Gi) || void 0 === n ? void 0 : n.call(t, i)) &&
      void 0 !== s
      ? s
      : [];
  }
  function Ds(t, i) {
    var n, s;
    return null !==
      (s = null === (n = t.ea) || void 0 === n ? void 0 : n.call(t, i)) &&
      void 0 !== s
      ? s
      : [];
  }
  class Os {
    constructor(t, i) {
      (this.xv = Gn({ width: 0, height: 0 })),
        (this._p = null),
        (this.up = null),
        (this.cp = null),
        (this.dp = !1),
        (this.fp = new k()),
        (this.vp = new k()),
        (this.pp = 0),
        (this.mp = !1),
        (this.bp = null),
        (this.wp = !1),
        (this.gp = null),
        (this.Mp = null),
        (this.Cv = !1),
        (this.Tv = () => {
          this.Cv || null === this.xp || this.Hi().Wh();
        }),
        (this.Rv = () => {
          this.Cv || null === this.xp || this.Hi().Wh();
        }),
        (this.Sp = t),
        (this.xp = i),
        this.xp.I_().l(this.yp.bind(this), this, !0),
        (this.kp = document.createElement("td")),
        (this.kp.style.padding = "0"),
        (this.kp.style.position = "relative");
      const n = document.createElement("div");
      (n.style.width = "100%"),
        (n.style.height = "100%"),
        (n.style.position = "relative"),
        (n.style.overflow = "hidden"),
        (this.Cp = document.createElement("td")),
        (this.Cp.style.padding = "0"),
        (this.Tp = document.createElement("td")),
        (this.Tp.style.padding = "0"),
        this.kp.appendChild(n),
        (this.zv = us(n, Gn({ width: 16, height: 16 }))),
        this.zv.subscribeSuggestedBitmapSizeChanged(this.Tv);
      const s = this.zv.canvasElement;
      (s.style.position = "absolute"),
        (s.style.zIndex = "1"),
        (s.style.left = "0"),
        (s.style.top = "0"),
        (this.Ev = us(n, Gn({ width: 16, height: 16 }))),
        this.Ev.subscribeSuggestedBitmapSizeChanged(this.Rv);
      const e = this.Ev.canvasElement;
      (e.style.position = "absolute"),
        (e.style.zIndex = "2"),
        (e.style.left = "0"),
        (e.style.top = "0"),
        (this.Pp = document.createElement("tr")),
        this.Pp.appendChild(this.Cp),
        this.Pp.appendChild(this.kp),
        this.Pp.appendChild(this.Tp),
        this.Rp(),
        (this.$v = new ms(this.Ev.canvasElement, this, {
          jf: () => null === this.bp && !this.Sp.W().handleScroll.vertTouchDrag,
          Hf: () => null === this.bp && !this.Sp.W().handleScroll.horzTouchDrag,
        }));
    }
    S() {
      null !== this._p && this._p.S(),
        null !== this.up && this.up.S(),
        this.Ev.unsubscribeSuggestedBitmapSizeChanged(this.Rv),
        cs(this.Ev.canvasElement),
        this.Ev.dispose(),
        this.zv.unsubscribeSuggestedBitmapSizeChanged(this.Tv),
        cs(this.zv.canvasElement),
        this.zv.dispose(),
        null !== this.xp && this.xp.I_().p(this),
        this.$v.S();
    }
    Jv() {
      return f(this.xp);
    }
    Dp(t) {
      null !== this.xp && this.xp.I_().p(this),
        (this.xp = t),
        null !== this.xp &&
          this.xp.I_().l(Os.prototype.yp.bind(this), this, !0),
        this.Rp();
    }
    Pv() {
      return this.Sp;
    }
    Uv() {
      return this.Pp;
    }
    Rp() {
      if (null !== this.xp && (this.Op(), 0 !== this.Hi().wt().length)) {
        if (null !== this._p) {
          const t = this.xp.k_();
          this._p.Zi(f(t));
        }
        if (null !== this.up) {
          const t = this.xp.C_();
          this.up.Zi(f(t));
        }
      }
    }
    Bp() {
      null !== this._p && this._p.bt(), null !== this.up && this.up.bt();
    }
    m_() {
      return null !== this.xp ? this.xp.m_() : 0;
    }
    b_(t) {
      this.xp && this.xp.b_(t);
    }
    If(t) {
      if (!this.xp) return;
      this.Ap();
      const i = t.localX,
        n = t.localY;
      this.Vp(i, n, t);
    }
    nv(t) {
      this.Ap(), this.zp(), this.Vp(t.localX, t.localY, t);
    }
    Lf(t) {
      var i;
      if (!this.xp) return;
      this.Ap();
      const n = t.localX,
        s = t.localY;
      this.Vp(n, s, t);
      const e = this.pr(n, s);
      this.Sp.Ep(
        null !== (i = null == e ? void 0 : e.Mv) && void 0 !== i ? i : null
      ),
        this.Hi().Ic(e && { Lc: e.Lc, wv: e.wv });
    }
    Gf(t) {
      null !== this.xp && (this.Ap(), this.Ip(t));
    }
    Df(t) {
      null !== this.xp && this.Lp(this.vp, t);
    }
    Cf(t) {
      this.Df(t);
    }
    qf(t) {
      this.Ap(), this.Np(t), this.Vp(t.localX, t.localY, t);
    }
    Zf(t) {
      null !== this.xp && (this.Ap(), (this.mp = !1), this.Fp(t));
    }
    Kf(t) {
      null !== this.xp && this.Ip(t);
    }
    dv(t) {
      if (((this.mp = !0), null === this.bp)) {
        const i = { x: t.localX, y: t.localY };
        this.Wp(i, i, t);
      }
    }
    cv(t) {
      null !== this.xp && (this.Ap(), this.xp.$t().Ic(null), this.jp());
    }
    Hp() {
      return this.fp;
    }
    $p() {
      return this.vp;
    }
    hv() {
      (this.pp = 1), this.Hi().Hn();
    }
    lv(t, i) {
      if (!this.Sp.W().handleScale.pinch) return;
      const n = 5 * (i - this.pp);
      (this.pp = i), this.Hi().Xc(t.nt, n);
    }
    tv(t) {
      (this.mp = !1), (this.wp = null !== this.bp), this.zp();
      const i = this.Hi().Hc();
      null !== this.bp &&
        i.kt() &&
        ((this.gp = { x: i.Yt(), y: i.Xt() }),
        (this.bp = { x: t.localX, y: t.localY }));
    }
    $f(t) {
      if (null === this.xp) return;
      const i = t.localX,
        n = t.localY;
      if (null === this.bp) this.Np(t);
      else {
        this.wp = !1;
        const s = f(this.gp),
          e = s.x + (i - this.bp.x),
          r = s.y + (n - this.bp.y);
        this.Vp(e, r, t);
      }
    }
    Xf(t) {
      0 === this.Pv().W().trackingMode.exitMode && (this.wp = !0),
        this.Up(),
        this.Fp(t);
    }
    pr(t, i) {
      const n = this.xp;
      return null === n
        ? null
        : (function (t, i, n) {
            const s = t.Wo(),
              e = (function (t, i, n) {
                var s, e;
                let r, h;
                for (const o of t) {
                  const t =
                    null !==
                      (e =
                        null === (s = o.ua) || void 0 === s
                          ? void 0
                          : s.call(o, i, n)) && void 0 !== e
                      ? e
                      : [];
                  for (const i of t)
                    (l = i.zOrder),
                      (!(a = null == r ? void 0 : r.zOrder) ||
                        ("top" === l && "top" !== a) ||
                        ("normal" === l && "bottom" === a)) &&
                        ((r = i), (h = o));
                }
                var l, a;
                return r && h ? { gv: r, Lc: h } : null;
              })(s, i, n);
            if ("top" === (null == e ? void 0 : e.gv.zOrder)) return Ss(e);
            for (const r of s) {
              if (
                e &&
                e.Lc === r &&
                "bottom" !== e.gv.zOrder &&
                !e.gv.isBackground
              )
                return Ss(e);
              const s = ys(r.Cn(t), i, n);
              if (null !== s) return { Lc: r, mv: s.mv, wv: s.wv };
              if (
                e &&
                e.Lc === r &&
                "bottom" !== e.gv.zOrder &&
                e.gv.isBackground
              )
                return Ss(e);
            }
            return (null == e ? void 0 : e.gv) ? Ss(e) : null;
          })(n, t, i);
    }
    qp(t, i) {
      f("left" === i ? this._p : this.up).Zv(
        Gn({ width: t, height: this.xv.height })
      );
    }
    Yp() {
      return this.xv;
    }
    Zv(t) {
      Jn(this.xv, t) ||
        ((this.xv = t),
        (this.Cv = !0),
        this.zv.resizeCanvasElement(t),
        this.Ev.resizeCanvasElement(t),
        (this.Cv = !1),
        (this.kp.style.width = t.width + "px"),
        (this.kp.style.height = t.height + "px"));
    }
    Xp() {
      const t = f(this.xp);
      t.y_(t.k_()), t.y_(t.C_());
      for (const i of t.Ra())
        if (t.ur(i)) {
          const n = i.Dt();
          null !== n && t.y_(n), i.Rn();
        }
    }
    hp() {
      return this.zv.bitmapSize;
    }
    lp(t, i, n) {
      const s = this.hp();
      s.width > 0 && s.height > 0 && t.drawImage(this.zv.canvasElement, i, n);
    }
    Qv(t) {
      if (0 === t) return;
      if (null === this.xp) return;
      if (
        (t > 1 && this.Xp(),
        null !== this._p && this._p.Qv(t),
        null !== this.up && this.up.Qv(t),
        1 !== t)
      ) {
        this.zv.applySuggestedBitmapSize();
        const t = ss(this.zv);
        null !== t &&
          (t.useBitmapCoordinateSpace((t) => {
            this.ip(t);
          }),
          this.xp &&
            (this.Kp(t, Ts),
            this.Zp(t),
            this.Gp(t),
            this.Kp(t, Ps),
            this.Kp(t, Rs)));
      }
      this.Ev.applySuggestedBitmapSize();
      const i = ss(this.Ev);
      null !== i &&
        (i.useBitmapCoordinateSpace(({ context: t, bitmapSize: i }) => {
          t.clearRect(0, 0, i.width, i.height);
        }),
        this.Jp(i),
        this.Kp(i, Ds));
    }
    Qp() {
      return this._p;
    }
    tm() {
      return this.up;
    }
    np(t, i) {
      this.Kp(t, i);
    }
    yp() {
      null !== this.xp && this.xp.I_().p(this), (this.xp = null);
    }
    Ip(t) {
      this.Lp(this.fp, t);
    }
    Lp(t, i) {
      const n = i.localX,
        s = i.localY;
      t.M() && t.m(this.Hi().St().zu(n), { x: n, y: s }, i);
    }
    ip({ context: t, bitmapSize: i }) {
      const { width: n, height: s } = i,
        e = this.Hi(),
        r = e.q(),
        h = e.dd();
      r === h ? q(t, 0, 0, n, s, h) : K(t, 0, 0, n, s, r, h);
    }
    Zp(t) {
      const i = f(this.xp).L_().jh().gt();
      null !== i && i.K(t, !1);
    }
    Gp(t) {
      const i = this.Hi().jc();
      this.im(t, Ps, ds, i), this.im(t, Ps, fs, i);
    }
    Jp(t) {
      this.im(t, Ps, fs, this.Hi().Hc());
    }
    Kp(t, i) {
      const n = f(this.xp).Wo();
      for (const s of n) this.im(t, i, ds, s);
      for (const s of n) this.im(t, i, fs, s);
    }
    im(t, i, n, s) {
      const e = f(this.xp),
        r = e.$t().Ec(),
        h = null !== r && r.Lc === s,
        l = null !== r && h && void 0 !== r.wv ? r.wv.br : void 0;
      vs(i, (i) => n(i, t, h, l), s, e);
    }
    Op() {
      if (null === this.xp) return;
      const t = this.Sp,
        i = this.xp.k_().W().visible,
        n = this.xp.C_().W().visible;
      i ||
        null === this._p ||
        (this.Cp.removeChild(this._p.Uv()), this._p.S(), (this._p = null)),
        n ||
          null === this.up ||
          (this.Tp.removeChild(this.up.Uv()), this.up.S(), (this.up = null));
      const s = t.$t().hd();
      i &&
        null === this._p &&
        ((this._p = new Cs(this, t.W(), s, "left")),
        this.Cp.appendChild(this._p.Uv())),
        n &&
          null === this.up &&
          ((this.up = new Cs(this, t.W(), s, "right")),
          this.Tp.appendChild(this.up.Uv()));
    }
    nm(t) {
      return (t.fv && this.mp) || null !== this.bp;
    }
    sm(t) {
      return Math.max(0, Math.min(t, this.xv.width - 1));
    }
    rm(t) {
      return Math.max(0, Math.min(t, this.xv.height - 1));
    }
    Vp(t, i, n) {
      this.Hi().nd(this.sm(t), this.rm(i), n, f(this.xp));
    }
    jp() {
      this.Hi().ed();
    }
    Up() {
      this.wp && ((this.bp = null), this.jp());
    }
    Wp(t, i, n) {
      (this.bp = t), (this.wp = !1), this.Vp(i.x, i.y, n);
      const s = this.Hi().Hc();
      this.gp = { x: s.Yt(), y: s.Xt() };
    }
    Hi() {
      return this.Sp.$t();
    }
    Fp(t) {
      if (!this.dp) return;
      const i = this.Hi(),
        n = this.Jv();
      if (
        (i.B_(n, n.dn()),
        (this.cp = null),
        (this.dp = !1),
        i.Jc(),
        null !== this.Mp)
      ) {
        const t = performance.now(),
          n = i.St();
        this.Mp.Pr(n.Nu(), t), this.Mp.Ku(t) || i.qn(this.Mp);
      }
    }
    Ap() {
      this.bp = null;
    }
    zp() {
      if (!this.xp) return;
      if (
        (this.Hi().Hn(),
        document.activeElement !== document.body &&
          document.activeElement !== document.documentElement)
      )
        f(document.activeElement).blur();
      else {
        const t = document.getSelection();
        null !== t && t.removeAllRanges();
      }
      !this.xp.dn().Li() && this.Hi().St().Li();
    }
    Np(t) {
      if (null === this.xp) return;
      const i = this.Hi(),
        n = i.St();
      if (n.Li()) return;
      const s = this.Sp.W(),
        e = s.handleScroll,
        r = s.kineticScroll;
      if (
        (!e.pressedMouseMove || t.fv) &&
        ((!e.horzTouchDrag && !e.vertTouchDrag) || !t.fv)
      )
        return;
      const h = this.xp.dn(),
        l = performance.now();
      if (
        (null !== this.cp ||
          this.nm(t) ||
          (this.cp = {
            x: t.clientX,
            y: t.clientY,
            Td: l,
            hm: t.localX,
            lm: t.localY,
          }),
        null !== this.cp &&
          !this.dp &&
          (this.cp.x !== t.clientX || this.cp.y !== t.clientY))
      ) {
        if ((t.fv && r.touch) || (!t.fv && r.mouse)) {
          const t = n.ee();
          (this.Mp = new _s(0.2 / t, 7 / t, 0.997, 15 / t)),
            this.Mp.jd(n.Nu(), this.cp.Td);
        } else this.Mp = null;
        h.Li() || i.D_(this.xp, h, t.localY), i.Zc(t.localX), (this.dp = !0);
      }
      this.dp &&
        (h.Li() || i.O_(this.xp, h, t.localY),
        i.Gc(t.localX),
        null !== this.Mp && this.Mp.jd(n.Nu(), l));
    }
  }
  class Bs {
    constructor(t, i, n, s, e) {
      (this.ft = !0),
        (this.xv = Gn({ width: 0, height: 0 })),
        (this.Tv = () => this.Qv(3)),
        (this.Dv = "left" === t),
        (this.Tc = n.hd),
        (this._n = i),
        (this.am = s),
        (this.om = e),
        (this.Vv = document.createElement("div")),
        (this.Vv.style.width = "25px"),
        (this.Vv.style.height = "100%"),
        (this.Vv.style.overflow = "hidden"),
        (this.zv = us(this.Vv, Gn({ width: 16, height: 16 }))),
        this.zv.subscribeSuggestedBitmapSizeChanged(this.Tv);
    }
    S() {
      this.zv.unsubscribeSuggestedBitmapSizeChanged(this.Tv),
        cs(this.zv.canvasElement),
        this.zv.dispose();
    }
    Uv() {
      return this.Vv;
    }
    Yp() {
      return this.xv;
    }
    Zv(t) {
      Jn(this.xv, t) ||
        ((this.xv = t),
        this.zv.resizeCanvasElement(t),
        (this.Vv.style.width = `${t.width}px`),
        (this.Vv.style.height = `${t.height}px`),
        (this.ft = !0));
    }
    Qv(t) {
      if (t < 3 && !this.ft) return;
      if (0 === this.xv.width || 0 === this.xv.height) return;
      (this.ft = !1), this.zv.applySuggestedBitmapSize();
      const i = ss(this.zv);
      null !== i &&
        i.useBitmapCoordinateSpace((t) => {
          this.ip(t), this.Be(t);
        });
    }
    hp() {
      return this.zv.bitmapSize;
    }
    lp(t, i, n) {
      const s = this.hp();
      s.width > 0 && s.height > 0 && t.drawImage(this.zv.canvasElement, i, n);
    }
    Be({
      context: t,
      bitmapSize: i,
      horizontalPixelRatio: n,
      verticalPixelRatio: s,
    }) {
      if (!this.am()) return;
      t.fillStyle = this._n.timeScale.borderColor;
      const e = Math.floor(this.Tc.W().C * n),
        r = Math.floor(this.Tc.W().C * s),
        h = this.Dv ? i.width - e : 0;
      t.fillRect(h, 0, e, r);
    }
    ip({ context: t, bitmapSize: i }) {
      q(t, 0, 0, i.width, i.height, this.om());
    }
  }
  function As(t) {
    return (i) => {
      var n, s;
      return null !==
        (s = null === (n = i._a) || void 0 === n ? void 0 : n.call(i, t)) &&
        void 0 !== s
        ? s
        : [];
    };
  }
  const Vs = As("normal"),
    zs = As("top"),
    Es = As("bottom");
  class Is {
    constructor(t, i) {
      (this._m = null),
        (this.um = null),
        (this.k = null),
        (this.dm = !1),
        (this.xv = Gn({ width: 0, height: 0 })),
        (this.fm = new k()),
        (this.yv = new Gt(5)),
        (this.Cv = !1),
        (this.Tv = () => {
          this.Cv || this.Sp.$t().Wh();
        }),
        (this.Rv = () => {
          this.Cv || this.Sp.$t().Wh();
        }),
        (this.Sp = t),
        (this.W_ = i),
        (this._n = t.W().layout),
        (this.vm = document.createElement("tr")),
        (this.pm = document.createElement("td")),
        (this.pm.style.padding = "0"),
        (this.bm = document.createElement("td")),
        (this.bm.style.padding = "0"),
        (this.Vv = document.createElement("td")),
        (this.Vv.style.height = "25px"),
        (this.Vv.style.padding = "0"),
        (this.wm = document.createElement("div")),
        (this.wm.style.width = "100%"),
        (this.wm.style.height = "100%"),
        (this.wm.style.position = "relative"),
        (this.wm.style.overflow = "hidden"),
        this.Vv.appendChild(this.wm),
        (this.zv = us(this.wm, Gn({ width: 16, height: 16 }))),
        this.zv.subscribeSuggestedBitmapSizeChanged(this.Tv);
      const n = this.zv.canvasElement;
      (n.style.position = "absolute"),
        (n.style.zIndex = "1"),
        (n.style.left = "0"),
        (n.style.top = "0"),
        (this.Ev = us(this.wm, Gn({ width: 16, height: 16 }))),
        this.Ev.subscribeSuggestedBitmapSizeChanged(this.Rv);
      const s = this.Ev.canvasElement;
      (s.style.position = "absolute"),
        (s.style.zIndex = "2"),
        (s.style.left = "0"),
        (s.style.top = "0"),
        this.vm.appendChild(this.pm),
        this.vm.appendChild(this.Vv),
        this.vm.appendChild(this.bm),
        this.gm(),
        this.Sp.$t().p_().l(this.gm.bind(this), this),
        (this.$v = new ms(this.Ev.canvasElement, this, {
          jf: () => !0,
          Hf: () => !this.Sp.W().handleScroll.horzTouchDrag,
        }));
    }
    S() {
      this.$v.S(),
        null !== this._m && this._m.S(),
        null !== this.um && this.um.S(),
        this.Ev.unsubscribeSuggestedBitmapSizeChanged(this.Rv),
        cs(this.Ev.canvasElement),
        this.Ev.dispose(),
        this.zv.unsubscribeSuggestedBitmapSizeChanged(this.Tv),
        cs(this.zv.canvasElement),
        this.zv.dispose();
    }
    Uv() {
      return this.vm;
    }
    Mm() {
      return this._m;
    }
    xm() {
      return this.um;
    }
    nv(t) {
      if (this.dm) return;
      this.dm = !0;
      const i = this.Sp.$t();
      !i.St().Li() &&
        this.Sp.W().handleScale.axisPressedMouseMove.time &&
        i.Yc(t.localX);
    }
    tv(t) {
      this.nv(t);
    }
    sv() {
      const t = this.Sp.$t();
      !t.St().Li() &&
        this.dm &&
        ((this.dm = !1),
        this.Sp.W().handleScale.axisPressedMouseMove.time && t.td());
    }
    qf(t) {
      const i = this.Sp.$t();
      !i.St().Li() &&
        this.Sp.W().handleScale.axisPressedMouseMove.time &&
        i.Qc(t.localX);
    }
    $f(t) {
      this.qf(t);
    }
    Zf() {
      this.dm = !1;
      const t = this.Sp.$t();
      (t.St().Li() && !this.Sp.W().handleScale.axisPressedMouseMove.time) ||
        t.td();
    }
    Xf() {
      this.Zf();
    }
    Df() {
      this.Sp.W().handleScale.axisDoubleClickReset.time && this.Sp.$t().Xn();
    }
    Cf() {
      this.Df();
    }
    If() {
      this.Sp.$t().W().handleScale.axisPressedMouseMove.time && this.ap(1);
    }
    cv() {
      this.ap(0);
    }
    Yp() {
      return this.xv;
    }
    Sm() {
      return this.fm;
    }
    ym(t, i, n) {
      Jn(this.xv, t) ||
        ((this.xv = t),
        (this.Cv = !0),
        this.zv.resizeCanvasElement(t),
        this.Ev.resizeCanvasElement(t),
        (this.Cv = !1),
        (this.Vv.style.width = `${t.width}px`),
        (this.Vv.style.height = `${t.height}px`),
        this.fm.m(t)),
        null !== this._m && this._m.Zv(Gn({ width: i, height: t.height })),
        null !== this.um && this.um.Zv(Gn({ width: n, height: t.height }));
    }
    km() {
      const t = this.Cm();
      return Math.ceil(t.C + t.T + t.P + t.L + t.A + t.Tm);
    }
    bt() {
      this.Sp.$t().St().Na();
    }
    hp() {
      return this.zv.bitmapSize;
    }
    lp(t, i, n) {
      const s = this.hp();
      s.width > 0 && s.height > 0 && t.drawImage(this.zv.canvasElement, i, n);
    }
    Qv(t) {
      if (0 === t) return;
      if (1 !== t) {
        this.zv.applySuggestedBitmapSize();
        const i = ss(this.zv);
        null !== i &&
          (i.useBitmapCoordinateSpace((t) => {
            this.ip(t), this.Be(t), this.Pm(i, Es);
          }),
          this.sp(i),
          this.Pm(i, Vs)),
          null !== this._m && this._m.Qv(t),
          null !== this.um && this.um.Qv(t);
      }
      this.Ev.applySuggestedBitmapSize();
      const i = ss(this.Ev);
      null !== i &&
        (i.useBitmapCoordinateSpace(({ context: t, bitmapSize: i }) => {
          t.clearRect(0, 0, i.width, i.height);
        }),
        this.Rm([...this.Sp.$t().wt(), this.Sp.$t().Hc()], i),
        this.Pm(i, zs));
    }
    Pm(t, i) {
      const n = this.Sp.$t().wt();
      for (const s of n) vs(i, (i) => ds(i, t, !1, void 0), s, void 0);
      for (const s of n) vs(i, (i) => fs(i, t, !1, void 0), s, void 0);
    }
    ip({ context: t, bitmapSize: i }) {
      q(t, 0, 0, i.width, i.height, this.Sp.$t().dd());
    }
    Be({ context: t, bitmapSize: i, verticalPixelRatio: n }) {
      if (this.Sp.W().timeScale.borderVisible) {
        t.fillStyle = this.Dm();
        const s = Math.max(1, Math.floor(this.Cm().C * n));
        t.fillRect(0, 0, i.width, s);
      }
    }
    sp(t) {
      const i = this.Sp.$t().St(),
        n = i.Na();
      if (!n || 0 === n.length) return;
      const s = this.W_.maxTickMarkWeight(n),
        e = this.Cm(),
        r = i.W();
      r.borderVisible &&
        r.ticksVisible &&
        t.useBitmapCoordinateSpace(
          ({ context: t, horizontalPixelRatio: i, verticalPixelRatio: s }) => {
            (t.strokeStyle = this.Dm()), (t.fillStyle = this.Dm());
            const r = Math.max(1, Math.floor(i)),
              h = Math.floor(0.5 * i);
            t.beginPath();
            const l = Math.round(e.T * s);
            for (let s = n.length; s--; ) {
              const e = Math.round(n[s].coord * i);
              t.rect(e - h, 0, r, l);
            }
            t.fill();
          }
        ),
        t.useMediaCoordinateSpace(({ context: t }) => {
          const i = e.C + e.T + e.L + e.P / 2;
          (t.textAlign = "center"),
            (t.textBaseline = "middle"),
            (t.fillStyle = this.$()),
            (t.font = this.Xv());
          for (const e of n)
            if (e.weight < s) {
              const n = e.needAlignCoordinate
                ? this.Om(t, e.coord, e.label)
                : e.coord;
              t.fillText(e.label, n, i);
            }
          this.Sp.W().timeScale.allowBoldLabels && (t.font = this.Bm());
          for (const e of n)
            if (e.weight >= s) {
              const n = e.needAlignCoordinate
                ? this.Om(t, e.coord, e.label)
                : e.coord;
              t.fillText(e.label, n, i);
            }
        });
    }
    Om(t, i, n) {
      const s = this.yv.Mi(t, n),
        e = s / 2,
        r = Math.floor(i - e) + 0.5;
      return (
        r < 0
          ? (i += Math.abs(0 - r))
          : r + s > this.xv.width && (i -= Math.abs(this.xv.width - (r + s))),
        i
      );
    }
    Rm(t, i) {
      const n = this.Cm();
      for (const s of t) for (const t of s.Ji()) t.gt().K(i, n);
    }
    Dm() {
      return this.Sp.W().timeScale.borderColor;
    }
    $() {
      return this._n.textColor;
    }
    j() {
      return this._n.fontSize;
    }
    Xv() {
      return z(this.j(), this._n.fontFamily);
    }
    Bm() {
      return z(this.j(), this._n.fontFamily, "bold");
    }
    Cm() {
      null === this.k &&
        (this.k = {
          C: 1,
          N: NaN,
          L: NaN,
          A: NaN,
          Wi: NaN,
          T: 5,
          P: NaN,
          R: "",
          Fi: new Gt(),
          Tm: 0,
        });
      const t = this.k,
        i = this.Xv();
      if (t.R !== i) {
        const n = this.j();
        (t.P = n),
          (t.R = i),
          (t.L = (3 * n) / 12),
          (t.A = (3 * n) / 12),
          (t.Wi = (9 * n) / 12),
          (t.N = 0),
          (t.Tm = (4 * n) / 12),
          t.Fi.Qe();
      }
      return this.k;
    }
    ap(t) {
      this.Vv.style.cursor = 1 === t ? "ew-resize" : "default";
    }
    gm() {
      const t = this.Sp.$t(),
        i = t.W();
      i.leftPriceScale.visible ||
        null === this._m ||
        (this.pm.removeChild(this._m.Uv()), this._m.S(), (this._m = null)),
        i.rightPriceScale.visible ||
          null === this.um ||
          (this.bm.removeChild(this.um.Uv()), this.um.S(), (this.um = null));
      const n = { hd: this.Sp.$t().hd() },
        s = () => i.leftPriceScale.borderVisible && t.St().W().borderVisible,
        e = () => t.dd();
      i.leftPriceScale.visible &&
        null === this._m &&
        ((this._m = new Bs("left", i, n, s, e)),
        this.pm.appendChild(this._m.Uv())),
        i.rightPriceScale.visible &&
          null === this.um &&
          ((this.um = new Bs("right", i, n, s, e)),
          this.bm.appendChild(this.um.Uv()));
    }
  }
  const Ls =
    !!es &&
    !!navigator.userAgentData &&
    navigator.userAgentData.brands.some((t) => t.brand.includes("Chromium")) &&
    !!es &&
    ((
      null ===
        (Ns =
          null === navigator || void 0 === navigator
            ? void 0
            : navigator.userAgentData) || void 0 === Ns
        ? void 0
        : Ns.platform
    )
      ? "Windows" === navigator.userAgentData.platform
      : navigator.userAgent.toLowerCase().indexOf("win") >= 0);
  var Ns;
  class Fs {
    constructor(t, i, n) {
      var s;
      (this.Am = []),
        (this.Vm = 0),
        (this.no = 0),
        (this.h_ = 0),
        (this.zm = 0),
        (this.Em = 0),
        (this.Im = null),
        (this.Lm = !1),
        (this.fp = new k()),
        (this.vp = new k()),
        (this.yc = new k()),
        (this.Nm = null),
        (this.Fm = null),
        (this.Wm = t),
        (this._n = i),
        (this.W_ = n),
        (this.vm = document.createElement("div")),
        this.vm.classList.add("tv-lightweight-charts"),
        (this.vm.style.overflow = "hidden"),
        (this.vm.style.direction = "ltr"),
        (this.vm.style.width = "100%"),
        (this.vm.style.height = "100%"),
        ((s = this.vm).style.userSelect = "none"),
        (s.style.webkitUserSelect = "none"),
        (s.style.msUserSelect = "none"),
        (s.style.MozUserSelect = "none"),
        (s.style.webkitTapHighlightColor = "transparent"),
        (this.jm = document.createElement("table")),
        this.jm.setAttribute("cellspacing", "0"),
        this.vm.appendChild(this.jm),
        (this.Hm = this.$m.bind(this)),
        Ws(this._n) && this.Um(!0),
        (this.Hi = new Bn(this.Cc.bind(this), this._n, n)),
        this.$t().$c().l(this.qm.bind(this), this),
        (this.Ym = new Is(this, this.W_)),
        this.jm.appendChild(this.Ym.Uv());
      const e = i.autoSize && this.Xm();
      let r = this._n.width,
        h = this._n.height;
      if (e || 0 === r || 0 === h) {
        const i = t.getBoundingClientRect();
        (r = r || i.width), (h = h || i.height);
      }
      this.Km(r, h),
        this.Zm(),
        t.appendChild(this.vm),
        this.Gm(),
        this.Hi.St().Qu().l(this.Hi.ql.bind(this.Hi), this),
        this.Hi.p_().l(this.Hi.ql.bind(this.Hi), this);
    }
    $t() {
      return this.Hi;
    }
    W() {
      return this._n;
    }
    Jm() {
      return this.Am;
    }
    Qm() {
      return this.Ym;
    }
    S() {
      this.Um(!1),
        0 !== this.Vm && window.cancelAnimationFrame(this.Vm),
        this.Hi.$c().p(this),
        this.Hi.St().Qu().p(this),
        this.Hi.p_().p(this),
        this.Hi.S();
      for (const t of this.Am)
        this.jm.removeChild(t.Uv()), t.Hp().p(this), t.$p().p(this), t.S();
      (this.Am = []),
        f(this.Ym).S(),
        null !== this.vm.parentElement &&
          this.vm.parentElement.removeChild(this.vm),
        this.yc.S(),
        this.fp.S(),
        this.vp.S(),
        this.tb();
    }
    Km(t, i, n = !1) {
      if (this.no === i && this.h_ === t) return;
      const s = (function (t) {
        const i = Math.floor(t.width),
          n = Math.floor(t.height);
        return Gn({ width: i - (i % 2), height: n - (n % 2) });
      })(Gn({ width: t, height: i }));
      (this.no = s.height), (this.h_ = s.width);
      const e = this.no + "px",
        r = this.h_ + "px";
      (f(this.vm).style.height = e),
        (f(this.vm).style.width = r),
        (this.jm.style.height = e),
        (this.jm.style.width = r),
        n ? this.ib(ht.ns(), performance.now()) : this.Hi.ql();
    }
    Qv(t) {
      void 0 === t && (t = ht.ns());
      for (let i = 0; i < this.Am.length; i++) this.Am[i].Qv(t.Wn(i).Ln);
      this._n.timeScale.visible && this.Ym.Qv(t.Fn());
    }
    Fh(t) {
      const i = Ws(this._n);
      this.Hi.Fh(t);
      const n = Ws(this._n);
      n !== i && this.Um(n), this.Gm(), this.nb(t);
    }
    Hp() {
      return this.fp;
    }
    $p() {
      return this.vp;
    }
    $c() {
      return this.yc;
    }
    sb() {
      null !== this.Im &&
        (this.ib(this.Im, performance.now()), (this.Im = null));
      const t = this.eb(null),
        i = document.createElement("canvas");
      (i.width = t.width), (i.height = t.height);
      const n = f(i.getContext("2d"));
      return this.eb(n), i;
    }
    rb(t) {
      if ("left" === t && !this.hb()) return 0;
      if ("right" === t && !this.lb()) return 0;
      if (0 === this.Am.length) return 0;
      return f("left" === t ? this.Am[0].Qp() : this.Am[0].tm()).Gv();
    }
    ab() {
      return this._n.autoSize && null !== this.Nm;
    }
    ob() {
      return this.vm;
    }
    Ep(t) {
      (this.Fm = t),
        this.Fm
          ? this.ob().style.setProperty("cursor", t)
          : this.ob().style.removeProperty("cursor");
    }
    _b() {
      return this.Fm;
    }
    ub() {
      return d(this.Am[0]).Yp();
    }
    nb(t) {
      (void 0 !== t.autoSize ||
        !this.Nm ||
        (void 0 === t.width && void 0 === t.height)) &&
        (t.autoSize && !this.Nm && this.Xm(),
        !1 === t.autoSize && null !== this.Nm && this.tb(),
        t.autoSize ||
          (void 0 === t.width && void 0 === t.height) ||
          this.Km(t.width || this.h_, t.height || this.no));
    }
    eb(t) {
      let i = 0,
        n = 0;
      const s = this.Am[0],
        e = (i, n) => {
          let s = 0;
          for (let e = 0; e < this.Am.length; e++) {
            const r = this.Am[e],
              h = f("left" === i ? r.Qp() : r.tm()),
              l = h.hp();
            null !== t && h.lp(t, n, s), (s += l.height);
          }
        };
      if (this.hb()) {
        e("left", 0);
        i += f(s.Qp()).hp().width;
      }
      for (let s = 0; s < this.Am.length; s++) {
        const e = this.Am[s],
          r = e.hp();
        null !== t && e.lp(t, i, n), (n += r.height);
      }
      if (((i += s.hp().width), this.lb())) {
        e("right", i);
        i += f(s.tm()).hp().width;
      }
      const r = (i, n, s) => {
        f("left" === i ? this.Ym.Mm() : this.Ym.xm()).lp(f(t), n, s);
      };
      if (this._n.timeScale.visible) {
        const i = this.Ym.hp();
        if (null !== t) {
          let e = 0;
          this.hb() && (r("left", e, n), (e = f(s.Qp()).hp().width)),
            this.Ym.lp(t, e, n),
            (e += i.width),
            this.lb() && r("right", e, n);
        }
        n += i.height;
      }
      return Gn({ width: i, height: n });
    }
    cb() {
      let t = 0,
        i = 0,
        n = 0;
      for (const s of this.Am)
        this.hb() &&
          (i = Math.max(
            i,
            f(s.Qp()).Yv(),
            this._n.leftPriceScale.minimumWidth
          )),
          this.lb() &&
            (n = Math.max(
              n,
              f(s.tm()).Yv(),
              this._n.rightPriceScale.minimumWidth
            )),
          (t += s.m_());
      (i = ls(i)), (n = ls(n));
      const s = this.h_,
        e = this.no,
        r = Math.max(s - i - n, 0),
        h = this._n.timeScale.visible;
      let l = h ? Math.max(this.Ym.km(), this._n.timeScale.minimumHeight) : 0;
      var a;
      l = (a = l) + (a % 2);
      const o = 0 + l,
        _ = e < o ? 0 : e - o,
        u = _ / t;
      let c = 0;
      for (let t = 0; t < this.Am.length; ++t) {
        const s = this.Am[t];
        s.Dp(this.Hi.Wc()[t]);
        let e = 0,
          h = 0;
        (h = t === this.Am.length - 1 ? _ - c : Math.round(s.m_() * u)),
          (e = Math.max(h, 2)),
          (c += e),
          s.Zv(Gn({ width: r, height: e })),
          this.hb() && s.qp(i, "left"),
          this.lb() && s.qp(n, "right"),
          s.Jv() && this.Hi.Uc(s.Jv(), e);
      }
      this.Ym.ym(Gn({ width: h ? r : 0, height: l }), h ? i : 0, h ? n : 0),
        this.Hi.w_(r),
        this.zm !== i && (this.zm = i),
        this.Em !== n && (this.Em = n);
    }
    Um(t) {
      t
        ? this.vm.addEventListener("wheel", this.Hm, { passive: !1 })
        : this.vm.removeEventListener("wheel", this.Hm);
    }
    fb(t) {
      switch (t.deltaMode) {
        case t.DOM_DELTA_PAGE:
          return 120;
        case t.DOM_DELTA_LINE:
          return 32;
      }
      return Ls ? 1 / window.devicePixelRatio : 1;
    }
    $m(t) {
      if (
        !(
          (0 !== t.deltaX && this._n.handleScroll.mouseWheel) ||
          (0 !== t.deltaY && this._n.handleScale.mouseWheel)
        )
      )
        return;
      const i = this.fb(t),
        n = (i * t.deltaX) / 100,
        s = (-i * t.deltaY) / 100;
      if (
        (t.cancelable && t.preventDefault(),
        0 !== s && this._n.handleScale.mouseWheel)
      ) {
        const i = Math.sign(s) * Math.min(1, Math.abs(s)),
          n = t.clientX - this.vm.getBoundingClientRect().left;
        this.$t().Xc(n, i);
      }
      0 !== n && this._n.handleScroll.mouseWheel && this.$t().Kc(-80 * n);
    }
    ib(t, i) {
      var n;
      const s = t.Fn();
      3 === s && this.vb(),
        (3 !== s && 2 !== s) ||
          (this.pb(t),
          this.mb(t, i),
          this.Ym.bt(),
          this.Am.forEach((t) => {
            t.Bp();
          }),
          3 === (null === (n = this.Im) || void 0 === n ? void 0 : n.Fn()) &&
            (this.Im.Jn(t),
            this.vb(),
            this.pb(this.Im),
            this.mb(this.Im, i),
            (t = this.Im),
            (this.Im = null))),
        this.Qv(t);
    }
    mb(t, i) {
      for (const n of t.Gn()) this.Qn(n, i);
    }
    pb(t) {
      const i = this.Hi.Wc();
      for (let n = 0; n < i.length; n++) t.Wn(n).Nn && i[n].z_();
    }
    Qn(t, i) {
      const n = this.Hi.St();
      switch (t.$n) {
        case 0:
          n.ic();
          break;
        case 1:
          n.nc(t.Ot);
          break;
        case 2:
          n.Kn(t.Ot);
          break;
        case 3:
          n.Zn(t.Ot);
          break;
        case 4:
          n.ju();
          break;
        case 5:
          t.Ot.Ku(i) || n.Zn(t.Ot.Zu(i));
      }
    }
    Cc(t) {
      null !== this.Im ? this.Im.Jn(t) : (this.Im = t),
        this.Lm ||
          ((this.Lm = !0),
          (this.Vm = window.requestAnimationFrame((t) => {
            if (((this.Lm = !1), (this.Vm = 0), null !== this.Im)) {
              const i = this.Im;
              (this.Im = null), this.ib(i, t);
              for (const n of i.Gn())
                if (5 === n.$n && !n.Ot.Ku(t)) {
                  this.$t().qn(n.Ot);
                  break;
                }
            }
          })));
    }
    vb() {
      this.Zm();
    }
    Zm() {
      const t = this.Hi.Wc(),
        i = t.length,
        n = this.Am.length;
      for (let t = i; t < n; t++) {
        const t = d(this.Am.pop());
        this.jm.removeChild(t.Uv()), t.Hp().p(this), t.$p().p(this), t.S();
      }
      for (let s = n; s < i; s++) {
        const i = new Os(this, t[s]);
        i.Hp().l(this.bb.bind(this), this),
          i.$p().l(this.wb.bind(this), this),
          this.Am.push(i),
          this.jm.insertBefore(i.Uv(), this.Ym.Uv());
      }
      for (let n = 0; n < i; n++) {
        const i = t[n],
          s = this.Am[n];
        s.Jv() !== i ? s.Dp(i) : s.Rp();
      }
      this.Gm(), this.cb();
    }
    gb(t, i, n) {
      var s;
      const e = new Map();
      if (null !== t) {
        this.Hi.wt().forEach((i) => {
          const n = i.An().sl(t);
          null !== n && e.set(i, n);
        });
      }
      let r;
      if (null !== t) {
        const i =
          null === (s = this.Hi.St().$i(t)) || void 0 === s
            ? void 0
            : s.originalTime;
        void 0 !== i && (r = i);
      }
      const h = this.$t().Ec(),
        l = null !== h && h.Lc instanceof qi ? h.Lc : void 0,
        a = null !== h && void 0 !== h.wv ? h.wv.mr : void 0;
      return {
        Mb: r,
        ie: null != t ? t : void 0,
        xb: null != i ? i : void 0,
        Sb: l,
        yb: e,
        kb: a,
        Cb: null != n ? n : void 0,
      };
    }
    bb(t, i, n) {
      this.fp.m(() => this.gb(t, i, n));
    }
    wb(t, i, n) {
      this.vp.m(() => this.gb(t, i, n));
    }
    qm(t, i, n) {
      this.yc.m(() => this.gb(t, i, n));
    }
    Gm() {
      const t = this._n.timeScale.visible ? "" : "none";
      this.Ym.Uv().style.display = t;
    }
    hb() {
      return this.Am[0].Jv().k_().W().visible;
    }
    lb() {
      return this.Am[0].Jv().C_().W().visible;
    }
    Xm() {
      return (
        "ResizeObserver" in window &&
        ((this.Nm = new ResizeObserver((t) => {
          const i = t.find((t) => t.target === this.Wm);
          i && this.Km(i.contentRect.width, i.contentRect.height);
        })),
        this.Nm.observe(this.Wm, { box: "border-box" }),
        !0)
      );
    }
    tb() {
      null !== this.Nm && this.Nm.disconnect(), (this.Nm = null);
    }
  }
  function Ws(t) {
    return Boolean(t.handleScroll.mouseWheel || t.handleScale.mouseWheel);
  }
  function js(t, i) {
    var n = {};
    for (var s in t)
      Object.prototype.hasOwnProperty.call(t, s) &&
        i.indexOf(s) < 0 &&
        (n[s] = t[s]);
    if (null != t && "function" == typeof Object.getOwnPropertySymbols) {
      var e = 0;
      for (s = Object.getOwnPropertySymbols(t); e < s.length; e++)
        i.indexOf(s[e]) < 0 &&
          Object.prototype.propertyIsEnumerable.call(t, s[e]) &&
          (n[s[e]] = t[s[e]]);
    }
    return n;
  }
  function Hs(t, i, n, s) {
    const e = n.value,
      r = { ie: i, ot: t, Ot: [e, e, e, e], Mb: s };
    return void 0 !== n.color && (r.O = n.color), r;
  }
  function $s(t, i, n, s) {
    const e = n.value,
      r = { ie: i, ot: t, Ot: [e, e, e, e], Mb: s };
    return (
      void 0 !== n.lineColor && (r.lt = n.lineColor),
      void 0 !== n.topColor && (r.ks = n.topColor),
      void 0 !== n.bottomColor && (r.Cs = n.bottomColor),
      r
    );
  }
  function Us(t, i, n, s) {
    const e = n.value,
      r = { ie: i, ot: t, Ot: [e, e, e, e], Mb: s };
    return (
      void 0 !== n.topLineColor && (r.Ce = n.topLineColor),
      void 0 !== n.bottomLineColor && (r.Te = n.bottomLineColor),
      void 0 !== n.topFillColor1 && (r.Me = n.topFillColor1),
      void 0 !== n.topFillColor2 && (r.xe = n.topFillColor2),
      void 0 !== n.bottomFillColor1 && (r.Se = n.bottomFillColor1),
      void 0 !== n.bottomFillColor2 && (r.ye = n.bottomFillColor2),
      r
    );
  }
  function qs(t, i, n, s) {
    const e = { ie: i, ot: t, Ot: [n.open, n.high, n.low, n.close], Mb: s };
    return void 0 !== n.color && (e.O = n.color), e;
  }
  function Ys(t, i, n, s) {
    const e = { ie: i, ot: t, Ot: [n.open, n.high, n.low, n.close], Mb: s };
    return (
      void 0 !== n.color && (e.O = n.color),
      void 0 !== n.borderColor && (e.Bt = n.borderColor),
      void 0 !== n.wickColor && (e.Uh = n.wickColor),
      e
    );
  }
  function Xs(t, i, n, s, e) {
    const r = d(e)(n),
      h = Math.max(...r),
      l = Math.min(...r),
      a = r[r.length - 1],
      o = [a, h, l, a],
      _ = n,
      { time: u, color: c } = _;
    return { ie: i, ot: t, Ot: o, Mb: s, We: js(_, ["time", "color"]), O: c };
  }
  function Ks(t) {
    return void 0 !== t.Ot;
  }
  function Zs(t, i) {
    return void 0 !== i.customValues && (t.Tb = i.customValues), t;
  }
  function Gs(t) {
    return (i, n, s, e, r, h) =>
      (function (t, i) {
        return i ? i(t) : void 0 === (n = t).open && void 0 === n.value;
        var n;
      })(s, h)
        ? Zs({ ot: i, ie: n, Mb: e }, s)
        : Zs(t(i, n, s, e, r), s);
  }
  function Js(t) {
    return {
      Candlestick: Gs(Ys),
      Bar: Gs(qs),
      Area: Gs($s),
      Baseline: Gs(Us),
      Histogram: Gs(Hs),
      Line: Gs(Hs),
      Custom: Gs(Xs),
    }[t];
  }
  function Qs(t) {
    return { ie: 0, Pb: new Map(), sa: t };
  }
  function te(t, i) {
    if (void 0 !== t && 0 !== t.length)
      return { Rb: i.key(t[0].ot), Db: i.key(t[t.length - 1].ot) };
  }
  function ie(t) {
    let i;
    return (
      t.forEach((t) => {
        void 0 === i && (i = t.Mb);
      }),
      d(i)
    );
  }
  class ne {
    constructor(t) {
      (this.Ob = new Map()),
        (this.Bb = new Map()),
        (this.Ab = new Map()),
        (this.Vb = []),
        (this.W_ = t);
    }
    S() {
      this.Ob.clear(), this.Bb.clear(), this.Ab.clear(), (this.Vb = []);
    }
    zb(t, i) {
      let n = 0 !== this.Ob.size,
        s = !1;
      const e = this.Bb.get(t);
      if (void 0 !== e)
        if (1 === this.Bb.size) (n = !1), (s = !0), this.Ob.clear();
        else for (const i of this.Vb) i.pointData.Pb.delete(t) && (s = !0);
      let r = [];
      if (0 !== i.length) {
        const n = i.map((t) => t.time),
          e = this.W_.createConverterToInternalObj(i),
          h = Js(t.Kh()),
          l = t.xa(),
          a = t.Sa();
        r = i.map((i, r) => {
          const o = e(i.time),
            _ = this.W_.key(o);
          let u = this.Ob.get(_);
          void 0 === u && ((u = Qs(o)), this.Ob.set(_, u), (s = !0));
          const c = h(o, u.ie, i, n[r], l, a);
          return u.Pb.set(t, c), c;
        });
      }
      n && this.Eb(), this.Ib(t, r);
      let h = -1;
      if (s) {
        const t = [];
        this.Ob.forEach((i) => {
          t.push({
            timeWeight: 0,
            time: i.sa,
            pointData: i,
            originalTime: ie(i.Pb),
          });
        }),
          t.sort((t, i) => this.W_.key(t.time) - this.W_.key(i.time)),
          (h = this.Lb(t));
      }
      return this.Nb(
        t,
        h,
        (function (t, i, n) {
          const s = te(t, n),
            e = te(i, n);
          if (void 0 !== s && void 0 !== e)
            return { Zl: s.Db >= e.Db && s.Rb >= e.Rb };
        })(this.Bb.get(t), e, this.W_)
      );
    }
    od(t) {
      return this.zb(t, []);
    }
    Fb(t, i) {
      const n = i;
      !(function (t) {
        void 0 === t.Mb && (t.Mb = t.time);
      })(n),
        this.W_.preprocessData(i);
      const s = this.W_.createConverterToInternalObj([i])(i.time),
        e = this.Ab.get(t);
      if (void 0 !== e && this.W_.key(s) < this.W_.key(e))
        throw new Error(
          `Cannot update oldest data, last time=${e}, new time=${s}`
        );
      let r = this.Ob.get(this.W_.key(s));
      const h = void 0 === r;
      void 0 === r && ((r = Qs(s)), this.Ob.set(this.W_.key(s), r));
      const l = Js(t.Kh()),
        a = t.xa(),
        o = t.Sa(),
        _ = l(s, r.ie, i, n.Mb, a, o);
      r.Pb.set(t, _), this.Wb(t, _);
      const u = { Zl: Ks(_) };
      if (!h) return this.Nb(t, -1, u);
      const c = {
          timeWeight: 0,
          time: r.sa,
          pointData: r,
          originalTime: ie(r.Pb),
        },
        d = Pt(this.Vb, this.W_.key(c.time), (t, i) => this.W_.key(t.time) < i);
      this.Vb.splice(d, 0, c);
      for (let t = d; t < this.Vb.length; ++t) se(this.Vb[t].pointData, t);
      return this.W_.fillWeightsForPoints(this.Vb, d), this.Nb(t, d, u);
    }
    Wb(t, i) {
      let n = this.Bb.get(t);
      void 0 === n && ((n = []), this.Bb.set(t, n));
      const s = 0 !== n.length ? n[n.length - 1] : null;
      null === s || this.W_.key(i.ot) > this.W_.key(s.ot)
        ? Ks(i) && n.push(i)
        : Ks(i)
        ? (n[n.length - 1] = i)
        : n.splice(-1, 1),
        this.Ab.set(t, i.ot);
    }
    Ib(t, i) {
      0 !== i.length
        ? (this.Bb.set(t, i.filter(Ks)), this.Ab.set(t, i[i.length - 1].ot))
        : (this.Bb.delete(t), this.Ab.delete(t));
    }
    Eb() {
      for (const t of this.Vb)
        0 === t.pointData.Pb.size && this.Ob.delete(this.W_.key(t.time));
    }
    Lb(t) {
      let i = -1;
      for (let n = 0; n < this.Vb.length && n < t.length; ++n) {
        const s = this.Vb[n],
          e = t[n];
        if (this.W_.key(s.time) !== this.W_.key(e.time)) {
          i = n;
          break;
        }
        (e.timeWeight = s.timeWeight), se(e.pointData, n);
      }
      if (
        (-1 === i &&
          this.Vb.length !== t.length &&
          (i = Math.min(this.Vb.length, t.length)),
        -1 === i)
      )
        return -1;
      for (let n = i; n < t.length; ++n) se(t[n].pointData, n);
      return this.W_.fillWeightsForPoints(t, i), (this.Vb = t), i;
    }
    jb() {
      if (0 === this.Bb.size) return null;
      let t = 0;
      return (
        this.Bb.forEach((i) => {
          0 !== i.length && (t = Math.max(t, i[i.length - 1].ie));
        }),
        t
      );
    }
    Nb(t, i, n) {
      const s = { Hb: new Map(), St: { Vu: this.jb() } };
      if (-1 !== i)
        this.Bb.forEach((i, e) => {
          s.Hb.set(e, { We: i, $b: e === t ? n : void 0 });
        }),
          this.Bb.has(t) || s.Hb.set(t, { We: [], $b: n }),
          (s.St.Ub = this.Vb),
          (s.St.qb = i);
      else {
        const i = this.Bb.get(t);
        s.Hb.set(t, { We: i || [], $b: n });
      }
      return s;
    }
  }
  function se(t, i) {
    (t.ie = i),
      t.Pb.forEach((t) => {
        t.ie = i;
      });
  }
  function ee(t) {
    const i = { value: t.Ot[3], time: t.Mb };
    return void 0 !== t.Tb && (i.customValues = t.Tb), i;
  }
  function re(t) {
    const i = ee(t);
    return void 0 !== t.O && (i.color = t.O), i;
  }
  function he(t) {
    const i = ee(t);
    return (
      void 0 !== t.lt && (i.lineColor = t.lt),
      void 0 !== t.ks && (i.topColor = t.ks),
      void 0 !== t.Cs && (i.bottomColor = t.Cs),
      i
    );
  }
  function le(t) {
    const i = ee(t);
    return (
      void 0 !== t.Ce && (i.topLineColor = t.Ce),
      void 0 !== t.Te && (i.bottomLineColor = t.Te),
      void 0 !== t.Me && (i.topFillColor1 = t.Me),
      void 0 !== t.xe && (i.topFillColor2 = t.xe),
      void 0 !== t.Se && (i.bottomFillColor1 = t.Se),
      void 0 !== t.ye && (i.bottomFillColor2 = t.ye),
      i
    );
  }
  function ae(t) {
    const i = {
      open: t.Ot[0],
      high: t.Ot[1],
      low: t.Ot[2],
      close: t.Ot[3],
      time: t.Mb,
    };
    return void 0 !== t.Tb && (i.customValues = t.Tb), i;
  }
  function oe(t) {
    const i = ae(t);
    return void 0 !== t.O && (i.color = t.O), i;
  }
  function _e(t) {
    const i = ae(t),
      { O: n, Bt: s, Uh: e } = t;
    return (
      void 0 !== n && (i.color = n),
      void 0 !== s && (i.borderColor = s),
      void 0 !== e && (i.wickColor = e),
      i
    );
  }
  function ue(t) {
    return {
      Area: he,
      Line: re,
      Baseline: le,
      Histogram: re,
      Bar: oe,
      Candlestick: _e,
      Custom: ce,
    }[t];
  }
  function ce(t) {
    const i = t.Mb;
    return Object.assign(Object.assign({}, t.We), { time: i });
  }
  const de = {
      vertLine: {
        color: "#9598A1",
        width: 1,
        style: 3,
        visible: !0,
        labelVisible: !0,
        labelBackgroundColor: "#131722",
      },
      horzLine: {
        color: "#9598A1",
        width: 1,
        style: 3,
        visible: !0,
        labelVisible: !0,
        labelBackgroundColor: "#131722",
      },
      mode: 1,
    },
    fe = {
      vertLines: { color: "#D6DCDE", style: 0, visible: !0 },
      horzLines: { color: "#D6DCDE", style: 0, visible: !0 },
    },
    ve = {
      background: { type: "solid", color: "#FFFFFF" },
      textColor: "#191919",
      fontSize: 12,
      fontFamily: V,
    },
    pe = {
      autoScale: !0,
      mode: 0,
      invertScale: !1,
      alignLabels: !0,
      borderVisible: !0,
      borderColor: "#2B2B43",
      entireTextOnly: !1,
      visible: !1,
      ticksVisible: !1,
      scaleMargins: { bottom: 0.1, top: 0.2 },
      minimumWidth: 0,
    },
    me = {
      rightOffset: 0,
      barSpacing: 6,
      minBarSpacing: 0.5,
      fixLeftEdge: !1,
      fixRightEdge: !1,
      lockVisibleTimeRangeOnResize: !1,
      rightBarStaysOnScroll: !1,
      borderVisible: !0,
      borderColor: "#2B2B43",
      visible: !0,
      timeVisible: !1,
      secondsVisible: !0,
      shiftVisibleRangeOnNewBar: !0,
      allowShiftVisibleRangeOnWhitespaceReplacement: !1,
      ticksVisible: !1,
      uniformDistribution: !1,
      minimumHeight: 0,
      allowBoldLabels: !0,
    },
    be = {
      color: "rgba(0, 0, 0, 0)",
      visible: !1,
      fontSize: 48,
      fontFamily: V,
      fontStyle: "",
      text: "",
      horzAlign: "center",
      vertAlign: "center",
    };
  function we() {
    return {
      width: 0,
      height: 0,
      autoSize: !1,
      layout: ve,
      crosshair: de,
      grid: fe,
      overlayPriceScales: Object.assign({}, pe),
      leftPriceScale: Object.assign(Object.assign({}, pe), { visible: !1 }),
      rightPriceScale: Object.assign(Object.assign({}, pe), { visible: !0 }),
      timeScale: me,
      watermark: be,
      localization: {
        locale: es ? navigator.language : "",
        dateFormat: "dd MMM 'yy",
      },
      handleScroll: {
        mouseWheel: !0,
        pressedMouseMove: !0,
        horzTouchDrag: !0,
        vertTouchDrag: !0,
      },
      handleScale: {
        axisPressedMouseMove: { time: !0, price: !0 },
        axisDoubleClickReset: { time: !0, price: !0 },
        mouseWheel: !0,
        pinch: !0,
      },
      kineticScroll: { mouse: !1, touch: !0 },
      trackingMode: { exitMode: 1 },
    };
  }
  class ge {
    constructor(t, i) {
      (this.Yb = t), (this.Xb = i);
    }
    applyOptions(t) {
      this.Yb.$t().Nc(this.Xb, t);
    }
    options() {
      return this.Ei().W();
    }
    width() {
      return rt(this.Xb) ? this.Yb.rb(this.Xb) : 0;
    }
    Ei() {
      return f(this.Yb.$t().Fc(this.Xb)).Dt;
    }
  }
  function Me(t, i, n) {
    const s = js(t, ["time", "originalTime"]),
      e = Object.assign({ time: i }, s);
    return void 0 !== n && (e.originalTime = n), e;
  }
  const xe = {
    color: "#FF0000",
    price: 0,
    lineStyle: 2,
    lineWidth: 1,
    lineVisible: !0,
    axisLabelVisible: !0,
    title: "",
    axisLabelColor: "",
    axisLabelTextColor: "",
  };
  class Se {
    constructor(t) {
      this.zh = t;
    }
    applyOptions(t) {
      this.zh.Fh(t);
    }
    options() {
      return this.zh.W();
    }
    Kb() {
      return this.zh;
    }
  }
  class ye {
    constructor(t, i, n, s, e) {
      (this.Zb = new k()),
        (this.zs = t),
        (this.Gb = i),
        (this.Jb = n),
        (this.W_ = e),
        (this.Qb = s);
    }
    S() {
      this.Zb.S();
    }
    priceFormatter() {
      return this.zs.fa();
    }
    priceToCoordinate(t) {
      const i = this.zs.Ct();
      return null === i ? null : this.zs.Dt().Rt(t, i.Ot);
    }
    coordinateToPrice(t) {
      const i = this.zs.Ct();
      return null === i ? null : this.zs.Dt().fn(t, i.Ot);
    }
    barsInLogicalRange(t) {
      if (null === t) return null;
      const i = new gn(new mn(t.from, t.to)).su(),
        n = this.zs.An();
      if (n.Li()) return null;
      const s = n.sl(i.Rs(), 1),
        e = n.sl(i.ui(), -1),
        r = f(n.tl()),
        h = f(n.Bn());
      if (null !== s && null !== e && s.ie > e.ie)
        return { barsBefore: t.from - r, barsAfter: h - t.to };
      const l = {
        barsBefore: null === s || s.ie === r ? t.from - r : s.ie - r,
        barsAfter: null === e || e.ie === h ? h - t.to : h - e.ie,
      };
      return null !== s && null !== e && ((l.from = s.Mb), (l.to = e.Mb)), l;
    }
    setData(t) {
      this.W_, this.zs.Kh(), this.Gb.tw(this.zs, t), this.iw("full");
    }
    update(t) {
      this.zs.Kh(), this.Gb.nw(this.zs, t), this.iw("update");
    }
    dataByIndex(t, i) {
      const n = this.zs.An().sl(t, i);
      if (null === n) return null;
      return ue(this.seriesType())(n);
    }
    data() {
      const t = ue(this.seriesType());
      return this.zs
        .An()
        .Qs()
        .map((i) => t(i));
    }
    subscribeDataChanged(t) {
      this.Zb.l(t);
    }
    unsubscribeDataChanged(t) {
      this.Zb.v(t);
    }
    setMarkers(t) {
      this.W_;
      const i = t.map((t) =>
        Me(t, this.W_.convertHorzItemToInternal(t.time), t.time)
      );
      this.zs.Jl(i);
    }
    markers() {
      return this.zs.Ql().map((t) => Me(t, t.originalTime, void 0));
    }
    applyOptions(t) {
      this.zs.Fh(t);
    }
    options() {
      return O(this.zs.W());
    }
    priceScale() {
      return this.Jb.priceScale(this.zs.Dt().ya());
    }
    createPriceLine(t) {
      const i = C(O(xe), t),
        n = this.zs.ta(i);
      return new Se(n);
    }
    removePriceLine(t) {
      this.zs.ia(t.Kb());
    }
    seriesType() {
      return this.zs.Kh();
    }
    attachPrimitive(t) {
      this.zs.ga(t),
        t.attached &&
          t.attached({
            chart: this.Qb,
            series: this,
            requestUpdate: () => this.zs.$t().ql(),
          });
    }
    detachPrimitive(t) {
      this.zs.Ma(t), t.detached && t.detached();
    }
    iw(t) {
      this.Zb.M() && this.Zb.m(t);
    }
  }
  class ke {
    constructor(t, i, n) {
      (this.sw = new k()),
        (this.du = new k()),
        (this.fm = new k()),
        (this.Hi = t),
        (this.Ml = t.St()),
        (this.Ym = i),
        this.Ml.Gu().l(this.ew.bind(this)),
        this.Ml.Ju().l(this.rw.bind(this)),
        this.Ym.Sm().l(this.hw.bind(this)),
        (this.W_ = n);
    }
    S() {
      this.Ml.Gu().p(this),
        this.Ml.Ju().p(this),
        this.Ym.Sm().p(this),
        this.sw.S(),
        this.du.S(),
        this.fm.S();
    }
    scrollPosition() {
      return this.Ml.Nu();
    }
    scrollToPosition(t, i) {
      i ? this.Ml.Xu(t, 1e3) : this.Hi.Zn(t);
    }
    scrollToRealTime() {
      this.Ml.Yu();
    }
    getVisibleRange() {
      const t = this.Ml.Tu();
      return null === t
        ? null
        : { from: t.from.originalTime, to: t.to.originalTime };
    }
    setVisibleRange(t) {
      const i = {
          from: this.W_.convertHorzItemToInternal(t.from),
          to: this.W_.convertHorzItemToInternal(t.to),
        },
        n = this.Ml.Ou(i);
      this.Hi._d(n);
    }
    getVisibleLogicalRange() {
      const t = this.Ml.Cu();
      return null === t ? null : { from: t.Rs(), to: t.ui() };
    }
    setVisibleLogicalRange(t) {
      c(t.from <= t.to, "The from index cannot be after the to index."),
        this.Hi._d(t);
    }
    resetTimeScale() {
      this.Hi.Xn();
    }
    fitContent() {
      this.Hi.ic();
    }
    logicalToCoordinate(t) {
      const i = this.Hi.St();
      return i.Li() ? null : i.zt(t);
    }
    coordinateToLogical(t) {
      return this.Ml.Li() ? null : this.Ml.zu(t);
    }
    timeToCoordinate(t) {
      const i = this.W_.convertHorzItemToInternal(t),
        n = this.Ml.Ta(i, !1);
      return null === n ? null : this.Ml.zt(n);
    }
    coordinateToTime(t) {
      const i = this.Hi.St(),
        n = i.zu(t),
        s = i.$i(n);
      return null === s ? null : s.originalTime;
    }
    width() {
      return this.Ym.Yp().width;
    }
    height() {
      return this.Ym.Yp().height;
    }
    subscribeVisibleTimeRangeChange(t) {
      this.sw.l(t);
    }
    unsubscribeVisibleTimeRangeChange(t) {
      this.sw.v(t);
    }
    subscribeVisibleLogicalRangeChange(t) {
      this.du.l(t);
    }
    unsubscribeVisibleLogicalRangeChange(t) {
      this.du.v(t);
    }
    subscribeSizeChange(t) {
      this.fm.l(t);
    }
    unsubscribeSizeChange(t) {
      this.fm.v(t);
    }
    applyOptions(t) {
      this.Ml.Fh(t);
    }
    options() {
      return Object.assign(Object.assign({}, O(this.Ml.W())), {
        barSpacing: this.Ml.ee(),
      });
    }
    ew() {
      this.sw.M() && this.sw.m(this.getVisibleRange());
    }
    rw() {
      this.du.M() && this.du.m(this.getVisibleLogicalRange());
    }
    hw(t) {
      this.fm.m(t.width, t.height);
    }
  }
  function Ce(t) {
    if (void 0 === t || "custom" === t.type) return;
    const i = t;
    void 0 !== i.minMove &&
      void 0 === i.precision &&
      (i.precision = (function (t) {
        if (t >= 1) return 0;
        let i = 0;
        for (; i < 8; i++) {
          const n = Math.round(t);
          if (Math.abs(n - t) < 1e-8) return i;
          t *= 10;
        }
        return i;
      })(i.minMove));
  }
  function Te(t) {
    return (
      (function (t) {
        if (D(t.handleScale)) {
          const i = t.handleScale;
          t.handleScale = {
            axisDoubleClickReset: { time: i, price: i },
            axisPressedMouseMove: { time: i, price: i },
            mouseWheel: i,
            pinch: i,
          };
        } else if (void 0 !== t.handleScale) {
          const { axisPressedMouseMove: i, axisDoubleClickReset: n } =
            t.handleScale;
          D(i) && (t.handleScale.axisPressedMouseMove = { time: i, price: i }),
            D(n) &&
              (t.handleScale.axisDoubleClickReset = { time: n, price: n });
        }
        const i = t.handleScroll;
        D(i) &&
          (t.handleScroll = {
            horzTouchDrag: i,
            vertTouchDrag: i,
            mouseWheel: i,
            pressedMouseMove: i,
          });
      })(t),
      t
    );
  }
  class Pe {
    constructor(t, i, n) {
      (this.lw = new Map()),
        (this.aw = new Map()),
        (this.ow = new k()),
        (this._w = new k()),
        (this.uw = new k()),
        (this.cw = new ne(i));
      const s = void 0 === n ? O(we()) : C(O(we()), Te(n));
      (this.W_ = i),
        (this.Yb = new Fs(t, s, i)),
        this.Yb.Hp().l((t) => {
          this.ow.M() && this.ow.m(this.dw(t()));
        }, this),
        this.Yb.$p().l((t) => {
          this._w.M() && this._w.m(this.dw(t()));
        }, this),
        this.Yb.$c().l((t) => {
          this.uw.M() && this.uw.m(this.dw(t()));
        }, this);
      const e = this.Yb.$t();
      this.fw = new ke(e, this.Yb.Qm(), this.W_);
    }
    remove() {
      this.Yb.Hp().p(this),
        this.Yb.$p().p(this),
        this.Yb.$c().p(this),
        this.fw.S(),
        this.Yb.S(),
        this.lw.clear(),
        this.aw.clear(),
        this.ow.S(),
        this._w.S(),
        this.uw.S(),
        this.cw.S();
    }
    resize(t, i, n) {
      this.autoSizeActive() || this.Yb.Km(t, i, n);
    }
    addCustomSeries(t, i) {
      const n = v(t),
        s = Object.assign(Object.assign({}, h), n.defaultOptions());
      return this.pw("Custom", s, i, n);
    }
    addAreaSeries(t) {
      return this.pw("Area", s, t);
    }
    addBaselineSeries(t) {
      return this.pw("Baseline", e, t);
    }
    addBarSeries(t) {
      return this.pw("Bar", i, t);
    }
    addCandlestickSeries(i = {}) {
      return (
        (function (t) {
          void 0 !== t.borderColor &&
            ((t.borderUpColor = t.borderColor),
            (t.borderDownColor = t.borderColor)),
            void 0 !== t.wickColor &&
              ((t.wickUpColor = t.wickColor), (t.wickDownColor = t.wickColor));
        })(i),
        this.pw("Candlestick", t, i)
      );
    }
    addHistogramSeries(t) {
      return this.pw("Histogram", r, t);
    }
    addLineSeries(t) {
      return this.pw("Line", n, t);
    }
    removeSeries(t) {
      const i = d(this.lw.get(t)),
        n = this.cw.od(i);
      this.Yb.$t().od(i), this.mw(n), this.lw.delete(t), this.aw.delete(i);
    }
    tw(t, i) {
      this.mw(this.cw.zb(t, i));
    }
    nw(t, i) {
      this.mw(this.cw.Fb(t, i));
    }
    subscribeClick(t) {
      this.ow.l(t);
    }
    unsubscribeClick(t) {
      this.ow.v(t);
    }
    subscribeCrosshairMove(t) {
      this.uw.l(t);
    }
    unsubscribeCrosshairMove(t) {
      this.uw.v(t);
    }
    subscribeDblClick(t) {
      this._w.l(t);
    }
    unsubscribeDblClick(t) {
      this._w.v(t);
    }
    priceScale(t) {
      return new ge(this.Yb, t);
    }
    timeScale() {
      return this.fw;
    }
    applyOptions(t) {
      this.Yb.Fh(Te(t));
    }
    options() {
      return this.Yb.W();
    }
    takeScreenshot() {
      return this.Yb.sb();
    }
    autoSizeActive() {
      return this.Yb.ab();
    }
    chartElement() {
      return this.Yb.ob();
    }
    paneSize() {
      const t = this.Yb.ub();
      return { height: t.height, width: t.width };
    }
    setCrosshairPosition(t, i, n) {
      const s = this.lw.get(n);
      if (void 0 === s) return;
      const e = this.Yb.$t()._r(s);
      null !== e && this.Yb.$t().sd(t, i, e);
    }
    clearCrosshairPosition() {
      this.Yb.$t().ed(!0);
    }
    pw(t, i, n = {}, s) {
      Ce(n.priceFormat);
      const e = C(O(l), O(i), n),
        r = this.Yb.$t().ld(t, e, s),
        h = new ye(r, this, this, this, this.W_);
      return this.lw.set(h, r), this.aw.set(r, h), h;
    }
    mw(t) {
      const i = this.Yb.$t();
      i.rd(t.St.Vu, t.St.Ub, t.St.qb),
        t.Hb.forEach((t, i) => i.J(t.We, t.$b)),
        i.Iu();
    }
    bw(t) {
      return d(this.aw.get(t));
    }
    dw(t) {
      const i = new Map();
      t.yb.forEach((t, n) => {
        const s = n.Kh(),
          e = ue(s)(t);
        if ("Custom" !== s)
          c(
            (function (t) {
              return void 0 !== t.open || void 0 !== t.value;
            })(e)
          );
        else {
          const t = n.Sa();
          c(!t || !1 === t(e));
        }
        i.set(this.bw(n), e);
      });
      const n = void 0 !== t.Sb && this.aw.has(t.Sb) ? this.bw(t.Sb) : void 0;
      return {
        time: t.Mb,
        logical: t.ie,
        point: t.xb,
        hoveredSeries: n,
        hoveredObjectId: t.kb,
        seriesData: i,
        sourceEvent: t.Cb,
      };
    }
  }
  function Re(t, i, n) {
    let s;
    if (R(t)) {
      const i = document.getElementById(t);
      c(null !== i, `Cannot find element in DOM with id=${t}`), (s = i);
    } else s = t;
    const e = new Pe(s, i, n);
    return i.setOptions(e.options()), e;
  }
  const De = Object.assign(Object.assign({}, l), h);
  var Oe = Object.freeze({
    __proto__: null,
    get ColorType() {
      return Dn;
    },
    get CrosshairMode() {
      return st;
    },
    get LastPriceAnimationMode() {
      return Pn;
    },
    get LineStyle() {
      return o;
    },
    get LineType() {
      return a;
    },
    get MismatchDirection() {
      return Bi;
    },
    get PriceLineSource() {
      return Rn;
    },
    get PriceScaleMode() {
      return un;
    },
    get TickMarkType() {
      return On;
    },
    get TrackingModeExitMode() {
      return Tn;
    },
    createChart: function (t, i) {
      return Re(t, new Zn(), Zn.Dd(i));
    },
    createChartEx: Re,
    customSeriesDefaultOptions: De,
    isBusinessDay: An,
    isUTCTimestamp: Vn,
    version: function () {
      return "4.1.4";
    },
  });
  window.LightweightCharts = Oe;
})();
