import QtQuick
import Quickshell.Io

// DIRECTORATE telemetry: CPU and memory as segmented instrument meters.
// Segments are cyan; past 85% they turn alarm red.
Item {
  id: root
  property var bar
  property string moduleName
  property var settings

  readonly property color cyan: "#37a8c2"
  readonly property color red: "#d24646"
  readonly property color fg: bar ? bar.foreground : "#b0cbd0"
  readonly property string family: bar ? bar.fontFamily : "monospace"
  readonly property int segments: 10

  property real cpu: 0
  property real mem: 0
  property var lastTotal: 0
  property var lastIdle: 0

  implicitWidth: row.implicitWidth + 16
  implicitHeight: bar ? bar.barSize : 26

  function parse(textValue) {
    var lines = textValue.split("\n")
    var memTotal = 0, memAvail = 0
    for (var i = 0; i < lines.length; i++) {
      var l = lines[i]
      if (l.indexOf("cpu ") === 0) {
        var p = l.trim().split(/\s+/).slice(1).map(Number)
        var idle = p[3] + (p[4] || 0)
        var total = 0
        for (var j = 0; j < p.length; j++) total += p[j]
        if (root.lastTotal > 0) {
          var dt = total - root.lastTotal
          var di = idle - root.lastIdle
          if (dt > 0) root.cpu = Math.max(0, Math.min(1, 1 - di / dt))
        }
        root.lastTotal = total
        root.lastIdle = idle
      } else if (l.indexOf("MemTotal:") === 0) {
        memTotal = Number(l.split(/\s+/)[1])
      } else if (l.indexOf("MemAvailable:") === 0) {
        memAvail = Number(l.split(/\s+/)[1])
      }
    }
    if (memTotal > 0) root.mem = 1 - memAvail / memTotal
  }

  Process {
    id: probe
    command: ["cat", "/proc/stat", "/proc/meminfo"]
    stdout: StdioCollector {
      onStreamFinished: root.parse(this.text)
    }
  }

  Timer {
    interval: 2000
    running: true
    repeat: true
    triggeredOnStart: true
    onTriggered: probe.running = true
  }

  component Meter: Row {
    id: meter
    property string label
    property real value
    spacing: 5

    Text {
      anchors.verticalCenter: parent.verticalCenter
      text: meter.label
      color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.45)
      font.family: root.family
      font.pixelSize: 10
      font.letterSpacing: 1.5
    }

    Row {
      anchors.verticalCenter: parent.verticalCenter
      spacing: 1
      Repeater {
        model: root.segments
        Rectangle {
          required property int index
          readonly property bool on: index < Math.round(meter.value * root.segments)
          width: 4; height: 9
          color: on ? (meter.value > 0.85 ? root.red : root.cyan) : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.12)
        }
      }
    }

    Text {
      anchors.verticalCenter: parent.verticalCenter
      text: ("  " + Math.round(meter.value * 100)).slice(-3) + "%"
      color: root.fg
      font.family: root.family
      font.pixelSize: 10
    }
  }

  Row {
    id: row
    anchors.centerIn: parent
    spacing: 14
    Meter { label: "CPU"; value: root.cpu }
    Meter { label: "MEM"; value: root.mem }
  }

  MouseArea {
    anchors.fill: parent
    onClicked: if (root.bar) root.bar.run("omarchy-launch-or-focus-tui btop")
  }
}
