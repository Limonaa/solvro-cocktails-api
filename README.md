# Solvro Cocktails API

Backendowe API do zarządzania koktajlami i składnikami, stworzone na potrzeby zadania rekrutacyjnego dla koła naukowego Solvro.

Projekt realizuje pełny zestaw operacji CRUD dla przepisów i składników, uwzględniając relacje bazodanowe, walidację danych, bezpieczne usuwanie oraz autoryzację JWT.

---

## Technologie

* **Python / Django** (wersja 6.1)
* **Django REST Framework (DRF)**
* **Simple JWT** (autoryzacja użytkowników)
* **Django Filter & DRF Spectacular** (filtrowanie oraz dokumentacja OpenAPI 3 / Swagger)
* **SQLite** (lokalna baza danych)

---

## Uruchomienie projektu lokalnie

Postępuj zgodnie z poniższymi krokami, aby uruchomić projekt na swoim komputerze:

### 1. Sklonuj repozytorium i przejdź do katalogu projektu

```bash
git clone <https://github.com/Limonaa/solvro-cocktails-api>
cd solvro_rekru
```

### 2. Utwórz i aktywuj wirtualne środowisko
- Windows
```bash
python -m venv .venv
.venv\Scripts\Activate
```
- Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Zainstaluj wymagane zależności
```bash
pip install djangorestframework django-filter djangorestframework-simplejwt drf-spectacular
```

### 4. Wykonaj migracje bazy danych
```bash
python manage.py migrate
```

### 5. Stwórz konto administratora (opcjonalne)
```bash
python manage.py createsuperuser
```

### 6. Uruchom serwer
```bash
python manage.py runserver
```

Aplikacja jest dostępna na: `http://127.0.0.1:8000`

## Dokumentacja API
Projekt posiada w pełni wygenerowaną dokumentację:
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`

## Uwierzytelnianie i Uprawnienia (JWT)
Projekt wykorzystuje autoryzację opartą na tokenach JWT z następującymi regułami dostępu:
- **Przeglądanie (GET):** Dostępne dla wszystkich użytkowników (bez logowania).
- **Tworzenie (POST):** Wymaga uwierzytelnienia (autor przepisu przypisywany jest automatycznie).
- **Edycja i usuwanie (PUT / PATCH / DELETE):** Dozwolone wyłącznie dla **autora koktajlu** lub **administratora**.

Endpoints autoryzacji:
1. Rejestracja użytkownika: wyślij żądanie POST na `http://127.0.0.1:8000/api/register/` z polami: `username`, `password`, (opcjonalnie `email`).
2. Logowanie: wyślij żądanie POST na adres `http://127.0.0.1:8000/api/login/` z polami `username` i `password`.
3. Odświeżenie tokenu: wyślij żądanie POST na adres `http://127.0.0.1:8000/api/token/refresh` z polem `refresh`.

W nagłówku zapytań wymagających uwierzytelnienia przekaż uzyskany token `access`: `Authorization: Bearer <access_token>`.

## Uruchamianie testów
Projekt posiada zestaw testów jednostkowych i integracyjnych pokrywających logikę biznesową (walidację unikalności, ochronę przed usunięciem w użyciu oraz filtrowanie).

```bash
python manage.py test
```

## Schemat bazy danych

```mermaid
erDiagram
    User ||--o{ Cocktail : "author (creates)"
    Cocktail ||--|{ CocktailIngredient : "recipe_items"
    Ingredient ||--|{ CocktailIngredient : "recipe_items"

    User {
        int id PK
        string username
        string email
        string password
    }

    Cocktail {
        int id PK
        string name
        string category
        string instructions
        datetime created_at
    }

    Ingredient {
        int id PK
        string name
        string description
        boolean is_alcoholic
        string image_url
    }

    CocktailIngredient {
        int id PK
        decimal amount
        string unit
    }
