import importlib.util
import pathlib

from collections import UserDict
from typing import Optional, List


class Field:
    """Базове поле запису."""
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class Name(Field):
    """Обов'язкове поле імені контакта."""
    def __init__(self, value: str):
        value = (value or "").strip()
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    """
    Поле телефону з валідацією:
    - рівно 10 цифр (лише цифри)
    Дозволено вводити з пробілами/дефісами/круглими дужками 
    — вони будуть очищені.
    """
    def __init__(self, value: str):
        raw = "".join(ch for ch in str(value) if ch.isdigit())
        if len(raw) != 10:
            raise ValueError("Phone must contain exactly 10 digits.")
        super().__init__(raw)


class Record:
    """
    Запис контакту: ім'я + список телефонів.
    """
    def __init__(self, name: str):
        self.name: Name = Name(name)
        self.phones: List[Phone] = []

    def add_phone(self, phone_value: str) -> None:
        """Додати новий телефон (з валідацією). Ігнорує дублікати."""
        phone = Phone(phone_value)
        if not any(p.value == phone.value for p in self.phones):
            self.phones.append(phone)

    def remove_phone(self, phone_value: str) -> None:
        """Видалити телефон за значенням. Підіймає KeyError, якщо не знайдено."""
        target = self.find_phone(phone_value)
        if target is None:
            raise KeyError(phone_value)
        self.phones.remove(target)

    def edit_phone(self, old_value: str, new_value: str) -> None:
        """Змінити існуючий номер на новий. Якщо старого нема — KeyError."""
        target = self.find_phone(old_value)
        if target is None:
            raise KeyError(old_value)
        new_phone = Phone(new_value)  # валідація
        target.value = new_phone.value

    def find_phone(self, phone_value: str) -> Optional[Phone]:
        """Знайти телефон за значенням (ігнорує нецифрові символи у пошуку)."""
        normalized = "".join(ch for ch in str(phone_value) if ch.isdigit())
        for p in self.phones:
            if p.value == normalized:
                return p
        return None

    def __str__(self) -> str:
        phones_str = "; ".join(p.value for p in self.phones) if self.phones else "(no phones)"
        return f"Contact name: {self.name.value}, phones: {phones_str}"

    def __repr__(self) -> str:
        return f"Record(name={self.name!r}, phones={self.phones!r})"


class AddressBook(UserDict):
    """
    Адресна книга на базі UserDict:
    - ключ: ім'я (str)
    - значення: Record
    """
    def add_record(self, record: Record) -> None:
        """Додати або замінити запис у книзі за ім'ям."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        """Знайти запис за ім'ям. Повертає Record або None."""
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Видалити запис за ім'ям. Підіймає KeyError, якщо не існує."""
        del self.data[name]


if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("123-456-7890")
    john_record.add_phone("(555) 555-5555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("555-555-5555")
    print(f"{john.name}: {found_phone}")  # John: 5555555555

    # Видалення запису Jane
    book.delete("Jane")