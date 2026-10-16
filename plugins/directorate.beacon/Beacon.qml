import Quickshell
import Quickshell.Hyprland
import Quickshell.Io
import Quickshell.Wayland
import QtQuick

// DIRECTORATE: STN-0117 beacon.
//
// At the desk: a click-through layer just above the wallpaper blinks your chair
// in institutional blue and pulses your link to the mainframe, while the
// SUPERVISION sheet is the background.
//
// Away: while the screensaver runs under the DIRECTORATE theme, an overlay
// covers it with the SUPERVISION sheet and your chair blinking red. The overlay
// takes no input, so keys and the mouse still reach (and dismiss) the
// screensaver underneath. The lock screen shows the same in the lock plugin clone.
Item {
  id: root

  readonly property string home: Quickshell.env("HOME")
  readonly property string backgroundLink: home + "/.local/state/omarchy/current/background"
  readonly property string themeNameFile: home + "/.local/state/omarchy/current/theme.name"
  readonly property string themeDir: home + "/.config/omarchy/themes/directorate"
  readonly property string sheetImage: themeDir + "/backgrounds/6-supervision.png"
  readonly property string screensaverClass: "org.omarchy.screensaver"

  property bool atDesk: false
  property bool screensaver: false
  property var seat: null
  readonly property bool themeActive: themeNameView.text().trim() === "directorate"

  FileView {
    id: seatView
    path: root.themeDir + "/extras/build/6-supervision.seat.json"
    watchChanges: true
    onFileChanged: reload()
    onLoaded: {
      try { root.seat = JSON.parse(text()) } catch (e) { root.seat = null }
    }
    onLoadFailed: root.seat = null
  }

  FileView {
    id: themeNameView
    path: root.themeNameFile
    watchChanges: true
    onFileChanged: reload()
  }

  Process {
    id: readlinkProc
    command: ["readlink", "-f", root.backgroundLink]
    stdout: StdioCollector {
      onStreamFinished: root.atDesk = String(text || "").trim().endsWith("/6-supervision.png")
    }
  }

  Process {
    id: clientsProc
    command: ["hyprctl", "clients", "-j"]
    stdout: StdioCollector {
      onStreamFinished: {
        var found = false
        try {
          var clients = JSON.parse(text)
          for (var i = 0; i < clients.length; i++)
            if (clients[i].class === root.screensaverClass) found = true
        } catch (e) {}
        root.screensaver = found
      }
    }
  }

  function checkScreensaver() {
    if (!clientsProc.running) clientsProc.running = true
  }

  Connections {
    target: Hyprland
    function onRawEvent(event) {
      var name = String(event && event.name ? event.name : "")
      if (name === "openwindow" || name === "closewindow") root.checkScreensaver()
    }
  }

  Timer {
    interval: 1500
    running: true
    repeat: true
    triggeredOnStart: true
    onTriggered: if (!readlinkProc.running) readlinkProc.running = true
  }

  Component.onCompleted: checkScreensaver()

  // ---- at the desk
  Variants {
    model: root.atDesk && root.seat ? Quickshell.screens : []

    PanelWindow {
      required property var modelData

      screen: modelData
      anchors { top: true; bottom: true; left: true; right: true }
      color: "transparent"
      exclusionMode: ExclusionMode.Ignore
      mask: Region {}

      WlrLayershell.namespace: "directorate-beacon"
      WlrLayershell.layer: WlrLayer.Bottom
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

      StationPulse {
        anchors.fill: parent
        seat: root.seat
        seatColor: root.seat.active
        linkColor: root.seat.link
        linkActive: true
      }
    }
  }

  // ---- away: over the screensaver
  Variants {
    model: root.screensaver && root.themeActive && root.seat ? Quickshell.screens : []

    PanelWindow {
      required property var modelData

      screen: modelData
      anchors { top: true; bottom: true; left: true; right: true }
      color: "#0b0b0a"
      exclusionMode: ExclusionMode.Ignore
      mask: Region {}

      WlrLayershell.namespace: "directorate-away"
      WlrLayershell.layer: WlrLayer.Overlay
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

      Image {
        anchors.fill: parent
        source: "file://" + root.sheetImage
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: false
      }

      StationPulse {
        anchors.fill: parent
        seat: root.seat
        seatColor: root.seat.away
        linkColor: root.seat.link
        linkActive: false
      }
    }
  }
}
