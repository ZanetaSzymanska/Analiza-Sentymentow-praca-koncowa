#!/bin/bash

sudo apt install python-dev libffi-dev libssl-dev
sudo apt remove python-openssl
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --force-reinstall

#python3 -m pip install scikit-learn
#python3 -m pip install -U pip setuptools wheel
#python3 -m pip install -U spacy
#python3 -m spacy download en
#python3 -m spacy download en_core_web_sm
#python3 -m spacy download xx_ent_wiki_sm

python3 -m pip install virtualenv
mkdir gettweets
cd gettweets
virtualenv gettweets
source gettweets/bin/activate
pip install tweepy progressbar pyOpenSSL requests[security]
pip install TextBlob

#pip install scikit-learn
#pip install -U pip setuptools wheel
#pip install -U spacy
#python -m spacy download en
#python -m spacy download en_core_web_sm
#python -m spacy download xx_ent_wiki_sm
