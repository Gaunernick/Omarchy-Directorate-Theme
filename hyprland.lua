-- DIRECTORATE — the floor plan.
--
-- Windows are cubicles: hard rectangles on an 8px module, separated by
-- narrow corridors and set inside a wide perimeter wall. Only the operator's
-- active station is lit; every other station recedes into the concrete.
-- Motion is mechanical: short, decisive, no bounce.

local active_border_color = "rgb(0e62fe)"
local inactive_border_color = "rgb(2a2e30)"

hl.config({
  general = {
    -- 8px corridors between stations (4 + 4), 8px perimeter wall.
    gaps_in = 4,
    gaps_out = 8,
    border_size = 2,

    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  decoration = {
    rounding = 0,

    -- Unlit stations.
    dim_inactive = true,
    dim_strength = 0.28,

    shadow = { enabled = false },
    blur = { enabled = false },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },

    groupbar = {
      font_family = "BlexMono Nerd Font",
      font_size = 11,
      font_weight_active = "bold",
      font_weight_inactive = "normal",
      height = 18,
      indicator_height = 2,
      indicator_gap = 0,
      gaps_in = 4,
      gradients = false,
      text_color = "rgb(e7ecec)",
      text_color_inactive = "rgb(5c6360)",
      col = {
        active = "rgb(0e62fe)",
        inactive = "rgb(2a2e30)",
      },
    },
  },
})

-- Mechanical motion: a servo that snaps into place, never overshoots.
hl.curve("servo", { type = "bezier", points = { { 0.2, 0 }, { 0, 1 } } })

-- Borders switch state instantly, like a relay.
hl.animation({ leaf = "border", enabled = false })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 2.2, bezier = "servo", style = "popin 96%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.2, bezier = "linear", style = "popin 96%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 2.4, bezier = "servo" })
-- Workspaces slide like filing-cabinet drawers.
hl.animation({ leaf = "workspaces", enabled = true, speed = 2.6, bezier = "servo", style = "slidevert" })

-- No translucency. Concrete is opaque.
o.window({ tag = "default-opacity" }, { opacity = "1 1" })
