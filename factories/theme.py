from model.theme import Theme

DefaultTheme = Theme()

JungleTheme = Theme(
    color="green",
    bg_color="yellow",
    custom_line_chars=["█", "▓", "▒", "░"],
    custom_line_type="back&forth",
)
