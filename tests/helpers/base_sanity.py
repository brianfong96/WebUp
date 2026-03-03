from __future__ import annotations

from abc import ABC, abstractmethod


class BaseSanityCheck(ABC):
    name: str

    @abstractmethod
    def run(self) -> tuple[bool, str]:
        raise NotImplementedError
