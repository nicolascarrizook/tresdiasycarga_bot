"""
Utility functions for keyboard creation and management.
"""
from typing import List, Dict, Any, Optional, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import math

from ..config import KEYBOARD_TEXTS


class KeyboardBuilder:
    """Builder class for creating keyboards."""
    
    def __init__(self):
        self.buttons = []
        self.current_row = []
    
    def add_button(self, text: str, callback_data: str = None, 
                   url: str = None, request_contact: bool = False,
                   request_location: bool = False) -> "KeyboardBuilder":
        """Add button to current row."""
        
        if callback_data or url:
            # Inline button
            if callback_data:
                button = InlineKeyboardButton(text=text, callback_data=callback_data)
            else:
                button = InlineKeyboardButton(text=text, url=url)
        else:
            # Reply button
            button = KeyboardButton(
                text=text,
                request_contact=request_contact,
                request_location=request_location
            )
        
        self.current_row.append(button)
        return self
    
    def new_row(self) -> "KeyboardBuilder":
        """Start new row."""
        if self.current_row:
            self.buttons.append(self.current_row)
            self.current_row = []
        return self
    
    def add_row(self, buttons: List[Dict[str, Any]]) -> "KeyboardBuilder":
        """Add entire row of buttons."""
        self.new_row()
        
        for button_config in buttons:
            self.add_button(**button_config)
        
        return self
    
    def build_inline(self) -> InlineKeyboardMarkup:
        """Build inline keyboard."""
        if self.current_row:
            self.buttons.append(self.current_row)
        
        return InlineKeyboardMarkup(self.buttons)
    
    def build_reply(self, resize_keyboard: bool = True,
                   one_time_keyboard: bool = True,
                   selective: bool = False) -> ReplyKeyboardMarkup:
        """Build reply keyboard."""
        if self.current_row:
            self.buttons.append(self.current_row)
        
        return ReplyKeyboardMarkup(
            keyboard=self.buttons,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective
        )


def create_paginated_keyboard(items: List[Dict[str, Any]], 
                            page: int = 1, 
                            items_per_page: int = 8,
                            callback_prefix: str = "page") -> InlineKeyboardMarkup:
    """Create paginated keyboard."""
    
    total_items = len(items)
    total_pages = math.ceil(total_items / items_per_page)
    
    # Calculate start and end indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Create buttons for current page
    builder = KeyboardBuilder()
    
    for item in items[start_idx:end_idx]:
        builder.add_button(
            text=item["text"],
            callback_data=item["callback_data"]
        ).new_row()
    
    # Add navigation buttons
    nav_buttons = []
    
    if page > 1:
        nav_buttons.append({
            "text": "⬅️ Anterior",
            "callback_data": f"{callback_prefix}_{page - 1}"
        })
    
    if page < total_pages:
        nav_buttons.append({
            "text": "➡️ Siguiente",
            "callback_data": f"{callback_prefix}_{page + 1}"
        })
    
    if nav_buttons:
        builder.add_row(nav_buttons)
    
    # Add page info
    if total_pages > 1:
        builder.add_button(
            text=f"📄 {page}/{total_pages}",
            callback_data="page_info"
        ).new_row()
    
    return builder.build_inline()


def create_numbered_keyboard(items: List[str], 
                           callback_prefix: str = "item",
                           columns: int = 2) -> InlineKeyboardMarkup:
    """Create numbered keyboard."""
    
    builder = KeyboardBuilder()
    
    for i, item in enumerate(items, 1):
        builder.add_button(
            text=f"{i}. {item}",
            callback_data=f"{callback_prefix}_{i}"
        )
        
        if i % columns == 0:
            builder.new_row()
    
    return builder.build_inline()


def create_column_keyboard(items: List[Dict[str, Any]], 
                          columns: int = 2) -> InlineKeyboardMarkup:
    """Create keyboard with specified number of columns."""
    
    builder = KeyboardBuilder()
    
    for i, item in enumerate(items):
        builder.add_button(
            text=item["text"],
            callback_data=item["callback_data"]
        )
        
        if (i + 1) % columns == 0:
            builder.new_row()
    
    return builder.build_inline()


def add_navigation_buttons(keyboard: InlineKeyboardMarkup,
                          back_data: str = "back",
                          skip_data: str = "skip",
                          cancel_data: str = "cancel",
                          show_skip: bool = False) -> InlineKeyboardMarkup:
    """Add navigation buttons to existing keyboard."""
    
    # Convert existing keyboard to list of rows
    rows = [list(row) for row in keyboard.inline_keyboard]
    
    # Create navigation row
    nav_row = []
    
    if back_data:
        nav_row.append(
            InlineKeyboardButton(
                text=KEYBOARD_TEXTS["common"]["back"],
                callback_data=back_data
            )
        )
    
    if show_skip and skip_data:
        nav_row.append(
            InlineKeyboardButton(
                text=KEYBOARD_TEXTS["common"]["skip"],
                callback_data=skip_data
            )
        )
    
    if nav_row:
        rows.append(nav_row)
    
    # Add cancel button
    if cancel_data:
        rows.append([
            InlineKeyboardButton(
                text=KEYBOARD_TEXTS["common"]["cancel"],
                callback_data=cancel_data
            )
        ])
    
    return InlineKeyboardMarkup(rows)


def add_cancel_button(keyboard: InlineKeyboardMarkup,
                     cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """Add cancel button to existing keyboard."""
    
    # Convert existing keyboard to list of rows
    rows = [list(row) for row in keyboard.inline_keyboard]
    
    # Add cancel button
    rows.append([
        InlineKeyboardButton(
            text=KEYBOARD_TEXTS["common"]["cancel"],
            callback_data=cancel_data
        )
    ])
    
    return InlineKeyboardMarkup(rows)


def create_confirmation_keyboard(confirm_text: str = None,
                               cancel_text: str = None,
                               confirm_data: str = "confirm",
                               cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """Create confirmation keyboard."""
    
    confirm_text = confirm_text or KEYBOARD_TEXTS["common"]["yes"]
    cancel_text = cancel_text or KEYBOARD_TEXTS["common"]["no"]
    
    return KeyboardBuilder().add_button(
        text=confirm_text,
        callback_data=confirm_data
    ).add_button(
        text=cancel_text,
        callback_data=cancel_data
    ).build_inline()


def create_multi_select_keyboard(items: List[Dict[str, Any]],
                               selected_items: List[str] = None,
                               callback_prefix: str = "select",
                               done_callback: str = "done") -> InlineKeyboardMarkup:
    """Create multi-select keyboard."""
    
    selected_items = selected_items or []
    builder = KeyboardBuilder()
    
    for item in items:
        item_id = item["id"]
        is_selected = item_id in selected_items
        
        text = item["text"]
        if is_selected:
            text = f"✅ {text}"
        
        builder.add_button(
            text=text,
            callback_data=f"{callback_prefix}_{item_id}"
        ).new_row()
    
    # Add done button
    builder.add_button(
        text=KEYBOARD_TEXTS["common"]["confirm"],
        callback_data=done_callback
    ).new_row()
    
    return builder.build_inline()


def create_dynamic_keyboard(items: List[Dict[str, Any]],
                          layout: str = "auto",
                          max_columns: int = 3) -> InlineKeyboardMarkup:
    """Create dynamic keyboard based on content."""
    
    builder = KeyboardBuilder()
    
    if layout == "auto":
        # Auto-determine layout based on text length
        columns = 1
        avg_text_length = sum(len(item["text"]) for item in items) / len(items)
        
        if avg_text_length < 10:
            columns = min(max_columns, 3)
        elif avg_text_length < 20:
            columns = min(max_columns, 2)
        else:
            columns = 1
    
    elif layout == "single":
        columns = 1
    elif layout == "double":
        columns = 2
    elif layout == "triple":
        columns = 3
    else:
        columns = 1
    
    for i, item in enumerate(items):
        builder.add_button(
            text=item["text"],
            callback_data=item["callback_data"]
        )
        
        if (i + 1) % columns == 0:
            builder.new_row()
    
    return builder.build_inline()


def create_menu_keyboard(menu_items: List[Dict[str, Any]],
                        title: str = None,
                        footer: str = None) -> InlineKeyboardMarkup:
    """Create menu keyboard."""
    
    builder = KeyboardBuilder()
    
    if title:
        builder.add_button(
            text=title,
            callback_data="menu_title"
        ).new_row()
    
    for item in menu_items:
        emoji = item.get("emoji", "")
        text = f"{emoji} {item['text']}" if emoji else item["text"]
        
        builder.add_button(
            text=text,
            callback_data=item["callback_data"]
        ).new_row()
    
    if footer:
        builder.add_button(
            text=footer,
            callback_data="menu_footer"
        ).new_row()
    
    return builder.build_inline()


def create_grid_keyboard(items: List[Dict[str, Any]],
                        rows: int = 3,
                        columns: int = 3) -> InlineKeyboardMarkup:
    """Create grid keyboard."""
    
    builder = KeyboardBuilder()
    
    for i, item in enumerate(items[:rows * columns]):
        builder.add_button(
            text=item["text"],
            callback_data=item["callback_data"]
        )
        
        if (i + 1) % columns == 0:
            builder.new_row()
    
    return builder.build_inline()


def merge_keyboards(*keyboards: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    """Merge multiple keyboards into one."""
    
    all_rows = []
    
    for keyboard in keyboards:
        all_rows.extend(keyboard.inline_keyboard)
    
    return InlineKeyboardMarkup(all_rows)


def get_keyboard_stats(keyboard: InlineKeyboardMarkup) -> Dict[str, int]:
    """Get keyboard statistics."""
    
    total_buttons = 0
    total_rows = len(keyboard.inline_keyboard)
    
    for row in keyboard.inline_keyboard:
        total_buttons += len(row)
    
    return {
        "total_buttons": total_buttons,
        "total_rows": total_rows,
        "average_buttons_per_row": total_buttons / total_rows if total_rows > 0 else 0
    }


def validate_keyboard(keyboard: InlineKeyboardMarkup) -> Tuple[bool, List[str]]:
    """Validate keyboard structure."""
    
    errors = []
    
    if not keyboard.inline_keyboard:
        errors.append("Keyboard has no buttons")
        return False, errors
    
    # Check for empty rows
    for i, row in enumerate(keyboard.inline_keyboard):
        if not row:
            errors.append(f"Row {i} is empty")
    
    # Check for duplicate callback data
    callback_data_set = set()
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data:
                if button.callback_data in callback_data_set:
                    errors.append(f"Duplicate callback_data: {button.callback_data}")
                callback_data_set.add(button.callback_data)
    
    # Check button text length
    for row in keyboard.inline_keyboard:
        for button in row:
            if len(button.text) > 64:
                errors.append(f"Button text too long: {button.text[:20]}...")
    
    return len(errors) == 0, errors


def optimize_keyboard(keyboard: InlineKeyboardMarkup,
                     max_buttons_per_row: int = 3) -> InlineKeyboardMarkup:
    """Optimize keyboard layout."""
    
    all_buttons = []
    
    # Collect all buttons
    for row in keyboard.inline_keyboard:
        all_buttons.extend(row)
    
    # Redistribute buttons
    builder = KeyboardBuilder()
    
    for i, button in enumerate(all_buttons):
        builder.current_row.append(button)
        
        if (i + 1) % max_buttons_per_row == 0:
            builder.new_row()
    
    return builder.build_inline()