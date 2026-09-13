-- Flag-striped border with a tekhelet neon glow on the focused window
local active_border_color = { colors = { "rgba(3d7effff)", "rgba(ffffffff)", "rgba(3d7effff)" }, angle = 90 }
local inactive_border_color = "rgba(1b2a5a99)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },

  decoration = {
    shadow = {
      enabled = true,
      range = 14,
      render_power = 3,
      color = "rgba(3d7effaa)",
      color_inactive = "rgba(00000055)",
    },
  },
})
