import QtQuick

// DIRECTORATE designation plate: station code.
Item {
  id: root
  property var bar
  property string moduleName
  property var settings

  readonly property color fg: bar ? bar.foreground : "#b0cbd0"
  readonly property string family: bar ? bar.fontFamily : "monospace"

  implicitWidth: row.implicitWidth + 16
  implicitHeight: bar ? bar.barSize : 26

  Row {
    id: row
    anchors.centerIn: parent
    spacing: 8

    Text {
      anchors.verticalCenter: parent.verticalCenter
      text: root.settings && root.settings.station ? root.settings.station : "STN-0117"
      color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.45)
      font.family: root.family
      font.pixelSize: 10
      font.letterSpacing: 1.5
    }
  }
}
