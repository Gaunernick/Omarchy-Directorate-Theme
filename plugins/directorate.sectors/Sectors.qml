import QtQuick
import QtQuick.Layouts
import Quickshell.Hyprland
import qs.Commons
import qs.Ui

// DIRECTORATE workspaces: a row of numbered sector cells.
// Active sector is a solid institutional-blue block (matches the active window frame), occupied sectors carry a hairline
// frame, empty sectors are barely-there outlines.
BarWidget {
  id: root
  moduleName: "directorate.sectors"

  function workspaceById(id) {
    var values = Hyprland.workspaces.values
    for (var i = 0; i < values.length; i++) {
      if (values[i].id === id) return values[i]
    }
    return null
  }

  function workspaceIds() {
    var ids = [1, 2, 3, 4, 5]
    var values = Hyprland.workspaces.values
    for (var i = 0; i < values.length; i++) {
      var id = values[i].id
      if (id > 0 && id <= 10 && ids.indexOf(id) === -1) ids.push(id)
    }
    ids.sort(function(left, right) { return left - right })
    return ids
  }

  function focusWorkspace(id) {
    if (!root.bar) return
    root.bar.run("hyprctl dispatch " + Util.shellQuote("hl.dsp.focus({ workspace = \"" + id + "\" })"))
  }

  readonly property color activeColor: "#0e62fe"
  readonly property int cellWidth: 24
  readonly property int cellHeight: Math.max(12, root.barSize - 10)
  readonly property real trailingGap: root.vertical ? 0 : 10

  implicitWidth: grid.implicitWidth + trailingGap
  implicitHeight: root.vertical ? grid.implicitHeight : root.barSize

  GridLayout {
    id: grid
    anchors.verticalCenter: parent.verticalCenter
    anchors.left: parent.left
    columns: root.vertical ? 1 : root.workspaceIds().length
    columnSpacing: 3
    rowSpacing: 3

    Repeater {
      model: root.workspaceIds()

      Rectangle {
        id: cell
        required property int modelData

        readonly property var workspace: root.workspaceById(modelData)
        readonly property bool occupied: workspace !== null && workspace.toplevels.values.length > 0
        readonly property bool focused: Hyprland.focusedWorkspace !== null && Hyprland.focusedWorkspace.id === modelData

        Layout.preferredWidth: root.vertical ? root.barSize - 8 : root.cellWidth
        Layout.preferredHeight: root.vertical ? 16 : root.cellHeight
        radius: 0
        color: focused ? root.activeColor : "transparent"
        border.width: focused ? 0 : 1
        border.color: mouse.containsMouse
          ? Color.accent
          : Util.alpha(Color.foreground, occupied ? 0.55 : 0.14)

        Text {
          anchors.centerIn: parent
          text: (cell.modelData < 10 ? "0" : "") + String(cell.modelData)
          color: cell.focused ? "#e7ecec" : Util.alpha(Color.foreground, cell.occupied ? 1.0 : 0.35)
          font.family: root.bar ? root.bar.fontFamily : "monospace"
          font.pixelSize: 11
          font.bold: cell.focused
          font.letterSpacing: 0.5
        }

        MouseArea {
          id: mouse
          anchors.fill: parent
          hoverEnabled: true
          cursorShape: Qt.PointingHandCursor
          onClicked: root.focusWorkspace(cell.modelData)
        }
      }
    }
  }
}
