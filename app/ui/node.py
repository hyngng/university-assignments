"""Canvas node widget renderer."""

import tkinter as tk
from typing import Optional

from app.tools import ToolRegistry


def _darken_hex(hex_color: str, factor: float = 0.85) -> str:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return f"#{hex_color}"
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"


class NodeWidget:
    """A drawn canvas node with title and status text."""

    def __init__(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        tool_id: str,
        label: str,
        width: float = 260,
        height: float = 56,
    ) -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self.tool_id = tool_id
        self.label = label
        self.width = width
        self.height = height

        tool_def = ToolRegistry.get(tool_id)
        self.fill_color = tool_def.color_hex
        self.dark_fill_color = _darken_hex(self.fill_color, 0.75)
        self.text_color = tool_def.text_color
        self.display_name = tool_def.display_name

        self.rect_id: Optional[int] = None
        self.title_id: Optional[int] = None
        self.status_id: Optional[int] = None
        self.shadow_id: Optional[int] = None
        self._completed = False

    def _get_chamfered_points(self, x1: float, y1: float, x2: float, y2: float, cut: float) -> list[float]:
        return [
            x1 + cut, y1,
            x2 - cut, y1,
            x2, y1 + cut,
            x2, y2 - cut,
            x2 - cut, y2,
            x1 + cut, y2,
            x1, y2 - cut,
            x1, y1 + cut,
        ]

    def draw(self, scale: float = 1.0) -> None:
        w = self.width * scale / 2
        h = self.height * scale / 2
        x1, y1 = self.x - w, self.y - h
        x2, y2 = self.x + w, self.y + h
        cut = 12 * scale
        shadow_offset = 4 * scale

        self.shadow_id = self.canvas.create_polygon(
            self._get_chamfered_points(
                x1 + shadow_offset,
                y1 + shadow_offset,
                x2 + shadow_offset,
                y2 + shadow_offset,
                cut,
            ),
            fill="#111111",
            outline="",
            width=0,
            smooth=True,
        )
        self.rect_id = self.canvas.create_polygon(
            self._get_chamfered_points(x1, y1, x2, y2, cut),
            fill=self.dark_fill_color,
            outline=self.text_color,
            width=2,
            smooth=True,
        )
        self.title_id = self.canvas.create_text(
            self.x,
            self.y - 10 * scale,
            text=self.display_name,
            fill=self.text_color,
            font=("Segoe UI", max(9, int(13 * scale)), "bold"),
            anchor="center",
        )
        self.status_id = self.canvas.create_text(
            self.x,
            self.y + 12 * scale,
            text="[실행 중...]",
            fill="#666666",
            font=("Segoe UI", max(8, int(10 * scale))),
            anchor="center",
        )

    def update_scale(self, scale: float) -> None:
        w = self.width * scale / 2
        h = self.height * scale / 2
        x1, y1 = self.x - w, self.y - h
        x2, y2 = self.x + w, self.y + h
        cut = 12 * scale
        shadow_offset = 4 * scale

        if self.shadow_id:
            self.canvas.coords(
                self.shadow_id,
                *self._get_chamfered_points(
                    x1 + shadow_offset,
                    y1 + shadow_offset,
                    x2 + shadow_offset,
                    y2 + shadow_offset,
                    cut,
                ),
            )
        if self.rect_id:
            self.canvas.coords(self.rect_id, *self._get_chamfered_points(x1, y1, x2, y2, cut))
        if self.title_id:
            self.canvas.coords(self.title_id, self.x, self.y - 10 * scale)
            self.canvas.itemconfigure(
                self.title_id,
                font=("Segoe UI", max(9, int(13 * scale)), "bold"),
            )
        if self.status_id:
            self.canvas.coords(self.status_id, self.x, self.y + 12 * scale)
            self.canvas.itemconfigure(
                self.status_id,
                font=("Segoe UI", max(8, int(10 * scale))),
            )

    def set_completed(self) -> None:
        if self.status_id and not self._completed:
            self.canvas.itemconfigure(self.status_id, text="[완료]", fill="#4AF626")
            if self.rect_id:
                self.canvas.itemconfigure(self.rect_id, fill=self.fill_color)
            self._completed = True

    def set_active(self) -> None:
        if self.status_id:
            self.canvas.itemconfigure(self.status_id, text="[실행 중...]", fill="#666666")
        if self.rect_id:
            self.canvas.itemconfigure(self.rect_id, fill=self.dark_fill_color)
        self._completed = False

    def dim(self) -> None:
        if self.rect_id:
            self.canvas.itemconfigure(self.rect_id, fill="#1A1A1A", outline="#333333")
        if self.title_id:
            self.canvas.itemconfigure(self.title_id, fill="#555555")
        if self.status_id:
            self.canvas.itemconfigure(self.status_id, fill="#444444")
        if self.shadow_id:
            self.canvas.itemconfigure(self.shadow_id, fill="#0A0A0A")
