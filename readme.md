# Kolejny web serwis
Tym razem celem jest śledzenie tego jak zmieniają się strony Uniwersytetu Warszawskiego

# Jak to ma wyglądać?
- Otwarte api do zarządzania tym jaki serwis ma być śledzony (i dla kogo - w przyszłości)
- Jeden serwis zajmuje się kontrolowaniem zawartości bazy danych z użytkownikami, zadaniami i screenshotami
- Drugi żyje sobie w tle, wykonuje zadania, o których dowiaduje się z bazy danych i dodaje do niej efekty swojej pracy
- Jakiś minimalny front w czymkolwiek... Pewnie w html'u by wykorzystać template'y Django
- Prawodopodobnie apka będzize działać na Dockerze i spróbuję uniknąć Nginxa

# TODO
1. Postawić minimalne api do zarządzania treścią bazy danych
1. Zrobić daemona do robienia screenshotów używającego tego co już kiedyś napisałem
    - PhantomJS w repo lub instalacja gdzieś
1. Front

# Start-up
```
virtualenv env
source env/bin/activate

pip install django
pip install djangorestframework
pip install pygments  # We'll be using this for the code highlighting

```