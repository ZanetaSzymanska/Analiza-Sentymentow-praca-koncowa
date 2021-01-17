
## **Analiza danych i sentymentów z mediów społecznościowych na przykładzie Twittera z wykorzystaniem narzędzi Big Data dostępnych na platformie Azure**

**4.  Implementacja**

**4.1. Tworzenie klastra HDInsight Spark w Azure**

`	`Implementacja projektu rozpoczyna się od stworzenia klastra HDInsight Spark w Azure Cloud.  Aby utworzyć taki klaster niezbędne jest podanie następujących informacji:

\1) Resource group

\2) Cluster name and region

\3) Cluster type and version

\4) Cluster login username and password

![](Praca\_końcowa\_Żaneta\_Szymańska.008.png)5) Primary storage account and container

![](Praca\_końcowa\_Żaneta\_Szymańska.009.png)









\6) Node configurations

Free trial licencja pozwala nam na utworzenie następujących nodów (mamy do duspozycji jedynie 12 cores):

– Head node → 2 nody → 4 cores

– Zookeeper node → 3 nody → 6 cores

![](Praca\_końcowa\_Żaneta\_Szymańska.010.png)– Worker node → 1 node → 2 cores

`	`Następnie należy sprawdzić, czy podane dane zostały poprawnie zwalidowane i potwierdzić utworzenie klastra. W Azure Cloud tego typu klaster tworzy się w około 15 minut.

**4.2. Pobieranie danych z Twitter API**

`          `Mając utworzony klaster należy pomyśleć o tym skąd zostaną pobrane dane do analizy. W projekcie został wybrany do tego Twitter API. Aby móc z niego skorzystać należy stworzyć konto i zalogować się na stronę <https://developer.twitter.com/en/portal/projects-and-apps> , a następnie należy wykonać kolejne kroki:

\1) Wybrać aplikację, która została dodana na koncie użytkownika podczas rejestracji (dowolna nazwa aplikacji), a następnie kliknąć Szczegóły.

\2) Wybrać kartę Klucze i tokeny.

\3) W sekcji Consumer API Keys skopiować wartości klucza API do Consumer\_key i API Secret Key do Consumer\_secret.

Wszystkie niezbędne kroki można znaleźć w dokumentacji na stronie : [https://developer.twitter.com/en/docs/labs/tweets-and-users/quick-start/get-tweets#:~:text=Navigate%20to%20your%20app%20dashboard,API%20Secret%20Key%20into%20consumer_secret%20](https://developer.twitter.com/en/docs/labs/tweets-and-users/quick-start/get-tweets).

![](Praca\_końcowa\_Żaneta\_Szymańska.011.png)

`	`Nastepnie zostaje zbudowane środowisko potrzebne do uruchomienia skryptu pobierającego tweety. Nowe środowisko Python jest budowane w celu izolacji od środowiska klastrowego. W ten sposób można instalować biblioteki nie obawiając się o uszkodzenie klastra. Wszytskie komendy zostają wywołane z powłoki bash na headnode, do którego można się zalogować poprzez ssh, np.: *ssh sshuser@sentiment-analysis-hdinsight-cluster-spark-ssh.azurehdinsight.net*

W powyższym przykładzie  *sentiment-analysis-hdinsight-cluster-spark* jest nazwą klastra.

Wszystkie skrypty użyte w projekcie znajdują się w repozytorium GitHub : <https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa>

Skrypt ustawiający środowisko : [install_env.sh](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/install_env.sh)

*sudo apt install python-dev libffi-dev libssl-dev*

*sudo apt remove python-openssl*

*curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py*

*python3 get-pip.py --force-reinstall*

*python3 -m pip install virtualenv*

*mkdir gettweets*

*cd gettweets*

*virtualenv gettweets*

*source gettweets/bin/activate*

*pip install tweepy progressbar pyOpenSSL requests[security]*

*pip install TextBlob*











`	`W tak utworzonym środowisku zostają uruchomione skrypty do pobierania tweetów: [gettweets_USA_elections_2020_10K.py](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/gettweets_USA_elections_2020_10K.py) i [gettweets_pandemic_10K_per_file.py](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/gettweets_pandemic_10K_per_file.py) . Skrypty są napisany w  języku Python. Tweety pobierane są w postaci json i zapisywane w pliku w podziale na 10 tysięcy tweetów w jednym pliku. Do pobierania tweetów jest wykorzystana biblioteka tweepy i tweepy.streaming.

Główną częścią kodu odpowiedzialną za pobieranie tweetów jest metoda *on\_data*

*def on\_data(self, data):*

`        `*data.lower()*

`        `*tweet = json.loads(data)*

`        `*if 'text' in data and 'location' in data and tweet['user']['location']:*

`            `*blob = TextBlob(tweet["text"])*

`            `*tweet['polarity'] = round(blob.sentiment.polarity,5)*

`            `*tweet['subjectivity'] = blob.sentiment.subjectivity*

`            `*tweet['sentiment'] = str(blob.sentiment)*

`            `*#Append the tweet to the json file*

`            `*with open(self.filename, 'a') as tweet\_file:*

`                `*tweet\_file.write(json.dumps(tweet))*

`                `*tweet\_file.write("\n")*

`                `*#Increment the number of tweets*

`                `*self.num\_tweets += 1*

`                `*#Check to see if we have hit max\_tweets and exit if so*

`                `*if self.num\_tweets >= max\_tweets:*

`                    `*self.pbar.finish()*

`                    `*#sys.exit(0)*

`                    `*if self.num\_files >= max\_files:*

`                        `*sys.exit(0)*

`                    `*else:*

`                        `*self.num\_files += 1*

`                        `*self.filename = 'tweets\_pandemic\_10K\_'+str(self.num\_files)+'.json'*

`                        `*self.num\_tweets = 0*

`                        `*self.pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=max\_tweets).start()*

`                        `*print(self.filename)* 

`                `*else:*

`                    `*#increment the progress bar*

`                    `*self.pbar.update(self.num\_tweets)*

`        `*return True*




**4.3. Dodawanie sentymentów do pobranych danych**

`	`Podczas pobierania danych zostają dodane sentymenty w postaci trzech wartości:

\1) tweet['polarity'] = round(blob.sentiment.polarity,5)

\2) tweet['subjectivity'] = blob.sentiment.subjectivity

\3) tweet['sentiment'] = str(blob.sentiment)

Do obliczenia powyższych wartości jest wykorzystana biblioteka T*extBlob.* 

TextBlob jest doskonałą biblioteką typu open source do wykonywania zadań NLP. Jest to leksykon sentymentów (w formie pliku XML), z którego korzysta, aby uzyskać zarówno wyniki polaryzacji, jak i subiektywności. Wynik polaryzacji to liczba zmiennoprzecinkowa w zakresie (-1,1), a subiektywność jest zmienną w zakresie (0,1) gdzie 0 jest bardzo obiektywna i 1 jest bardzo subiektywna. Wyniki z TextBlob są znormalizowaną skalą w porównaniu z Afinn. TextBlob jest oparty na NLTK (Natural Language Toolkit) i zapewnia łatwy w użyciu interfejs do biblioteki NLTK.

**4.4. Tworzenie tabel w Hive na podstawie pobranych danych**

`	`Kolejnym krokiem do analizy tweetów wraz z dodanymi sentymentami jest import plików json do bazy danych, z której kolejno będzie korzystać Spark i na podstawie której, będzie można utworzyć DataFrame do dalszej analizy. Na potrzeby tego projektu dane  z json zostały zaimportowane do bazy Apache Hive w postaci tabel oraz informacje znajdujące się w tweetach zostały poddane wstępnej obróbce.

`	`Apache Hive to rozproszony, odporny na błędy system hurtowni danych, który umożliwia analitykę na masową skalę. Hurtownia danych stanowi centralny magazyn informacji, które można łatwo analizować w celu podejmowania świadomych decyzji opartych na danych. Hive umożliwia użytkownikom odczytywanie, zapisywanie i zarządzanie petabajtami danych przy użyciu języka SQL.Hive jest oparty na Apache Hadoop, który jest platformą open source używaną do wydajnego przechowywania i przetwarzania dużych zestawów danych. W rezultacie Hive jest ściśle zintegrowany z Hadoop i jest zaprojektowany do szybkiej pracy na petabajtach danych. To, co czyni Hive wyjątkowym, to możliwość wykonywania zapytań w dużych zestawach danych z wykorzystaniem Apache Tez lub MapReduce z interfejsem podobnym do SQL.

`	`Proces importowania danych z plików json do Apache Hive został zautomatyzowany poprzez uruchomienie odpowiednich skryptów przy użyciu klienta Beeline. 

Skrypty odpowiedzialne za utworzenie table w Apache Hive  to : [twitter_pandemic.hql](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/twitter_pandemic.hql) i [twitter_USA_elections_2020.hql](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/twitter_USA_elections_2020.hql),

a ich cały kod źródłowy jest dostępny na GitHub.

*beeline -u 'jdbc:hive2://localhost:10001/;transportMode=http' -i twitter\_pandemic.hql*


Skrypty uruchamiamy używając następujące polecenia:

Poniżej znajduje się przykładowa zawartość skryptów.

*-- Create it, pointing toward the tweets logged from Twitter*

*CREATE EXTERNAL TABLE tweets\_pandemic\_raw (*

`    `*json\_response STRING*

*)*

*STORED AS TEXTFILE LOCATION '/tutorials/twitter/tweets\_pandemic';*






*-- Select tweets from the imported data, parse the JSON,*

*-- and insert into the tweets table*

*FROM tweets\_pandemic\_raw*

*INSERT OVERWRITE TABLE tweets\_pandemic\_temp*

*SELECT*

`    `*cast(get\_json\_object(json\_response, '$.id\_str') as BIGINT),*

`    `*get\_json\_object(json\_response, '$.created\_at'),*

`    `*concat(substr (get\_json\_object(json\_response, '$.created\_at'),1,10),' ',*

`    `*substr (get\_json\_object(json\_response, '$.created\_at'),27,4)),*

`    `*substr (get\_json\_object(json\_response, '$.created\_at'),27,4),*

`  `*...*

`        `*trim(lower(get\_json\_object(json\_response, '$.entities.user\_mentions[4].screen\_name')))),*

`    `*trim(lower(get\_json\_object(json\_response, '$.entities.hashtags[0].text'))),*

`    `*trim(lower(get\_json\_object(json\_response, '$.entities.user\_mentions[0].screen\_name'))),*

`    `*get\_json\_object(json\_response, '$.user.screen\_name'),*

`    `*get\_json\_object(json\_response, '$.user.name'),*

`    `*cast (get\_json\_object(json\_response, '$.user.followers\_count') as INT),*

`    `*cast (get\_json\_object(json\_response, '$.user.listed\_count') as INT),*

`    `*cast (get\_json\_object(json\_response, '$.user.friends\_count') as INT),*

`    `*get\_json\_object(json\_response, '$.user.lang'),*

`    `*get\_json\_object(json\_response, '$.user.location'),*

`    `*get\_json\_object(json\_response, '$.user.time\_zone'),*

`    `*get\_json\_object(json\_response, '$.user.profile\_image\_url'),*

`    `*json\_response*

*WHERE (length(json\_response) > 500) ;*

*WHERE (length(json\_response) > 500) ;*

Poniższy screenshot pokazuje jak wygląda ładowanie danych do  tabel w Hive i szybkość tego procesu.

\1. Dla danych odnośnie pandemii.

\2. Dla danych odnośnie wyborów w USA.

![](Praca\_końcowa\_Żaneta\_Szymańska.017.png)

![](Praca\_końcowa\_Żaneta\_Szymańska.018.png)

**4.5. Analiza danych i sentymentów przy użyciu Jupyter Notebooks i PySpark**

`	`Kiedy tweety znajdują się w bazie, można przejść do kolejnego kroku jakim jest ich analiza i prezentacja. Do tego celu zostało użyte narzędzie Jupyter Notebook z PySpark3 kernel, gdzie są do dyspozycji  Python3 oraz Spark. Klaster HDInsight Spark udostępniaja kernels, które można używać z  Jupyter Notebook na platformie Apache Spark do testowania aplikacji. Kernel to program, który uruchamia i interpretuje kod. W HDInsight Spark ammy do dyspozycji trzy kernels: 

– PySpark - dla aplikacji napisanych w Pythonie2.

– PySpark3 - dla aplikacji napisanych w Pythonie3.

– Spark - dla aplikacji napisanych w Scali.

`	`Cały proces analizy jest zaprezentowany w Jupyter Notebook znajdującym się na GitHub:  [**Analiza_sentymentow_dla_tweets_projekt_koncowy_COVID-19.ipynb](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/Analiza_sentymentow_dla_tweets_projekt_koncowy_COVID-19.ipynb) **, Analiza\_sentymentow\_dla\_tweets\_projekt\_koncowy-USA\_elections\_2020.ipynb** oraz **[Sentiment_tweets_analysis.ipynb](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/Sentiment_tweets_analysis.ipynb)** .

`	`W tej części zostanie omówiony proces jaki został przedstawiony w [**Analiza_sentymentow_dla_tweets_projekt_koncowy_CO](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/Analiza_sentymentow_dla_tweets_projekt_koncowy_COVID-19.ipynb)[VID-19.ipyn](https://github.com/ZanetaSzymanska/Analiza-Sentymentow-praca-koncowa/blob/main/Analiza_sentymentow_dla_tweets_projekt_koncowy_COVID-19.ipynb) **i w  Analiza\_sentymentow\_dla\_tweets\_projekt\_koncowy-USA\_elections\_2020.ipynb .**

**1) Przygotowanie danych**

`	`Po zadeklarowaniu bibliotek i uruchomieniu sesji Sparka, zostaje sprawdzona zawartość tabel w bazie Hive oraz ich opis.  

`	`Kolejno wykorzystując magic cells (%%sql) odwołuję się do tabel Hive i sprawdzam jakie można zauważyć tendencje emocjonalne w tweetach o danej ![](Praca\_końcowa\_Żaneta\_Szymańska.019.png)tematyce.



Dla pozostałych przetwarzań zostaje utworzony Pandas DataFrame za pomocą megic cells : %%sql -q -o df -n -1, gdzie q – brak wizualizacji, o – wynik zapytania zapisany do Pandas DataFrame, n – liczba rekordów zapisana do Pandas DataFrame (-1 – wszystkie wiersze).



**2) Czyszczenie danych**

`	`Aby była możliwość analizy tekstu postów, należy tweety na początku „oczyścić”.  W sekcji „Czyszczenie danych” stosując biblioteki Python  takie jak bs4 czy nltk.tokenize są dokonywane usunięcia zbednych znaków HTML oraz XML i podział ciągu tekstu na podciągi. 

*from nltk.tokenize import WordPunctTokenizer*

*token = WordPunctTokenizer()*

*reg1 = r'@[A-Za-z0-9]+' # usuwanie liczb i znaków specjalnych*

*reg2 = r'<[^<]+?>'  # usuwanie znaków specjalnych*

*comb = r'|'.join((reg1, reg2)) # łączę obie zmienne regresji i uzyję ich poniżej w funkcji*

*def clean(tweet):*

`    `*s = BeautifulSoup(tweet, 'lxml')*

`    `*s\_soup = s.get\_text()  #wydobycie tekstu z tweeta , czyli usunięcie znaczników HTML i XML*

`    `*strip = re.sub(comb, '', s\_soup)  #usuwanie znaków specjalnych*

`    `*letter = re.sub("[^a-zA-Z]", " ", strip)  #wybór słów zaczynających się na literę*

`    `*lower = letter.lower() # zmiana wielkości liter na małe*

`    `*replaceprefix = re.sub("^u'", "'", lower) # usunięcie prefixu ‘u’*

`    `*word = token.tokenize(replaceprefix) #dzielenie tekstu → tokenizacja*

`    `*return (" ".join(word)).strip() #łączenie tokenów w tweet*


![](Praca\_końcowa\_Żaneta\_Szymańska.021.png)













`	`Takiemu czyszczeniu poddawane są wszystkie tweety w pobranym zbiorze a następnie zapisane w pliku csv wraz z identyfikatorem posta i znacznikiem sentymentu, gdzie 0 oznacza nastrój negatywny a 1 to nastrój pozytywny.

*%%local*

*%%time*

*%cd /home/sshuser/gettweets*

*%pwd*

*df\_new.to\_csv('tweets\_pandemic\_clean.csv',encoding='utf-8')*






**3)  Metoda słownikowa analizy sentymentów**

`	`Kolejna część prezentuje proste podejście do analizy sentymentów przy użyciu PySpark i DataFrame Spark. W tym celu należy zaimportować niezbędne biblioteki oraz uruchomić Spark SQL. Spark SQL to komponent znajdujący się w Spark Core, który ułatwia przetwarzanie danych ustrukturyzowanych i częściowo ustrukturyzowanych oraz integrację kilku formatów danych jako źródła (Hive, Parquet, JSON). Pozwala na transformację RDD za pomocą SQL (Structured Query Language). Aby uruchomić Spark SQL w swoim notesie należy utworzyć kontekst SQL.

*from pyspark import SparkConf, SparkContext*

*from pyspark.sql import SQLContext*

*from pyspark.sql import functions as fn* 

*import findspark*

*findspark.init() #aby umożliwić importowanie pyspark jako zwykłej biblioteki.*

*import warnings*


*conf = SparkConf().setMaster("local[4]").setAppName("Sentiment\_Project")  # 4 wątki*

*sc = SparkContext.getOrCreate(conf = conf)*

*sqlContext = SQLContext(sc)*

*tweet\_clean\_df = sqlContext.read.csv('/HdiNotebooks/tweets\_pandemic\_clean.csv', header=True, inferSchema=True)*
*tweet\_clean\_df = sqlContext.read.csv('/HdiNotebooks/tweets\_pandemic\_clean.csv', header=True, inferSchema=True)*

Zostaje utworzony DataFrame Spark z wcześniej zapisanych danych w formacie csv.

*inferSchema  zostaje ustawiony na na True , aby* automatycznie wnioskować typy kolumn na podstawie danych. 

Z nowego DataFrame zostają usunięte puste wiersze i następuje przegląd negatywnyc , pozytywnych  postów i obliczenie średniej długości obu rodzaju tweetów. 

Do dalszej analizy jest dodany słownik z predefiniowanymi emocjami.

![](Praca\_końcowa\_Żaneta\_Szymańska.025.png)Słownik został utworzony na podstawie listy pozytywnych i negatywnych słów, które zostały znalezione na udostępnionym publicznym GitHub (<https://github.com/sridharswamy/Twitter-Sentiment-Analysis-Using-Spark-Streaming-And-Kafka/tree/master/Dataset>).

Słowa z tweetów są porównywane ze słowami z DataFrame a ich sentyment są porównywane. Zatem wyznaczone przez TextBlob sentymenty są porównywane ze słownikiem sentymentów i jest wyznaczana dokładność pomiaru sentymentów. 

Do tego celu najlepiej posiadać taką samą liczbę badanej wartości w tym przypadku dokładności wyznaczania sentymentów. Zatem na początku ujednolicam liczbę postów pozytywnych i negatywnych do liczby tweetów ze mniejszego zbioru. Tak przygotowane dane poddaje ponownie procesowi tokenizacji (tym razem dla obiektu DataFrame Spark) .  Następnie zbiór słów zostaje porównany ze słownikiem , rozbijając podzielone słowa na różne wiersze za pomocą funkcji fn.explode i łącząc DataFrame’y. Poprzez średnią ocenę słów dla każdego tweeta i post zostaje sklasyfikowany jako „Pozytywny”, gdy średnia jest większa niż 0 i "Negatywny", jeśli jest mniejsza niż 0, a następnie obliczony zostaje wynik dokładności tej metody.

*token = RegexTokenizer().setGaps(False).setPattern("\\p{L}+").setInputCol("tweet").setOutputCol("splittweet")*

*word\_df = token.transform(tweet\_clean\_df)*

*from pyspark.sql import functions as fn* 

*df\_predict =*

` `*df\_joined\_wo\_null.groupBy('id').agg(fn.avg('sentiment').alias('avg\_sentim')).withColumn('pred\_sentim',*

` `*fn.when(fn.col('avg\_sentim') > 0, 1).otherwise(0))*

*result=tweet\_clean\_df.join(df\_predict, 'id').select(fn.expr('float(sentiment =*

` `*pred\_sentim)').alias('accuracy\_method')).select(fn.avg('accuracy\_method'))*


Tą metodę można nazwać metodą słownikową, która następnie porównamy z modelem regresji logistycznej.

**4.6. Prezentacja  wyników w postaci graficznej** 

`	`Gdy tweety są już oczyszczone można przejść do kolejnego etapu analizy postów jakim jest wizualizacja i wyciąganie pierwszych wniosków. 

W tej cześći przedstawione są dwa wnioski :

\1. Do pierwszego zoobrazowania została użyta bibliotekia Wordcloud, aby zobaczyć częstotliwość słów zgodnie z kolumną tweet. Wykorzystana została bilinearna metoda interpolacji, aby zwiększyć płynność tekstu w chmurze.


*arr = df\_new.tweet.values*

*obj = np.array2string(arr, precision=2, separator=',',suppress\_small=True)*

*type(obj)*

*wordcloud = WordCloud(width=1600, height=800,max\_font\_size=200).generate(obj)*

*plt.figure(figsize=(12,10))*

*plt.imshow(wordcloud, interpolation="bilinear")*

*plt.axis("off")*

*plt.show()*

\2. Kolejna wizualizacja prezentuje wykres słupkowy, który przedstawia całkowitą liczbę pozytywnych i negatywnych słów dla ogólnego porównania nastrojów. W celu przedstawienia sentymentów została użyta metoda groupby na kolumnie sentymenty (indeksowanie po tej kolumnie zostało pominięte)

*df\_grouped = df\_new.groupby('sentiment', as\_index = False).count()*

*labels\_word = ['Negative','Positive']*

*ax = df\_grouped.plot(kind = 'bar', x = 'sentiment', y='tweet')*

*ax.set\_xticklabels(labels\_word)*

*ax.set\_xticklabels(labels\_word)*



**4.7. Implementacja uczenia maszynowego dla klasyfikacji textu przy użyciu Pyspark ML**

`	`W tej czeście będzie wykorzystywane metody z następujących bibliotek:

– pyspark.ml

– pyspark.ml.linalg

--pyspark.ml.classification

– pyspark.ml.feature

Kolejne procesy będą służyć przygotowaniu danych do obliczenia wyiku dokładności przy uzyciu modelu regresji logistycznej.

Aby taki model powstał należy wykonać następujące kroki:

\1) Usunięcie zbędnych słów (stop words) z tweetów 

W tym celu została wykorzystana lista „stop words” dostępna publicznie na stronie lextek (http://www.lextek.com/manuals/onix/stopwords1.html)

![](Praca\_końcowa\_Żaneta\_Szymańska.029.png)










*from pyspark.ml.feature import StopWordsRemover*

*filter = StopWordsRemover().setStopWords(stop\_words).setCaseSensitive(False).setInputCol("splittweet").setOutputCol("words\_filter")*

*filter = StopWordsRemover().setStopWords(stop\_words).setCaseSensitive(False).setInputCol("splittweet").setOutputCol("words\_filter")*Słowa znajdujące się na tej liście zostały usunięte z postów przy użyciu metody *StopWordsRemover.*






\2) Liczenie wektoryzatora - CountVectorizer

CountVectorizer i CountVectorizerModel mają na celu pomóc w konwersji kolekcji dokumentów tekstowych na wektory liczby tokenów. Gdy słownik nie jest dostępny, CountVectorizer może służyć jako estymator do wyodrębniania słownictwa i generuje CountVectorizerModel. Model tworzy rzadkie reprezentacje dokumentów w słowniku, które mogą być następnie przekazywane do innych algorytmów. 

Dla tweetów CountVectorizer utworzy słownik o rozmiarze 131, który zawiera terminy pandemic, wait, data czy offering. Następnie nastąpi dopasowanie modelu CountVectorizer. Podczas procesu dopasowania CountVectorizer wybierze najlepsze słowa VocabSize uporządkowane według częstotliwości terminów. Model wytworzy rzadki wektor, który można wprowadzić do innych algorytmów.

\3) Pipeline Estymator

W uczeniu maszynowym często uruchamia się sekwencję algorytmów do przetwarzania danych i uczenia się na ich podstawie. Np. Prosty proces przetwarzania dokumentów tekstowych może obejmować kilka etapów:

– Podziel tekst każdego dokumentu na słowa (stage = token)

– Usuń zbędne słow tzw. stop words (stage = filter)

– Konwertuj słowa każdego dokumentu na numeryczny wektor cech (stage = vector\_count)

MLlib reprezentuje taki przepływ pracy jak potok, który składa się z sekwencji PipelineStages (transformatorów i estymatorów) uruchamianych w określonej kolejności. 


*C\_Pipeline\_Est = Pipeline(stages=[token, filter, vector\_count]).fit(tweet\_clean\_df.limit(1000))*
*C\_Pipeline\_Est = Pipeline(stages=[token, filter, vector\_count]).fit(tweet\_clean\_df.limit(1000))*![](Praca\_końcowa\_Żaneta\_Szymańska.032.png)



**4) IDF (Odwrotna częstotliwość dokumentu- Inverse Document Frequency)**

Termin „częstotliwość odwrotna częstotliwości dokumentu” (IDF) jest metodą wektoryzacji cech szeroko stosowaną w eksploracji tekstów, aby odzwierciedlić znaczenie terminu w dokumencie. Oznaczając termin przez t, dokument przez d, a korpus przez D, to częstotliwość dokumentu DF (t, D) jest liczbą dokumentów zawierających termin t. Jeśli do pomiaru ważności uzywa się tylko częstotliwości terminów, bardzo łatwo jest przecenić terminy, które pojawiają się bardzo często, ale zawierają niewiele informacji o dokumencie, np. „A”, „the” i „of”. Jeśli termin pojawia się bardzo często w całym korpusie, oznacza to, że nie zawiera specjalnych informacji o konkretnym dokumencie. Odwrotna częstotliwość dokumentów jest liczbową miarą ilości informacji dostarczanych przez termin:

![](Praca\_końcowa\_Żaneta\_Szymańska.033.png)


gdzie | D | to całkowita liczba dokumentów w korpusie. Ponieważ używany jest logarytm, jeśli termin pojawia się we wszystkich dokumentach, jego wartość IDF przyjmuje wartość 0. Należy zauważyć, że stosowany jest termin wygładzający, aby uniknąć dzielenia przez zero dla terminów spoza korpusu. Wartość TF-IDF jest po prostu produktem TF i IDF:

![](Praca\_końcowa\_Żaneta\_Szymańska.034.png)


Istnieje kilka wariantów definicji częstotliwości terminów i częstotliwości dokumentów. W spark.mllib oddzielamy TF i IDF, aby były elastyczne.

*from pyspark.ml.feature import IDF*

*IDF = IDF().setInputCol('TF').setOutputCol('TF\_IDF')*

*IDF\_pip = Pipeline(stages=[C\_Pipeline\_Est, IDF]).fit(tweet\_clean\_df)*

*TF\_IDF = IDF\_pip.transform(tweet\_clean\_df)*

*TF\_IDF.select('id', 'words\_filter', 'TF', "TF\_IDF").show(4)*

Zatem obliczony IDF zostaje dodany do Pipeline tworząc szereg transformacji dla tweetów.
Do modelu machine learning niezbędne jest wydzielenie z całości zbioru danych treningowych, danych walidacyjnych i danych testowych. Wybrałam podział w stosunku 80:10:10 

![](Praca\_końcowa\_Żaneta\_Szymańska.036.png)

![](Praca\_końcowa\_Żaneta\_Szymańska.037.png)

**Model regresji logistycznej**

Dla kolejnego wyliczenia wyniku dokładności został użyty prosty model regresji jakim jest model regresji logistycznej. Regresja logistyczna to algorytm klasyfikacji uczenia maszynowego, który jest używany do przewidywania prawdopodobieństwa jakościowej zmiennej zależnej. W regresji logistycznej zmienną zależną jest zmienna binarna, która zawiera dane zakodowane jako 1 (tak, sukces itp.) lub 0 (nie, niepowodzenie itp.). Innymi słowy, model regresji logistycznej przewiduje P (Y = 1) jako funkcję X.

Założenia regresji logistycznej:

– Binarna regresja logistyczna wymaga, aby zmienna zależna była binarna.

– W przypadku regresji binarnej poziom czynnika 1 zmiennej zależnej powinien reprezentować pożądany wynik.

– Należy uwzględnić tylko znaczące zmienne.

– Zmienne niezależne powinny być od siebie niezależne. Oznacza to, że model powinien mieć niewielką lub żadną współliniowość.

– Regresja logistyczna wymaga dość dużych próbek.

W celu wyznaczenia modelu regresji logistycznej została użyta biblioteka pyspark.ml.classification i metoda LogisticRegression. 

![](Praca\_końcowa\_Żaneta\_Szymańska.038.png)

Jak widzimy do pipeline zIDF dodajemy model regresji logistycznej i uruchamiamy go na danych treningowych. Tak przetrenowany model zostaje zastosowany na danych walidacyjnych a następnie na danych testowych w celu wyznaczenia predykcji sentymentów.

Rezultatem końcowym jest wynik dokładności (accuracy) uczenia poprzez model regesji logistycznej. 


*acc = pred\_test.filter(pred\_test.sentiment ==* 

*pred\_test.prediction).count() / float(df\_test.count())*



Wynik można porównać z wynikiem metody słownikowej, która była obliczona we wcześniejszeym etapie i zobaczyć, czy podejście uczenia maszynowego daje lepsze rezultaty niż proste porównanie słownikowe.
