# Analiza-Sentymentow-praca-koncowa
Analiza danych i sentymentów z mediów społecznościowych na przykładzie Twittera z wykorzystaniem narzędzi Big Data dostępnych na platformie Azure



Kiedy tweety znajdują się w bazie, można przejść do kolejnego kroku jakim jest ich analiza i prezentacja. Do tego celu zostało użyte narzędzie Jupyter Notebook z PySpark3 kernel, gdzie są do dyspozycji  Python3 oraz Spark. Klaster HDInsight Spark udostępniaja kernels, które można używać z  Jupyter Notebook na platformie Apache Spark do testowania aplikacji. Kernel to program, który uruchamia i interpretuje kod. W HDInsight Spark ammy do dyspozycji trzy kernels: 
– PySpark - dla aplikacji napisanych w Pythonie2.
– PySpark3 - dla aplikacji napisanych w Pythonie3.
– Spark - dla aplikacji napisanych w Scali.
	Cały proces analizy jest zaprezentowany w Jupyter Notebook znajdującym się na GitHub:  Analiza_sentymentow_dla_tweets_projekt_koncowy_COVID-19.ipynb , Analiza_sentymentow_dla_tweets_projekt_koncowy-USA_elections_2020.ipynb oraz Sentiment_tweets_analysis.ipynb .
	W tej części zostanie omówiony proces jaki został przedstawiony w Analiza_sentymentow_dla_tweets_projekt_koncowy_COVID-19.ipyn i w  Analiza_sentymentow_dla_tweets_projekt_koncowy-USA_elections_2020.ipynb .

1) Przygotowanie danych
	Po zadeklarowaniu bibliotek i uruchomieniu sesji Sparka, zostaje sprawdzona zawartość tabel w bazie Hive oraz ich opis.  
	Kolejno wykorzystując magic cells (%%sql) odwołuję się do tabel Hive i sprawdzam jakie można zauważyć tendencje emocjonalne w tweetach o danej tematyce.
	
Dla pozostałych przetwarzań zostaje utworzony Pandas DataFrame za pomocą megic cells : %%sql -q -o df -n -1, gdzie q – brak wizualizacji, o – wynik zapytania zapisany do Pandas DataFrame, n – liczba rekordów zapisana do Pandas DataFrame (-1 – wszystkie wiersze).
	
2) Czyszczenie danych
	Aby była możliwość analizy tekstu postów, należy tweety na początku „oczyścić”.  W sekcji „Czyszczenie danych” stosując biblioteki Python  takie jak bs4 czy nltk.tokenize są dokonywane usunięcia zbednych znaków HTML oraz XML i podział ciągu tekstu na podciągi. 















	Takiemu czyszczeniu poddawane są wszystkie tweety w pobranym zbiorze a następnie zapisane w pliku csv wraz z identyfikatorem posta i znacznikiem sentymentu, gdzie 0 oznacza nastrój negatywny a 1 to nastrój pozytywny.





       3)  Metoda słownikowa analizy sentymentów
       	Kolejna część prezentuje proste podejście do analizy sentymentów przy użyciu PySpark i DataFrame Spark. W tym celu należy zaimportować niezbędne biblioteki oraz uruchomić Spark SQL. Spark SQL to komponent znajdujący się w Spark Core, który ułatwia przetwarzanie danych ustrukturyzowanych i częściowo ustrukturyzowanych oraz integrację kilku formatów danych jako źródła (Hive, Parquet, JSON). Pozwala na transformację RDD za pomocą SQL (Structured Query Language). Aby uruchomić Spark SQL w swoim notesie należy utworzyć kontekst SQL.
       
       Zostaje utworzony DataFrame Spark z wcześniej zapisanych danych w formacie csv.
       inferSchema  zostaje ustawiony na na True , aby automatycznie wnioskować typy kolumn na podstawie danych. 
       Z nowego DataFrame zostają usunięte puste wiersze i następuje przegląd negatywnyc , pozytywnych  postów i obliczenie średniej długości obu rodzaju tweetów. 
       Do dalszej analizy jest dodany słownik z predefiniowanymi emocjami.
       Słownik został utworzony na podstawie listy pozytywnych i negatywnych słów, które zostały znalezione na udostępnionym publicznym GitHub (https://github.com/sridharswamy/Twitter-Sentiment-Analysis-Using-Spark-Streaming-And-Kafka/tree/master/Dataset).
       Słowa z tweetów są porównywane ze słowami z DataFrame a ich sentyment są porównywane. Zatem wyznaczone przez TextBlob sentymenty są porównywane ze słownikiem sentymentów i jest wyznaczana dokładność pomiaru sentymentów. 
       Do tego celu najlepiej posiadać taką samą liczbę badanej wartości w tym przypadku dokładności wyznaczania sentymentów. Zatem na początku ujednolicam liczbę postów pozytywnych i negatywnych do liczby tweetów ze mniejszego zbioru. Tak przygotowane dane poddaje ponownie procesowi tokenizacji (tym razem dla obiektu DataFrame Spark) .  Następnie zbiór słów zostaje porównany ze słownikiem , rozbijając podzielone słowa na różne wiersze za pomocą funkcji fn.explode i łącząc DataFrame’y. Poprzez średnią ocenę słów dla każdego tweeta i post zostaje sklasyfikowany jako „Pozytywny”, gdy średnia jest większa niż 0 i "Negatywny", jeśli jest mniejsza niż 0, a następnie obliczony zostaje wynik dokładności tej metody.
           
           Tą metodę można nazwać metodą słownikową, która następnie porównamy z modelem regresji logistycznej.
           
           4.6. Prezentacja  wyników w postaci graficznej 
           
	Gdy tweety są już oczyszczone można przejść do kolejnego etapu analizy postów jakim jest wizualizacja i wyciąganie pierwszych wniosków. 
W tej cześći przedstawione są dwa wnioski :
1. Do pierwszego zoobrazowania została użyta bibliotekia Wordcloud, aby zobaczyć częstotliwość słów zgodnie z kolumną tweet. Wykorzystana została bilinearna metoda interpolacji, aby zwiększyć płynność tekstu w chmurze.

2. Kolejna wizualizacja prezentuje wykres słupkowy, który przedstawia całkowitą liczbę pozytywnych i negatywnych słów dla ogólnego porównania nastrojów. W celu przedstawienia sentymentów została użyta metoda groupby na kolumnie sentymenty (indeksowanie po tej kolumnie zostało pominięte)




           4.7. Implementacja uczenia maszynowego dla klasyfikacji textu przy użyciu Pyspark ML

	W tej czeście będzie wykorzystywane metody z następujących bibliotek:
– pyspark.ml
– pyspark.ml.linalg
--pyspark.ml.classification
– pyspark.ml.feature
Kolejne procesy będą służyć przygotowaniu danych do obliczenia wyiku dokładności przy uzyciu modelu regresji logistycznej.
Aby taki model powstał należy wykonać następujące kroki:
1) Usunięcie zbędnych słów (stop words) z tweetów 
W tym celu została wykorzystana lista „stop words” dostępna publicznie na stronie lextek (http://www.lextek.com/manuals/onix/stopwords1.html)










Słowa znajdujące się na tej liście zostały usunięte z postów przy użyciu metody StopWordsRemover.






2) Liczenie wektoryzatora - CountVectorizer
CountVectorizer i CountVectorizerModel mają na celu pomóc w konwersji kolekcji dokumentów tekstowych na wektory liczby tokenów. Gdy słownik nie jest dostępny, CountVectorizer może służyć jako estymator do wyodrębniania słownictwa i generuje CountVectorizerModel. Model tworzy rzadkie reprezentacje dokumentów w słowniku, które mogą być następnie przekazywane do innych algorytmów. 
Dla tweetów CountVectorizer utworzy słownik o rozmiarze 131, który zawiera terminy pandemic, wait, data czy offering. Następnie nastąpi dopasowanie modelu CountVectorizer. Podczas procesu dopasowania CountVectorizer wybierze najlepsze słowa VocabSize uporządkowane według częstotliwości terminów. Model wytworzy rzadki wektor, który można wprowadzić do innych algorytmów.

3) Pipeline Estymator
W uczeniu maszynowym często uruchamia się sekwencję algorytmów do przetwarzania danych i uczenia się na ich podstawie. Np. Prosty proces przetwarzania dokumentów tekstowych może obejmować kilka etapów:
– Podziel tekst każdego dokumentu na słowa (stage = token)
– Usuń zbędne słow tzw. stop words (stage = filter)
– Konwertuj słowa każdego dokumentu na numeryczny wektor cech (stage = vector_count)
MLlib reprezentuje taki przepływ pracy jak potok, który składa się z sekwencji PipelineStages (transformatorów i estymatorów) uruchamianych w określonej kolejności. 





4) IDF (Odwrotna częstotliwość dokumentu- Inverse Document Frequency)
Termin „częstotliwość odwrotna częstotliwości dokumentu” (IDF) jest metodą wektoryzacji cech szeroko stosowaną w eksploracji tekstów, aby odzwierciedlić znaczenie terminu w dokumencie. Oznaczając termin przez t, dokument przez d, a korpus przez D, to częstotliwość dokumentu DF (t, D) jest liczbą dokumentów zawierających termin t. Jeśli do pomiaru ważności uzywa się tylko częstotliwości terminów, bardzo łatwo jest przecenić terminy, które pojawiają się bardzo często, ale zawierają niewiele informacji o dokumencie, np. „A”, „the” i „of”. Jeśli termin pojawia się bardzo często w całym korpusie, oznacza to, że nie zawiera specjalnych informacji o konkretnym dokumencie. Odwrotna częstotliwość dokumentów jest liczbową miarą ilości informacji dostarczanych przez termin:



gdzie | D | to całkowita liczba dokumentów w korpusie. Ponieważ używany jest logarytm, jeśli termin pojawia się we wszystkich dokumentach, jego wartość IDF przyjmuje wartość 0. Należy zauważyć, że stosowany jest termin wygładzający, aby uniknąć dzielenia przez zero dla terminów spoza korpusu. Wartość TF-IDF jest po prostu produktem TF i IDF:



Istnieje kilka wariantów definicji częstotliwości terminów i częstotliwości dokumentów. W spark.mllib oddzielamy TF i IDF, aby były elastyczne.
Zatem obliczony IDF zostaje dodany do Pipeline tworząc szereg transformacji dla tweetów.
Do modelu machine learning niezbędne jest wydzielenie z całości zbioru danych treningowych, danych walidacyjnych i danych testowych. Wybrałam podział w stosunku 80:10:10 


Model regresji logistycznej

Dla kolejnego wyliczenia wyniku dokładności został użyty prosty model regresji jakim jest model regresji logistycznej. Regresja logistyczna to algorytm klasyfikacji uczenia maszynowego, który jest używany do przewidywania prawdopodobieństwa jakościowej zmiennej zależnej. W regresji logistycznej zmienną zależną jest zmienna binarna, która zawiera dane zakodowane jako 1 (tak, sukces itp.) lub 0 (nie, niepowodzenie itp.). Innymi słowy, model regresji logistycznej przewiduje P (Y = 1) jako funkcję X.
Założenia regresji logistycznej:
– Binarna regresja logistyczna wymaga, aby zmienna zależna była binarna.
– W przypadku regresji binarnej poziom czynnika 1 zmiennej zależnej powinien reprezentować pożądany wynik.
– Należy uwzględnić tylko znaczące zmienne.
– Zmienne niezależne powinny być od siebie niezależne. Oznacza to, że model powinien mieć niewielką lub żadną współliniowość.
– Regresja logistyczna wymaga dość dużych próbek.
W celu wyznaczenia modelu regresji logistycznej została użyta biblioteka pyspark.ml.classification i metoda LogisticRegression. 

Jak widzimy do pipeline zIDF dodajemy model regresji logistycznej i uruchamiamy go na danych treningowych. Tak przetrenowany model zostaje zastosowany na danych walidacyjnych a następnie na danych testowych w celu wyznaczenia predykcji sentymentów.
Rezultatem końcowym jest wynik dokładności (accuracy) uczenia poprzez model regesji logistycznej. 


Wynik można porównać z wynikiem metody słownikowej, która była obliczona we wcześniejszeym etapie i zobaczyć, czy podejście uczenia maszynowego daje lepsze rezultaty niż proste porównanie słownikowe.
