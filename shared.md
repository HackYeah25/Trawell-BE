this is shared place of booth fe and be of trawell 


# Travel AI Assistant - Holistyczny Opis Funkcjonalności

## 🎯 CZYM JEST TA APLIKACJA

AI-powered asystent planowania podróży, który poznaje użytkownika, sugeruje destynacje, planuje wyjazdy i pomaga grupom znaleźć wspólne miejsce.

---

## 📋 GŁÓWNE FUNKCJONALNOŚCI

### **1. TWORZENIE PROFILU PODRÓŻNIKA** ⭐ (Krok pierwszy)

**Co robi:**
- Konwersacja z AI która buduje profil użytkownika
- System ma zestaw pytań (w YAML) i dba o wyczerpujące odpowiedzi
- Profil zapisywany w Supabase jako JSON
- Profil = **Prompt #1** we wszystkich późniejszych rozmowach

---

### **2. SOLO BRAINSTORM - Odkrywanie Destynacji**

**Co robi:**
- Użytkownik rozmawia z AI o tym gdzie chce jechać
- AI sugeruje destynacje na podstawie profilu + sezonowość + ceny lotów + pogoda
- Pokazuje 3-5 propozycji z uzasadnieniem "dlaczego to dla Ciebie"
- Użytkownik może iterować ("a coś taniej?", "a w lipcu?")

**Co widzi użytkownik:**
- Karty destynacji (zdjęcie, opis, sezon, budżet)
- Mapa z pinezkami
- Highlighty (tanie loty, idealna pogoda)
- Możliwość zapisania/bookmarkowania

**Integracje backendu:**
- Flight API (Skyscanner/Google Flights)
- Weather API
- Seasonality detection

---

### **3. GROUP BRAINSTORM** 🌟 **WYRÓŻNIK**

**Co robi:**
- Osoba tworzy "room" → dostaje kod (np. "ABC123")
- Inni joinują przez kod
- Każdy ma swój profil z kroku 1
- AI analizuje wszystkie profile → wykrywa konflikty/wspólne punkty
- System informuje: "Macie różne preferencje w X, znajdę kompromis"

**Jak działa rozmowa:**
- Wszyscy piszą czego chcą, co im pasuje
- AI moderuje jako "5. osoba w grupie"
- AI odzywa się tylko gdy:
  - Wszyscy się wypowiedzieli
  - Ktoś go bezpośrednio zapyta
  - Wykryje impas
  - Ktoś kliknie przycisk "AI, co myślisz?"

**Co AI robi:**
- Syntetyzuje wszystkie wypowiedzi
- Proponuje destynacje które zadowolą grupę
- Wskazuje jak zaspokoić różne potrzeby (np. "poranek aktywny dla Ani, popołudnie relaks dla Tomka")
- Przy dużych konfliktach: sugeruje split itinerary

**Co widzi użytkownik:**
- **Lewa strona:** Chat grupowy (wszyscy + AI)
- **Prawa strona:** Propozycje destynacji (karty + mapa)
- Lista uczestników
- Wskaźniki zgodności profili
- Real-time synchronizacja wiadomości

**Tech:**
- WebSocket dla każdego uczestnika
- Supabase Realtime dla sync wiadomości
- AI Moderator Agent (LangChain)
- Streaming responses

---

### **4. PLANOWANIE WYJAZDU**

**Co robi:**
- Szczegółowy plan dla wybranej destynacji
- Wyszukiwanie lotów z cenami
- Prognoza pogody na daty wyjazdu
- Lista miejsc wartych zobaczenia (bez przesadnych detali)
- Praktyczne info: godziny otwarcia, ceny biletów, darmowe dni w muzeach
- Kulturowe guidelines (dress code, szczepienia, customs)
- Lokalne eventy (koncerty, mecze, strajki, maraton)
- Zagrożenia klimatyczne

**Co widzi użytkownik:**
- Timeline/itinerary wycieczki
- Mapy z POI
- Karty z atrakcjami
- Flight comparison
- Weather forecast w