"""
Homework 3: The Bounded Backpack -- starter.

Complete BoundedBackpack below. See HW3_The_Bounded_Backpack.md,
Part B, for the full requirements.
"""

import threading
import time
from typing import Any, List, Optional


class BackpackTimeoutError(Exception):
    """Raised when push()/pop() waits longer than its timeout without success."""


class BoundedBackpack:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._items: List[Any] = []
        self._condition = threading.Condition()

    def __len__(self) -> int:
        with self._condition:
            return len(self._items)

    def push(self, item: Any, timeout: Optional[float] = None) -> None:
        """
        Block while the backpack is full, waiting until space is
        available (or `timeout` seconds elapse -> BackpackTimeoutError).
        Insert at the top (LIFO), then wake any thread waiting in pop().
        """
        start_time = time.monotonic()

        with self._condition:
            while len(self._items) >= self.capacity:
                if timeout is None:
                    self._condition.wait()
                else:
                    elapsed = time.monotonic() - start_time
                    remaining = timeout - elapsed

                    if remaining <= 0:
                        raise BackpackTimeoutError(
                            "push() timed out waiting for space"
                        )

                    self._condition.wait(timeout=remaining)

                    # Check whether the timeout expired while waiting.
                    if len(self._items) >= self.capacity:
                        elapsed = time.monotonic() - start_time
                        if elapsed >= timeout:
                            raise BackpackTimeoutError(
                                "push() timed out waiting for space"
                            )

            self._items.append(item)

            # Wake threads waiting for an item to become available.
            self._condition.notify_all()

    def pop(self, timeout: Optional[float] = None) -> Any:
        """
        Block while the backpack is empty, waiting until an item is
        available (or `timeout` seconds elapse -> BackpackTimeoutError).
        Remove and return the top item, then wake any thread waiting in push().
        """
        start_time = time.monotonic()

        with self._condition:
            while not self._items:
                if timeout is None:
                    self._condition.wait()
                else:
                    elapsed = time.monotonic() - start_time
                    remaining = timeout - elapsed

                    if remaining <= 0:
                        raise BackpackTimeoutError(
                            "pop() timed out waiting for an item"
                        )

                    self._condition.wait(timeout=remaining)

                    # Check whether the timeout expired while waiting.
                    if not self._items:
                        elapsed = time.monotonic() - start_time
                        if elapsed >= timeout:
                            raise BackpackTimeoutError(
                                "pop() timed out waiting for an item"
                            )

            item = self._items.pop()

            # Wake threads waiting for space to become available.
            self._condition.notify_all()

            return item
