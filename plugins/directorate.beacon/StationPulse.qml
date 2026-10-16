import QtQuick
import QtQuick.Shapes

// DIRECTORATE: STN-0117 on the SUPERVISION sheet. Fills its parent, maps the
// sheet's artboard the way PreserveAspectCrop does, blinks the chair and, while
// the link is live, pulses the route from the mainframe with a packet riding it.
// `seat` is build/6-supervision.seat.json. A copy lives in the lock plugin clone.
Item {
  id: root

  property var seat: null
  property color seatColor: "#0e62fe"
  property color linkColor: "#37a8c2"
  property bool linkActive: true
  property int period: 1600   // ms per half-cycle: dark -> lit or lit -> dark

  readonly property bool ready: !!seat && !!seat.artboard
  readonly property real artW: ready ? seat.artboard[0] : 1920
  readonly property real artH: ready ? seat.artboard[1] : 1080
  readonly property real k: Math.max(width / artW, height / artH)
  readonly property real ox: (width - artW * k) / 2
  readonly property real oy: (height - artH * k) / 2
  readonly property real s: ready ? seat.size * k : 0

  readonly property var points: {
    var out = []
    var route = ready && seat.route ? seat.route : []
    for (var i = 0; i < route.length; i++) out.push(Qt.point(ox + route[i][0] * k, oy + route[i][1] * k))
    return out
  }
  readonly property real routeLength: {
    var total = 0
    for (var i = 1; i < points.length; i++) total += Math.hypot(points[i].x - points[i - 1].x, points[i].y - points[i - 1].y)
    return total
  }

  function pointAt(t) {
    if (points.length < 2) return Qt.point(0, 0)
    var left = t * routeLength
    for (var i = 1; i < points.length; i++) {
      var a = points[i - 1], b = points[i]
      var seg = Math.hypot(b.x - a.x, b.y - a.y)
      if (left <= seg || i === points.length - 1) {
        var f = seg > 0 ? Math.min(1, left / seg) : 0
        return Qt.point(a.x + (b.x - a.x) * f, a.y + (b.y - a.y) * f)
      }
      left -= seg
    }
    return points[points.length - 1]
  }

  visible: ready

  // ---- link: a soft glow and a brighter core trace, breathing together
  Item {
    anchors.fill: parent
    visible: root.linkActive && root.points.length > 1
    opacity: 0.15

    SequentialAnimation on opacity {
      loops: Animation.Infinite
      running: root.linkActive
      NumberAnimation { to: 0.9; duration: root.period * 0.9; easing.type: Easing.InOutSine }
      NumberAnimation { to: 0.15; duration: root.period * 1.1; easing.type: Easing.InOutSine }
    }

    Repeater {
      model: [{ w: 6.0, a: 0.18 }, { w: 3.2, a: 0.35 }, { w: 1.6, a: 1.0 }]
      Shape {
        required property var modelData
        anchors.fill: parent
        preferredRendererType: Shape.CurveRenderer
        opacity: modelData.a
        ShapePath {
          strokeColor: root.linkColor
          strokeWidth: modelData.w * root.k
          fillColor: "transparent"
          joinStyle: ShapePath.MiterJoin
          capStyle: ShapePath.FlatCap
          PathPolyline { path: root.points }
        }
      }
    }
  }

  // ---- packet: core -> seat, then a short rest
  Item {
    id: packet
    visible: root.linkActive && root.points.length > 1
    property real t: 0
    readonly property point at: root.pointAt(t)
    x: at.x
    y: at.y
    opacity: t > 0.97 ? (1 - t) / 0.03 : 1

    SequentialAnimation on t {
      loops: Animation.Infinite
      running: root.linkActive
      NumberAnimation { from: 0; to: 1; duration: 2600; easing.type: Easing.InOutQuad }
      PauseAnimation { duration: 1100 }
    }

    Rectangle {
      width: 6 * root.k; height: width; radius: width / 2
      x: -width / 2; y: -height / 2
      color: root.linkColor
      opacity: 0.35
    }
    Rectangle {
      width: 2.6 * root.k; height: width; radius: width / 2
      x: -width / 2; y: -height / 2
      color: "#e7ecec"
    }
  }

  // ---- the seat
  Item {
    x: root.ready ? root.ox + root.seat.x * root.k : 0
    y: root.ready ? root.oy + root.seat.y * root.k : 0
    opacity: 0.08

    SequentialAnimation on opacity {
      loops: Animation.Infinite
      running: true
      NumberAnimation { to: 1.0; duration: root.period; easing.type: Easing.InOutSine }
      PauseAnimation { duration: 250 }
      NumberAnimation { to: 0.08; duration: root.period; easing.type: Easing.InOutSine }
      PauseAnimation { duration: 450 }
    }

    Repeater {
      model: [{ r: 7.0, a: 0.10 }, { r: 4.5, a: 0.18 }, { r: 2.6, a: 0.30 }]
      Rectangle {
        required property var modelData
        width: root.s * modelData.r * 2
        height: width
        radius: width / 2
        x: -width / 2
        y: -height / 2
        color: root.seatColor
        opacity: modelData.a
      }
    }

    // Same shape as honeycomb_desks.chair()
    Item {
      rotation: root.ready ? root.seat.deg : 0
      Rectangle {
        x: -root.s * 0.5; y: -root.s * 0.42
        width: root.s; height: root.s * 0.8
        radius: root.s * 0.2
        color: root.seatColor
        antialiasing: true
      }
      Rectangle {
        x: -root.s * 0.55; y: root.s * 0.42
        width: root.s * 1.1; height: root.s * 0.28
        radius: root.s * 0.1
        color: root.seatColor
        antialiasing: true
      }
    }
  }
}
